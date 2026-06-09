"""Exponential backoff retry helper (Challenge 3)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    operation: str = "operation",
) -> T:
    """Retry an async callable with exponential backoff."""
    last_exc: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await fn()
        except Exception as exc:
            last_exc = exc
            if attempt == max_attempts:
                break

            from common.observability import record_metric

            record_metric("retries")
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            logger.warning(
                "%s failed (attempt %d/%d): %s — retrying in %.1fs",
                operation,
                attempt,
                max_attempts,
                exc,
                delay,
            )
            await asyncio.sleep(delay)

    assert last_exc is not None
    raise last_exc
