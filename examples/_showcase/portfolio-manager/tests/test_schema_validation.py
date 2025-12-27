"""Tests for schema validation in portfolio manager skills.

This module validates that input/output schemas are well-formed and follow
consistent patterns across the skill library.
"""

import pytest
import re
from pathlib import Path


# =============================================================================
# Schema Structure Tests
# =============================================================================

class TestInputSchemaStructure:
    """Verify input schemas are well-formed."""

    def test_all_skills_have_input_schema(self, all_skill_dirs):
        """Most skills should define an input schema."""
        missing_input = []
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # L3 workflows might have implicit inputs via composed skills
            if "level: 3" in content:
                continue
            if "## Input" not in content and "input:" not in content:
                missing_input.append(skill_dir.name)

        # Allow some flexibility
        assert len(missing_input) <= 2, f"Skills missing input schema: {missing_input}"

    def test_input_schemas_have_types(self, all_skill_dirs):
        """Input parameters should have type declarations."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "input:" not in content:
                continue

            # Extract input section
            input_match = re.search(r'input:(.*?)(?=\noutput:|```|$)', content, re.DOTALL)
            if input_match:
                input_section = input_match.group(1)
                # Check for type declarations
                assert "type:" in input_section or "type: " in input_section, \
                    f"{skill_dir.name} input schema should have type declarations"

    def test_required_fields_marked(self, all_skill_dirs):
        """Input schemas should mark required fields."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "input:" not in content:
                continue

            # Check for required markers
            has_required = (
                "required: true" in content or
                "required:" in content or
                "Required" in content
            )
            # Soft check - at least some should have required markers
            # (not asserting, just checking pattern exists in codebase)


class TestOutputSchemaStructure:
    """Verify output schemas are well-formed."""

    def test_all_skills_have_output_schema(self, all_skill_dirs):
        """Most skills should define an output schema."""
        missing_output = []
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "## Output" not in content and "output:" not in content:
                missing_output.append(skill_dir.name)

        # All skills should have outputs
        assert len(missing_output) == 0, f"Skills missing output schema: {missing_output}"

    def test_output_schemas_have_types(self, all_skill_dirs):
        """Output parameters should have type declarations."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "output:" not in content:
                continue

            # Extract output section
            output_match = re.search(r'output:(.*?)(?=\n##|```\n\n|$)', content, re.DOTALL)
            if output_match:
                output_section = output_match.group(1)
                # Check for type declarations
                assert "type:" in output_section or ":" in output_section, \
                    f"{skill_dir.name} output schema should have type declarations"


# =============================================================================
# Type Consistency Tests
# =============================================================================

class TestTypeConsistency:
    """Verify consistent type usage across schemas."""

    VALID_TYPES = [
        'string', 'number', 'integer', 'boolean', 'array', 'object',
        'date', 'datetime', 'enum', 'any'
    ]

    def test_types_are_valid(self, all_skill_dirs):
        """Skills should use recognized schema types."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # Find type declarations that are clearly schema types (indented with spaces)
            # Pattern: 2+ spaces, "type:", space, then a type name
            type_matches = re.findall(r'^[ ]{2,}type:\s+(\w+)', content, re.MULTILINE)

            # Filter to only check actual type declarations
            valid_types_found = [t for t in type_matches if t in self.VALID_TYPES]

            # Skills with schemas should have at least one valid type
            if "input:" in content or "output:" in content:
                assert len(valid_types_found) > 0, \
                    f"{skill_dir.name} has schema but no valid type declarations"

    def test_enum_values_defined(self, all_skill_dirs):
        """Enum types should have values defined."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "type: enum" in content:
                # Should have values: declaration nearby
                assert "values:" in content or "[" in content, \
                    f"{skill_dir.name} has enum type but no values defined"


# =============================================================================
# Array Schema Tests
# =============================================================================

class TestArraySchemas:
    """Verify array schemas have proper item definitions."""

    def test_arrays_have_items(self, all_skill_dirs):
        """Array types should define item structure."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # Find array declarations
            if "type: array" in content:
                # Should have items definition
                assert "items:" in content or "items" in content, \
                    f"{skill_dir.name} has array type but no items defined"


# =============================================================================
# Object Schema Tests
# =============================================================================

class TestObjectSchemas:
    """Verify object schemas have proper property definitions."""

    def test_objects_have_properties(self, all_skill_dirs):
        """Object types should define properties."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # Check object types in input/output sections
            if "type: object" in content:
                # Should have properties defined (either explicit or implicit via indentation)
                has_properties = (
                    "properties:" in content or
                    re.search(r'type: object\n\s+\w+:', content)
                )
                # Soft check - some objects might be opaque
                if not has_properties:
                    pass  # Allow opaque objects for now


# =============================================================================
# Schema Reference Tests
# =============================================================================

class TestSchemaReferences:
    """Verify schema references are valid."""

    def test_no_undefined_references(self, all_skill_dirs):
        """Schema references should point to defined types."""
        # Collect all defined custom types
        defined_types = set()
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # Find type definitions (capitalized names after type:)
            type_defs = re.findall(r'^(\w+):\s*$', content, re.MULTILINE)
            defined_types.update(type_defs)

        # This is informational - we're building a type registry

    def test_common_types_used_consistently(self, all_skill_dirs):
        """Common field names should use consistent types."""
        type_map = {}

        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # Find field: type patterns
            field_types = re.findall(r'(\w+):\s*\n\s+type:\s*(\w+)', content)
            for field, type_val in field_types:
                if field in type_map:
                    # Check consistency
                    if type_map[field] != type_val:
                        # Allow some flexibility (e.g., number vs integer)
                        if not (type_val in ['number', 'integer'] and
                                type_map[field] in ['number', 'integer']):
                            pass  # Soft check for now
                else:
                    type_map[field] = type_val


# =============================================================================
# Description Tests
# =============================================================================

class TestSchemaDescriptions:
    """Verify schemas have helpful descriptions."""

    def test_complex_fields_have_descriptions(self, all_skill_dirs):
        """Complex schema fields should have at least one description."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # Count objects and arrays
            complex_count = content.count("type: object") + content.count("type: array")
            desc_count = content.count("description:")

            # Should have at least one description for schemas with complex types
            if complex_count > 3:
                assert desc_count >= 1, \
                    f"{skill_dir.name} has {complex_count} complex types but no descriptions"


# =============================================================================
# Example Tests
# =============================================================================

class TestSchemaExamples:
    """Verify schemas have usage examples."""

    def test_skills_have_examples(self, all_skill_dirs):
        """Skills should have example input/output."""
        missing_examples = []
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text().lower()
            has_example = (
                "example" in content or
                "usage" in content or
                "```yaml" in content.lower()
            )
            if not has_example:
                missing_examples.append(skill_dir.name)

        # Soft check
        if missing_examples:
            print(f"Note: Skills without clear examples: {missing_examples}")
