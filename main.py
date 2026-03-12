"""Application entrypoint.

Architecture:
  - FastAPI handles the REST control plane (/skills, /health)
  - FastMCP is mounted at /mcp via its ASGI http_app (StreamableHTTP transport)
  - Lifespan initializes the StreamableHTTPSessionManager task group

MCP endpoint:
  Clients connect to POST /mcp (StreamableHTTP) or GET /mcp/sse (SSE) depending
  on their transport preference.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from src.routes.skills import router as skills_router, set_skill_manager
from src.services import SkillManager
from src.config import settings
from src.server import mcp
from src.security import MCPAuthMiddleware

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Create the FastMCP ASGI app instance
# ---------------------------------------------------------------------------
mcp_app = mcp.http_app(path="/mcp")

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise shared resources on startup; clean up on shutdown."""
    logger.info("Starting up Dev Guru …")

    # Initialize SkillManager
    skills_dir = os.path.join(os.getcwd(), "skills")
    manager = SkillManager(skills_dir=skills_dir)
    set_skill_manager(manager)

    # Log security status
    if settings.api_key:
        logger.info("API_KEY is set — endpoints are protected with X-API-Key header.")
    else:
        logger.warning("API_KEY is not set — endpoints are open (no authentication).")

    logger.info("Dev Guru ready.")

    # Run the FastMCP ASGI app's lifespan context manager
    # This is REQUIRED to initialize the StreamableHTTPSessionManager task group.
    async with mcp_app.router.lifespan_context(app):
        yield  # ← server handles requests here

    logger.info("Shutting down.")


app = FastAPI(
    title="Dev Guru API",
    description=(
        "An AI-powered code consultation MCP server.\n\n"
        "- **REST control plane** (`/skills`): install, update, list, delete skills.\n"
        "- **MCP endpoint** (`/mcp`): StreamableHTTP transport for MCP clients."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware (Starlette applies in reverse registration order)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# MCPAuthMiddleware is added AFTER CORSMiddleware so that it runs FIRST
app.add_middleware(MCPAuthMiddleware)
# ProxyHeadersMiddleware runs before everything to set the client IP correctly
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# ---------------------------------------------------------------------------
# REST routes
# ---------------------------------------------------------------------------
app.include_router(skills_router)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="Health check")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})

# ---------------------------------------------------------------------------
# FastMCP mounted at /
#
# IMPORTANT: When FastAPI mounts at "/", it forwards everything.
# By passing mcp_app here, we ensure the same instance that has its
# lifespan initialized above is the one handling requests.
# ---------------------------------------------------------------------------
app.mount("/", mcp_app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
