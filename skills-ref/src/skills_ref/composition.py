"""Skill composition validation.

Validates that skills can be composed together based on type compatibility.
No arbitrary 'levels' - just output types matching input types.

Unix philosophy: any skill can pipe into any other skill if the types match.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .errors import SkillError
from .parser import find_skill_md, parse_frontmatter


@dataclass
class CompositionType:
    """Type declaration for skill input/output.

    Attributes:
        type_name: The type identifier (e.g., 'email-list', 'message-stream')
        description: Human-readable description of what this type contains
    """

    type_name: str
    description: Optional[str] = None

    def matches(self, other: "CompositionType") -> bool:
        """Check if this type is compatible with another type."""
        # Exact match
        if self.type_name == other.type_name:
            return True
        # Wildcard types
        if self.type_name == "*" or other.type_name == "*":
            return True
        return False


@dataclass
class SkillComposition:
    """Composition metadata for a skill.

    Attributes:
        name: Skill name
        inputs: List of types this skill can consume (empty = no input required)
        outputs: List of types this skill produces (empty = no structured output)
    """

    name: str
    inputs: list[CompositionType]
    outputs: list[CompositionType]

    def can_receive_from(self, other: "SkillComposition") -> bool:
        """Check if this skill can receive output from another skill."""
        if not other.outputs:
            return False  # Source produces nothing
        if not self.inputs:
            return True  # We accept anything (or nothing)

        # Check if any output matches any input
        for output in other.outputs:
            for input_type in self.inputs:
                if input_type.matches(output):
                    return True
        return False


@dataclass
class CompositionResult:
    """Result of a composition check."""

    valid: bool
    source: str
    target: str
    reason: str
    matched_type: Optional[str] = None


def parse_composition_metadata(metadata: dict) -> Optional[SkillComposition]:
    """Extract composition types from skill metadata.

    Looks for optional 'composition' field in frontmatter:
        composition:
          inputs: [email-list, message-list]
          outputs: [intel-brief]

    Returns None if no composition metadata present.
    """
    comp_data = metadata.get("composition")
    if not comp_data:
        return None

    name = metadata.get("name", "unknown")

    inputs = []
    if "inputs" in comp_data:
        input_list = comp_data["inputs"]
        if isinstance(input_list, list):
            inputs = [CompositionType(type_name=t) for t in input_list]
        elif isinstance(input_list, str):
            inputs = [CompositionType(type_name=input_list)]

    outputs = []
    if "outputs" in comp_data:
        output_list = comp_data["outputs"]
        if isinstance(output_list, list):
            outputs = [CompositionType(type_name=t) for t in output_list]
        elif isinstance(output_list, str):
            outputs = [CompositionType(type_name=output_list)]

    return SkillComposition(name=name, inputs=inputs, outputs=outputs)


def read_composition(skill_dir: Path) -> Optional[SkillComposition]:
    """Read composition metadata from a skill directory.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        SkillComposition if composition metadata exists, None otherwise

    Raises:
        SkillError: If skill directory is invalid or SKILL.md cannot be parsed
    """
    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        raise SkillError(f"Path does not exist: {skill_dir}")

    if not skill_dir.is_dir():
        raise SkillError(f"Not a directory: {skill_dir}")

    skill_md = find_skill_md(skill_dir)
    if skill_md is None:
        raise SkillError(f"Missing SKILL.md in {skill_dir}")

    content = skill_md.read_text()
    metadata, _ = parse_frontmatter(content)

    return parse_composition_metadata(metadata)


def check_composition(
    source_dir: Path, target_dir: Path
) -> CompositionResult:
    """Check if source skill can compose into target skill.

    Args:
        source_dir: Path to source skill directory
        target_dir: Path to target skill directory

    Returns:
        CompositionResult indicating validity and reason
    """
    try:
        source_comp = read_composition(source_dir)
        target_comp = read_composition(target_dir)
    except SkillError as e:
        return CompositionResult(
            valid=False,
            source=str(source_dir),
            target=str(target_dir),
            reason=str(e),
        )

    source_name = source_comp.name if source_comp else source_dir.name
    target_name = target_comp.name if target_comp else target_dir.name

    # No composition metadata = we can't validate
    if source_comp is None and target_comp is None:
        return CompositionResult(
            valid=True,
            source=source_name,
            target=target_name,
            reason="No composition constraints defined (both skills lack composition metadata)",
        )

    if source_comp is None:
        return CompositionResult(
            valid=True,
            source=source_name,
            target=target_name,
            reason=f"Source skill '{source_name}' has no composition metadata (unconstrained)",
        )

    if target_comp is None:
        return CompositionResult(
            valid=True,
            source=source_name,
            target=target_name,
            reason=f"Target skill '{target_name}' has no composition metadata (unconstrained)",
        )

    # Both have composition metadata - check compatibility
    if target_comp.can_receive_from(source_comp):
        # Find which type matched
        matched = None
        for output in source_comp.outputs:
            for input_type in target_comp.inputs:
                if input_type.matches(output):
                    matched = output.type_name
                    break
            if matched:
                break

        return CompositionResult(
            valid=True,
            source=source_name,
            target=target_name,
            reason=f"Type compatible: {source_name} outputs '{matched}' which {target_name} accepts",
            matched_type=matched,
        )

    # Incompatible
    source_outputs = ", ".join(o.type_name for o in source_comp.outputs) or "(none)"
    target_inputs = ", ".join(i.type_name for i in target_comp.inputs) or "(none)"

    return CompositionResult(
        valid=False,
        source=source_name,
        target=target_name,
        reason=f"Type mismatch: {source_name} outputs [{source_outputs}] but {target_name} expects [{target_inputs}]",
    )
