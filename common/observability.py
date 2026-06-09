"""Lightweight observability helpers (Challenge 4)."""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)

_metrics: dict[str, int] = {
    "agent_invocations": 0,
    "delegations": 0,
    "retries": 0,
    "errors": 0,
}


def setup_langsmith() -> None:
    """Enable LangSmith tracing when LANGCHAIN_TRACING_V2=true."""
    if os.getenv("LANGCHAIN_TRACING_V2", "").lower() != "true":
        return

    project = os.getenv("LANGCHAIN_PROJECT", "legal-multiagent")
    logger.info("LangSmith tracing enabled (project=%s)", project)


def record_metric(name: str, amount: int = 1) -> None:
    _metrics[name] = _metrics.get(name, 0) + amount


def get_metrics() -> dict[str, int]:
    return dict(_metrics)


@contextmanager
def trace_operation(name: str, **metadata: Any):
    """Log duration and count for an operation."""
    record_metric("agent_invocations")
    start = time.perf_counter()
    logger.info("START %s %s", name, metadata or "")
    try:
        yield
    except Exception:
        record_metric("errors")
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("END %s (%.0fms) metrics=%s", name, elapsed_ms, get_metrics())
