import pytest
from src.router import get_agent
from src.config import settings
from unittest.mock import patch

def test_router_novice():
    with patch("src.config.settings.gemini_api_key", "test_key"):
        agent = get_agent("novice")
        assert agent.description == "Developer Guru"

def test_router_medium():
    with patch("src.config.settings.anthropic_api_key", "test_key"):
        agent = get_agent("medium")
        assert agent.description == "Developer Guru"

def test_router_expert_openai():
    with patch("src.config.settings.openai_api_key", "test_key"):
        agent = get_agent("expert")
        assert agent.description == "Developer Guru"

def test_router_expert_openrouter():
    with patch("src.config.settings.openai_api_key", None):
        with patch("src.config.settings.openrouter_api_key", "test_key"):
            agent = get_agent("expert")
            assert agent.description == "Developer Guru"

def test_router_invalid_level():
    with pytest.raises(ValueError, match="Invalid level"):
        get_agent("god_mode")

def test_router_missing_config():
    with patch("src.config.settings.gemini_api_key", None):
        with patch("src.config.settings.openrouter_api_key", None):
            with pytest.raises(ValueError, match="GEMINI_API_KEY or OPENROUTER_API_KEY is required"):
                get_agent("novice")
