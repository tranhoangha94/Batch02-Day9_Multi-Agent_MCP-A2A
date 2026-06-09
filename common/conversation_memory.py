"""In-process conversation memory keyed by A2A context_id (Challenge 1)."""

from __future__ import annotations

from collections import defaultdict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

_history: dict[str, list[BaseMessage]] = defaultdict(list)
_MAX_MESSAGES = 20


def get_history(context_id: str, *, max_messages: int = 10) -> list[BaseMessage]:
    """Return recent messages for a conversation thread."""
    messages = _history.get(context_id, [])
    return messages[-max_messages:]


def append_exchange(context_id: str, question: str, answer: str) -> None:
    """Store a user question and assistant answer."""
    thread = _history[context_id]
    thread.append(HumanMessage(content=question))
    thread.append(AIMessage(content=answer))
    if len(thread) > _MAX_MESSAGES:
        del thread[: len(thread) - _MAX_MESSAGES]


def format_history(context_id: str) -> str:
    """Format prior turns as plain text for prompts."""
    lines: list[str] = []
    for msg in get_history(context_id):
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)
