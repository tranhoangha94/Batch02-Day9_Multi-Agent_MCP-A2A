"""API key authentication for A2A FastAPI apps (Challenge 2)."""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

API_KEY_HEADER = "X-API-Key"
DEFAULT_EXEMPT_PATHS = {"/.well-known/agent.json", "/health"}


def get_a2a_api_key() -> str | None:
    """Return configured API key, or None if auth is disabled."""
    return os.getenv("A2A_API_KEY") or None


def install_api_key_auth(app, exempt_paths: set[str] | None = None) -> None:
    """Attach API-key middleware when A2A_API_KEY is set in the environment."""
    api_key = get_a2a_api_key()
    if not api_key:
        return

    paths = exempt_paths or DEFAULT_EXEMPT_PATHS

    class APIKeyMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            if request.url.path in paths:
                return await call_next(request)

            provided = request.headers.get(API_KEY_HEADER)
            if provided != api_key:
                return JSONResponse(
                    {"error": "Unauthorized", "detail": "Invalid or missing API key"},
                    status_code=401,
                )
            return await call_next(request)

    app.add_middleware(APIKeyMiddleware)


def auth_headers() -> dict[str, str]:
    """Headers for outbound A2A HTTP calls."""
    api_key = get_a2a_api_key()
    if not api_key:
        return {}
    return {API_KEY_HEADER: api_key}
