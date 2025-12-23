"""Skill validation logic."""

import re
import unicodedata
from pathlib import Path
from typing import Optional

from .errors import ParseError
from .parser import find_skill_md, parse_frontmatter

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500

# Allowed frontmatter fields per Agent Skills Spec
ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
    # Composability fields
    "level",
    "operation",
    "composes",
    # Type checking fields (including generics)
    "type_params",
    "inputs",
    "outputs",
    # Continuous improvement fields
    "lessons",
    # Versioning fields
    "version",
    "version_history",
    "requires",
    # Optional formalism fields (semantic foundations)
    "formalism",
    "effects",
    "ports",
    "wiring",
}

# Built-in primitive types for type checking
PRIMITIVE_TYPES = {
    "string", "number", "integer", "boolean", "date", "datetime", "any"
}

# Built-in generic types (higher-order skills)
# Maps type name to number of type parameters
GENERIC_TYPES = {
    "Skill": 2,  # Skill<Input, Output> - skills as first-class values
}

# Valid values for composability fields
VALID_LEVELS = {1, 2, 3}
VALID_OPERATIONS = {"READ", "WRITE", "TRANSFORM"}

# Valid values for lessons
VALID_LESSON_STATUSES = {"observed", "proposed", "validated", "applied", "deprecated"}
LESSON_ID_PATTERN = r"^L-[A-Za-z0-9-]+-\d{3}$"  # L-SKILL-NNN format

# Valid values for versioning
SEMVER_PATTERN = r"^\d+\.\d+\.\d+$"  # MAJOR.MINOR.PATCH
VALID_CHANGE_TYPES = {"breaking", "feature", "fix"}
VERSION_CONSTRAINT_PATTERN = r"^(>=|~|\^)?\d+\.\d+(\.\d+)?$"  # >=1.0.0, ^2.0, ~1.2.0

# Valid values for optional formalism (semantic foundations)
VALID_FORMALISM_LEVELS = {"basic", "typed", "effects", "formal"}
VALID_EFFECT_TYPES = {
    "Query", "Mutate", "Fail", "Timeout", "Memo",
    "Log", "Network", "FileRead", "FileWrite",
}
VALID_PORT_DIRECTIONS = {"in", "out"}


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


def _validate_level(level) -> list[str]:
    """Validate the level field for composability.

    Level indicates where a skill sits in the composition hierarchy:
    - 1 (Atomic): Single-purpose operations
    - 2 (Composite): Combines multiple atomic skills
    - 3 (Workflow): Complex orchestration with decision logic
    """
    errors = []

    # Try to coerce string to int (strictyaml returns strings)
    if isinstance(level, str):
        try:
            level = int(level)
        except ValueError:
            errors.append(f"Field 'level' must be an integer, got string '{level}'")
            return errors

    if not isinstance(level, int):
        errors.append(f"Field 'level' must be an integer, got {type(level).__name__}")
        return errors

    if level not in VALID_LEVELS:
        errors.append(
            f"Field 'level' must be 1, 2, or 3 (got {level}). "
            "1=Atomic, 2=Composite, 3=Workflow"
        )

    return errors


def _validate_operation(operation) -> list[str]:
    """Validate the operation field for safety classification.

    Operation classifies a skill's safety level:
    - READ: Only reads data, no side effects (safe)
    - WRITE: Creates, modifies, or deletes data (needs confirmation)
    - TRANSFORM: Local-only transformation (safe)
    """
    errors = []

    if not isinstance(operation, str):
        errors.append(f"Field 'operation' must be a string, got {type(operation).__name__}")
        return errors

    if operation not in VALID_OPERATIONS:
        errors.append(
            f"Field 'operation' must be one of {sorted(VALID_OPERATIONS)}, got '{operation}'"
        )

    return errors


def _validate_composes(composes, level=None) -> list[str]:
    """Validate the composes field for skill dependencies.

    Composes lists the skills this skill depends on.
    """
    errors = []

    if not isinstance(composes, list):
        errors.append(f"Field 'composes' must be a list, got {type(composes).__name__}")
        return errors

    for i, skill_name in enumerate(composes):
        if not isinstance(skill_name, str):
            errors.append(f"Field 'composes[{i}]' must be a string, got {type(skill_name).__name__}")
        elif not skill_name.strip():
            errors.append(f"Field 'composes[{i}]' cannot be empty")

    # Warn if level 1 has composes (atomic skills shouldn't compose)
    if level == 1 and composes:
        errors.append(
            "Level 1 (Atomic) skills should not have 'composes'. "
            "Atomic skills wrap primitives, not other skills."
        )

    return errors


