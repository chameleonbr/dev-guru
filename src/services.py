import os
import shutil
import zipfile
import base64
import io
import httpx
from typing import List, Optional
from .skill_models import SkillSummary, SkillDetail

class SkillManager:
    def __init__(self, skills_dir: str):
        self.skills_dir = os.path.abspath(skills_dir)
        os.makedirs(self.skills_dir, exist_ok=True)

    def list_skills(self) -> List[SkillSummary]:
        skills = []
        for name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, name)
            if os.path.isdir(skill_path):
                # Basic skill discovery: look for SKILL.md
                skill_md = os.path.join(skill_path, "SKILL.md")
                description = "No description available."
                if os.path.exists(skill_md):
                    with open(skill_md, "r") as f:
                        # Extract first few lines for description
                        lines = f.readlines()
                        description = "".join(lines[:5]).strip()
                
                skills.append(SkillSummary(
                    name=name,
                    description=description
                ))
        return skills

    def get_skill(self, name: str) -> Optional[SkillDetail]:
        skill_path = os.path.join(self.skills_dir, name)
        if not os.path.isdir(skill_path):
            return None
        
        skill_md = os.path.join(skill_path, "SKILL.md")
        instructions = ""
        if os.path.exists(skill_md):
            with open(skill_md, "r") as f:
                instructions = f.read()
        
        files = []
        for root, _, filenames in os.walk(skill_path):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), skill_path)
                files.append(rel_path)
        
        return SkillDetail(
            name=name,
            description=instructions[:100], # Simplified
            instructions=instructions,
            files=files
        )

    async def install_skill(
        self, 
        url: Optional[str] = None, 
        zip_base64: Optional[str] = None, 
        overwrite: bool = False
    ) -> List[str]:
        zip_data = None
        if url:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                zip_data = response.content
        elif zip_base64:
            zip_data = base64.b64decode(zip_base64)
        else:
            raise ValueError("URL or zip_base64 must be provided.")

        return self._extract_and_install_skills(zip_data, overwrite)

    def _extract_and_install_skills(self, zip_data: bytes, overwrite: bool) -> List[str]:
        installed = []
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            # We assume the zip contains a folder which is the skill
            # Or multiple folders
            for name in z.namelist():
                if name.endswith("/") or "/" not in name:
                    continue
                
                # Get the top-level directory name
                top_dir = name.split("/")[0]
                if top_dir not in installed:
                    target_path = os.path.join(self.skills_dir, top_dir)
                    if os.path.exists(target_path):
                        if not overwrite:
                            raise FileExistsError(f"Skill '{top_dir}' already exists.")
                        shutil.rmtree(target_path)
                    
                    # Extract only files belonging to this top_dir
                    for member in z.namelist():
                        if member.startswith(top_dir + "/"):
                            z.extract(member, self.skills_dir)
                    
                    installed.append(top_dir)
        return installed

    def delete_skill(self, name: str) -> bool:
        skill_path = os.path.join(self.skills_dir, name)
        if os.path.isdir(skill_path):
            shutil.rmtree(skill_path)
            return True
        return False

    def delete_all_skills(self) -> int:
        count = 0
        for name in os.listdir(self.skills_dir):
            if self.delete_skill(name):
                count += 1
        return count
