# Test Suite Documentation

This document describes the test coverage for the skills-ref validator and its benefits.

## Overview

The test suite contains **184 tests** organised into six major categories, providing comprehensive validation of the Agent Skills specification.

## Test Categories

### 1. Core Skill Validation (~25 tests)

**What it tests:**
- SKILL.md file existence and structure
- Name validation (lowercase, hyphens, length limits)
- Description and compatibility field limits
- Directory-name matching
- Unexpected fields detection
- i18n support (Chinese, Russian, Unicode normalisation)

**Benefits:**
- **Prevents broken skills** from being published
- **Enforces naming consistency** across skill ecosystems
- **Enables internationalisation** for global adoption
- **Catches typos early** before they cause runtime issues

### 2. Composability (~20 tests)

**What it tests:**
- Level field validation (1=Atomic, 2=Composite, 3=Workflow)
- Operation types (READ, WRITE, TRANSFORM)
- Composes field structure and validation
- Business rules (e.g., Level 1 cannot compose other skills)
- Backwards compatibility with non-composable skills

**Benefits:**
- **Enforces MECE principles** at the architecture level
- **Prevents circular dependencies** before they cause infinite loops
- **Ensures deterministic tool selection** by validating composition graphs
- **Maintains backwards compatibility** so existing skills continue to work

### 3. Type System (~25 tests)

**What it tests:**
- Input/output field schemas
- Type compatibility (integer→number, datetime→date)
- Epistemic requirements (requires_source, requires_rationale)
- Range constraints with min/max validation
- Composition type checking between parent and child skills

**Benefits:**
- **Catches type mismatches at build time** rather than runtime
- **Prevents hallucination** through epistemic requirements
- **Enables IDE autocompletion** and documentation generation
- **Reduces integration bugs** when composing skills

### 4. Higher-Order Skills (~35 tests)

**What it tests:**
- Generic type parsing (`Skill<A, B>`)
- Type parameter validation (uppercase, no duplicates, scope)
- Decorator patterns (with-retry, with-cache)
- Combinator patterns (map-skill, fan-out)
- Type preservation through wrappers

**Benefits:**
- **Enables powerful abstractions** like retry, caching, and batching
- **Reduces code duplication** through generic skill wrappers
- **Validates complex compositions** that would otherwise fail at runtime
- **Supports functional programming patterns** in skill definitions

### 5. Lessons System (~45 tests)

**What it tests:**
- Lesson ID format (L-SKILL-NNN)
- Required fields (id, context, learned)
- Status lifecycle (observed→proposed→validated→applied→deprecated)
- Confidence thresholds for status transitions
- Business rules (validated needs confidence ≥0.8, applied needs proposed_edit)

**Benefits:**
- **Enables continuous improvement** through structured feedback
- **Prevents premature crystallisation** of unvalidated patterns
- **Creates audit trail** linking skill changes to lessons learned
- **Supports human-in-the-loop approval** before applying changes

### 6. Versioning (~34 tests)

**What it tests:**
- Semantic versioning format (MAJOR.MINOR.PATCH)
- Version history consistency
- Version constraints (>=, ^, ~, exact)
- Deprecated version rules (requires sunset_date)
- Breaking change requirements (requires migration guidance)

**Benefits:**
- **Protects consumers** from unexpected breaking changes
- **Enables safe evolution** of skills over time
- **Provides migration paths** when breaking changes are necessary
- **Supports dependency resolution** like npm or cargo

## Why Comprehensive Testing Matters

### For Skill Authors

1. **Fast feedback** - Errors caught before publishing
2. **Clear error messages** - Know exactly what to fix
3. **Confidence** - Know your skill meets the specification

### For Skill Consumers

1. **Reliability** - Published skills are validated
2. **Predictability** - Compositions work as expected
3. **Safety** - Type mismatches caught before runtime

### For the Ecosystem

1. **Interoperability** - Skills from different authors compose correctly
2. **Trust** - Validation creates a baseline quality standard
3. **Evolution** - Versioning enables safe updates without breaking consumers

## Running Tests

```bash
cd skills-ref
python -m pytest tests/ -v
```

### Quick check (summary only):
```bash
python -m pytest tests/ -q
```

### Run specific category:
```bash
# Core validation
python -m pytest tests/test_validator.py -k "test_valid_skill or test_invalid"

# Lessons
python -m pytest tests/test_validator.py -k "Lesson"

# Versioning
python -m pytest tests/test_validator.py -k "Version"
```

## Test Design Principles

1. **Each test validates one thing** - Clear, focused assertions
2. **Tests use temporary directories** - No side effects between tests
3. **Business rules are explicit** - Comments explain why rules exist
4. **Edge cases are covered** - Unicode, empty strings, boundary values
5. **Error messages are checked** - Ensures helpful feedback for users

## Contributing

When adding new features to the specification:

1. **Write tests first** - Define expected behaviour
2. **Cover happy path and errors** - Both valid and invalid cases
3. **Add business rule tests** - Enforce semantic constraints
4. **Update this README** - Document what the tests cover