def _validate_lesson(lesson: dict, index: int, skill_name: str) -> list[str]:
    """Validate a single lesson definition.

    Lessons capture patterns discovered during execution that could improve
    the skill definition. They follow a structured schema for:
    - Tracking confidence over time
    - Proposing specific edits
    - Human approval before crystallising into skill

    Args:
        lesson: Lesson dictionary from YAML
        index: Index in the lessons list (for error messages)
        skill_name: Name of the skill (for ID validation)

    Returns:
        List of validation error messages
    """
    errors = []
    context = f"lessons[{index}]"

    if not isinstance(lesson, dict):
        errors.append(f"Field '{context}' must be a mapping")
        return errors

    # Required fields
    if "id" not in lesson:
        errors.append(f"Field '{context}' missing required 'id'")
    else:
        lesson_id = lesson["id"]
        if not isinstance(lesson_id, str):
            errors.append(f"Field '{context}.id' must be a string")
        elif not re.match(LESSON_ID_PATTERN, lesson_id):
            errors.append(
                f"Field '{context}.id' must match pattern L-SKILL-NNN "
                f"(got '{lesson_id}')"
            )

    if "context" not in lesson:
        errors.append(f"Field '{context}' missing required 'context'")
    elif not isinstance(lesson["context"], str) or not lesson["context"].strip():
        errors.append(f"Field '{context}.context' must be a non-empty string")

    if "learned" not in lesson:
        errors.append(f"Field '{context}' missing required 'learned'")
    elif not isinstance(lesson["learned"], str) or not lesson["learned"].strip():
        errors.append(f"Field '{context}.learned' must be a non-empty string")

    # Optional fields with validation
    if "confidence" in lesson:
        confidence = lesson["confidence"]
        # Handle string numbers from YAML
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except ValueError:
                errors.append(f"Field '{context}.confidence' must be a number")
                confidence = None
        if confidence is not None:
            if not isinstance(confidence, (int, float)):
                errors.append(f"Field '{context}.confidence' must be a number")
            elif not 0.0 <= confidence <= 1.0:
                errors.append(
                    f"Field '{context}.confidence' must be between 0.0 and 1.0 "
                    f"(got {confidence})"
                )

    if "status" in lesson:
        status = lesson["status"]
        if not isinstance(status, str):
            errors.append(f"Field '{context}.status' must be a string")
        elif status not in VALID_LESSON_STATUSES:
            errors.append(
                f"Field '{context}.status' must be one of "
                f"{sorted(VALID_LESSON_STATUSES)}, got '{status}'"
            )

    if "source" in lesson and not isinstance(lesson["source"], str):
        errors.append(f"Field '{context}.source' must be a string")

    if "proposed_edit" in lesson and not isinstance(lesson["proposed_edit"], str):
        errors.append(f"Field '{context}.proposed_edit' must be a string")

    if "validated_at" in lesson and not isinstance(lesson["validated_at"], str):
        errors.append(f"Field '{context}.validated_at' must be a string (ISO date)")

    if "applied_at" in lesson and not isinstance(lesson["applied_at"], str):
        errors.append(f"Field '{context}.applied_at' must be a string (ISO date)")

    # Business logic validations
    status = lesson.get("status", "observed")
    raw_confidence = lesson.get("confidence", 0.5)

    # Coerce confidence to float for business logic checks
    try:
        confidence = float(raw_confidence) if raw_confidence is not None else 0.5
    except (ValueError, TypeError):
        confidence = None

    # Validated lessons should have high confidence
    if status == "validated" and confidence is not None and confidence < 0.8:
        errors.append(
            f"Field '{context}': validated lessons should have confidence >= 0.8 "
            f"(got {confidence})"
        )

    # Applied lessons should have a proposed_edit
    if status == "applied" and "proposed_edit" not in lesson:
        errors.append(
            f"Field '{context}': applied lessons must have 'proposed_edit' "
            "documenting what was changed"
        )

    return errors


def _validate_lessons(lessons: list, skill_name: str) -> list[str]:
    """Validate the lessons field for continuous improvement.

    Lessons enable skills to evolve based on execution feedback:
    1. Observations accumulate during execution
    2. High-confidence lessons are proposed for review
    3. Validated lessons can suggest edits
    4. Applied lessons are crystallised into the skill

    Args:
        lessons: List of lesson definitions
        skill_name: Name of the skill (for ID validation)

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(lessons, list):
        errors.append(f"Field 'lessons' must be a list, got {type(lessons).__name__}")
        return errors

    seen_ids = set()
    for i, lesson in enumerate(lessons):
        lesson_errors = _validate_lesson(lesson, i, skill_name)
        errors.extend(lesson_errors)

        # Check for duplicate IDs
        if isinstance(lesson, dict) and "id" in lesson:
            lesson_id = lesson["id"]
            if lesson_id in seen_ids:
                errors.append(f"Duplicate lesson ID: '{lesson_id}'")
            seen_ids.add(lesson_id)

    return errors


def _validate_version(version: str) -> list[str]:
    """Validate semantic version format.

    Args:
        version: Version string to validate

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(version, str):
        errors.append(f"Field 'version' must be a string, got {type(version).__name__}")
        return errors

    if not re.match(SEMVER_PATTERN, version):
        errors.append(
            f"Field 'version' must be in semver format MAJOR.MINOR.PATCH "
            f"(got '{version}')"
        )

    return errors


