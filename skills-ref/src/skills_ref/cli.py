"""CLI for skills-ref library."""

import json
import sys
from pathlib import Path

import click

from .errors import SkillError
from .parser import read_properties
from .prompt import to_prompt
from .validator import validate


def _is_skill_md_file(path: Path) -> bool:
    """Check if path points directly to a SKILL.md or skill.md file."""
    return path.is_file() and path.name.lower() == "skill.md"


@click.group()
@click.version_option()
def main():
    """Reference library for Agent Skills."""
    pass


@main.command("validate")
@click.argument("skill_path", type=click.Path(exists=True, path_type=Path))
def validate_cmd(skill_path: Path):
    """Validate a skill directory.

    Checks that the skill has a valid SKILL.md with proper frontmatter,
    correct naming conventions, and required fields.

    Exit codes:
        0: Valid skill
        1: Validation errors found
    """
    if _is_skill_md_file(skill_path):
        skill_path = skill_path.parent

    errors = validate(skill_path)

    if errors:
        click.echo(f"Validation failed for {skill_path}:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        sys.exit(1)
    else:
        click.echo(f"Valid skill: {skill_path}")


@main.command("read-properties")
@click.argument("skill_path", type=click.Path(exists=True, path_type=Path))
def read_properties_cmd(skill_path: Path):
    """Read and print skill properties as JSON.

    Parses the YAML frontmatter from SKILL.md and outputs the
    properties as JSON.

    Exit codes:
        0: Success
        1: Parse error
    """
    try:
        if _is_skill_md_file(skill_path):
            skill_path = skill_path.parent

        props = read_properties(skill_path)
        click.echo(json.dumps(props.to_dict(), indent=2))
    except SkillError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("to-prompt")
@click.argument(
    "skill_paths", type=click.Path(exists=True, path_type=Path), nargs=-1, required=True
)
def to_prompt_cmd(skill_paths: tuple[Path, ...]):
    """Generate <available_skills> XML for agent prompts.

    Accepts one or more skill directories.

    Exit codes:
        0: Success
        1: Error
    """
    try:
        resolved_paths = []
        for skill_path in skill_paths:
            if _is_skill_md_file(skill_path):
                resolved_paths.append(skill_path.parent)
            else:
                resolved_paths.append(skill_path)

        output = to_prompt(resolved_paths)
        click.echo(output)
    except SkillError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
