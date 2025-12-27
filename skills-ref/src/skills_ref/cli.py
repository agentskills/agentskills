"""CLI for skills-ref library."""

import json
import sys
from pathlib import Path

import click

from .errors import SkillError
from .graph import CompositionGraph, validate_composition
from .parser import read_properties
from .prompt import to_prompt
from .validator import typecheck_composition, validate


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


@main.command("graph")
@click.argument(
    "skill_paths", type=click.Path(exists=True, path_type=Path), nargs=-1, required=True
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["ascii", "mermaid", "json"]),
    default="ascii",
    help="Output format for the graph.",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Check for circular dependencies and missing skills.",
)
def graph_cmd(skill_paths: tuple[Path, ...], format: str, validate: bool):
    """Visualize the composition graph of skills.

    Accepts one or more skill directories or root directories containing skills.
    Shows how skills compose each other and detects circular dependencies.

    Output formats:
        ascii:   ASCII tree representation (default)
        mermaid: Mermaid diagram syntax for documentation
        json:    JSON representation of nodes and edges

    Examples:
        skills-ref graph ./skills/_atomic ./skills/_composite
        skills-ref graph --format=mermaid ./skills
        skills-ref graph --no-validate ./skills

    Exit codes:
        0: Success (and valid if --validate)
        1: Errors found (cycles or missing dependencies)
    """
    graph = CompositionGraph()

    # Add all skills from provided paths
    for skill_path in skill_paths:
        if _is_skill_md_file(skill_path):
            graph.add_skill(skill_path.parent)
        elif skill_path.is_dir():
            # Check if it's a skill directory or a root containing skills
            from .parser import find_skill_md

            if find_skill_md(skill_path):
                graph.add_skill(skill_path)
            else:
                graph.add_skills_from_directory(skill_path)

    if not graph.nodes:
        click.echo("No skills found in the provided paths.", err=True)
        sys.exit(1)

    # Perform validation if requested
    if validate:
        analysis = graph.analyze()

        if analysis.cycles:
            click.echo("Circular dependencies detected:", err=True)
            for cycle in analysis.cycles:
                click.echo(f"  - {cycle}", err=True)

        if analysis.missing_dependencies:
            click.echo("Missing dependencies:", err=True)
            for skill, missing in analysis.missing_dependencies.items():
                for dep in missing:
                    click.echo(f"  - '{skill}' requires unknown skill '{dep}'", err=True)

        if analysis.level_violations:
            click.echo("Level hierarchy warnings:", err=True)
            for warning in analysis.level_violations:
                click.echo(f"  - {warning}", err=True)

        if not analysis.is_valid:
            click.echo("", err=True)
            click.echo(
                f"Graph has {len(analysis.cycles)} cycle(s) and "
                f"{sum(len(m) for m in analysis.missing_dependencies.values())} "
                f"missing dependency reference(s).",
                err=True,
            )

    # Output the graph
    click.echo("")
    if format == "ascii":
        click.echo(graph.to_ascii())
    elif format == "mermaid":
        click.echo(graph.to_mermaid())
    elif format == "json":
        analysis = graph.analyze()
        output = {
            "nodes": {
                name: {
                    "level": node.level,
                    "operation": node.operation,
                    "composes": node.composes,
                    "path": str(node.path) if node.path else None,
                }
                for name, node in analysis.nodes.items()
            },
            "edges": dict(analysis.edges),
            "statistics": {
                "total_skills": len(analysis.nodes),
                "roots": analysis.get_roots(),
                "leaves": analysis.get_leaves(),
                "cycles": len(analysis.cycles),
                "missing_deps": sum(len(m) for m in analysis.missing_dependencies.values()),
            },
        }
        click.echo(json.dumps(output, indent=2))

    # Exit with error if validation failed
    if validate:
        analysis = graph.analyze()
        if not analysis.is_valid:
            sys.exit(1)


@main.command("typecheck")
@click.argument(
    "skill_paths", type=click.Path(exists=True, path_type=Path), nargs=-1, required=True
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed type information for each skill."
)
def typecheck_cmd(skill_paths: tuple[Path, ...], verbose: bool):
    """Type-check skill compositions for type compatibility.

    Validates that composed skills have compatible input/output types,
    similar to static type checking in strongly-typed languages.

    This catches composition errors at build time:
    - Input type mismatches between parent and child skills
    - Output type mismatches in composition chains
    - Missing required inputs for composed skills

    Examples:
        skills-ref typecheck ./skills
        skills-ref typecheck -v ./skills/_composite ./skills/_workflows
        skills-ref typecheck ./skills/trip-optimize

    Exit codes:
        0: All type checks pass
        1: Type errors found
    """
    from .parser import find_skill_md

    # Collect all skills
    all_skills = {}
    skill_dirs = []

    for skill_path in skill_paths:
        if _is_skill_md_file(skill_path):
            skill_dirs.append(skill_path.parent)
        elif skill_path.is_dir():
            if find_skill_md(skill_path):
                skill_dirs.append(skill_path)
            else:
                # Recursively find all skills in directory
                for skill_md in skill_path.rglob("SKILL.md"):
                    skill_dirs.append(skill_md.parent)
                for skill_md in skill_path.rglob("skill.md"):
                    if skill_md.parent not in skill_dirs:
                        skill_dirs.append(skill_md.parent)

    if not skill_dirs:
        click.echo("No skills found in the provided paths.", err=True)
        sys.exit(1)

    # Load all skill properties
    for skill_dir in skill_dirs:
        try:
            props = read_properties(skill_dir)
            all_skills[props.name] = props
            if verbose:
                inputs_str = ", ".join(
                    f"{f.name}: {f.type}" for f in (props.inputs or [])
                ) or "(none)"
                outputs_str = ", ".join(
                    f"{f.name}: {f.type}" for f in (props.outputs or [])
                ) or "(none)"
                click.echo(f"Loaded: {props.name}")
                click.echo(f"  inputs:  {inputs_str}")
                click.echo(f"  outputs: {outputs_str}")
                if props.composes:
                    click.echo(f"  composes: {', '.join(props.composes)}")
                click.echo("")
        except SkillError as e:
            click.echo(f"Warning: Could not load {skill_dir}: {e}", err=True)

    # Type-check all skills that have composition
    all_errors = []
    checked_count = 0

    for name, props in all_skills.items():
        if not props.composes:
            continue

        checked_count += 1
        errors = typecheck_composition(props, all_skills)
        if errors:
            all_errors.append((name, errors))

    # Report results
    if verbose:
        click.echo(f"Type-checked {checked_count} composed skill(s)")
        click.echo("")

    if all_errors:
        click.echo("Type errors found:", err=True)
        for skill_name, errors in all_errors:
            click.echo(f"\n  {skill_name}:", err=True)
            for error in errors:
                click.echo(f"    - {error}", err=True)
        click.echo("")
        click.echo(
            f"Found {sum(len(e) for _, e in all_errors)} type error(s) "
            f"in {len(all_errors)} skill(s).",
            err=True,
        )
        sys.exit(1)
    else:
        click.echo(
            f"All type checks passed ({checked_count} composed skill(s), "
            f"{len(all_skills)} total skill(s))"
        )


if __name__ == "__main__":
    main()
