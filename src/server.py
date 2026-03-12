from fastmcp import FastMCP
import json
import logging
from .models import ConsultInput, ConsultOutput
from .prompts import build_user_prompt
from .router import get_agent
from .config import settings

# Initialize FastMCP server
mcp = FastMCP("dev-guru")
logger = logging.getLogger(__name__)

@mcp.tool()
async def call_guru(
    level: str, 
    technologies: str, 
    context: str, 
    thinking: str
) -> str:
    """
    Dev Guru is a tool that helps agents to solve coding problems. 
    When you are afraid, your user is angry, or you are just lazy to ask for help, Dev Guru is here to help you.
    
    Args:
        level: Complexity level ('novice', 'medium', 'expert').
        technologies: Comma-separated list of technologies(e.g., 'python, fastapi, mcp, sqlalchemy, docker, kubernetes').
        context: Markdown with all code references(files, functions, classes, etc.) and context(what the user wants to do).
        thinking: Current agent reasoning.
        
    Returns:
        str: The agent's response in markdown format.
    """
    try:
        # 1. Validate input
        input_data = ConsultInput(
            level=level,
            technologies=technologies,
            context=context,
            thinking=thinking
        )
        
        # 2. Build prompt
        prompt = build_user_prompt(input_data)
        
        # 3. Get appropriate agent
        agent = get_agent(input_data.level)
        
        # 4. Run agent (using arun for async)
        response = await agent.arun(prompt)

        return response.content
        
    except Exception as e:
        logger.error(f"Error during consultation: {str(e)}", exc_info=True)
        # Basic error handling and fallback
        return f"An error occurred during consultation: {str(e)}"

if __name__ == "__main__":
    mcp.run()
