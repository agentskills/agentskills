"""Tests for MCP (Model Context Protocol) integration skills."""

import pytest
import re
import yaml
from pathlib import Path

from conftest import (
    MCP_ATOMIC_SKILLS,
    MCP_COMPOSITE_SKILLS,
    MCP_WORKFLOW_SKILLS,
)


class TestMCPSkillsExist:
    """Test that all MCP skills exist with proper structure."""

    @pytest.mark.parametrize("skill_name", MCP_ATOMIC_SKILLS)
    def test_mcp_atomic_skill_exists(self, atomic_dir, skill_name):
        """Each MCP atomic skill should have a SKILL.md file."""
        skill_path = atomic_dir / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing SKILL.md for atomic skill: {skill_name}"

    @pytest.mark.parametrize("skill_name", MCP_COMPOSITE_SKILLS)
    def test_mcp_composite_skill_exists(self, composite_dir, skill_name):
        """Each MCP composite skill should have a SKILL.md file."""
        skill_path = composite_dir / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing SKILL.md for composite skill: {skill_name}"

    @pytest.mark.parametrize("skill_name", MCP_WORKFLOW_SKILLS)
    def test_mcp_workflow_skill_exists(self, workflows_dir, skill_name):
        """Each MCP workflow skill should have a SKILL.md file."""
        skill_path = workflows_dir / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing SKILL.md for workflow skill: {skill_name}"


class TestMCPSkillMetadata:
    """Test metadata consistency for MCP skills."""

    def _extract_metadata(self, skill_path):
        """Extract metadata block from SKILL.md."""
        content = skill_path.read_text()
        yaml_match = re.search(
            r"## Metadata\s*```yaml\s*(.*?)```",
            content,
            re.DOTALL,
        )
        if yaml_match:
            return yaml.safe_load(yaml_match.group(1))
        return None

    @pytest.mark.parametrize("skill_name", MCP_ATOMIC_SKILLS)
    def test_mcp_atomic_has_level_1(self, atomic_dir, skill_name):
        """MCP atomic skills should have level: 1."""
        skill_path = atomic_dir / skill_name / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None, f"No metadata found for {skill_name}"
        assert metadata.get("level") == 1, f"{skill_name} should have level: 1"

    @pytest.mark.parametrize("skill_name", MCP_COMPOSITE_SKILLS)
    def test_mcp_composite_has_level_2(self, composite_dir, skill_name):
        """MCP composite skills should have level: 2."""
        skill_path = composite_dir / skill_name / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None, f"No metadata found for {skill_name}"
        assert metadata.get("level") == 2, f"{skill_name} should have level: 2"

    @pytest.mark.parametrize("skill_name", MCP_WORKFLOW_SKILLS)
    def test_mcp_workflow_has_level_3(self, workflows_dir, skill_name):
        """MCP workflow skills should have level: 3."""
        skill_path = workflows_dir / skill_name / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None, f"No metadata found for {skill_name}"
        assert metadata.get("level") == 3, f"{skill_name} should have level: 3"

    @pytest.mark.parametrize("skill_name", MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS)
    def test_mcp_skills_have_domain(self, showcase_dir, skill_name):
        """All MCP skills should have domain: mcp."""
        # Find the skill in the appropriate directory
        for level_dir in ["_atomic", "_composite", "_workflows"]:
            skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                metadata = self._extract_metadata(skill_path)
                assert metadata is not None, f"No metadata found for {skill_name}"
                assert metadata.get("domain") == "mcp", f"{skill_name} should have domain: mcp"
                return
        pytest.fail(f"Skill {skill_name} not found")


