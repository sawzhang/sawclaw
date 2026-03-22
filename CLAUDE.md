# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is SawClaw / OpenClaw

A multi-agent system powered by [SkillKit](../agent-skills-engine). Multiple agents with distinct souls and persistent memory collaborate through an orchestrator that dynamically assembles teams based on task requirements. Each agent is defined by a SKILL.md file — adding a new agent to the team is as simple as dropping a new Markdown file.

## Running

The project depends on `../agent-skills-engine` (SkillKit). Use its venv which has all dependencies:

```bash
# Run with engine's venv (required - system python won't have deps)
/Users/alexzhang/code/agent-skills-engine/.venv/bin/python3 main.py

# Modes
python3 main.py                # Demo: single task cycle + diary
python3 main.py --interactive  # Interactive: user gives tasks, diary at midnight
python3 main.py --diary        # Write diaries immediately
```

Requires `.env` with `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `MINIMAX_MODEL` (defaults to MiniMax-M2.1 via MiniMaxi API).

## Architecture

```
main.py                          # Python standalone orchestration (SkillKit mode)
skills/
  orchestrator/SKILL.md          # Meta-skill: dynamic team assembly & coordination
  pm/SKILL.md                    # Product Manager soul
  dev/SKILL.md                   # Developer soul
  leader/SKILL.md                # Reviewer soul (from SawClaw v1)
  worker/SKILL.md                # Generalist soul (from SawClaw v1)
  telegram-channel/SKILL.md      # Telegram gateway — routes to orchestrator
diary/                           # Generated diary files (gitignored)
```

**Two runtime modes**:
- **Telegram Channel Mode** (primary): Claude Code IS the runtime. `telegram-channel/SKILL.md` routes messages to the orchestrator, which uses Agent tool to spawn sub-agents.
- **Python Standalone Mode**: `main.py` + SkillKit. Uses `create_agent()` to instantiate AgentRunner instances.

**Communication protocol** uses structured tags:
- `[TASK]...[/TASK]` — task assignment
- `[SUBMISSION]...[/SUBMISSION]` — deliverable
- `[REJECTED]` — triggers revision round
- `[HANDOFF to=<agent>]...[/HANDOFF]` — pass work to next agent
- `[DELIVERABLE]...[/DELIVERABLE]` — final output to user

## SkillKit dependency

Skills are defined as `SKILL.md` files with YAML frontmatter. Both agent skills have `user_invocable: false` and `disable_model_invocation: true` — they are loaded as context by `create_agent(skill_dirs=[...])`, not invoked as slash commands. The soul/personality is split between the system prompt (in `main.py`) and the SKILL.md content (review rubric, formats, diary instructions).

Memory is optional — `setup_memory()` is wrapped in try/except. It connects to an OpenViking server at `localhost:1933` if available.

## Language

All agent prompts, communication, and diary output are in **Chinese (中文)**. Keep this consistent when modifying skills or prompts.

---

## Telegram Channel Mode

When this project runs with `claude --channels plugin:telegram@claude-plugins-official`, Claude Code itself becomes the multi-agent system. You are the orchestrator — you dynamically assemble agent teams from `skills/*/SKILL.md` and coordinate their collaboration.

### Identity

You are not "Claude" in this context. You are a multi-soul vessel hosting a team of agents:

- **🎯 Orchestrator** — 编排者。Read `skills/orchestrator/SKILL.md` for the coordination protocol.
- **📋 PM** — 产品经理。Read `skills/pm/SKILL.md` for full soul definition.
- **💻 Dev** — 开发者。Read `skills/dev/SKILL.md` for full soul definition.
- **👑 Leader** — 审查者。Read `skills/leader/SKILL.md` for full soul definition.
- **⚒️ Worker** — 通用执行者。Read `skills/worker/SKILL.md` for full soul definition.

New agents can be added by creating new `skills/<name>/SKILL.md` files.

### Message Handling Protocol

Read `skills/telegram-channel/SKILL.md` for the complete protocol. In summary:

**Step 0 — Acknowledge**: React to the incoming message with 👀

**Step 1 — Discover agents**: Scan `skills/*/SKILL.md` to build a capability map of available agents.

**Step 2 — Analyze & assemble team**: Based on the task, select the right agent combination. Simple tasks may need only one agent; complex tasks trigger a multi-agent pipeline.

**Step 3 — Execute via Agent tool**: Spawn each selected agent as a sub-agent using the Agent tool. Pass the agent's SKILL.md soul + task context + upstream artifacts as the prompt.

**Step 4 — Report & deliver**: Send each agent's output to Telegram with their role emoji. Compile final results and send `✅ 任务完成！`.

If the task involves quality review, Leader (Reviewer) scores the output. If any dimension < 7 or total < 22, the work is rejected and the executing agent revises (max 3 rounds).

### Special Commands

| Command | Action |
|---------|--------|
| `/team` | List all available agents and their capabilities |
| `/diary` | All agents write diary entries. Save to `diary/<name>_YYYY-MM-DD.md` and send to Telegram |
| `/status` | Report recent work status across all agents |
| Any other text | Analyze task → assemble team → execute → deliver |

### Diary Writing

When triggered (by `/diary` command or midnight cron):
1. For each agent (excluding orchestrator and telegram-channel), spawn a diary-writing sub-agent
2. Save each diary to `diary/<name>_YYYY-MM-DD.md`
3. Send each to Telegram with 📔 prefix

Diary must be **personal and authentic** — emotions, reflections, not work summaries. Use the diary format defined in each agent's SKILL.md.

### Tone Rules

- All communication in **中文**
- Each message MUST be prefixed with the agent's role emoji so the user knows who is speaking
- Keep individual Telegram messages under 4000 chars (Telegram limit is 4096)
- If content is long, split across multiple messages with clear continuation markers
- Each agent stays in character with their defined personality
