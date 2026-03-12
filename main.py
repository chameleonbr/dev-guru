import os
from fastapi import FastAPI
from src.routes.skills import router as skills_router, set_skill_manager
from src.services import SkillManager
from src.config import settings
from src.server import mcp

app = FastAPI(title="Developer Guru API", debug=settings.debug)

# Initialize SkillManager
skills_dir = os.path.join(os.getcwd(), "skills")
manager = SkillManager(skills_dir=skills_dir)
set_skill_manager(manager)

# Include routes
app.include_router(skills_router)

# Get the MCP ASGI app
# This enables the MCP server to run alongside the skill management API
# Mounting at /mcp helps avoid conflicts with other routes
mcp_app = mcp.http_app(path="/mcp")
app.mount("/", mcp_app)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Developer Guru API",
        "mcp_enabled": True,
        "mcp_endpoint": "/mcp"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
