"""CLI for skills-ref library."""

import json
import sys
from pathlib import Path

import click

from .errors import SkillError
from .evaluator import evaluate_skill
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


@main.command("evaluate")
@click.argument("skill_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
@click.option(
    "--min-score",
    type=float,
    default=0.0,
    help="Minimum acceptable overall score (0-100)",
)
def evaluate_cmd(skill_path: Path, output_json: bool, min_score: float):
    """Evaluate a skill for quality metrics.

    Assesses skill completeness, clarity, and structure, providing
    scores and actionable findings for improvement.

    Exit codes:
        0: Skill passes evaluation
        1: Skill has errors or score below threshold
    """
    try:
        if _is_skill_md_file(skill_path):
            skill_path = skill_path.parent

        result = evaluate_skill(skill_path)

        if output_json:
            # JSON output
            output = {
                "skill_path": str(result.skill_path),
                "skill_name": result.skill_name,
                "scores": result.scores,
                "overall_score": result.overall_score,
                "findings": [
                    {
                        "severity": f.severity.value,
                        "category": f.category,
                        "message": f.message,
                        "suggestion": f.suggestion,
                    }
                    for f in result.findings
                ],
            }
            click.echo(json.dumps(output, indent=2))
        else:
            # Human-readable output
            click.echo(f"\n{'='*60}")
            click.echo(f"Skill Quality Evaluation: {result.skill_name or skill_path.name}")
            click.echo(f"{'='*60}\n")

            # Scores
            click.echo("Scores:")
            for dimension, score in sorted(result.scores.items()):
                color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
                click.echo(
                    f"  {dimension.capitalize():15s}: "
                    + click.style(f"{score:.1f}/100", fg=color)
                )
            click.echo(
                f"  {'Overall':15s}: "
                + click.style(f"{result.overall_score:.1f}/100", bold=True)
            )

            # Findings
            if result.findings:
                click.echo(f"\nFindings ({len(result.findings)}):")
                for finding in result.findings:
                    severity_color = (
                        "red"
                        if finding.severity == "error"
                        else "yellow" if finding.severity == "warning" else "blue"
                    )
                    click.echo(
                        f"\n  [{click.style(finding.severity.upper(), fg=severity_color)}] "
                        f"{finding.category}: {finding.message}"
                    )
                    if finding.suggestion:
                        click.echo(f"    → {finding.suggestion}")
            else:
                click.echo("\n✓ No findings - excellent skill quality!")

            click.echo()

        # Exit with error if there are errors or score is below threshold
        if result.has_errors or result.overall_score < min_score:
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
