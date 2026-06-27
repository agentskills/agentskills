"""Skill validation logic."""

import unicodedata
from pathlib import Path
from typing import Optional

from .errors import ParseError
from .parser import find_skill_md, parse_frontmatter

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_LICENSE_LENGTH = 100
MAX_ALLOWED_TOOLS_LENGTH = 1024
MAX_METADATA_KEY_LENGTH = 64
MAX_METADATA_VALUE_LENGTH = 1024

# Allowed frontmatter fields per Agent Skills Spec
ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}


def _validate_name(name: str, skill_dir: Path) -> list[str]:
    """Validate skill name format and directory match.

    Skill names support i18n characters (Unicode letters) plus hyphens.
    Names must be lowercase and cannot start/end with hyphens.
    """
    errors = []

    if not name or not isinstance(name, str) or not name.strip():
        errors.append("Field 'name' must be a non-empty string")
        return errors

    name = unicodedata.normalize("NFKC", name.strip())

    if len(name) > MAX_SKILL_NAME_LENGTH:
        errors.append(
            f"Skill name '{name}' exceeds {MAX_SKILL_NAME_LENGTH} character limit "
            f"({len(name)} chars)"
        )

    if name != name.lower():
        errors.append(f"Skill name '{name}' must be lowercase")

    if name.startswith("-") or name.endswith("-"):
        errors.append("Skill name cannot start or end with a hyphen")

    if "--" in name:
        errors.append("Skill name cannot contain consecutive hyphens")

    if not all(c.isalnum() or c == "-" for c in name):
        errors.append(
            f"Skill name '{name}' contains invalid characters. "
            "Only letters, digits, and hyphens are allowed."
        )

    if skill_dir:
        dir_name = unicodedata.normalize("NFKC", skill_dir.name)
        if dir_name != name:
            errors.append(
                f"Directory name '{skill_dir.name}' must match skill name '{name}'"
            )

    return errors


def _validate_description(description: str) -> list[str]:
    """Validate description format."""
    errors = []

    if not description or not isinstance(description, str) or not description.strip():
        errors.append("Field 'description' must be a non-empty string")
        return errors

    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"Description exceeds {MAX_DESCRIPTION_LENGTH} character limit "
            f"({len(description)} chars)"
        )

    return errors


def _validate_compatibility(compatibility: str) -> list[str]:
    """Validate compatibility format."""
    errors = []

    if not isinstance(compatibility, str):
        errors.append("Field 'compatibility' must be a string")
        return errors

    if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
        errors.append(
            f"Compatibility exceeds {MAX_COMPATIBILITY_LENGTH} character limit "
            f"({len(compatibility)} chars)"
        )

    return errors


def _validate_license(license_str: str) -> list[str]:
    """Validate license format."""
    errors = []

    if not isinstance(license_str, str):
        errors.append("Field 'license' must be a string")
        return errors

    if len(license_str) > MAX_LICENSE_LENGTH:
        errors.append(
            f"License exceeds {MAX_LICENSE_LENGTH} character limit "
            f"({len(license_str)} chars)"
        )

    return errors


def _validate_allowed_tools(allowed_tools: str) -> list[str]:
    """Validate allowed-tools format."""
    errors = []

    if not isinstance(allowed_tools, str):
        errors.append("Field 'allowed-tools' must be a string")
        return errors

    if len(allowed_tools) > MAX_ALLOWED_TOOLS_LENGTH:
        errors.append(
            f"Allowed tools exceed {MAX_ALLOWED_TOOLS_LENGTH} character limit "
            f"({len(allowed_tools)} chars)"
        )

    return errors


def _validate_metadata_dict(custom_metadata: dict) -> list[str]:
    """Validate custom metadata structure and limits."""
    errors = []

    if not isinstance(custom_metadata, dict):
        errors.append("Field 'metadata' must be a dictionary")
        return errors

    for k, v in custom_metadata.items():
        if not isinstance(k, str):
            errors.append("Metadata keys must be strings")
            continue
        if len(k) > MAX_METADATA_KEY_LENGTH:
            errors.append(
                f"Metadata key '{k}' exceeds {MAX_METADATA_KEY_LENGTH} character limit"
            )

        if not isinstance(v, str):
            errors.append(f"Metadata value for '{k}' must be a string")
            continue
        if len(v) > MAX_METADATA_VALUE_LENGTH:
            errors.append(
                f"Metadata value for '{k}' exceeds {MAX_METADATA_VALUE_LENGTH} character limit"
            )

    return errors


def _validate_metadata_fields(metadata: dict) -> list[str]:
    """Validate that only allowed fields are present."""
    errors = []

    extra_fields = set(metadata.keys()) - ALLOWED_FIELDS
    if extra_fields:
        errors.append(
            f"Unexpected fields in frontmatter: {', '.join(sorted(extra_fields))}. "
            f"Only {sorted(ALLOWED_FIELDS)} are allowed."
        )

    return errors


def validate_metadata(metadata: dict, skill_dir: Optional[Path] = None) -> list[str]:
    """Validate parsed skill metadata.

    This is the core validation function that works on already-parsed metadata,
    avoiding duplicate file I/O when called from the parser.

    Args:
        metadata: Parsed YAML frontmatter dictionary
        skill_dir: Optional path to skill directory (for name-directory match check)

    Returns:
        List of validation error messages. Empty list means valid.
    """
    errors = []
    errors.extend(_validate_metadata_fields(metadata))

    if "name" not in metadata:
        errors.append("Missing required field in frontmatter: name")
    else:
        errors.extend(_validate_name(metadata["name"], skill_dir))

    if "description" not in metadata:
        errors.append("Missing required field in frontmatter: description")
    else:
        errors.extend(_validate_description(metadata["description"]))

    if "compatibility" in metadata:
        errors.extend(_validate_compatibility(metadata["compatibility"]))

    if "license" in metadata:
        errors.extend(_validate_license(metadata["license"]))

    if "allowed-tools" in metadata:
        errors.extend(_validate_allowed_tools(metadata["allowed-tools"]))

    if "metadata" in metadata:
        errors.extend(_validate_metadata_dict(metadata["metadata"]))

    return errors


def validate(skill_dir: Path) -> list[str]:
    """Validate a skill directory.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        List of validation error messages. Empty list means valid.
    """
    skill_dir = Path(skill_dir)

    try:
        if not skill_dir.exists():
            return [f"Path does not exist: {skill_dir.name}"]

        if not skill_dir.is_dir():
            return [f"Not a directory: {skill_dir.name}"]

        skill_md = find_skill_md(skill_dir)
        if skill_md is None:
            return ["Missing required file: SKILL.md"]

        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read(1024 * 1024 + 1)
            if len(content) > 1024 * 1024:
                return [f"SKILL.md in {skill_dir.name} exceeds 1MB size limit"]
        metadata, _ = parse_frontmatter(content)
    except OSError as e:
        return [f"Failed to read SKILL.md in {skill_dir.name}: {e.strerror}"]
    except UnicodeDecodeError:
        return [f"SKILL.md in {skill_dir.name} is not valid UTF-8"]
    except ParseError as e:
        return [str(e)]
    except RuntimeError:
        return [
            f"Failed to read SKILL.md in {skill_dir.name}: Symlink loop or unresolvable path"
        ]

    return validate_metadata(metadata, skill_dir)
