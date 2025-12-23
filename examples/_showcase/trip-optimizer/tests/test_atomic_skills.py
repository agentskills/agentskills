"""Tests for trip optimizer atomic (L1) skills."""

import pytest
import re
from pathlib import Path


class TestAtomicSkillsExist:
    """Test that all expected atomic skills exist."""

    def test_all_atomic_skills_have_directories(self, atomic_dir, atomic_skills):
        """Each expected atomic skill should have a directory."""
        for skill_name in atomic_skills:
            skill_path = atomic_dir / skill_name
            assert skill_path.exists(), f"Missing atomic skill directory: {skill_name}"
            assert skill_path.is_dir(), f"Atomic skill should be a directory: {skill_name}"

    def test_all_atomic_skills_have_skill_md(self, atomic_dir, atomic_skills):
        """Each atomic skill should have a SKILL.md file."""
        for skill_name in atomic_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md for atomic skill: {skill_name}"


class TestAtomicSkillStructure:
    """Test the structure of atomic skill definitions."""

    @pytest.fixture
    def atomic_skill_files(self, atomic_dir, atomic_skills):
        """Return list of SKILL.md paths for all atomic skills."""
        return [atomic_dir / name / "SKILL.md" for name in atomic_skills]

    def test_atomic_skills_have_yaml_frontmatter(self, atomic_skill_files):
        """All atomic skills should have YAML frontmatter."""
        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            assert content.startswith("---"), f"Missing YAML frontmatter in {skill_file.parent.name}"
            # Should have closing ---
            match = re.search(r'^---\n.*?\n---', content, re.DOTALL)
            assert match, f"Invalid YAML frontmatter in {skill_file.parent.name}"

    def test_atomic_skills_have_required_fields(self, atomic_skill_files):
        """All atomic skills should have required fields."""
        required_fields = ['name', 'description', 'level', 'operation']

        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            for field in required_fields:
                assert f"{field}:" in content, f"Missing {field} in {skill_file.parent.name}"

    def test_atomic_skills_are_level_1(self, atomic_skill_files):
        """All atomic skills should be level 1."""
        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            assert "level: 1" in content, f"{skill_file.parent.name} should be level 1"

    def test_atomic_skills_have_valid_operation(self, atomic_skill_files):
        """All atomic skills should have a valid operation type."""
        valid_operations = ['READ', 'WRITE', 'TRANSFORM']

        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            has_valid_op = any(f"operation: {op}" in content for op in valid_operations)
            assert has_valid_op, f"Invalid operation in {skill_file.parent.name}"


class TestAtomicSkillContent:
    """Test the content quality of atomic skills."""

    def test_flight_search_has_inputs(self, atomic_dir):
        """flight-search should have inputs section."""
        skill_file = atomic_dir / "flight-search" / "SKILL.md"
        content = skill_file.read_text()
        assert "## Inputs" in content or "| Parameter" in content, \
            "flight-search should have inputs section"

    def test_flight_search_has_origin_destination(self, atomic_dir):
        """flight-search should have origin and destination inputs."""
        skill_file = atomic_dir / "flight-search" / "SKILL.md"
        content = skill_file.read_text()
        assert "origin" in content.lower(), "flight-search should have origin input"
        assert "destination" in content.lower(), "flight-search should have destination input"

    def test_hotel_search_has_outputs(self, atomic_dir):
        """hotel-search should have outputs section."""
        skill_file = atomic_dir / "hotel-search" / "SKILL.md"
        content = skill_file.read_text()
        has_outputs = ("## Outputs" in content or
                      "| Field" in content or
                      "hotels" in content.lower())
        assert has_outputs, "hotel-search should have outputs"

    def test_weather_fetch_is_read_operation(self, atomic_dir):
        """weather-fetch should be READ operation."""
        skill_file = atomic_dir / "weather-fetch" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: READ" in content, "weather-fetch should be READ operation"

    def test_visa_check_is_read_operation(self, atomic_dir):
        """visa-check should be READ operation."""
        skill_file = atomic_dir / "visa-check" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: READ" in content, "visa-check should be READ operation"


class TestAtomicSkillDataTypes:
    """Test data type handling in atomic skills."""

    def test_search_skills_are_read_operation(self, atomic_dir):
        """Skills with 'search' in name should be READ operation."""
        search_skills = ["flight-search", "hotel-search", "activity-search"]
        for skill_name in search_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "operation: READ" in content, f"{skill_name} should be READ operation"

    def test_fetch_skills_are_read_operation(self, atomic_dir):
        """Skills with 'fetch' in name should be READ operation."""
        fetch_skills = ["weather-fetch"]
        for skill_name in fetch_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "operation: READ" in content, f"{skill_name} should be READ operation"

    def test_check_skills_are_read_operation(self, atomic_dir):
        """Skills with 'check' in name should be READ operation."""
        check_skills = ["visa-check"]
        for skill_name in check_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "operation: READ" in content, f"{skill_name} should be READ operation"


class TestTravelDomain:
    """Test travel domain-specific content."""

    def test_flight_search_has_date_inputs(self, atomic_dir):
        """flight-search should have date inputs."""
        skill_file = atomic_dir / "flight-search" / "SKILL.md"
        content = skill_file.read_text()
        has_date = "date" in content.lower() or "departure" in content.lower()
        assert has_date, "flight-search should have date inputs"

    def test_weather_fetch_has_weather_data(self, atomic_dir):
        """weather-fetch should return weather data."""
        skill_file = atomic_dir / "weather-fetch" / "SKILL.md"
        content = skill_file.read_text()
        has_weather = ("temperature" in content.lower() or
                      "sunshine" in content.lower() or
                      "rain" in content.lower())
        assert has_weather, "weather-fetch should return weather data"

    def test_visa_check_has_passport_input(self, atomic_dir):
        """visa-check should reference passport or nationality."""
        skill_file = atomic_dir / "visa-check" / "SKILL.md"
        content = skill_file.read_text()
        has_passport = ("passport" in content.lower() or
                       "nationality" in content.lower() or
                       "citizen" in content.lower())
        assert has_passport, "visa-check should reference passport/nationality"
