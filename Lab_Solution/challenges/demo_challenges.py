"""Demo các Bài Tập Nâng Cao (CODELAB Phần 6).

Chạy: uv run python challenges/demo_challenges.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from common.conversation_memory import append_exchange, format_history, get_history
from common.observability import get_metrics, setup_langsmith, trace_operation
from common.retry import retry_async


async def demo_memory() -> None:
    print("\n=== Challenge 1: Conversation Memory ===")
    ctx = "demo-session-001"
    append_exchange(ctx, "What is an NDA?", "An NDA is a non-disclosure agreement.")
    append_exchange(ctx, "What happens if it is breached?", "Breach may trigger damages and injunctions.")

    print(f"History turns: {len(get_history(ctx))}")
    print(format_history(ctx))


async def demo_retry() -> None:
    print("\n=== Challenge 3: Retry with Exponential Backoff ===")
    attempts = 0

    async def flaky_call() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError(f"simulated failure #{attempts}")
        return "success"

    result = await retry_async(flaky_call, max_attempts=3, operation="flaky_call")
    print(f"Result after {attempts} attempts: {result}")


def demo_observability() -> None:
    print("\n=== Challenge 4: Observability ===")
    setup_langsmith()
    with trace_operation("demo_operation", agent="challenge_runner"):
        pass
    print(f"Metrics snapshot: {get_metrics()}")
    print("LangSmith: set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY to enable tracing.")


def demo_auth() -> None:
    print("\n=== Challenge 2: API Key Authentication ===")
    key = os.getenv("A2A_API_KEY")
    if key:
        print("A2A_API_KEY is set — agents require X-API-Key header.")
    else:
        print("A2A_API_KEY not set — auth disabled (OK for local dev).")
        print("Set A2A_API_KEY in .env to enable authentication.")


async def main() -> None:
    print("=" * 60)
    print("ADVANCED CHALLENGES DEMO")
    print("=" * 60)

    demo_auth()
    await demo_memory()
    await demo_retry()
    demo_observability()

    print("\n" + "=" * 60)
    print("Done. For full A2A test: .\\start_all.ps1 then uv run python test_client.py")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