def _validate_version_change(change: dict, version: str, index: int) -> list[str]:
    """Validate a single change entry in version history.

    Args:
        change: Change dictionary from YAML
        version: Version string this change belongs to
        index: Index in the changes list

    Returns:
        List of validation error messages
    """
    errors = []
    context = f"version_history[{version}].changes[{index}]"

    if not isinstance(change, dict):
        errors.append(f"Field '{context}' must be a mapping")
        return errors

    # Required fields
    if "change_type" not in change:
        errors.append(f"Field '{context}' missing required 'change_type'")
    else:
        change_type = change["change_type"]
        if not isinstance(change_type, str):
            errors.append(f"Field '{context}.change_type' must be a string")
        elif change_type not in VALID_CHANGE_TYPES:
            errors.append(
                f"Field '{context}.change_type' must be one of "
                f"{sorted(VALID_CHANGE_TYPES)}, got '{change_type}'"
            )

    if "description" not in change:
        errors.append(f"Field '{context}' missing required 'description'")
    elif not isinstance(change["description"], str) or not change["description"].strip():
        errors.append(f"Field '{context}.description' must be a non-empty string")

    # Optional fields
    if "lesson_id" in change and not isinstance(change["lesson_id"], str):
        errors.append(f"Field '{context}.lesson_id' must be a string")

    if "migration" in change:
        migration = change["migration"]
        if not isinstance(migration, str):
            errors.append(f"Field '{context}.migration' must be a string")
        elif change.get("change_type") == "breaking" and not migration.strip():
            errors.append(
                f"Field '{context}': breaking changes should have migration guidance"
            )

    return errors


def _validate_version_entry(entry: dict, index: int) -> list[str]:
    """Validate a single version entry in version history.

    Args:
        entry: Version entry dictionary from YAML
        index: Index in the version_history list

    Returns:
        List of validation error messages
    """
    errors = []
    context = f"version_history[{index}]"

    if not isinstance(entry, dict):
        errors.append(f"Field '{context}' must be a mapping")
        return errors

    # Required fields
    if "version" not in entry:
        errors.append(f"Field '{context}' missing required 'version'")
    else:
        version = entry["version"]
        if not isinstance(version, str):
            errors.append(f"Field '{context}.version' must be a string")
        elif not re.match(SEMVER_PATTERN, version):
            errors.append(
                f"Field '{context}.version' must be in semver format "
                f"(got '{version}')"
            )

    if "released_at" not in entry:
        errors.append(f"Field '{context}' missing required 'released_at'")
    elif not isinstance(entry["released_at"], str):
        errors.append(f"Field '{context}.released_at' must be a string (ISO date)")

    # Optional changes list
    version_str = entry.get("version", f"index-{index}")
    if "changes" in entry:
        changes = entry["changes"]
        if not isinstance(changes, list):
            errors.append(f"Field '{context}.changes' must be a list")
        else:
            for i, change in enumerate(changes):
                errors.extend(_validate_version_change(change, version_str, i))

    # Optional deprecated flag
    if "deprecated" in entry:
        deprecated = entry["deprecated"]
        if not isinstance(deprecated, bool):
            # Handle string "true"/"false" from YAML
            if isinstance(deprecated, str):
                if deprecated.lower() not in ("true", "false"):
                    errors.append(f"Field '{context}.deprecated' must be a boolean")
            else:
                errors.append(f"Field '{context}.deprecated' must be a boolean")

    # Optional sunset_date
    if "sunset_date" in entry and not isinstance(entry["sunset_date"], str):
        errors.append(f"Field '{context}.sunset_date' must be a string (ISO date)")

    # Business logic: deprecated versions should have sunset_date
    deprecated = entry.get("deprecated", False)
    if deprecated is True or (isinstance(deprecated, str) and deprecated.lower() == "true"):
        if "sunset_date" not in entry:
            errors.append(
                f"Field '{context}': deprecated versions should have 'sunset_date'"
            )

    return errors


