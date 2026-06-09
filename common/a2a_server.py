"""Shared helpers for A2A agent HTTP servers."""

from __future__ import annotations

from common.auth import install_api_key_auth
from common.observability import setup_langsmith


def finalize_agent_app(app):
    """Apply cross-cutting concerns to an agent FastAPI app."""
    setup_langsmith()
    install_api_key_auth(app)
    return app
