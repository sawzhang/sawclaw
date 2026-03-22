# SawClaw / OpenClaw — Multi-Agent System

A dynamic multi-agent system where agents are defined by SKILL.md files and an orchestrator routes work via HANDOFF chains.

## Agents

| Agent | Emoji | Role | Capabilities | Outputs To | Accepts From |
|-------|-------|------|-------------|------------|--------------|
| **Orchestrator** | 🎯 | Orchestrator | 团队组建, 任务编排, 协调调度, 进度管控 | — | — |
| **PM** | 📋 | PM | 需求分析, 用户故事, 优先级排序, 产品规划 | dev | orchestrator |
| **Dev** | 💻 | Dev | 代码实现, 架构设计, 技术选型, 问题排查 | leader | orchestrator, pm |
| **Leader** | 👑 | Reviewer | 质量审查, 反馈指导, 标准把控, 团队激励 | dev, worker, pm | orchestrator, dev, worker, pm |
| **Worker** | ⚒️ | Generalist | 任务执行, 内容创作, 调研分析, 文档撰写 | leader | orchestrator, leader |

## Adding a New Agent

Create `skills/<name>/SKILL.md` with frontmatter containing `name`, `metadata.emoji`, `metadata.role`, `metadata.capabilities`, `metadata.outputs_to`, and `metadata.accepts_from`. The orchestrator will auto-discover it.

## Communication Protocol

Agents communicate using structured tags:

- `[TASK]...[/TASK]` — task assignment
- `[SUBMISSION]...[/SUBMISSION]` — intermediate deliverable
- `[REJECTED]...[/REJECTED]` — triggers revision round
- `[HANDOFF to=<agent>]...[/HANDOFF]` — agent-driven routing to next agent
- `[DELIVERABLE]...[/DELIVERABLE]` — final output (terminates chain)
- `[SCHEDULED_TASK]...[/SCHEDULED_TASK]` — cron-triggered task marker

### HANDOFF-driven Routing

Instead of the orchestrator hardcoding pipelines, **agents declare who handles work next**:

1. Agent completes work → includes `[HANDOFF to=X]` in output
2. Orchestrator parses the tag → spawns agent X with upstream context
3. Chain continues until `[DELIVERABLE]` or no HANDOFF
4. Safety: max 10 hops, max 3 review rounds per agent pair

### Example Flow

```
User: "设计一个登录功能"

📋 PM → [SUBMISSION] 需求文档 + [HANDOFF to=dev]
💻 Dev → [SUBMISSION] 技术方案 + [HANDOFF to=leader]
👑 Leader → [REJECTED] + [HANDOFF to=dev]  (质量不达标)
💻 Dev → [SUBMISSION] 修改版 + [HANDOFF to=leader]
👑 Leader → 通过！
🎯 Orchestrator → ✅ 任务完成！[DELIVERABLE]
```

## Review Standards

Submissions scored on 3 dimensions (1-10): Completeness, Quality, Format.
Pass threshold: each dimension >= 7, total >= 22.

## Scheduled Tasks

Agents can declare recurring schedules in their SKILL.md metadata:

```yaml
metadata:
  schedules:
    - cron: "57 23 * * *"
      task: "diary_all"
      description: "所有 agent 写日记"
```

Schedules are auto-registered via CronCreate on session start. Session-scoped (7-day expiry).

## Diary

All agents write personal diary entries. Saved to `diary/<name>_YYYY-MM-DD.md`.
Triggered by `/diary` command or daily cron at 23:57.
