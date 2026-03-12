from agno.agent import Agent
from .config import settings, validate_config_for_level
from .providers import get_gemini_agent, get_claude_agent, get_openai_agent

def get_agent(level: str) -> Agent:
    """
    Rotes the request to the appropriate Agno agent based on the requested level.
    """
    # 1. Validate that the required configuration exists for the level
    validate_config_for_level(level)
    
    # 2. Route to the correct provider
    if level == "novice":
        return get_gemini_agent()
    elif level == "medium":
        return get_claude_agent()
    elif level == "expert":
        return get_openai_agent()
    else:
        raise ValueError(f"Invalid level: {level}. Choice from 'novice', 'medium', 'expert'.")