def _validate_version_history(version_history: list, current_version: str) -> list[str]:
    """Validate version history list.

    Args:
        version_history: List of version entries
        current_version: The current version string (for consistency check)

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(version_history, list):
        errors.append(
            f"Field 'version_history' must be a list, got {type(version_history).__name__}"
        )
        return errors

    seen_versions = set()
    has_current = False

    for i, entry in enumerate(version_history):
        errors.extend(_validate_version_entry(entry, i))

        # Check for duplicate versions
        if isinstance(entry, dict) and "version" in entry:
            version = entry["version"]
            if version in seen_versions:
                errors.append(f"Duplicate version in history: '{version}'")
            seen_versions.add(version)

            if version == current_version:
                has_current = True

    # Current version should be in history
    if current_version and not has_current and seen_versions:
        errors.append(
            f"Current version '{current_version}' not found in version_history"
        )

    return errors


def _validate_requires_entry(entry: dict, index: int) -> list[str]:
    """Validate a single requires entry.

    Args:
        entry: Requires entry dictionary from YAML
        index: Index in the requires list

    Returns:
        List of validation error messages
    """
    errors = []
    context = f"requires[{index}]"

    if not isinstance(entry, dict):
        errors.append(f"Field '{context}' must be a mapping")
        return errors

    if "skill_name" not in entry:
        errors.append(f"Field '{context}' missing required 'skill_name'")
    elif not isinstance(entry["skill_name"], str) or not entry["skill_name"].strip():
        errors.append(f"Field '{context}.skill_name' must be a non-empty string")

    if "constraint" not in entry:
        errors.append(f"Field '{context}' missing required 'constraint'")
    else:
        constraint = entry["constraint"]
        if not isinstance(constraint, str):
            errors.append(f"Field '{context}.constraint' must be a string")
        elif not re.match(VERSION_CONSTRAINT_PATTERN, constraint):
            errors.append(
                f"Field '{context}.constraint' must be a valid version constraint "
                f"(e.g., '>=1.0.0', '^2.0', '~1.2.0'), got '{constraint}'"
            )

    return errors


def _validate_requires(requires: list) -> list[str]:
    """Validate version requirements list.

    Args:
        requires: List of version requirement entries

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(requires, list):
        errors.append(f"Field 'requires' must be a list, got {type(requires).__name__}")
        return errors

    seen_skills = set()
    for i, entry in enumerate(requires):
        errors.extend(_validate_requires_entry(entry, i))

        # Check for duplicate skill requirements
        if isinstance(entry, dict) and "skill_name" in entry:
            skill_name = entry["skill_name"]
            if skill_name in seen_skills:
                errors.append(f"Duplicate requirement for skill: '{skill_name}'")
            seen_skills.add(skill_name)

    return errors


# =============================================================================
# Optional Formalism Validation (Semantic Foundations)
# =============================================================================


def _validate_formalism(formalism: str) -> list[str]:
    """Validate formalism level declaration.

    Args:
        formalism: Declared formalism level

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(formalism, str):
        errors.append(f"Field 'formalism' must be a string, got {type(formalism).__name__}")
        return errors

    if formalism not in VALID_FORMALISM_LEVELS:
        errors.append(
            f"Invalid formalism level: '{formalism}'. "
            f"Valid levels: {sorted(VALID_FORMALISM_LEVELS)}"
        )

    return errors


def _validate_effect(effect: dict, index: int) -> list[str]:
    """Validate a single effect declaration.

    Args:
        effect: Effect declaration dictionary
        index: Position in effects list

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(effect, dict):
        errors.append(f"Field 'effects[{index}]' must be a mapping")
        return errors

    # Required: name
    if "name" not in effect:
        errors.append(f"Field 'effects[{index}]' missing required 'name'")
        return errors

    name = effect["name"]
    if not isinstance(name, str):
        errors.append(f"Field 'effects[{index}].name' must be a string")
    elif name not in VALID_EFFECT_TYPES:
        errors.append(
            f"Unknown effect type: '{name}'. "
            f"Valid effects: {sorted(VALID_EFFECT_TYPES)}"
        )

    # Optional: description
    if "description" in effect and not isinstance(effect["description"], str):
        errors.append(f"Field 'effects[{index}].description' must be a string")

    # Optional: handled_by
    if "handled_by" in effect and not isinstance(effect["handled_by"], str):
        errors.append(f"Field 'effects[{index}].handled_by' must be a string")

    return errors


def _validate_effects(effects: list) -> list[str]:
    """Validate effects list.

    Args:
        effects: List of effect declarations

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(effects, list):
        errors.append(f"Field 'effects' must be a list, got {type(effects).__name__}")
        return errors

    seen_effects = set()
    for i, effect in enumerate(effects):
        errors.extend(_validate_effect(effect, i))

        # Check for duplicates
        if isinstance(effect, dict) and "name" in effect:
            name = effect["name"]
            if name in seen_effects:
                errors.append(f"Duplicate effect declaration: '{name}'")
            seen_effects.add(name)

    return errors


def _validate_port(port: dict, index: int) -> list[str]:
    """Validate a single port declaration.

    Args:
        port: Port declaration dictionary
        index: Position in ports list

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(port, dict):
        errors.append(f"Field 'ports[{index}]' must be a mapping")
        return errors

    # Required: name
    if "name" not in port:
        errors.append(f"Field 'ports[{index}]' missing required 'name'")
    elif not isinstance(port["name"], str):
        errors.append(f"Field 'ports[{index}].name' must be a string")

    # Required: type
    if "type" not in port:
        errors.append(f"Field 'ports[{index}]' missing required 'type'")
    elif not isinstance(port["type"], str):
        errors.append(f"Field 'ports[{index}].type' must be a string")

    # Required: direction
    if "direction" not in port:
        errors.append(f"Field 'ports[{index}]' missing required 'direction'")
    elif not isinstance(port["direction"], str):
        errors.append(f"Field 'ports[{index}].direction' must be a string")
    elif port["direction"] not in VALID_PORT_DIRECTIONS:
        errors.append(
            f"Invalid port direction: '{port['direction']}'. "
            f"Valid directions: {sorted(VALID_PORT_DIRECTIONS)}"
        )

    # Optional: field
    if "field" in port and not isinstance(port["field"], str):
        errors.append(f"Field 'ports[{index}].field' must be a string")

    return errors


