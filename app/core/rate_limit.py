"""Shared HTTP and WebSocket rate limiting configuration."""

from __future__ import annotations

from limits import parse
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.websockets import WebSocket

RATE_LIMIT = "60/minute"

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])
_websocket_limit = parse(RATE_LIMIT)


def websocket_rate_limit_key(websocket: WebSocket, user_id: str | None = None) -> str:
    """Build a stable per-user key, falling back to the client IP."""
    if user_id:
        return f"user:{user_id}"
    client_host = websocket.client.host if websocket.client else "unknown"
    return f"ip:{client_host}"


def allow_websocket_request(websocket: WebSocket, user_id: str | None = None) -> bool:
    """Consume one WebSocket request from the shared SlowAPI fixed window."""
    return limiter.limiter.hit(_websocket_limit, websocket_rate_limit_key(websocket, user_id))
