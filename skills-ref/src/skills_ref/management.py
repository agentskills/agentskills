import re
from collections import defaultdict
from pathlib import Path
import shutil

from .validator import check_if_skill_exist, _validate_name, _validate_description
from .parser import get_local_supporting_agents
from .utils import build_skill_instructions_template, load_supporting_agents
from .errors import SkillError, ValidationError


def create_skill(skill_name: str, skill_description: str, project_level: bool = True) -> list:
    """
    Creates a skill based on the project_level.
    
    Args:
        skill_name (str): The name of the skill.
        skill_description (str): The description of what the skill should do.
        project_level (bool): Specifies where the skill should be saved, (default: True).

    Returns:
        dict: dict of skill configs where the skill is saved per available agent.
    """
    if errors := _validate_name(skill_name):
        raise ValidationError("Invalid skill name",errors=errors)

    if errors := _validate_description(skill_name):
        raise ValidationError("Invalid skill name",errors=errors)

    if skill_info := check_if_skill_exist(skill_name=skill_name, project_level=project_level):
        return skill_info

    available_agents = get_local_supporting_agents()
    created_files = defaultdict()

    for agent in available_agents:
        base_path = Path.cwd() if project_level else Path.resolve(available_agents.get(agent).get('config_dir'))
        skill_dir = Path.joinpath(base_path, f'.{agent}/skills/{skill_name}')
        Path.mkdir(skill_dir, parents=True, exist_ok=True)
        skill_file = Path.joinpath(skill_dir, "SKILL.md")
        content = build_skill_instructions_template(name=skill_name, description=skill_description)
        skill_file.write_text(content)
        created_files[agent] = {'agent': agent, 'file': skill_file}

    return created_files

def edit_skill(skill_name: str, description: str = None, project_level: bool = True) -> list:
    """
    Edits a skills based on the project_level.
    
    Args:
        skill_name (str): The skill name 
        skill_description (str): The description of what the skill should do.
        project_level (bool): Specifies where the skill should be saved, (default: True)
                    if True the skill will be saved in the project scope, else it will be saved globally

    Returns:
        bool: Action completed successfully.
    """
    if errors := _validate_description(skill_name):
        raise ValidationError("Invalid skill name",errors=errors)

    if not (skill_files := check_if_skill_exist(skill_name=skill_name, project_level=project_level)):
          raise SkillError(f'Skill {skill_name}, not found.')
          
    for agent in skill_files:
        if skill_files.get(agent):
            skill_file = skill_files.get(agent)
            break

    initial_content = Path(skill_file).read_text()
    edited_content = re.sub(
        r'^description:\s*.*$',
        f'description: {description}',
        initial_content,
        count=1,
        flags=re.MULTILINE
    )

    for agent in skill_files:
        if skill_files.get(agent):
            skill_file = skill_files.get(agent)
            skill_file = Path(skill_file)
            skill_file.write_text(edited_content)
    return True

def delete_skill(skill_name: str, project_level: bool = True) -> bool:
    """
    Deletes a skills based on the project_level.

    Args:
        skill_name (str): The skill name 
        skill_description (str): The description of what the skill should do.
        project_level (bool): Specifies where the skill should be saved, (default: True)
                    if True the skill will be saved in the project scope, else it will be saved globally

    Returns:
        bool: Action completed successfully.
    """
    if not (skill_files := check_if_skill_exist(skill_name=skill_name, project_level=project_level)):
        raise SkillError(f'Skill {skill_name}, not found.')

    for agent in skill_files:
        if skill_files.get(agent):
            skill_file = (skill_files.get(agent))
            shutil.rmtree(Path(skill_file).parent)
    return True

def list_skills(project_level: bool = True) -> list:
    """
    Lists all the available skills based on the project_level.

    Args:
        project_level (bool): Specifies where the skill should be saved, (default: True)
                    if True the skill will be saved in the project scope, else it will be saved globally

    Returns:
        list: Action completed successfully.
    """
    base_path = Path.cwd() if project_level else Path.home()
    skills = []

    for supported_agent in load_supporting_agents():
        skill={}
        if agent_path := Path(f'{base_path}/{supported_agent.get("skills_dir")}').resolve():
            available_skills = [skill_dir for skill_dir in agent_path.iterdir() if skill_dir.is_dir()]
            skill[supported_agent.get('name')] = available_skills
            skills.append(skill)

    return skills