def _validate_ports(ports: list) -> list[str]:
    """Validate ports list.

    Args:
        ports: List of port declarations

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(ports, list):
        errors.append(f"Field 'ports' must be a list, got {type(ports).__name__}")
        return errors

    seen_ports = set()
    for i, port in enumerate(ports):
        errors.extend(_validate_port(port, i))

        # Check for duplicate port names
        if isinstance(port, dict) and "name" in port:
            name = port["name"]
            if name in seen_ports:
                errors.append(f"Duplicate port name: '{name}'")
            seen_ports.add(name)

    return errors


def _validate_wire(wire: dict, index: int, known_skills: set[str]) -> list[str]:
    """Validate a single wire connection.

    Args:
        wire: Wire declaration dictionary
        index: Position in wiring list
        known_skills: Set of skill names (from composes + "input"/"output")

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(wire, dict):
        errors.append(f"Field 'wiring[{index}]' must be a mapping")
        return errors

    required_fields = ["from_skill", "from_port", "to_skill", "to_port"]
    for field in required_fields:
        if field not in wire:
            errors.append(f"Field 'wiring[{index}]' missing required '{field}'")
        elif not isinstance(wire[field], str):
            errors.append(f"Field 'wiring[{index}].{field}' must be a string")

    # Validate skill references if we have them
    if known_skills:
        if "from_skill" in wire and isinstance(wire["from_skill"], str):
            if wire["from_skill"] not in known_skills:
                errors.append(
                    f"Wire references unknown skill: '{wire['from_skill']}'. "
                    f"Known skills: {sorted(known_skills)}"
                )
        if "to_skill" in wire and isinstance(wire["to_skill"], str):
            if wire["to_skill"] not in known_skills:
                errors.append(
                    f"Wire references unknown skill: '{wire['to_skill']}'. "
                    f"Known skills: {sorted(known_skills)}"
                )

    return errors


def _validate_wiring(wiring: list, composes: list[str] | None) -> list[str]:
    """Validate wiring list.

    Args:
        wiring: List of wire declarations
        composes: List of composed skill names (for reference validation)

    Returns:
        List of validation error messages
    """
    errors = []

    if not isinstance(wiring, list):
        errors.append(f"Field 'wiring' must be a list, got {type(wiring).__name__}")
        return errors

    # Build set of known skill names: composed skills + "input"/"output" pseudo-skills
    known_skills = {"input", "output"}
    if composes:
        known_skills.update(composes)

    for i, wire in enumerate(wiring):
        errors.extend(_validate_wire(wire, i, known_skills))

    return errors


def _validate_type_params(type_params: list) -> tuple[list[str], set[str]]:
    """Validate type parameters for generic/higher-order skills.

    Type parameters enable polymorphic skills like:
    - map-skill<A, B>: Skill<A, B> → Skill<A[], B[]>
    - with-retry<A, B>: Skill<A, B> → Skill<A, B>

    Args:
        type_params: List of type parameter definitions

    Returns:
        Tuple of (error messages, set of type parameter names)
    """
    errors = []
    type_param_names = set()

    if not isinstance(type_params, list):
        errors.append(f"Field 'type_params' must be a list, got {type(type_params).__name__}")
        return errors, type_param_names

    for i, param in enumerate(type_params):
        if not isinstance(param, dict):
            errors.append(f"Field 'type_params[{i}]' must be a mapping")
            continue

        if "name" not in param:
            errors.append(f"Field 'type_params[{i}]' missing required 'name'")
            continue

        name = param["name"]
        if not isinstance(name, str):
            errors.append(f"Field 'type_params[{i}].name' must be a string")
            continue

        if not name.strip():
            errors.append(f"Field 'type_params[{i}].name' cannot be empty")
            continue

        # Type parameter names should be uppercase single letters or short identifiers
        if not name[0].isupper():
            errors.append(
                f"Type parameter '{name}' should start with uppercase "
                "(convention: A, B, T, Input, Output)"
            )

        if name in type_param_names:
            errors.append(f"Duplicate type parameter name: '{name}'")
        type_param_names.add(name)

        # Validate optional fields
        if "description" in param and not isinstance(param["description"], str):
            errors.append(f"Field 'type_params[{i}].description' must be a string")

        if "bound" in param:
            bound = param["bound"]
            if not isinstance(bound, str):
                errors.append(f"Field 'type_params[{i}].bound' must be a string")
            elif bound not in GENERIC_TYPES and bound not in PRIMITIVE_TYPES:
                errors.append(
                    f"Type parameter '{name}' has unknown bound '{bound}'. "
                    f"Valid bounds: {sorted(GENERIC_TYPES.keys())} or primitives"
                )

    return errors, type_param_names


