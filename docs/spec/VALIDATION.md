# Skill Validation Specification

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2025-01-15

## Overview

This document specifies the validation mechanisms for the Composable Skills Framework. Validation occurs at **composition time** (when skills are loaded and composed), not at runtime, catching errors before execution begins.

## Design Principles

1. **Fail Fast**: Catch errors at composition time, not runtime
2. **Explicit Contracts**: All inputs/outputs must have JSON Schema definitions
3. **Structural Typing**: Compatibility based on shape, not names
4. **Helpful Errors**: Error messages must include context and remediation

---

## 1. Schema Validation

### 1.1 JSON Schema Requirement

All skills MUST define input and output schemas using [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html).

```yaml
# REQUIRED for all L2/L3 skills, RECOMMENDED for L1
input_schema:
  type: object
  properties:
    user_id:
      type: string
      format: uuid
      description: "Unique user identifier"
    include_history:
      type: boolean
      default: false
  required:
    - user_id

output_schema:
  type: object
  properties:
    user:
      $ref: "#/$defs/User"
    history:
      type: array
      items:
        $ref: "#/$defs/Event"
  required:
    - user
```

### 1.2 Supported JSON Schema Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| `type` | ✅ | string, number, integer, boolean, object, array, null |
| `properties` | ✅ | Object property definitions |
| `required` | ✅ | Required property list |
| `additionalProperties` | ✅ | Control extra properties |
| `items` | ✅ | Array item schema |
| `enum` | ✅ | Enumerated values |
| `const` | ✅ | Constant values |
| `format` | ✅ | date, date-time, email, uri, uuid |
| `$ref` | ✅ | Schema references (local only) |
| `$defs` | ✅ | Schema definitions |
| `oneOf`, `anyOf`, `allOf` | ✅ | Schema composition |
| `if/then/else` | ⚠️ | Partial support |
| `pattern` | ✅ | Regex patterns for strings |
| `minimum`, `maximum` | ✅ | Numeric constraints |
| `minLength`, `maxLength` | ✅ | String length constraints |
| `minItems`, `maxItems` | ✅ | Array length constraints |

### 1.3 Schema Validation Algorithm

```python
from jsonschema import Draft202012Validator, ValidationError

def validate_skill_schema(skill: SkillDefinition) -> list[ValidationError]:
    """
    Validate a skill's input/output schemas are valid JSON Schema.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Check schema is valid JSON Schema
    if skill.input_schema:
        try:
            Draft202012Validator.check_schema(skill.input_schema)
        except SchemaError as e:
            errors.append(ValidationError(
                f"Invalid input_schema: {e.message}",
                path=["input_schema"] + list(e.path)
            ))

    if skill.output_schema:
        try:
            Draft202012Validator.check_schema(skill.output_schema)
        except SchemaError as e:
            errors.append(ValidationError(
                f"Invalid output_schema: {e.message}",
                path=["output_schema"] + list(e.path)
            ))

    return errors
```

---

## 2. Composition Validation

### 2.1 Contract Compatibility

When skill A composes skill B, A's expected input for B must be compatible with B's declared output.

**Compatibility Rule**: Output O is compatible with Input I if:
1. Every required property in I exists in O
2. Each property type in O is assignable to the corresponding type in I
3. O may have additional properties not in I (structural subtyping)

```python
def check_contract_compatibility(
    producer_output: dict,  # JSON Schema
    consumer_input: dict    # JSON Schema
) -> CompatibilityResult:
    """
    Check if producer's output satisfies consumer's input requirements.

    Uses structural typing: producer may have MORE fields than consumer needs.
    """
    errors = []

    # Get required fields from consumer
    consumer_required = set(consumer_input.get("required", []))
    consumer_props = consumer_input.get("properties", {})
    producer_props = producer_output.get("properties", {})

    # Check all required fields exist in producer
    for field in consumer_required:
        if field not in producer_props:
            errors.append(ContractError(
                error_type="MISSING_REQUIRED_FIELD",
                field=field,
                message=f"Consumer requires '{field}' but producer does not output it",
                producer_schema=producer_output,
                consumer_schema=consumer_input
            ))
            continue

        # Check type compatibility
        producer_type = producer_props[field]
        consumer_type = consumer_props[field]

        if not is_type_assignable(producer_type, consumer_type):
            errors.append(ContractError(
                error_type="TYPE_MISMATCH",
                field=field,
                message=f"Type mismatch for '{field}': "
                        f"producer outputs {producer_type.get('type')}, "
                        f"consumer expects {consumer_type.get('type')}",
                producer_schema=producer_type,
                consumer_schema=consumer_type
            ))

    return CompatibilityResult(
        compatible=len(errors) == 0,
        errors=errors
    )
```