class TestMCPSkillOperations:
    """Test operation types for MCP skills."""

    def _extract_metadata(self, skill_path):
        """Extract metadata block from SKILL.md."""
        content = skill_path.read_text()
        yaml_match = re.search(
            r"## Metadata\s*```yaml\s*(.*?)```",
            content,
            re.DOTALL,
        )
        if yaml_match:
            return yaml.safe_load(yaml_match.group(1))
        return None

    @pytest.mark.parametrize("skill_name", [
        "mcp-server-list",
        "mcp-tools-list",
        "mcp-resources-list",
        "mcp-prompts-list",
    ])
    def test_mcp_read_skills_are_read_operation(self, atomic_dir, skill_name):
        """MCP listing/query skills should have operation: READ."""
        skill_path = atomic_dir / skill_name / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None
        assert metadata.get("operation") == "READ", f"{skill_name} should be READ"

    def test_mcp_tool_call_is_write_operation(self, atomic_dir):
        """mcp-tool-call executes tools and should be WRITE."""
        skill_path = atomic_dir / "mcp-tool-call" / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None
        assert metadata.get("operation") == "WRITE"

    def test_mcp_tool_validate_is_read_operation(self, composite_dir):
        """mcp-tool-validate only checks schema, should be READ."""
        skill_path = composite_dir / "mcp-tool-validate" / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None
        assert metadata.get("operation") == "READ"

    def test_mcp_skill_map_is_transform_operation(self, composite_dir):
        """mcp-skill-map transforms data, should be TRANSFORM."""
        skill_path = composite_dir / "mcp-skill-map" / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None
        assert metadata.get("operation") == "TRANSFORM"


class TestMCPSkillSchemas:
    """Test input/output schemas for MCP skills."""

    def _extract_json_blocks(self, content, section_name):
        """Extract JSON blocks from a section."""
        pattern = rf"## {section_name}\s*```json\s*(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            import json
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    @pytest.mark.parametrize("skill_name", MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS)
    def test_mcp_skills_have_input_schema(self, showcase_dir, skill_name):
        """All MCP skills should have an input schema."""
        for level_dir in ["_atomic", "_composite", "_workflows"]:
            skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                schema = self._extract_json_blocks(content, "Input Schema")
                assert schema is not None, f"{skill_name} should have Input Schema"
                assert "type" in schema, f"{skill_name} Input Schema should have type"
                return
        pytest.fail(f"Skill {skill_name} not found")

    @pytest.mark.parametrize("skill_name", MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS)
    def test_mcp_skills_have_output_schema(self, showcase_dir, skill_name):
        """All MCP skills should have an output schema."""
        for level_dir in ["_atomic", "_composite", "_workflows"]:
            skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                schema = self._extract_json_blocks(content, "Output Schema")
                assert schema is not None, f"{skill_name} should have Output Schema"
                assert "type" in schema, f"{skill_name} Output Schema should have type"
                return
        pytest.fail(f"Skill {skill_name} not found")

    @pytest.mark.parametrize("skill_name", [
        "mcp-tool-call",
        "mcp-tool-retry",
        "mcp-reliable-execute",
    ])
    def test_execution_skills_have_server_param(self, showcase_dir, skill_name):
        """Execution-related skills should require server parameter."""
        for level_dir in ["_atomic", "_composite", "_workflows"]:
            skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                schema = self._extract_json_blocks(content, "Input Schema")
                assert schema is not None
                props = schema.get("properties", {})
                assert "server" in props, f"{skill_name} should have server parameter"
                required = schema.get("required", [])
                assert "server" in required, f"{skill_name} should require server"
                return
        pytest.fail(f"Skill {skill_name} not found")

    def test_mcp_tool_batch_has_server_in_calls(self, composite_dir):
        """mcp-tool-batch should have server parameter inside calls items."""
        skill_path = composite_dir / "mcp-tool-batch" / "SKILL.md"
        content = skill_path.read_text()
        schema = self._extract_json_blocks(content, "Input Schema")
        assert schema is not None
        # Server is inside each call item, not at top level
        calls_schema = schema.get("properties", {}).get("calls", {})
        items_schema = calls_schema.get("items", {})
        item_props = items_schema.get("properties", {})
        assert "server" in item_props, "Each call should have server parameter"
        item_required = items_schema.get("required", [])
        assert "server" in item_required, "Server should be required in each call"