def _parse_generic_type(type_str: str) -> tuple[Optional[str], list[str]]:
    """Parse a generic type string like 'Skill<A, B>' into base and params.

    Args:
        type_str: Type string to parse

    Returns:
        Tuple of (base_type, list of type parameters)
        Returns (None, []) if not a generic type
    """
    if "<" not in type_str:
        return None, []

    # Find the base type and parameters
    bracket_start = type_str.index("<")
    bracket_end = type_str.rindex(">")

    if bracket_end < bracket_start:
        return None, []

    base = type_str[:bracket_start]
    params_str = type_str[bracket_start + 1:bracket_end]

    # Split parameters, handling nested generics
    params = []
    depth = 0
    current = ""
    for char in params_str:
        if char == "<":
            depth += 1
            current += char
        elif char == ">":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            params.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        params.append(current.strip())

    return base, params


def _is_valid_type(
    type_str: str,
    type_params: Optional[set[str]] = None,
    custom_types: Optional[set[str]] = None
) -> tuple[bool, Optional[str]]:
    """Check if a type string is valid, considering type parameters.

    Args:
        type_str: Type string to validate
        type_params: Set of valid type parameter names (e.g., {'A', 'B'})
        custom_types: Set of custom type names

    Returns:
        Tuple of (is_valid, error_message)
    """
    type_params = type_params or set()
    custom_types = custom_types or set()

    # Handle list types
    if type_str.endswith("[]"):
        base = type_str[:-2]
        return _is_valid_type(base, type_params, custom_types)

    # Check if it's a type parameter
    if type_str in type_params:
        return True, None

    # Check if it's a primitive type
    if type_str in PRIMITIVE_TYPES:
        return True, None

    # Check if it's a custom type
    if type_str in custom_types:
        return True, None

    # Check if it's a generic type
    base, params = _parse_generic_type(type_str)
    if base is not None:
        if base not in GENERIC_TYPES:
            return False, f"Unknown generic type '{base}'"

        expected_param_count = GENERIC_TYPES[base]
        if len(params) != expected_param_count:
            return False, (
                f"Generic type '{base}' expects {expected_param_count} type parameters, "
                f"got {len(params)}"
            )

        # Recursively validate each type parameter
        for param in params:
            valid, err = _is_valid_type(param, type_params, custom_types)
            if not valid:
                return False, err

        return True, None

    return False, f"Unknown type '{type_str}'"


def _validate_field_schema(
    field: dict,
    context: str,
    custom_types: Optional[set] = None,
    type_params: Optional[set] = None
) -> list[str]:
    """Validate a single field schema definition.

    Args:
        field: Field schema dictionary
        context: Context string for error messages (e.g., "inputs[0]")
        custom_types: Optional set of custom type names defined in the skill
        type_params: Optional set of type parameter names (for generic skills)

    Returns:
        List of validation error messages
    """
    errors = []
    custom_types = custom_types or set()
    type_params = type_params or set()

    if not isinstance(field, dict):
        errors.append(f"Field '{context}' must be a mapping")
        return errors

    # Validate required 'name' field
    if "name" not in field:
        errors.append(f"Field '{context}' missing required 'name'")
    elif not isinstance(field["name"], str) or not field["name"].strip():
        errors.append(f"Field '{context}.name' must be a non-empty string")

    # Validate 'type' field using the enhanced type checker
    if "type" in field:
        field_type = field["type"]
        if not isinstance(field_type, str):
            errors.append(f"Field '{context}.type' must be a string")
        else:
            valid, err = _is_valid_type(field_type, type_params, custom_types)
            if not valid:
                errors.append(f"Field '{context}.type': {err}")

    # Validate epistemic requirements (handle string "true"/"false" from YAML)
    def _is_bool_like(val):
        if isinstance(val, bool):
            return True
        if isinstance(val, str):
            return val.lower() in ("true", "false")
        return False

    if "requires_source" in field and not _is_bool_like(field.get("requires_source")):
        errors.append(f"Field '{context}.requires_source' must be a boolean")

    if "requires_rationale" in field and not _is_bool_like(field.get("requires_rationale")):
        errors.append(f"Field '{context}.requires_rationale' must be a boolean")

    # Validate constraints (handle string numbers from YAML)
    def _to_int(val):
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            try:
                return int(val)
            except ValueError:
                return None
        return None

    if "min_length" in field:
        min_len = _to_int(field["min_length"])
        if min_len is None or min_len < 0:
            errors.append(f"Field '{context}.min_length' must be a non-negative integer")

    if "min_items" in field:
        min_items = _to_int(field["min_items"])
        if min_items is None or min_items < 0:
            errors.append(f"Field '{context}.min_items' must be a non-negative integer")

    if "range" in field:
        range_val = field["range"]
        if not isinstance(range_val, list) or len(range_val) != 2:
            errors.append(f"Field '{context}.range' must be a list of [min, max]")
        else:
            try:
                min_val, max_val = float(range_val[0]), float(range_val[1])
                if min_val > max_val:
                    errors.append(f"Field '{context}.range' min ({min_val}) > max ({max_val})")
            except (TypeError, ValueError):
                errors.append(f"Field '{context}.range' values must be numbers")

    return errors


