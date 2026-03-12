from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Annotated, Optional
from src.skill_models import (
    SkillSummary, 
    SkillDetail, 
    AddSkillRequest, 
    InstallResponse, 
    MessageResponse
)
from src.services import SkillManager
import os

router = APIRouter(prefix="/skills", tags=["Skills"])

# This would ideally be managed by a dependency injection setup in the main app
_manager: Optional[SkillManager] = None

def get_skill_manager() -> SkillManager:
    global _manager
    if _manager is None:
        # Fallback if not initialized
        _manager = SkillManager(skills_dir="skills")
    return _manager

def set_skill_manager(manager: SkillManager):
    global _manager
    _manager = manager

@router.get("", response_model=List[SkillSummary])
async def list_skills(manager: Annotated[SkillManager, Depends(get_skill_manager)]):
    return manager.list_skills()

@router.get("/{name}", response_model=SkillDetail)
async def get_skill(name: str, manager: Annotated[SkillManager, Depends(get_skill_manager)]):
    skill = manager.get_skill(name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found.")
    return skill

@router.post("", response_model=InstallResponse, status_code=status.HTTP_201_CREATED)
async def add_skill(
    body: AddSkillRequest, 
    manager: Annotated[SkillManager, Depends(get_skill_manager)]
):
    try:
        installed = await manager.install_skill(
            url=body.url, 
            zip_base64=body.zip_base64, 
            overwrite=body.overwrite
        )
        return InstallResponse(
            message=f"Successfully installed {len(installed)} skill(s).",
            installed_skills=installed
        )
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=InstallResponse, status_code=status.HTTP_201_CREATED)
async def upload_skill(
    manager: Annotated[SkillManager, Depends(get_skill_manager)],
    file: UploadFile = File(...),
    overwrite: bool = Form(False)
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=422, detail="Only .zip files are supported.")
    
    try:
        content = await file.read()
        installed = manager._extract_and_install_skills(content, overwrite=overwrite)
        return InstallResponse(
            message=f"Successfully installed {len(installed)} skill(s).",
            installed_skills=installed
        )
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{name}", response_model=MessageResponse)
async def delete_skill(name: str, manager: Annotated[SkillManager, Depends(get_skill_manager)]):
    if manager.delete_skill(name):
        return MessageResponse(message=f"Skill '{name}' deleted successfully.")
    raise HTTPException(status_code=404, detail=f"Skill '{name}' not found.")
