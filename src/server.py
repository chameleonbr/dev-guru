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
) -> dict:
    """
    Dev Guru is a tool that helps agents to solve coding problems. 
    When you are afraid, your user is angry, or you are just lazy to ask for help, Dev Guru is here to help you.
    
    Args:
        level: Complexity level ('novice', 'medium', 'expert').
        technologies: Comma-separated list of technologies(e.g., 'python, fastapi, mcp, sqlalchemy, docker, kubernetes').
        context: Markdown with all code references(files, functions, classes, etc.) and context(what the user wants to do).
        thinking: Current agent reasoning.
        
    Returns:
        A dictionary with 'thinking' (refined analysis) and 'suggestions' (actionable items).
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
        
        # 5. Extract structured output
        # Agno's output_schema puts the parsed object in response.content
        result = response.content
        logger.info(f"Agent returned: {result}")
        
        # If it's the expected Pydantic model
        if isinstance(result, ConsultOutput):
            return result.model_dump()
        
        # If it's a dictionary (some providers/settings might return this)
        if isinstance(result, dict):
            try:
                return ConsultOutput.model_validate(result).model_dump()
            except Exception:
                return result
            
        # If it's a string, attempt to parse it manually
        if isinstance(result, str):
            logger.info("Agent returned string content, attempting manual parsing.")
            try:
                clean_text = result.strip()
                
                # Extract JSON using outermost braces to avoid being fooled by internal backticks
                start_index = clean_text.find('{')
                end_index = clean_text.rfind('}')
                
                if start_index != -1 and end_index != -1:
                    clean_text = clean_text[start_index:end_index + 1]
                
                # Try to validate as JSON and match our schema
                parsed = ConsultOutput.model_validate_json(clean_text)
                return parsed.model_dump()
            except Exception as parse_err:
                logger.error(f"Manual parsing failed: {parse_err}. Raw content: {result}")
                # Last resort: try to find any JSON-like dict in the string
                return {
                    "thinking": result,
                    "suggestions": ["Failed to parse structured output. Raw response is above."]
                }

        # Fallback for other types
        return {
            "thinking": str(result),
            "suggestions": ["Unexpected response type from agent."]
        }
        
    except Exception as e:
        logger.error(f"Error during consultation: {str(e)}", exc_info=True)
        # Basic error handling and fallback
        return {
            "thinking": f"An error occurred during consultation: {str(e)}",
            "suggestions": [
                "The AI response could not be parsed as structured JSON.",
                "Verify your API keys and try again with a simpler context.",
                "Check the server logs for the raw response if this persists."
            ]
        }

if __name__ == "__main__":
    mcp.run()