def _validate_inputs_outputs(
    inputs: list,
    outputs: list,
    type_params: Optional[set[str]] = None
) -> list[str]:
    """Validate inputs and outputs field schemas.

    Args:
        inputs: List of input field schemas
        outputs: List of output field schemas
        type_params: Optional set of type parameter names (for generic skills)

    Returns:
        List of validation error messages
    """
    errors = []
    type_params = type_params or set()

    if inputs is not None:
        if not isinstance(inputs, list):
            errors.append("Field 'inputs' must be a list")
        else:
            for i, field in enumerate(inputs):
                errors.extend(_validate_field_schema(
                    field, f"inputs[{i}]", type_params=type_params
                ))

    if outputs is not None:
        if not isinstance(outputs, list):
            errors.append("Field 'outputs' must be a list")
        else:
            for i, field in enumerate(outputs):
                errors.extend(_validate_field_schema(
                    field, f"outputs[{i}]", type_params=type_params
                ))

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

    # Validate composability fields
    level = metadata.get("level")
    level_int = None  # Coerced level for use in composes validation
    if level is not None:
        errors.extend(_validate_level(level))
        # Coerce level for use in composes validation
        try:
            level_int = int(level) if isinstance(level, str) else level
        except (ValueError, TypeError):
            level_int = None

    if "operation" in metadata:
        errors.extend(_validate_operation(metadata["operation"]))

    if "composes" in metadata:
        errors.extend(_validate_composes(metadata["composes"], level=level_int))

    # Validate type parameters for generic/higher-order skills
    type_param_names = set()
    if "type_params" in metadata:
        type_param_errors, type_param_names = _validate_type_params(metadata["type_params"])
        errors.extend(type_param_errors)

    # Validate type checking fields (passing type_params for generic type validation)
    if "inputs" in metadata or "outputs" in metadata:
        errors.extend(_validate_inputs_outputs(
            metadata.get("inputs"),
            metadata.get("outputs"),
            type_params=type_param_names
        ))

    # Validate lessons for continuous improvement
    skill_name = metadata.get("name", "unknown")
    if "lessons" in metadata:
        errors.extend(_validate_lessons(metadata["lessons"], skill_name))

    # Validate versioning fields
    version = metadata.get("version")
    if version is not None:
        errors.extend(_validate_version(version))

    if "version_history" in metadata:
        errors.extend(_validate_version_history(
            metadata["version_history"],
            version  # Pass current version for consistency check
        ))

    if "requires" in metadata:
        errors.extend(_validate_requires(metadata["requires"]))

    # Validate optional formalism fields (only if present - all are optional)
    if "formalism" in metadata:
        errors.extend(_validate_formalism(metadata["formalism"]))

    if "effects" in metadata:
        errors.extend(_validate_effects(metadata["effects"]))

    if "ports" in metadata:
        errors.extend(_validate_ports(metadata["ports"]))

    if "wiring" in metadata:
        composes = metadata.get("composes")
        errors.extend(_validate_wiring(metadata["wiring"], composes))

    return errors


def validate(skill_dir: Path) -> list[str]:
    """Validate a skill directory.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        List of validation error messages. Empty list means valid.
    """
    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        return [f"Path does not exist: {skill_dir}"]

    if not skill_dir.is_dir():
        return [f"Not a directory: {skill_dir}"]

    skill_md = find_skill_md(skill_dir)
    if skill_md is None:
        return ["Missing required file: SKILL.md"]

    try:
        content = skill_md.read_text()
        metadata, _ = parse_frontmatter(content)
    except ParseError as e:
        return [str(e)]

    return validate_metadata(metadata, skill_dir)


def _types_compatible(
    output_type: str,
    input_type: str,
    type_bindings: Optional[dict[str, str]] = None
) -> bool:
    """Check if an output type is compatible with an input type.

    Args:
        output_type: Type of the output field
        input_type: Type of the input field
        type_bindings: Optional mapping of type parameters to concrete types

    Returns:
        True if types are compatible
    """
    type_bindings = type_bindings or {}

    # Resolve type parameters if bound
    if output_type in type_bindings:
        output_type = type_bindings[output_type]
    if input_type in type_bindings:
        input_type = type_bindings[input_type]

    # 'any' is compatible with everything
    if output_type == "any" or input_type == "any":
        return True

    # Handle list types
    output_is_list = output_type.endswith("[]")
    input_is_list = input_type.endswith("[]")

    if output_is_list != input_is_list:
        return False

    output_base = output_type.rstrip("[]")
    input_base = input_type.rstrip("[]")

    # Check for generic types
    output_generic, output_params = _parse_generic_type(output_base)
    input_generic, input_params = _parse_generic_type(input_base)

    # Both are generic types
    if output_generic and input_generic:
        if output_generic != input_generic:
            return False
        if len(output_params) != len(input_params):
            return False
        # Check each type parameter is compatible
        return all(
            _types_compatible(op, ip, type_bindings)
            for op, ip in zip(output_params, input_params)
        )

    # One is generic, one is not
    if output_generic or input_generic:
        return False

    # Exact match
    if output_base == input_base:
        return True

    # Number can satisfy integer (widening)
    if output_base == "integer" and input_base == "number":
        return True

    # datetime can satisfy date (has more info)
    if output_base == "datetime" and input_base == "date":
        return True

    return False


