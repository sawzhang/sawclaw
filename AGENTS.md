# SawClaw / OpenClaw — Multi-Agent System

A dynamic multi-agent system where agents are defined by SKILL.md files and an orchestrator assembles teams on-the-fly.

## Agents

| Agent | Emoji | Role | Capabilities |
|-------|-------|------|-------------|
| **Orchestrator** | 🎯 | Orchestrator | 团队组建, 任务编排, 协调调度, 进度管控 |
| **PM** | 📋 | PM | 需求分析, 用户故事, 优先级排序, 产品规划 |
| **Dev** | 💻 | Dev | 代码实现, 架构设计, 技术选型, 问题排查 |
| **Leader** | 👑 | Reviewer | 质量审查, 反馈指导, 标准把控, 团队激励 |
| **Worker** | ⚒️ | Generalist | 任务执行, 内容创作, 调研分析, 文档撰写 |

## Adding a New Agent

Create `skills/<name>/SKILL.md` with frontmatter containing `name`, `metadata.emoji`, `metadata.role`, and `metadata.capabilities`. The orchestrator will auto-discover it.

## Communication Protocol

- `[TASK]...[/TASK]` — task assignment
- `[SUBMISSION]...[/SUBMISSION]` — deliverable
- `[REJECTED]` — triggers revision (max 3 rounds)
- `[HANDOFF to=<agent>]...[/HANDOFF]` — pass work downstream
- `[DELIVERABLE]...[/DELIVERABLE]` — final output

## Review Standards

Submissions scored on 3 dimensions (1-10): Completeness, Quality, Format.
Pass threshold: each dimension >= 7, total >= 22.

## Diary

All agents write personal diary entries. Saved to `diary/<name>_YYYY-MM-DD.md`.
