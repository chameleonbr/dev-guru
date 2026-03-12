from pydantic import BaseModel, Field
from typing import List, Optional

class SkillSummary(BaseModel):
    name: str
    description: str
    version: Optional[str] = "0.1.0"

class SkillDetail(SkillSummary):
    instructions: str
    files: List[str]

class AddSkillRequest(BaseModel):
    url: Optional[str] = None
    zip_base64: Optional[str] = None
    overwrite: bool = False

class InstallResponse(BaseModel):
    message: str
    installed_skills: List[str]

class MessageResponse(BaseModel):
    message: str
