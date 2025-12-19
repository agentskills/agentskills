"""Skill validation logic."""

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
    # Type checking fields
    "inputs",
    "outputs",
}

# Built-in primitive types for type checking
PRIMITIVE_TYPES = {
    "string", "number", "integer", "boolean", "date", "datetime", "any"
}

# Valid values for composability fields
VALID_LEVELS = {1, 2, 3}
VALID_OPERATIONS = {"READ", "WRITE", "TRANSFORM"}


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


def _validate_field_schema(field: dict, context: str, custom_types: Optional[set] = None) -> list[str]:
    """Validate a single field schema definition.

    Args:
        field: Field schema dictionary
        context: Context string for error messages (e.g., "inputs[0]")
        custom_types: Optional set of custom type names defined in the skill

    Returns:
        List of validation error messages
    """
    errors = []
    custom_types = custom_types or set()

    if not isinstance(field, dict):
        errors.append(f"Field '{context}' must be a mapping")
        return errors

    # Validate required 'name' field
    if "name" not in field:
        errors.append(f"Field '{context}' missing required 'name'")
    elif not isinstance(field["name"], str) or not field["name"].strip():
        errors.append(f"Field '{context}.name' must be a non-empty string")

    # Validate 'type' field
    if "type" in field:
        field_type = field["type"]
        if not isinstance(field_type, str):
            errors.append(f"Field '{context}.type' must be a string")
        else:
            # Check if type is a primitive, list, or custom type
            base_type = field_type.rstrip("[]")  # Handle list types like "string[]"
            if base_type not in PRIMITIVE_TYPES and base_type not in custom_types:
                errors.append(
                    f"Field '{context}.type' unknown type '{field_type}'. "
                    f"Valid primitives: {sorted(PRIMITIVE_TYPES)}"
                )

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


def _validate_inputs_outputs(inputs: list, outputs: list) -> list[str]:
    """Validate inputs and outputs field schemas.

    Args:
        inputs: List of input field schemas
        outputs: List of output field schemas

    Returns:
        List of validation error messages
    """
    errors = []

    if inputs is not None:
        if not isinstance(inputs, list):
            errors.append("Field 'inputs' must be a list")
        else:
            for i, field in enumerate(inputs):
                errors.extend(_validate_field_schema(field, f"inputs[{i}]"))

    if outputs is not None:
        if not isinstance(outputs, list):
            errors.append("Field 'outputs' must be a list")
        else:
            for i, field in enumerate(outputs):
                errors.extend(_validate_field_schema(field, f"outputs[{i}]"))

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

    # Validate type checking fields
    if "inputs" in metadata or "outputs" in metadata:
        errors.extend(_validate_inputs_outputs(
            metadata.get("inputs"),
            metadata.get("outputs")
        ))

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


def _types_compatible(output_type: str, input_type: str) -> bool:
    """Check if an output type is compatible with an input type.

    Args:
        output_type: Type of the output field
        input_type: Type of the input field

    Returns:
        True if types are compatible
    """
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
