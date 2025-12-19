"""YAML frontmatter parsing for SKILL.md files."""

from pathlib import Path
from typing import Optional

import strictyaml

from .errors import ParseError, ValidationError
from .models import FieldSchema, SkillProperties


def _parse_field_schema(field_data: dict) -> FieldSchema:
    """Parse a FieldSchema from YAML data.

    Args:
        field_data: Dictionary containing field schema definition

    Returns:
        FieldSchema instance

    Raises:
        ValidationError: If required fields are missing
    """
    if not isinstance(field_data, dict):
        raise ValidationError("Field schema must be a mapping")

    name = field_data.get("name")
    if not name:
        raise ValidationError("Field schema missing required 'name'")

    field_type = field_data.get("type", "any")

    # Parse range as tuple if present
    range_val = field_data.get("range")
    if range_val is not None:
        if isinstance(range_val, list) and len(range_val) == 2:
            range_val = (float(range_val[0]), float(range_val[1]))
        else:
            range_val = None

    return FieldSchema(
        name=str(name),
        type=str(field_type),
        required=field_data.get("required", True),
        description=field_data.get("description"),
        default=field_data.get("default"),
        requires_source=field_data.get("requires_source", False),
        requires_rationale=field_data.get("requires_rationale", False),
        min_length=field_data.get("min_length"),
        min_items=field_data.get("min_items"),
        range=range_val,
    )


def _parse_field_schemas(fields_data: list) -> list[FieldSchema]:
    """Parse a list of FieldSchema from YAML data.

    Args:
        fields_data: List of field schema definitions

    Returns:
        List of FieldSchema instances
    """
    if not isinstance(fields_data, list):
        return []
    return [_parse_field_schema(f) for f in fields_data if isinstance(f, dict)]


def find_skill_md(skill_dir: Path) -> Optional[Path]:
    """Find the SKILL.md file in a skill directory.

    Prefers SKILL.md (uppercase) but accepts skill.md (lowercase).

    Args:
        skill_dir: Path to the skill directory

    Returns:
        Path to the SKILL.md file, or None if not found
    """
    for name in ("SKILL.md", "skill.md"):
        path = skill_dir / name
        if path.exists():
            return path
    return None


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from SKILL.md content.

    Args:
        content: Raw content of SKILL.md file

    Returns:
        Tuple of (metadata dict, markdown body)

    Raises:
        ParseError: If frontmatter is missing or invalid
    """
    if not content.startswith("---"):
        raise ParseError("SKILL.md must start with YAML frontmatter (---)")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ParseError("SKILL.md frontmatter not properly closed with ---")

    frontmatter_str = parts[1]
    body = parts[2].strip()

    try:
        parsed = strictyaml.load(frontmatter_str)
        metadata = parsed.data
    except strictyaml.YAMLError as e:
        raise ParseError(f"Invalid YAML in frontmatter: {e}")

    if not isinstance(metadata, dict):
        raise ParseError("SKILL.md frontmatter must be a YAML mapping")

    if "metadata" in metadata and isinstance(metadata["metadata"], dict):
        metadata["metadata"] = {str(k): str(v) for k, v in metadata["metadata"].items()}

    return metadata, body


def read_properties(skill_dir: Path) -> SkillProperties:
    """Read skill properties from SKILL.md frontmatter.

    This function parses the frontmatter and returns properties.
    It does NOT perform full validation. Use validate() for that.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        SkillProperties with parsed metadata

    Raises:
        ParseError: If SKILL.md is missing or has invalid YAML
        ValidationError: If required fields (name, description) are missing
    """
    skill_dir = Path(skill_dir)
    skill_md = find_skill_md(skill_dir)

    if skill_md is None:
        raise ParseError(f"SKILL.md not found in {skill_dir}")

    content = skill_md.read_text()
    metadata, _ = parse_frontmatter(content)

    if "name" not in metadata:
        raise ValidationError("Missing required field in frontmatter: name")
    if "description" not in metadata:
        raise ValidationError("Missing required field in frontmatter: description")

    name = metadata["name"]
    description = metadata["description"]

    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Field 'name' must be a non-empty string")
    if not isinstance(description, str) or not description.strip():
        raise ValidationError("Field 'description' must be a non-empty string")

    # Handle composes field - ensure it's a list
    composes = metadata.get("composes")
    if composes is not None and not isinstance(composes, list):
        composes = [composes] if composes else None

    # Handle level field - coerce to int if it's a valid integer string
    level = metadata.get("level")
    if level is not None:
        try:
            level = int(level)
        except (ValueError, TypeError):
            pass  # Let validator catch invalid levels

    # Parse inputs and outputs schemas
    inputs = None
    outputs = None
    if "inputs" in metadata:
        inputs = _parse_field_schemas(metadata["inputs"])
    if "outputs" in metadata:
        outputs = _parse_field_schemas(metadata["outputs"])

    return SkillProperties(
        name=name.strip(),
        description=description.strip(),
        license=metadata.get("license"),
        compatibility=metadata.get("compatibility"),
        allowed_tools=metadata.get("allowed-tools"),
        metadata=metadata.get("metadata"),
        # Composability fields
        level=level,
        operation=metadata.get("operation"),
        composes=composes,
        # Type checking fields
        inputs=inputs if inputs else None,
        outputs=outputs if outputs else None,
    )
