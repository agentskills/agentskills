"""Tests for skill composition validation."""

import pytest
from pathlib import Path
import tempfile
import os

from skills_ref.composition import (
    CompositionType,
    SkillComposition,
    CompositionResult,
    parse_composition_metadata,
    check_composition,
)


class TestCompositionType:
    """Test CompositionType matching."""

    def test_exact_match(self):
        t1 = CompositionType(type_name="email-list")
        t2 = CompositionType(type_name="email-list")
        assert t1.matches(t2)

    def test_mismatch(self):
        t1 = CompositionType(type_name="email-list")
        t2 = CompositionType(type_name="message-list")
        assert not t1.matches(t2)

    def test_wildcard_matches_any(self):
        wildcard = CompositionType(type_name="*")
        specific = CompositionType(type_name="email-list")
        assert wildcard.matches(specific)
        assert specific.matches(wildcard)


class TestSkillComposition:
    """Test SkillComposition compatibility checks."""

    def test_can_receive_matching_type(self):
        source = SkillComposition(
            name="email-read",
            inputs=[],
            outputs=[CompositionType(type_name="email-list")],
        )
        target = SkillComposition(
            name="customer-intel",
            inputs=[CompositionType(type_name="email-list")],
            outputs=[CompositionType(type_name="intel-brief")],
        )
        assert target.can_receive_from(source)

    def test_cannot_receive_mismatched_type(self):
        source = SkillComposition(
            name="email-read",
            inputs=[],
            outputs=[CompositionType(type_name="email-list")],
        )
        target = SkillComposition(
            name="slack-processor",
            inputs=[CompositionType(type_name="message-list")],
            outputs=[CompositionType(type_name="summary")],
        )
        assert not target.can_receive_from(source)

    def test_empty_inputs_accepts_anything(self):
        source = SkillComposition(
            name="source",
            inputs=[],
            outputs=[CompositionType(type_name="data")],
        )
        target = SkillComposition(
            name="target",
            inputs=[],  # No input constraints
            outputs=[CompositionType(type_name="result")],
        )
        assert target.can_receive_from(source)

    def test_empty_outputs_cannot_feed(self):
        source = SkillComposition(
            name="source",
            inputs=[],
            outputs=[],  # Produces nothing
        )
        target = SkillComposition(
            name="target",
            inputs=[CompositionType(type_name="data")],
            outputs=[],
        )
        assert not target.can_receive_from(source)


class TestParseCompositionMetadata:
    """Test parsing composition metadata from frontmatter."""

    def test_parse_full_composition(self):
        metadata = {
            "name": "test-skill",
            "description": "Test skill",
            "composition": {
                "inputs": ["email-list", "message-list"],
                "outputs": ["intel-brief"],
            },
        }
        comp = parse_composition_metadata(metadata)
        assert comp is not None
        assert comp.name == "test-skill"
        assert len(comp.inputs) == 2
        assert len(comp.outputs) == 1
        assert comp.inputs[0].type_name == "email-list"
        assert comp.outputs[0].type_name == "intel-brief"

    def test_parse_single_string_types(self):
        metadata = {
            "name": "simple",
            "composition": {
                "inputs": "data",
                "outputs": "result",
            },
        }
        comp = parse_composition_metadata(metadata)
        assert comp is not None
        assert len(comp.inputs) == 1
        assert comp.inputs[0].type_name == "data"

    def test_parse_no_composition(self):
        metadata = {
            "name": "basic-skill",
            "description": "No composition metadata",
        }
        comp = parse_composition_metadata(metadata)
        assert comp is None

    def test_parse_outputs_only(self):
        """Test skill with outputs but no inputs (like a reader skill)."""
        metadata = {
            "name": "reader",
            "composition": {
                "outputs": ["data"],
            },
        }
        comp = parse_composition_metadata(metadata)
        assert comp is not None
        assert comp.inputs == []
        assert len(comp.outputs) == 1


class TestCheckComposition:
    """Integration tests for composition checking with actual skill directories."""

    @pytest.fixture
    def temp_skills(self):
        """Create temporary skill directories for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source skill (no inputs, one output)
            source_dir = Path(tmpdir) / "email-read"
            source_dir.mkdir()
            (source_dir / "SKILL.md").write_text("""---
name: email-read
description: Read emails from various sources
composition:
  outputs:
    - email-list
---

# email-read

Reads emails.
""")

            # Create compatible target skill
            target_dir = Path(tmpdir) / "customer-intel"
            target_dir.mkdir()
            (target_dir / "SKILL.md").write_text("""---
name: customer-intel
description: Aggregate customer intelligence
composition:
  inputs:
    - email-list
    - message-list
  outputs:
    - intel-brief
---

# customer-intel

Aggregates intelligence.
""")

            # Create incompatible skill
            incompatible_dir = Path(tmpdir) / "slack-writer"
            incompatible_dir.mkdir()
            (incompatible_dir / "SKILL.md").write_text("""---
name: slack-writer
description: Write messages to Slack
composition:
  inputs:
    - message-draft
  outputs:
    - send-result
---

# slack-writer

Writes to Slack.
""")

            # Create skill without composition metadata
            unconstrained_dir = Path(tmpdir) / "basic-skill"
            unconstrained_dir.mkdir()
            (unconstrained_dir / "SKILL.md").write_text("""---
name: basic-skill
description: A basic skill without composition constraints
---

# basic-skill

Does basic things.
""")

            yield {
                "source": source_dir,
                "target": target_dir,
                "incompatible": incompatible_dir,
                "unconstrained": unconstrained_dir,
            }

    def test_compatible_composition(self, temp_skills):
        result = check_composition(temp_skills["source"], temp_skills["target"])
        assert result.valid is True
        assert "email-list" in result.reason
        assert result.matched_type == "email-list"

    def test_incompatible_composition(self, temp_skills):
        result = check_composition(temp_skills["source"], temp_skills["incompatible"])
        assert result.valid is False
        assert "Type mismatch" in result.reason

    def test_unconstrained_target(self, temp_skills):
        result = check_composition(temp_skills["source"], temp_skills["unconstrained"])
        assert result.valid is True
        assert "unconstrained" in result.reason.lower()

    def test_unconstrained_source(self, temp_skills):
        result = check_composition(temp_skills["unconstrained"], temp_skills["target"])
        assert result.valid is True
        assert "unconstrained" in result.reason.lower()

    def test_nonexistent_skill(self, temp_skills):
        fake_path = Path("/nonexistent/skill")
        result = check_composition(fake_path, temp_skills["target"])
        assert result.valid is False
        assert "does not exist" in result.reason