### 2.2 Type Assignability Rules

```python
def is_type_assignable(source: dict, target: dict) -> bool:
    """
    Check if source type can be assigned to target type.

    Rules:
    - Exact type match: always OK
    - integer → number: OK (widening)
    - string with format → string: OK (widening)
    - array<T> → array<U>: OK if T assignable to U
    - object with props → object with subset props: OK
    """
    source_type = source.get("type")
    target_type = target.get("type")

    # Exact match
    if source_type == target_type:
        # Check nested constraints
        if source_type == "array":
            return is_type_assignable(
                source.get("items", {}),
                target.get("items", {})
            )
        if source_type == "object":
            return check_object_assignability(source, target)
        return True

    # Widening: integer → number
    if source_type == "integer" and target_type == "number":
        return True

    # No other implicit conversions
    return False
```

### 2.3 Composition Graph Validation

```python
def validate_composition_graph(workflow: SkillDefinition) -> list[CompositionError]:
    """
    Validate the entire composition graph of a workflow.

    Checks:
    1. All composed skills exist
    2. No circular dependencies
    3. All contracts are compatible
    4. All required inputs are provided
    """
    errors = []

    # Build dependency graph
    graph = build_dependency_graph(workflow)

    # Check for cycles
    if cycles := detect_cycles(graph):
        errors.append(CompositionError(
            error_type="CIRCULAR_DEPENDENCY",
            message=f"Circular dependency detected: {' → '.join(cycles[0])}",
            skills_involved=cycles[0]
        ))
        return errors  # Cannot continue with cycle

    # Topological sort for execution order
    execution_order = topological_sort(graph)

    # Validate each edge (composition)
    for producer, consumer in graph.edges():
        producer_skill = load_skill(producer)
        consumer_skill = load_skill(consumer)

        result = check_contract_compatibility(
            producer_skill.output_schema,
            consumer_skill.input_schema
        )

        if not result.compatible:
            for err in result.errors:
                errors.append(CompositionError(
                    error_type=err.error_type,
                    message=err.message,
                    producer_skill=producer,
                    consumer_skill=consumer,
                    field=err.field
                ))

    return errors
```

---

## 3. Error Messages

### 3.1 Error Message Format

All validation errors MUST include:

```python
@dataclass
class ValidationError:
    error_code: str          # Machine-readable code (e.g., "E001")
    error_type: str          # Category (e.g., "TYPE_MISMATCH")
    message: str             # Human-readable description
    skill_name: str          # Which skill has the error
    location: list[str]      # Path to error (e.g., ["input_schema", "properties", "user_id"])
    context: dict            # Additional context for debugging
    remediation: str         # How to fix the error
```

### 3.2 Error Catalog

| Code | Type | Description | Example Remediation |
|------|------|-------------|---------------------|
| E001 | MISSING_REQUIRED_FIELD | Consumer requires field not in producer output | Add `{field}` to producer's output_schema |
| E002 | TYPE_MISMATCH | Producer outputs different type than consumer expects | Change producer's `{field}` type from `{actual}` to `{expected}` |
| E003 | CIRCULAR_DEPENDENCY | Skills form a dependency cycle | Remove composition: `{skill_a}` → `{skill_b}` |
| E004 | SKILL_NOT_FOUND | Composed skill does not exist | Create skill `{skill_name}` or fix spelling |
| E005 | INVALID_SCHEMA | JSON Schema is malformed | Fix schema syntax at `{path}` |
| E006 | VERSION_MISMATCH | Skill version doesn't satisfy constraint | Update to version satisfying `{constraint}` |
| E007 | MISSING_INPUT_SCHEMA | L2/L3 skill missing required input_schema | Add input_schema to skill definition |
| E008 | MISSING_OUTPUT_SCHEMA | L2/L3 skill missing required output_schema | Add output_schema to skill definition |

