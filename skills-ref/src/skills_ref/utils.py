import json


SUPPORTING_AGENTS_FILE = 'docs/supporting_agents.json'

def build_skill_instructions_template(
    name: str = "skill-name",
    description: str = "Describe what this skill does and when to use it"
):
    """
    Building the skill instruction template.

    Args:
        name: Name of the skill (default "skill-name")
        description: Description of the skill (default "skill-name")

    Returns:
        the markdown specification.
    """
    return f"""---\nname: {name}\ndescription: {description}.\n---\n# {name.replace("-", " ").title()}\n## Instructions\nAdd your skill instructions here.\n"""

def load_supporting_agents()-> list:
    """
    Load all agents that support the Agent Skills format.

    Returns:
        List of all agents that support the skill.
    """
    supporting_agents = []
    with open(SUPPORTING_AGENTS_FILE, 'r') as file:
        supporting_agents = json.load(file)
    return supporting_agents