class TestMCPComposition:
    """Test composition relationships in MCP skills."""

    def _extract_composes(self, skill_path):
        """Extract Composes section from SKILL.md."""
        content = skill_path.read_text()
        match = re.search(r"## Composes\s*(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if match:
            composes_text = match.group(1)
            # Extract skill names from bullet points
            skills = re.findall(r"- `([^`]+)`", composes_text)
            return skills
        return []

    @pytest.mark.parametrize("skill_name", MCP_COMPOSITE_SKILLS)
    def test_mcp_composite_skills_compose_atomics(self, composite_dir, skill_name):
        """MCP composite skills should compose atomic skills."""
        skill_path = composite_dir / skill_name / "SKILL.md"
        composes = self._extract_composes(skill_path)
        assert len(composes) > 0, f"{skill_name} should compose other skills"

    @pytest.mark.parametrize("skill_name", MCP_WORKFLOW_SKILLS)
    def test_mcp_workflow_skills_compose_others(self, workflows_dir, skill_name):
        """MCP workflow skills should compose other skills."""
        skill_path = workflows_dir / skill_name / "SKILL.md"
        composes = self._extract_composes(skill_path)
        assert len(composes) > 0, f"{skill_name} should compose other skills"

    def test_mcp_tool_discover_composes_list_and_intent(self, composite_dir):
        """mcp-tool-discover should compose tools-list and intent-classify."""
        skill_path = composite_dir / "mcp-tool-discover" / "SKILL.md"
        composes = self._extract_composes(skill_path)
        assert "mcp-tools-list" in composes
        assert "intent-classify" in composes

    def test_mcp_skill_generate_composes_multiple_skills(self, workflows_dir):
        """mcp-skill-generate should compose multiple MCP skills."""
        skill_path = workflows_dir / "mcp-skill-generate" / "SKILL.md"
        composes = self._extract_composes(skill_path)
        # Should compose at least 5 skills for full workflow
        assert len(composes) >= 5, "mcp-skill-generate should compose many skills"
        # Check some expected compositions
        assert "mcp-server-list" in composes
        assert "mcp-tools-list" in composes
        assert "mcp-skill-map" in composes


class TestMCPReliabilityPatterns:
    """Test reliability decorator patterns in MCP skills."""

    def _extract_metadata(self, skill_path):
        """Extract metadata block from SKILL.md."""
        content = skill_path.read_text()
        yaml_match = re.search(
            r"## Metadata\s*```yaml\s*(.*?)```",
            content,
            re.DOTALL,
        )
        if yaml_match:
            return yaml.safe_load(yaml_match.group(1))
        return None

    def test_mcp_tool_retry_has_retry_decorator(self, composite_dir):
        """mcp-tool-retry should declare retry decorator."""
        skill_path = composite_dir / "mcp-tool-retry" / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None
        decorators = metadata.get("decorators", [])
        assert "retry" in decorators, "mcp-tool-retry should have retry decorator"

    def test_mcp_tool_validate_has_validate_decorator(self, composite_dir):
        """mcp-tool-validate should declare validate decorator."""
        skill_path = composite_dir / "mcp-tool-validate" / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None
        decorators = metadata.get("decorators", [])
        assert "validate" in decorators

    def test_mcp_reliable_execute_has_multiple_decorators(self, workflows_dir):
        """mcp-reliable-execute should have comprehensive decorators."""
        skill_path = workflows_dir / "mcp-reliable-execute" / "SKILL.md"
        metadata = self._extract_metadata(skill_path)
        assert metadata is not None
        decorators = metadata.get("decorators", [])
        expected = ["validate", "retry", "timeout", "log"]
        for d in expected:
            assert d in decorators, f"mcp-reliable-execute should have {d} decorator"


class TestMCPErrorCodes:
    """Test error code documentation in MCP skills."""

    def _has_error_codes_section(self, skill_path):
        """Check if skill has Error Codes section."""
        content = skill_path.read_text()
        return "## Error Codes" in content

    @pytest.mark.parametrize("skill_name", MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS)
    def test_mcp_skills_document_error_codes(self, showcase_dir, skill_name):
        """All MCP skills should document error codes."""
        for level_dir in ["_atomic", "_composite", "_workflows"]:
            skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                assert self._has_error_codes_section(skill_path), \
                    f"{skill_name} should have Error Codes section"
                return
        pytest.fail(f"Skill {skill_name} not found")

    def test_mcp_error_codes_use_prefix(self, showcase_dir):
        """MCP error codes should use MCP_ prefix."""
        mcp_skills = MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS
        for skill_name in mcp_skills:
            for level_dir in ["_atomic", "_composite", "_workflows"]:
                skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
                if skill_path.exists():
                    content = skill_path.read_text()
                    # Find error code table
                    error_section = re.search(
                        r"## Error Codes\s*(.*?)(?=\n## |\Z)",
                        content,
                        re.DOTALL,
                    )
                    if error_section:
                        codes = re.findall(r"\| `?(MCP_\w+)`?", error_section.group(1))
                        if codes:
                            for code in codes:
                                assert code.startswith("MCP_"), \
                                    f"Error code {code} should use MCP_ prefix"
                    break


class TestMCPJsonRpcProtocol:
    """Test JSON-RPC protocol documentation in MCP skills."""

    def _has_jsonrpc_section(self, skill_path):
        """Check if skill documents JSON-RPC request format."""
        content = skill_path.read_text()
        return "## JSON-RPC Request" in content or "JSON-RPC" in content

    @pytest.mark.parametrize("skill_name", [
        "mcp-tools-list",
        "mcp-tool-call",
        "mcp-resources-list",
        "mcp-prompts-list",
    ])
    def test_protocol_skills_document_jsonrpc(self, atomic_dir, skill_name):
        """Protocol-level skills should document JSON-RPC format."""
        skill_path = atomic_dir / skill_name / "SKILL.md"
        assert self._has_jsonrpc_section(skill_path), \
            f"{skill_name} should document JSON-RPC request format"

    def test_mcp_tools_list_uses_tools_list_method(self, atomic_dir):
        """mcp-tools-list should use tools/list method."""
        skill_path = atomic_dir / "mcp-tools-list" / "SKILL.md"
        content = skill_path.read_text()
        assert '"method": "tools/list"' in content

    def test_mcp_tool_call_uses_tools_call_method(self, atomic_dir):
        """mcp-tool-call should use tools/call method."""
        skill_path = atomic_dir / "mcp-tool-call" / "SKILL.md"
        content = skill_path.read_text()
        assert '"method": "tools/call"' in content


class TestMCPExamples:
    """Test example documentation in MCP skills."""

    def _has_example_section(self, skill_path):
        """Check if skill has Example section."""
        content = skill_path.read_text()
        return "## Example" in content

    @pytest.mark.parametrize("skill_name", MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS)
    def test_mcp_skills_have_examples(self, showcase_dir, skill_name):
        """All MCP skills should have usage examples."""
        for level_dir in ["_atomic", "_composite", "_workflows"]:
            skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                assert self._has_example_section(skill_path), \
                    f"{skill_name} should have Example section"
                return
        pytest.fail(f"Skill {skill_name} not found")

    def test_examples_show_input_and_output(self, showcase_dir):
        """Examples should show both input and output."""
        mcp_skills = MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS
        for skill_name in mcp_skills[:5]:  # Check first 5 for speed
            for level_dir in ["_atomic", "_composite", "_workflows"]:
                skill_path = showcase_dir / level_dir / skill_name / "SKILL.md"
                if skill_path.exists():
                    content = skill_path.read_text()
                    example_section = re.search(
                        r"## Example\s*(.*?)(?=\n## |\Z)",
                        content,
                        re.DOTALL,
                    )
                    if example_section:
                        section_text = example_section.group(1)
                        assert "Input" in section_text or "**Input:**" in section_text, \
                            f"{skill_name} example should show input"
                        assert "Output" in section_text or "**Output" in section_text, \
                            f"{skill_name} example should show output"
                    break


class TestMCPSkillCount:
    """Test total MCP skill counts."""

    def test_total_mcp_atomic_skills(self):
        """Should have 5 MCP atomic skills."""
        assert len(MCP_ATOMIC_SKILLS) == 5

    def test_total_mcp_composite_skills(self):
        """Should have 5 MCP composite skills."""
        assert len(MCP_COMPOSITE_SKILLS) == 5

    def test_total_mcp_workflow_skills(self):
        """Should have 2 MCP workflow skills."""
        assert len(MCP_WORKFLOW_SKILLS) == 2

    def test_total_mcp_skills(self):
        """Should have 12 total MCP skills."""
        total = len(MCP_ATOMIC_SKILLS) + len(MCP_COMPOSITE_SKILLS) + len(MCP_WORKFLOW_SKILLS)
        assert total == 12