### 3.3 Example Error Messages

**Type Mismatch:**
```
ERROR E002: Type mismatch in composition

  email-sender → notification-router

  Field: recipient
  Producer outputs: { "type": "object", "properties": { "email": "string" } }
  Consumer expects: { "type": "string", "format": "email" }

  The 'email-sender' skill outputs 'recipient' as an object,
  but 'notification-router' expects a plain email string.

  Remediation:
  Option 1: Change email-sender to output recipient as a string
  Option 2: Add a transform skill between them to extract the email
  Option 3: Update notification-router to accept an object with email property
```

**Missing Required Field:**
```
ERROR E001: Missing required field in composition

  user-lookup → access-checker

  Field: permissions
  Consumer requires: permissions (array of strings)
  Producer outputs: { user_id, name, email }

  The 'user-lookup' skill does not output 'permissions',
  but 'access-checker' requires it.

  Remediation:
  Option 1: Add 'permissions' to user-lookup output_schema
  Option 2: Add a permission-lookup skill between them
  Option 3: Make 'permissions' optional in access-checker input_schema
```

---

## 4. Validation Timing

### 4.1 When Validation Occurs

| Phase | What's Validated | Errors Caught |
|-------|------------------|---------------|
| **Skill Load** | Schema syntax, required fields | E005, E007, E008 |
| **Composition** | Contract compatibility, cycles | E001, E002, E003, E004 |
| **Version Resolution** | Version constraints | E006 |
| **Pre-Execution** | Input data against schema | Runtime type errors |

### 4.2 Validation API

```python
class SkillValidator:
    """Validates skills and compositions."""

    def validate_skill(self, skill: SkillDefinition) -> ValidationResult:
        """Validate a single skill definition."""
        pass

    def validate_composition(
        self,
        workflow: SkillDefinition,
        skill_registry: SkillRegistry
    ) -> ValidationResult:
        """Validate a workflow's composition graph."""
        pass

    def validate_input(
        self,
        skill: SkillDefinition,
        input_data: dict
    ) -> ValidationResult:
        """Validate input data against skill's input_schema."""
        pass

    def validate_output(
        self,
        skill: SkillDefinition,
        output_data: dict
    ) -> ValidationResult:
        """Validate output data against skill's output_schema."""
        pass
```

---

## 5. Implementation Reference

### 5.1 Python Implementation

The reference implementation uses:
- `jsonschema` library for JSON Schema validation
- Custom contract checker for composition validation
- NetworkX for dependency graph analysis

See: `skills-ref/src/skills_ref/validation/` for implementation.

### 5.2 Standards Compliance

This specification is built on:
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html)
- [OpenAPI 3.1 Schema Object](https://spec.openapis.org/oas/v3.1.0#schema-object) (compatible)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) for requirement levels

---

## 6. Test Cases

See `tests/validation/` for comprehensive test cases including:
- `test_schema_validation.py` - Schema syntax validation
- `test_contract_compatibility.py` - Contract compatibility checking
- `test_composition_errors.py` - Composition error detection
- `test_error_messages.py` - Error message formatting

---

## Appendix A: Full Error Code Reference

```
E001  MISSING_REQUIRED_FIELD    Consumer requires field not output by producer
E002  TYPE_MISMATCH             Type incompatibility between skills
E003  CIRCULAR_DEPENDENCY       Dependency cycle detected
E004  SKILL_NOT_FOUND           Referenced skill does not exist
E005  INVALID_SCHEMA            JSON Schema syntax error
E006  VERSION_MISMATCH          Version constraint not satisfied
E007  MISSING_INPUT_SCHEMA      Required input_schema not defined
E008  MISSING_OUTPUT_SCHEMA     Required output_schema not defined
E009  INVALID_LEVEL             Invalid skill level (must be 1, 2, or 3)
E010  LEVEL_VIOLATION           L1 skill cannot compose other skills
E011  AMBIGUOUS_FIELD_MAPPING   Multiple fields could satisfy requirement
E012  FORMAT_MISMATCH           String format incompatibility
```
