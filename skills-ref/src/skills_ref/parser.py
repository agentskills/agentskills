"""YAML frontmatter parsing for SKILL.md files."""

from pathlib import Path
from typing import Optional

import strictyaml

from .errors import ParseError, ValidationError
from .models import FeatureDefinition, Features, SkillProperties


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

    features = None
    if "features" in metadata:
        features = _parse_features(metadata["features"])

    return SkillProperties(
        name=name.strip(),
        description=description.strip(),
        license=metadata.get("license"),
        compatibility=metadata.get("compatibility"),
        allowed_tools=metadata.get("allowed-tools"),
        features=features,
        metadata=metadata.get("metadata"),
    )


def _parse_features(raw: dict) -> Features:
    """Parse features field from frontmatter into Features model.

    Args:
        raw: Raw features dict from YAML parsing

    Returns:
        Features dataclass

    Raises:
        ValidationError: If features structure is invalid
    """
    if not isinstance(raw, dict):
        raise ValidationError("Field 'features' must be a mapping")

    if "default" not in raw:
        raise ValidationError("Field 'features.default' is required")
    if "available" not in raw:
        raise ValidationError("Field 'features.available' is required")

    default = raw["default"]
    if isinstance(default, str):
        default = [default]
    if not isinstance(default, list):
        raise ValidationError("Field 'features.default' must be a list")

    available_raw = raw["available"]
    if not isinstance(available_raw, dict):
        raise ValidationError("Field 'features.available' must be a mapping")

    available = {}
    for feat_name, feat_def in available_raw.items():
        if not isinstance(feat_def, dict):
            raise ValidationError(
                f"Feature '{feat_name}' definition must be a mapping"
            )
        if "description" not in feat_def:
            raise ValidationError(
                f"Feature '{feat_name}' is missing required field 'description'"
            )
        if "section" not in feat_def:
            raise ValidationError(
                f"Feature '{feat_name}' is missing required field 'section'"
            )

        requires = feat_def.get("requires", [])
        if isinstance(requires, str):
            requires = [requires]

        available[feat_name] = FeatureDefinition(
            description=feat_def["description"],
            section=feat_def["section"],
            requires=requires,
        )

    conflicts = raw.get("conflicts", [])
    if not isinstance(conflicts, list):
        raise ValidationError("Field 'features.conflicts' must be a list")

    return Features(default=default, available=available, conflicts=conflicts)
