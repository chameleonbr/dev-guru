from .models import ConsultInput

SYSTEM_PROMPT_TEMPLATE = """You are a senior development consultant.
Analyze the provided code reasoning, identify flaws, or confirm the approach.
You MUST respond in JSON format with exactly two fields: 'thinking' (string markdown) and 'suggestions' (array of strings markdown).
Do not include any text before or after the JSON block. Do not include markdown formatting like ```json ... ``` unless specifically required by the protocol.

Adapt your depth and language to the requested level:
- 'novice': Educational, providing clear examples and detailed explanations.
- 'medium': Direct and professional, discussing trade-offs and best practices.
- 'expert': Concise and advanced, focusing on architectural patterns, performance, and subtle edge cases.

The provided technologies define the scope. Do not suggest migrating to a completely different stack.
"""

USER_PROMPT_TEMPLATE = """## Level: {level}
## Technologies: {technologies}

### Context (Relevant Code)
{context}

### Agent's Reasoning
{thinking}

Analyze the reasoning above, refine it, and provide actionable suggestions.
Respond in JSON: {{ "thinking": "...", "suggestions": ["...", ...] }}
"""

def build_system_prompt() -> str:
    """Returns the system prompt for the consultant agent."""
    return SYSTEM_PROMPT_TEMPLATE

def build_user_prompt(data: ConsultInput) -> str:
    """Builds the user prompt injecting the consultation data."""
    return USER_PROMPT_TEMPLATE.format(
        level=data.level,
        technologies=data.technologies,
        context=data.context,
        thinking=data.thinking
    )
