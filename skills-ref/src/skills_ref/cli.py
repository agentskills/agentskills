"""CLI for skills-ref library."""

import json
import sys
from pathlib import Path

import click

from .errors import SkillError
from .parser import read_properties
from .prompt import to_prompt
from .validator import validate
from .composition import check_composition


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


@main.command("compose")
@click.argument("source_path", type=click.Path(exists=True, path_type=Path))
@click.argument("target_path", type=click.Path(exists=True, path_type=Path))
def compose_cmd(source_path: Path, target_path: Path):
    """Check if two skills can be composed together.

    Validates that the source skill's output types are compatible with
    the target skill's input types. Skills without composition metadata
    are treated as unconstrained (always compatible).

    Example:
        skills-ref compose ./slack-search ./slack-read

    Exit codes:
        0: Composition is valid
        1: Composition is invalid or error occurred
    """
    if _is_skill_md_file(source_path):
        source_path = source_path.parent
    if _is_skill_md_file(target_path):
        target_path = target_path.parent

    result = check_composition(source_path, target_path)

    if result.valid:
        click.echo(f"✓ {result.source} → {result.target}")
        click.echo(f"  {result.reason}")
    else:
        click.echo(f"✗ {result.source} → {result.target}", err=True)
        click.echo(f"  {result.reason}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
