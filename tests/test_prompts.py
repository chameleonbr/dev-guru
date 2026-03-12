from src.prompts import build_system_prompt, build_user_prompt
from src.models import ConsultInput

def test_build_system_prompt():
    prompt = build_system_prompt()
    assert "senior development consultant" in prompt.lower()
    assert "JSON" in prompt
    assert "'thinking'" in prompt
    assert "'suggestions'" in prompt

def test_build_user_prompt():
    data = ConsultInput(
        level="novice",
        technologies="python, mcp",
        context="print('hello')",
        thinking="I want to say hello"
    )
    prompt = build_user_prompt(data)
    assert "Level: novice" in prompt
    assert "Technologies: python, mcp" in prompt
    assert "print('hello')" in prompt
    assert "I want to say hello" in prompt
