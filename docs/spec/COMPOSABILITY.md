# Skill Composability Specification

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2025-01-15

## Overview

This document specifies the rules governing when and how skills can be composed. Composition is the process of combining multiple skills into higher-level skills or workflows.

---

## 1. Skill Levels

### 1.1 Level Definitions

| Level | Name | Description | Can Compose | Composed By |
|-------|------|-------------|-------------|-------------|
| L1 | Atomic | Single operation, no dependencies | Nothing | L2, L3 |
| L2 | Composite | Combines multiple L1 skills | L1 only | L3 |
| L3 | Workflow | Orchestrates L1 and L2 skills | L1, L2 | Nothing |

### 1.2 Level Rules

**Rule 1: Downward Composition Only**
A skill at level N may only compose skills at levels < N.

```
✅ L2 composes L1
✅ L3 composes L1
✅ L3 composes L2
❌ L1 composes anything
❌ L2 composes L2
❌ L2 composes L3
❌ L3 composes L3
```

**Rule 2: L1 Skills Are Leaf Nodes**
Atomic skills (L1) MUST NOT have a `composes` field.

**Rule 3: L2/L3 Skills Require Composition**
Composite (L2) and Workflow (L3) skills MUST have at least one skill in their `composes` list.

### 1.3 Level Validation

```python
def validate_level_rules(skill: SkillDefinition, registry: SkillRegistry) -> list[Error]:
    errors = []

    if skill.level == 1:
        if skill.composes:
            errors.append(Error(
                code="E010",
                message=f"L1 skill '{skill.name}' cannot compose other skills"
            ))

    elif skill.level in (2, 3):
        if not skill.composes:
            errors.append(Error(
                code="E013",
                message=f"L{skill.level} skill '{skill.name}' must compose at least one skill"
            ))

        for composed_name in skill.composes:
            composed = registry.get(composed_name)
            if not composed:
                errors.append(Error(code="E004", message=f"Skill '{composed_name}' not found"))
                continue

            if skill.level == 2 and composed.level != 1:
                errors.append(Error(
                    code="E014",
                    message=f"L2 skill '{skill.name}' can only compose L1 skills, "
                            f"but '{composed_name}' is L{composed.level}"
                ))

            if skill.level == 3 and composed.level == 3:
                errors.append(Error(
                    code="E015",
                    message=f"L3 skill '{skill.name}' cannot compose another L3 skill "
                            f"('{composed_name}')"
                ))

    return errors
```

---

## 2. Composition Constraints

### 2.1 Dependency Graph

Compositions form a Directed Acyclic Graph (DAG):

```
        ┌─────────────────────────────────────┐
        │           L3: pr-review             │
        └─────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌───────┐   ┌───────┐   ┌───────┐
    │  L2   │   │  L2   │   │  L1   │
    │ fetch │   │analyze│   │ post  │
    └───────┘   └───────┘   └───────┘
        │           │
    ┌───┴───┐   ┌───┴───┐
    ▼       ▼   ▼       ▼
  ┌───┐   ┌───┐ ┌───┐ ┌───┐
  │L1 │   │L1 │ │L1 │ │L1 │
  │git│   │api│ │ast│ │llm│
  └───┘   └───┘ └───┘ └───┘
```

### 2.2 Cycle Detection

**Rule 4: No Circular Dependencies**
The composition graph MUST be acyclic.

```python
def detect_cycles(graph: DiGraph) -> list[list[str]]:
    """
    Detect all cycles in the composition graph.

    Uses DFS with back-edge detection.
    Returns list of cycles (each cycle is a list of skill names).
    """
    cycles = []

    try:
        # NetworkX provides cycle detection
        cycles = list(nx.simple_cycles(graph))
    except nx.NetworkXNoCycle:
        pass

    return cycles
```

**Cycle Error Example:**
```
ERROR E003: Circular dependency detected

  skill-a → skill-b → skill-c → skill-a

  This creates an infinite loop. One of these compositions must be removed:
  - skill-a composes skill-b
  - skill-b composes skill-c
  - skill-c composes skill-a
```

### 2.3 Diamond Dependencies

Diamond dependencies are ALLOWED but require careful handling:

