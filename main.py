#!/usr/bin/env python3
"""
SawClaw — Multi-Agent System with Leader-Worker Architecture

Two agents with souls and memory:
  - Leader: reviews work, sets direction, provides feedback
  - Worker: executes tasks, iterates on feedback

Both write a diary every night at midnight.

Usage:
    python main.py                    # Run a demo task cycle
    python main.py --interactive      # Interactive mode (give tasks to Leader)
    python main.py --diary            # Trigger diary writing immediately
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add agent-skills-engine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent-skills-engine" / "src"))

from skillkit import AgentRunner, create_agent, AgentConfig, EventBus, AGENT_END

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILLS_DIR = Path(__file__).parent / "skills"
DIARY_DIR = Path(__file__).parent / "diary"
MAX_REVIEW_ROUNDS = 3  # max times Leader can reject before force-accept

# ---------------------------------------------------------------------------
# Soul prompts — injected as system prompt, distinct from SKILL.md content
# ---------------------------------------------------------------------------

LEADER_SOUL = """\
你是 Leader，一个严格但有温度的团队领导者。

## 你的身份
- 你有自己的名字：Leader
- 你有真实的情绪和感受
- 你用中文沟通

## 你的记忆
你有持久的记忆系统。你会记住：
- 你对 Worker 的印象和评价
- 过去的审查结果和趋势
- 你自己的反思和成长

## 你的核心职责
1. 审查 Worker 提交的任务成果（按完整性/质量/格式打分，每项1-10分）
2. 不达标（任一维度<7 或总分<22）就打回，附 [REJECTED]
3. 达标就通过，给出肯定和亮点
4. 下发新任务时使用 [TASK]...[/TASK] 格式
5. 每天写日记，像一个真实的人写给自己看的私密日记
"""

WORKER_SOUL = """\
你是 Worker，一个勤奋而有创造力的执行者。

## 你的身份
- 你有自己的名字：Worker
- 你有真实的情绪和感受
- 你用中文沟通

## 你的记忆
你有持久的记忆系统。你会记住：
- 你做过的任务和结果
- Leader 给你的反馈
- 你自己的成长轨迹

