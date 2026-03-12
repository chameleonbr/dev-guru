from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from .config import settings
from .models import ConsultOutput
from .prompts import build_system_prompt
from agno.skills import Skills, LocalSkills

def _create_agent(
    model_class: type,
    primary_api_key: str | None,
    model_id: str,
    openrouter_fallback_prefix: str
) -> Agent:
    """
    Generic agent factory that handles model instantiation and OpenRouter fallback.
    """
    if primary_api_key:
        model = model_class(id=model_id, api_key=primary_api_key)
    else:
        # For OpenRouter, ensure the model ID has the correct provider prefix
        full_model_id = model_id if "/" in model_id else f"{openrouter_fallback_prefix}/{model_id}"
        model = OpenRouter(id=full_model_id, api_key=settings.openrouter_api_key)
    
    return Agent(
        model=model,
        instructions=[build_system_prompt()],
        output_schema=ConsultOutput,
        skills=Skills([LocalSkills("./skills"),LocalSkills("../skills")]),
        markdown=True,
        description="Developer Guru"
    )

def get_gemini_agent() -> Agent:
    return _create_agent(
        model_class=Gemini,
        primary_api_key=settings.gemini_api_key,
        model_id=settings.novice_model,
        openrouter_fallback_prefix="google"
    )

def get_claude_agent() -> Agent:
    return _create_agent(
        model_class=Claude,
        primary_api_key=settings.anthropic_api_key,
        model_id=settings.medium_model,
        openrouter_fallback_prefix="anthropic"
    )

def get_openai_agent() -> Agent:
    return _create_agent(
        model_class=OpenAIChat,
        primary_api_key=settings.openai_api_key,
        model_id=settings.advanced_model,
        openrouter_fallback_prefix="openai"
    )
