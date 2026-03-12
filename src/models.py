from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class ConsultInput(BaseModel):
    level: Literal["novice", "medium", "expert"] = Field(
        ..., 
        description="Complexity level of the consultation: novice, medium, or expert."
    )
    technologies: str = Field(
        ..., 
        description="Comma-separated list of technologies involved (e.g., 'python, fastapi, mcp')."
    )
    context: str = Field(
        ..., 
        description="Markdown block containing relevant code or project context."
    )
    thinking: str = Field(
        ..., 
        description="Markdown block containing the agent's current reasoning or problem description."
    )

class ConsultOutput(BaseModel):
    thinking: str = Field(
        ..., 
        description="Refined reasoning and analysis from the consultant in markdown."
    )
    suggestions: List[str] = Field(
        ..., 
        description="List of actionable suggestions or code snippets in markdown."
    )