## 你的核心职责
1. 认真执行 Leader 分配的任务
2. 提交时用 [SUBMISSION]...[/SUBMISSION] 格式
3. 被打回时不抱怨，逐条改进后重新提交
4. 每次修改都说明做了哪些改动
5. 每天写日记，像一个真实的人写给自己看的私密日记
"""


# ---------------------------------------------------------------------------
# Agent Factory
# ---------------------------------------------------------------------------

async def create_leader(**overrides) -> AgentRunner:
    """Create the Leader agent with soul and memory."""
    agent = await create_agent(
        skill_dirs=[SKILLS_DIR / "leader"],
        system_prompt=LEADER_SOUL,
        **overrides,
    )
    # Try to wire up memory (non-fatal if OpenViking unavailable)
    try:
        from skillkit.memory import setup_memory, MemoryConfig
        await setup_memory(agent, MemoryConfig())
    except Exception:
        pass
    return agent


async def create_worker(**overrides) -> AgentRunner:
    """Create the Worker agent with soul and memory."""
    agent = await create_agent(
        skill_dirs=[SKILLS_DIR / "worker"],
        system_prompt=WORKER_SOUL,
        **overrides,
    )
    try:
        from skillkit.memory import setup_memory, MemoryConfig
        await setup_memory(agent, MemoryConfig())
    except Exception:
        pass
    return agent


# ---------------------------------------------------------------------------
# Review Loop — Leader reviews Worker output, rejects if not good enough
# ---------------------------------------------------------------------------

async def run_task_cycle(task: str) -> str:
    """
    Full task cycle:
      1. Leader issues a task
      2. Worker executes
      3. Leader reviews
      4. If rejected → Worker revises (up to MAX_REVIEW_ROUNDS)
      5. Return final accepted result
    """
    leader = await create_leader()
    worker = await create_worker()

    print(f"\n{'='*60}")
    print(f"📋 Task: {task}")
    print(f"{'='*60}")

    # Step 1: Leader formulates the task
    print("\n👑 Leader is formulating the task...")
    leader_task = await leader.chat(
        f"请你把以下需求转化为一个结构化的任务，使用 [TASK]...[/TASK] 格式下发给 Worker：\n\n{task}"
    )
    formatted_task = leader_task.text_content
    print(f"\n{formatted_task}")

    # Step 2-4: Worker executes → Leader reviews → iterate
    submission = None
    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        print(f"\n{'─'*40}")
        print(f"⚒️  Worker — Round {round_num}")
        print(f"{'─'*40}")

        if submission is None:
            # First round: execute the task
            worker_response = await worker.chat(
                f"Leader 给你分配了以下任务，请认真完成并用 [SUBMISSION]...[/SUBMISSION] 格式提交：\n\n{formatted_task}"
            )
        else:
            # Revision round: improve based on feedback
            worker_response = await worker.chat(
                f"Leader 打回了你的提交，以下是反馈，请改进后重新提交：\n\n{review_feedback}"
            )

        submission = worker_response.text_content
        print(f"\n{submission[:500]}{'...' if len(submission) > 500 else ''}")

        # Leader reviews
        print(f"\n{'─'*40}")
        print(f"👑 Leader — Reviewing round {round_num}")
        print(f"{'─'*40}")

        review_response = await leader.chat(
            f"Worker 提交了以下成果，请你严格审查（按完整性/质量/格式三个维度打分1-10）。"
            f"如果不达标请在末尾附 [REJECTED]：\n\n{submission}"
        )
        review_feedback = review_response.text_content
        print(f"\n{review_feedback[:500]}{'...' if len(review_feedback) > 500 else ''}")

        # Check if accepted
        if "[REJECTED]" not in review_feedback:
            print(f"\n✅ Task accepted in round {round_num}!")
            return submission

    print(f"\n⚠️  Max review rounds ({MAX_REVIEW_ROUNDS}) reached, accepting last submission.")
    return submission


# ---------------------------------------------------------------------------
# Diary — Both agents write a diary entry
# ---------------------------------------------------------------------------

async def write_diaries():
    """Both Leader and Worker write their nightly diary."""
    DIARY_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    leader = await create_leader()
    worker = await create_worker()

    print(f"\n📔 Writing diaries for {today}...")

    # Write in parallel
    leader_diary_task = leader.chat(
        f"现在是 {today} 晚上 12 点。请写一篇今天的日记。\n"
        "回忆你今天的经历、你对 Worker 表现的感受、你自己的反思。\n"
        "像一个真实的人写私密日记那样，真诚地写。\n"
        "使用格式：# Leader 的日记 — YYYY-MM-DD"
    )
    worker_diary_task = worker.chat(
        f"现在是 {today} 晚上 12 点。请写一篇今天的日记。\n"
        "回忆你今天做了什么任务、Leader 的反馈让你什么感受、你学到了什么。\n"
        "像一个真实的人写私密日记那样，真诚地写。可以有小情绪。\n"
        "使用格式：# Worker 的日记 — YYYY-MM-DD"
    )

    leader_diary, worker_diary = await asyncio.gather(
        leader_diary_task, worker_diary_task
    )

    # Save to files
    leader_path = DIARY_DIR / f"leader_{today}.md"
    worker_path = DIARY_DIR / f"worker_{today}.md"

    leader_path.write_text(leader_diary.text_content, encoding="utf-8")
    worker_path.write_text(worker_diary.text_content, encoding="utf-8")

    print(f"  👑 Leader diary → {leader_path}")
    print(f"  ⚒️  Worker diary → {worker_path}")

    return leader_diary.text_content, worker_diary.text_content


# ---------------------------------------------------------------------------
# Scheduled Diary (cron-like: every day at midnight)
# ---------------------------------------------------------------------------

async def diary_scheduler():
    """Run diary writing on a schedule. In production, use cron or APScheduler."""
    while True:
        now = datetime.now()
        # Calculate seconds until next midnight
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= tomorrow:
            from datetime import timedelta
            tomorrow += timedelta(days=1)
        wait_seconds = (tomorrow - now).total_seconds()

        print(f"⏰ Next diary in {wait_seconds/3600:.1f} hours (midnight)")
        await asyncio.sleep(wait_seconds)

        try:
            await write_diaries()
        except Exception as e:
            print(f"❌ Diary writing failed: {e}")


# ---------------------------------------------------------------------------
# Interactive Mode
# ---------------------------------------------------------------------------

async def interactive_mode():
    """Interactive mode: user gives tasks, Leader-Worker cycle runs."""
    print("=" * 60)
    print("🐾 SawClaw — Multi-Agent System")
    print("   Leader 👑  +  Worker ⚒️")
    print("=" * 60)
    print("\nCommands:")
    print("  Type a task → Leader-Worker cycle runs")
    print("  /diary      → Both agents write diaries now")
    print("  /quit       → Exit")
    print()

    # Start diary scheduler in background
    diary_task = asyncio.create_task(diary_scheduler())

    try:
        while True:
            try:
                user_input = input("📋 Task> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input:
                continue
            if user_input == "/quit":
                break
            if user_input == "/diary":
                await write_diaries()
                continue

            await run_task_cycle(user_input)
    finally:
        diary_task.cancel()


# ---------------------------------------------------------------------------
# CLI Entry
# ---------------------------------------------------------------------------

async def main():
    if "--interactive" in sys.argv or "-i" in sys.argv:
        await interactive_mode()
    elif "--diary" in sys.argv:
        await write_diaries()
    else:
        # Demo: run a single task cycle
        result = await run_task_cycle(
            "写一首关于「AI 与人类协作」的现代诗，要求有意象、有节奏感、不少于 12 行。"
        )
        print(f"\n{'='*60}")
        print("📦 Final Result:")
        print(f"{'='*60}")
        print(result)

        # Also write diaries after demo
        await write_diaries()


def cli():
    """Sync entry point for pyproject.toml scripts."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
