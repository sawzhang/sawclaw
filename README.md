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
2. **Orchestrator analyzes** — determines what agents are needed
3. **Team assembles** — agents are spawned with their soul (SKILL.md) injected
4. **Pipeline executes** — agents collaborate sequentially or in parallel
5. **Quality review** — Leader scores output on completeness, quality, and format (each ≥ 7/10, total ≥ 22/30 to pass)
6. **Delivery** — final result sent back to user

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
---

# Agent Name — Soul & Persona

Define personality, beliefs, speaking style, capabilities, output format, and diary format here.
```

The orchestrator auto-discovers new agents on every task.

## Communication Protocol

Agents communicate using structured tags:

- `[TASK]...[/TASK]` — task assignment
- `[SUBMISSION]...[/SUBMISSION]` — deliverable
- `[REJECTED]` — triggers revision (max 3 rounds)
- `[HANDOFF to=<agent>]...[/HANDOFF]` — pass work downstream
- `[DELIVERABLE]...[/DELIVERABLE]` — final output

## License

MIT
