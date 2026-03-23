# SawClaw

A multi-agent system where agents with distinct souls and persistent memory collaborate through an orchestrator that dynamically assembles teams based on task requirements.

Each agent is defined by a single `SKILL.md` file — adding a new agent is as simple as dropping a new Markdown file.

## Agents

| Agent | Role | Capabilities |
|-------|------|-------------|
| 🎯 Orchestrator | Coordinator | Team assembly, task routing, progress control |
| 📋 PM | Product Manager | Requirement analysis, user stories, prioritization |
| 💻 Dev | Developer | Architecture, code implementation, tech decisions |
| 👑 Leader | Reviewer | Quality review, feedback, standards enforcement |
| ⚒️ Worker | Generalist | Task execution, content creation, research |

## Quick Start

### Telegram Channel Mode (Primary)

Run as a Telegram bot with Claude Code as the multi-agent runtime:

```bash
claude --channels plugin:telegram@claude-plugins-official
```

Messages sent to the bot are routed through the orchestrator, which assembles the right agent team for each task.

### Python Standalone Mode

Requires [SkillKit](https://github.com/anthropics/agent-skills-engine) as a sibling directory.

```bash
# Copy and configure environment
cp .env.example .env

# Run demo task cycle
python main.py

# Interactive mode
python main.py --interactive

# Write diaries immediately
python main.py --diary
```

## How It Works

1. **Task arrives** — via Telegram or CLI
2. **Orchestrator selects starting agent** — based on task analysis and agent capabilities
3. **HANDOFF chain executes** — starting agent completes work and declares `[HANDOFF to=next_agent]`, orchestrator follows the chain
4. **Quality review** — Leader scores output on completeness, quality, and format (each ≥ 7/10, total ≥ 22/30 to pass). Rejects route back via HANDOFF.
5. **Delivery** — chain terminates with `[DELIVERABLE]`, result sent to user

Routing is **agent-driven**: each agent declares who handles work next, rather than the orchestrator hardcoding pipelines.

## Adding a New Agent

Create `skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: my-agent
description: "What this agent does"
metadata:
  emoji: "🔧"
  role: "Specialist"
  capabilities: ["skill1", "skill2"]
  outputs_to: ["leader"]          # who this agent can hand off to
  accepts_from: ["orchestrator"]   # who can send work to this agent
  schedules:                       # optional recurring tasks
    - cron: "57 23 * * *"
      task: "diary"
      description: "每天深夜写日记"
---

# Agent Name — Soul & Persona

Define personality, beliefs, speaking style, capabilities, output format, handoff behavior, and diary format here.
```

The orchestrator auto-discovers new agents on every task.

## Communication Protocol

Agents communicate using structured tags:

- `[TASK]...[/TASK]` — task assignment
- `[SUBMISSION]...[/SUBMISSION]` — intermediate deliverable
- `[REJECTED]...[/REJECTED]` — triggers revision (max 3 rounds)
- `[HANDOFF to=<agent>]...[/HANDOFF]` — **agent-driven routing** to next agent
- `[DELIVERABLE]...[/DELIVERABLE]` — final output (terminates chain)

## Memory System

Agents have persistent memory that accumulates across tasks:

- **Personal memory** (`memory/<agent>/learnings.md`) — each agent's experience and lessons learned
- **Shared memory** (`memory/shared/`) — team-wide decisions, user preferences, conventions
- **Task log** (`memory/task_log.md`) — structured history of all completed tasks
- **Diary** (`diary/<name>_YYYY-MM-DD.md`) — daily emotional/reflective journal

The orchestrator injects relevant memory when spawning agents and writes back learnings after each task.

## Scheduled Tasks

Agents can declare recurring tasks in their SKILL.md metadata. Schedules are auto-registered via CronCreate on session start. Managed with `/cron` command.

## License

MIT
