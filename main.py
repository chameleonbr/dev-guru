import logging
import os
from fastapi import FastAPI
from src.routes.skills import router as skills_router, set_skill_manager
from src.services import SkillManager
from src.config import settings
from src.server import mcp
from src.security import MCPAuthMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Dev Guru API", debug=settings.debug)

# Initialize SkillManager
skills_dir = os.path.join(os.getcwd(), "skills")
manager = SkillManager(skills_dir=skills_dir)
set_skill_manager(manager)

# Include routes
app.include_router(skills_router)

# MCP Auth Middleware (enforced only when API_KEY is set)
app.add_middleware(MCPAuthMiddleware)

# Get the MCP ASGI app and mount it
mcp_app = mcp.http_app(path="/mcp")
app.mount("/", mcp_app)

# Log security status
if settings.api_key:
    logger.info("API_KEY is set — endpoints are protected with X-API-Key header.")
else:
    logger.warning("API_KEY is not set — endpoints are open (no authentication).")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Dev Guru API",
        "mcp_enabled": True,
        "mcp_endpoint": "/mcp"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