```
        ┌────────────┐
        │  workflow  │
        └────────────┘
           │     │
     ┌─────┘     └─────┐
     ▼                 ▼
┌─────────┐       ┌─────────┐
│ skill-a │       │ skill-b │
└─────────┘       └─────────┘
     │                 │
     └────────┬────────┘
              ▼
        ┌───────────┐
        │ skill-c   │  ← Called twice!
        └───────────┘
```

**Rule 5: Diamond Warning**
If a skill appears multiple times in the dependency graph, emit a warning (not error).

```
WARNING: Diamond dependency detected

  'skill-c' is composed by both 'skill-a' and 'skill-b'

  This means 'skill-c' will execute twice per workflow run.
  Consider:
  - Extracting shared dependency to workflow level
  - Adding caching to 'skill-c' (if idempotent)
  - Accepting the duplicate execution (if intentional)
```

---

## 3. Contract Compatibility

### 3.1 Structural Subtyping

Compatibility is determined by structure, not names.

**Rule 6: Output Must Cover Input**
Producer output MUST include all required fields of consumer input.

```python
def is_structurally_compatible(producer_output: Schema, consumer_input: Schema) -> bool:
    """
    Check structural compatibility.

    Producer output is compatible with consumer input if:
    1. All required fields in consumer exist in producer
    2. Types are assignable (see type assignability rules)
    3. Producer may have EXTRA fields (they are ignored)
    """
    consumer_required = set(consumer_input.required or [])
    producer_fields = set(producer_output.properties.keys())

    # All required fields must be present
    missing = consumer_required - producer_fields
    if missing:
        return False

    # Check type compatibility for matching fields
    for field in consumer_required:
        if not is_type_assignable(
            producer_output.properties[field],
            consumer_input.properties[field]
        ):
            return False

    return True
```

### 3.2 Field Mapping

Explicit field mapping allows renaming between skills:

```yaml
composes:
  - skill: user-lookup
    output_mapping:
      user_id: id           # Rename 'user_id' to 'id' for next skill
      full_name: name       # Rename 'full_name' to 'name'

  - skill: permission-check
    input_mapping:
      id: user_id           # Map 'id' from previous to 'user_id' input
```

### 3.3 Optional vs Required Fields

**Rule 7: Optional Fields May Be Omitted**
Producer is not required to output optional fields.

```yaml
# Consumer input_schema
input_schema:
  type: object
  properties:
    user_id:
      type: string
    preferences:    # Optional - producer doesn't need to output this
      type: object
  required:
    - user_id       # Only user_id is required
```

---

## 4. Version Compatibility

### 4.1 Semantic Versioning

Skills use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (removed outputs, changed required inputs)
- **MINOR**: Backwards-compatible additions (new optional outputs)
- **PATCH**: Bug fixes, documentation

### 4.2 Version Constraints

Skills declare version requirements using npm-style constraints:

| Constraint | Meaning | Example |
|------------|---------|---------|
| `1.2.3` | Exact version | Only 1.2.3 |
| `>=1.2.0` | Minimum version | 1.2.0, 1.3.0, 2.0.0 |
| `^1.2.0` | Compatible with 1.x | 1.2.0, 1.9.0 (not 2.0.0) |
| `~1.2.0` | Patch updates only | 1.2.0, 1.2.5 (not 1.3.0) |

```yaml
requires:
  - skill: user-lookup
    version: "^1.2.0"    # Any 1.x version >= 1.2.0
  - skill: email-sender
    version: "~2.1.0"    # Any 2.1.x version
```

### 4.3 Breaking Change Detection

```python
def detect_breaking_changes(old: SkillDefinition, new: SkillDefinition) -> list[Change]:
    """
    Detect breaking changes between skill versions.

    Breaking changes:
    - Removed output field
    - Changed output field type (narrowing)
    - Added required input field
    - Removed optional input field that was previously output
    """
    changes = []

    # Check removed outputs
    old_outputs = set(old.output_schema.properties.keys())
    new_outputs = set(new.output_schema.properties.keys())

    for removed in old_outputs - new_outputs:
        changes.append(Change(
            type="BREAKING",
            field=removed,
            message=f"Output field '{removed}' was removed"
        ))

    # Check new required inputs
    old_required = set(old.input_schema.required or [])
    new_required = set(new.input_schema.required or [])

    for added in new_required - old_required:
        if added not in old.input_schema.properties:
            changes.append(Change(
                type="BREAKING",
                field=added,
                message=f"New required input field '{added}'"
            ))

    return changes
```