def typecheck_higher_order(
    wrapper_skill: "SkillProperties",
    wrapped_skill: "SkillProperties",
) -> list[str]:
    """Validate type compatibility when a higher-order skill wraps another skill.

    This implements type checking for skill transformers like:
    - with-retry<A, B> wrapping Skill<A, B> → produces Skill<A, B>
    - map-skill<A, B> wrapping Skill<A, B> → produces Skill<A[], B[]>

    Args:
        wrapper_skill: The higher-order skill (e.g., with-retry)
        wrapped_skill: The skill being wrapped (e.g., web-search)

    Returns:
        List of type error messages. Empty list means types are compatible.
    """
    errors = []

    if not wrapper_skill.type_params:
        # Not a generic skill, skip higher-order type checking
        return errors

    # Find the input that accepts a Skill<A, B>
    skill_input = None
    for inp in (wrapper_skill.inputs or []):
        if inp.type.startswith("Skill<"):
            skill_input = inp
            break

    if not skill_input:
        return errors  # No skill input to check

    # Parse the expected skill type from the wrapper
    _, expected_params = _parse_generic_type(skill_input.type)
    if len(expected_params) != 2:
        errors.append(
            f"Invalid Skill type in '{wrapper_skill.name}': "
            f"expected Skill<Input, Output>, got {skill_input.type}"
        )
        return errors

    expected_input_type, expected_output_type = expected_params

    # Get the wrapped skill's actual types
    wrapped_inputs = wrapped_skill.inputs or []
    wrapped_outputs = wrapped_skill.outputs or []

    # Build type bindings from the wrapped skill
    type_bindings = {}

    # If expected types are type parameters (e.g., 'A', 'B'), bind them
    wrapper_type_param_names = wrapper_skill.type_param_names

    if expected_input_type in wrapper_type_param_names:
        # Infer the binding from the wrapped skill's input types
        if wrapped_inputs:
            # For simplicity, use the first required input type
            for wi in wrapped_inputs:
                if wi.required:
                    type_bindings[expected_input_type] = wi.type
                    break

    if expected_output_type in wrapper_type_param_names:
        # Infer the binding from the wrapped skill's output types
        if wrapped_outputs:
            type_bindings[expected_output_type] = wrapped_outputs[0].type

    # Now validate that the wrapped skill's types are compatible
    # with the wrapper's expectations (considering bindings)

    return errors


def typecheck_composition(
    parent_skill: "SkillProperties",
    child_skills: dict[str, "SkillProperties"],
) -> list[str]:
    """Validate type compatibility between a skill and its composed dependencies.

    This implements static analysis similar to strongly-typed languages:
    - Ensures parent skill's inputs can satisfy child skill's required inputs
    - Ensures child skill's outputs can satisfy parent's expected types

    Args:
        parent_skill: The skill being validated (the one with 'composes')
        child_skills: Dictionary mapping skill names to their SkillProperties

    Returns:
        List of type error messages. Empty list means types are compatible.
    """
    from .models import SkillProperties  # Import here to avoid circular import

    errors = []

    if not parent_skill.composes:
        return errors

    parent_inputs = {f.name: f for f in (parent_skill.inputs or [])}
    parent_outputs = {f.name: f for f in (parent_skill.outputs or [])}

    for child_name in parent_skill.composes:
        if child_name not in child_skills:
            errors.append(
                f"Composed skill '{child_name}' not found. "
                f"Cannot verify type compatibility."
            )
            continue

        child = child_skills[child_name]
        child_inputs = child.inputs or []
        child_outputs = child.outputs or []

        # Check that required child inputs can be satisfied
        for child_input in child_inputs:
            if not child_input.required:
                continue

            # Check if parent has this input or produces it from another child
            if child_input.name in parent_inputs:
                parent_field = parent_inputs[child_input.name]
                if not _types_compatible(parent_field.type, child_input.type):
                    errors.append(
                        f"Type mismatch: '{parent_skill.name}' input "
                        f"'{child_input.name}' is {parent_field.type}, "
                        f"but '{child_name}' expects {child_input.type}"
                    )
            # Note: We don't error if input is missing - it might come from
            # another composed skill's output or be provided at runtime

        # Validate that child outputs match parent's expected output types
        for child_output in child_outputs:
            if child_output.name in parent_outputs:
                parent_field = parent_outputs[child_output.name]
                if not _types_compatible(child_output.type, parent_field.type):
                    errors.append(
                        f"Type mismatch: '{child_name}' output "
                        f"'{child_output.name}' is {child_output.type}, "
                        f"but '{parent_skill.name}' declares {parent_field.type}"
                    )

    return errors
