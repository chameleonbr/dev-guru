"""
Optional API-Key security for Dev Guru.

When API_KEY is set in the environment, all REST and MCP endpoints
require the X-API-Key header. When not set, endpoints are open.
"""
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .config import settings

# ---------------------------------------------------------------------------
# REST API-Key dependency (used by FastAPI routes)
# ---------------------------------------------------------------------------
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    api_key: Annotated[Optional[str], Security(_api_key_header)] = None,
) -> Optional[str]:
    """
    Validate the API key if one is configured.
    If API_KEY is not set, all requests are allowed.
    """
    if not settings.api_key:
        return None  # No key configured — open access

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header missing.",
        )
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    return api_key


# ---------------------------------------------------------------------------
# MCP Auth Middleware (used for the mounted FastMCP ASGI sub-app)
# ---------------------------------------------------------------------------
class MCPAuthMiddleware(BaseHTTPMiddleware):
    """Protect the /mcp endpoint with the same X-API-Key used by the REST API."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Only enforce on /mcp paths
        if not request.url.path.startswith("/mcp"):
            return await call_next(request)

        # Skip enforcement if no API_KEY is configured
        if not settings.api_key:
            return await call_next(request)

        key = request.headers.get("X-API-Key", "")
        if not key:
            return Response(
                content='{"detail": "X-API-Key header missing."}',
                status_code=401,
                media_type="application/json",
            )
        if key != settings.api_key:
            return Response(
                content='{"detail": "Invalid API key."}',
                status_code=403,
                media_type="application/json",
            )
        return await call_next(request)