---

## 5. Effect Propagation

### 5.1 Effect Inference

A composite skill's effects are the union of its composed skills' effects.

```
L2: data-pipeline
├── L1: fetch-data     (effects: Query, Network, Fail)
├── L1: transform      (effects: none)
└── L1: save-results   (effects: Mutate, Fail)

Inferred effects for data-pipeline: {Query, Network, Fail, Mutate}
```

### 5.2 Operation Inference

A composite skill's operation is the highest-severity of its composed skills:

```
TRANSFORM < READ < WRITE

L2: update-user-profile
├── L1: get-user       (operation: READ)
├── L1: validate       (operation: TRANSFORM)
└── L1: save-user      (operation: WRITE)

Inferred operation: WRITE (highest severity)
```

**Rule 8: Effect Monotonicity**
A composite skill's effects can only ADD to composed skills' effects, never remove.

---

## 6. Execution Semantics

### 6.1 Execution Order

Skills execute in topological order of the dependency graph.

```python
def get_execution_order(workflow: SkillDefinition) -> list[str]:
    """
    Get skills in execution order (topological sort).

    Skills with no dependencies execute first.
    Skills are executed when all their dependencies complete.
    """
    graph = build_dependency_graph(workflow)
    return list(nx.topological_sort(graph))
```

### 6.2 Parallel Execution

Skills with no mutual dependencies MAY execute in parallel:

```
        ┌────────────┐
        │  workflow  │
        └────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐
│fetch-a│ │fetch-b│ │fetch-c│  ← Can run in parallel
└───────┘ └───────┘ └───────┘
    │         │         │
    └─────────┼─────────┘
              ▼
        ┌───────────┐
        │  combine  │  ← Waits for all fetches
        └───────────┘
```

### 6.3 Error Handling

**Rule 9: Fail-Fast by Default**
If a skill fails, the workflow stops and propagates the error.

**Rule 10: Retry Configuration**
Skills may specify retry behavior:

```yaml
retry:
  max_attempts: 3
  backoff: exponential
  retry_on:
    - NetworkError
    - RateLimitError
```

---

## 7. Compatibility Guarantees

### 7.1 Forward Compatibility

New skill versions SHOULD NOT break existing consumers if:
- Only optional outputs are added
- Only optional inputs are added with defaults
- Patch version changes

### 7.2 Backward Compatibility

Old skill versions remain usable if:
- Consumer only uses fields that existed in old version
- Version constraints are satisfied

### 7.3 Migration Path

When breaking changes occur:
1. Release new major version
2. Mark old version as deprecated (with sunset date)
3. Provide migration guide in changelog
4. Remove old version after sunset date

---

## Appendix A: Composition Examples

### A.1 Simple Composition (L2)

```yaml
id: user-with-permissions
level: 2
composes:
  - user-lookup
  - permission-lookup

input_schema:
  type: object
  properties:
    user_id: { type: string }
  required: [user_id]

output_schema:
  type: object
  properties:
    user:
      type: object
      properties:
        id: { type: string }
        name: { type: string }
    permissions:
      type: array
      items: { type: string }
```

### A.2 Workflow with Branching (L3)

```yaml
id: pr-review-workflow
level: 3
composes:
  - fetch-pr-diff
  - analyze-security
  - analyze-performance
  - generate-review
  - post-comment

execution:
  - step: fetch-pr-diff
  - parallel:
      - step: analyze-security
      - step: analyze-performance
  - step: generate-review
    inputs:
      security: $analyze-security.output
      performance: $analyze-performance.output
  - step: post-comment
    condition: $input.auto_post == true
```

---

## Appendix B: Error Code Reference

| Code | Error | Cause |
|------|-------|-------|
| E010 | LEVEL_VIOLATION | L1 skill has composes field |
| E013 | MISSING_COMPOSITION | L2/L3 skill has empty composes |
| E014 | INVALID_L2_COMPOSE | L2 composing non-L1 skill |
| E015 | INVALID_L3_COMPOSE | L3 composing L3 skill |
| E016 | DIAMOND_WARNING | Same skill composed multiple times |
| E017 | VERSION_CONFLICT | Conflicting version requirements |
| E018 | DEPRECATED_SKILL | Using deprecated skill version |
