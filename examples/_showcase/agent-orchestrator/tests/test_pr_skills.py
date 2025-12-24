"""
Tests for pull request review skills.

These skills provide comprehensive PR review capabilities including
reading, commenting, reviewing, and iterative improvement workflows.
"""

import pytest
from pathlib import Path
import yaml
import re

# Test configuration
SHOWCASE_ROOT = Path(__file__).parent.parent
ATOMIC_DIR = SHOWCASE_ROOT / "_atomic"
COMPOSITE_DIR = SHOWCASE_ROOT / "_composite"
WORKFLOWS_DIR = SHOWCASE_ROOT / "_workflows"

PR_ATOMIC_SKILLS = [
    "pr-read",
    "pr-diff-read",
    "pr-comment-create",
    "pr-review-submit",
]

PR_COMPOSITE_SKILLS = [
    "pr-review",
    "pr-respond",
    "pr-improve",
]

PR_WORKFLOW_SKILLS = [
    "pr-review-complete",
]

ALL_PR_SKILLS = PR_ATOMIC_SKILLS + PR_COMPOSITE_SKILLS + PR_WORKFLOW_SKILLS


def read_skill(skill_name: str) -> str:
    """Read a skill file and return its content."""
    for dir_path in [ATOMIC_DIR, COMPOSITE_DIR, WORKFLOWS_DIR]:
        skill_path = dir_path / skill_name / "SKILL.md"
        if skill_path.exists():
            return skill_path.read_text()
    pytest.fail(f"Skill {skill_name} not found")


def extract_metadata(content: str) -> dict:
    """Extract metadata YAML block."""
    pattern = r"## Metadata\s*```yaml\n(.*?)```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}


class TestPRSkillsExist:
    """Verify all PR skills exist."""

    @pytest.mark.parametrize("skill_name", PR_ATOMIC_SKILLS)
    def test_atomic_skill_exists(self, skill_name):
        """Each atomic PR skill should have a SKILL.md file."""
        skill_path = ATOMIC_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing atomic skill: {skill_name}"

    @pytest.mark.parametrize("skill_name", PR_COMPOSITE_SKILLS)
    def test_composite_skill_exists(self, skill_name):
        """Each composite PR skill should have a SKILL.md file."""
        skill_path = COMPOSITE_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing composite skill: {skill_name}"

    @pytest.mark.parametrize("skill_name", PR_WORKFLOW_SKILLS)
    def test_workflow_skill_exists(self, skill_name):
        """Each workflow PR skill should have a SKILL.md file."""
        skill_path = WORKFLOWS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing workflow skill: {skill_name}"


class TestPRSkillsMetadata:
    """Test metadata consistency for PR skills."""

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_github_domain(self, skill_name):
        """All PR skills should have github domain."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        assert metadata.get("domain") == "github", \
            f"{skill_name} should have domain: github"

    @pytest.mark.parametrize("skill_name", PR_ATOMIC_SKILLS)
    def test_atomic_skills_are_level_1(self, skill_name):
        """Atomic PR skills should be level 1."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        assert metadata.get("level") == 1

    @pytest.mark.parametrize("skill_name", PR_COMPOSITE_SKILLS)
    def test_composite_skills_are_level_2(self, skill_name):
        """Composite PR skills should be level 2."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        assert metadata.get("level") == 2

    @pytest.mark.parametrize("skill_name", PR_WORKFLOW_SKILLS)
    def test_workflow_skills_are_level_3(self, skill_name):
        """Workflow PR skills should be level 3."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        assert metadata.get("level") == 3

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_code_review_tag(self, skill_name):
        """All PR skills should have code-review tag."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        tags = metadata.get("tags", [])
        assert "code-review" in tags, f"{skill_name} should have code-review tag"


class TestPRReadSkill:
    """Tests for pr-read atomic skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-read")

    def test_has_read_operation(self, skill_content):
        """pr-read should be a READ operation."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("operation") == "READ"

    def test_requires_repo_input(self, skill_content):
        """Should require repo parameter."""
        assert "repo:" in skill_content
        assert "owner/repo" in skill_content.lower()

    def test_requires_pr_number_input(self, skill_content):
        """Should require pr_number parameter."""
        assert "pr_number:" in skill_content

    def test_returns_pr_metadata(self, skill_content):
        """Should return PR metadata fields."""
        assert "title:" in skill_content
        assert "body:" in skill_content
        assert "state:" in skill_content
        assert "author:" in skill_content

    def test_supports_gh_cli(self, skill_content):
        """Should document gh CLI usage."""
        assert "gh pr view" in skill_content

    def test_supports_rest_api(self, skill_content):
        """Should document REST API usage."""
        assert "api.github.com" in skill_content

    def test_supports_mcp(self, skill_content):
        """Should document MCP server usage."""
        assert "MCP" in skill_content or "mcp" in skill_content

    def test_has_error_codes(self, skill_content):
        """Should document error codes."""
        assert "NOT_FOUND" in skill_content
        assert "Error Codes" in skill_content or "Error" in skill_content


class TestPRDiffReadSkill:
    """Tests for pr-diff-read atomic skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-diff-read")

    def test_has_read_operation(self, skill_content):
        """pr-diff-read should be a READ operation."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("operation") == "READ"

    def test_returns_file_list(self, skill_content):
        """Should return list of changed files."""
        assert "files:" in skill_content
        assert "filename:" in skill_content

    def test_returns_patch_content(self, skill_content):
        """Should return diff patch."""
        assert "patch:" in skill_content

    def test_returns_hunk_info(self, skill_content):
        """Should return hunk information for line positioning."""
        assert "hunk" in skill_content.lower()

    def test_supports_file_filter(self, skill_content):
        """Should support filtering by file pattern."""
        assert "filter" in skill_content.lower()

    def test_documents_line_positioning(self, skill_content):
        """Should explain line number to position mapping."""
        assert "line" in skill_content.lower()
        assert "position" in skill_content.lower() or "hunk" in skill_content.lower()


class TestPRCommentCreateSkill:
    """Tests for pr-comment-create atomic skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-comment-create")

    def test_has_write_operation(self, skill_content):
        """pr-comment-create should be a WRITE operation."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("operation") == "WRITE"

    def test_supports_general_comments(self, skill_content):
        """Should support general PR comments."""
        assert "general" in skill_content.lower()

    def test_supports_inline_comments(self, skill_content):
        """Should support inline/review comments."""
        assert "inline" in skill_content.lower()

    def test_supports_reply_comments(self, skill_content):
        """Should support reply to existing comments."""
        assert "reply" in skill_content.lower()

    def test_requires_body(self, skill_content):
        """Should require comment body."""
        assert "body:" in skill_content

    def test_supports_suggestions(self, skill_content):
        """Should support GitHub suggestion format."""
        assert "suggestion" in skill_content.lower()
        assert "```suggestion" in skill_content

    def test_documents_line_positioning(self, skill_content):
        """Should explain line number requirements."""
        assert "line:" in skill_content
        assert "path:" in skill_content

    def test_has_side_parameter(self, skill_content):
        """Should have LEFT/RIGHT side parameter for inline comments."""
        assert "side:" in skill_content
        assert "LEFT" in skill_content
        assert "RIGHT" in skill_content


class TestPRReviewSubmitSkill:
    """Tests for pr-review-submit atomic skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-review-submit")

    def test_has_write_operation(self, skill_content):
        """pr-review-submit should be a WRITE operation."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("operation") == "WRITE"

    def test_supports_approve(self, skill_content):
        """Should support APPROVE event."""
        assert "APPROVE" in skill_content

    def test_supports_request_changes(self, skill_content):
        """Should support REQUEST_CHANGES event."""
        assert "REQUEST_CHANGES" in skill_content

    def test_supports_comment(self, skill_content):
        """Should support COMMENT event."""
        assert "COMMENT" in skill_content

    def test_supports_batch_comments(self, skill_content):
        """Should support submitting multiple comments in one review."""
        assert "comments:" in skill_content

    def test_documents_review_states(self, skill_content):
        """Should document review state meanings."""
        assert "APPROVED" in skill_content or "Approve" in skill_content
        assert "CHANGES_REQUESTED" in skill_content or "REQUEST_CHANGES" in skill_content


class TestPRReviewComposite:
    """Tests for pr-review composite skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-review")

    def test_composes_atomic_skills(self, skill_content):
        """Should compose atomic PR skills."""
        assert "## Composes" in skill_content
        assert "pr-read" in skill_content
        assert "pr-diff-read" in skill_content

    def test_has_review_focus_areas(self, skill_content):
        """Should support focus areas for review."""
        assert "security" in skill_content.lower()
        assert "performance" in skill_content.lower()
        assert "correctness" in skill_content.lower()

    def test_has_severity_levels(self, skill_content):
        """Should categorise issues by severity."""
        assert "critical" in skill_content.lower()
        assert "high" in skill_content.lower()
        assert "medium" in skill_content.lower()

    def test_returns_issues_found(self, skill_content):
        """Should return list of issues found."""
        assert "issues_found:" in skill_content

    def test_makes_decision(self, skill_content):
        """Should determine review decision."""
        assert "decision:" in skill_content
        assert "APPROVE" in skill_content
        assert "REQUEST_CHANGES" in skill_content

    def test_has_execution_flow(self, skill_content):
        """Should document execution flow."""
        assert "GATHER" in skill_content or "FETCH" in skill_content or "gather" in skill_content
        assert "ANALYSE" in skill_content or "analyse" in skill_content.lower()


class TestPRRespondComposite:
    """Tests for pr-respond composite skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-respond")

    def test_composes_atomic_skills(self, skill_content):
        """Should compose atomic PR skills."""
        assert "## Composes" in skill_content
        assert "pr-read" in skill_content
        assert "pr-comment-create" in skill_content

    def test_classifies_comment_types(self, skill_content):
        """Should classify different comment types."""
        assert "question" in skill_content.lower()
        assert "suggestion" in skill_content.lower()

    def test_has_response_strategies(self, skill_content):
        """Should have strategies for different comment types."""
        assert "response" in skill_content.lower()
        assert "explanation" in skill_content.lower() or "acknowledge" in skill_content.lower()

    def test_supports_tone_options(self, skill_content):
        """Should support different response tones."""
        assert "tone:" in skill_content
        assert "professional" in skill_content.lower()


class TestPRImproveComposite:
    """Tests for pr-improve composite skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-improve")

    def test_composes_atomic_skills(self, skill_content):
        """Should compose atomic PR skills."""
        assert "## Composes" in skill_content
        assert "pr-read" in skill_content

    def test_applies_suggestions(self, skill_content):
        """Should apply GitHub suggestions."""
        assert "suggestion" in skill_content.lower()
        assert "apply" in skill_content.lower()

    def test_runs_tests(self, skill_content):
        """Should support running tests."""
        assert "run_tests" in skill_content or "test" in skill_content.lower()

    def test_creates_commits(self, skill_content):
        """Should create commits for changes."""
        assert "commit" in skill_content.lower()

    def test_notifies_reviewers(self, skill_content):
        """Should notify reviewers of changes."""
        assert "notify" in skill_content.lower()


class TestPRReviewCompleteWorkflow:
    """Tests for pr-review-complete workflow skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("pr-review-complete")

    def test_composes_all_pr_skills(self, skill_content):
        """Should compose multiple PR skills."""
        assert "## Composes" in skill_content
        assert "pr-read" in skill_content
        assert "pr-review" in skill_content

    def test_has_state_machine(self, skill_content):
        """Should have workflow state machine."""
        assert "INITIAL_REVIEW" in skill_content
        assert "AWAITING_CHANGES" in skill_content
        assert "APPROVED" in skill_content

    def test_supports_reviewer_role(self, skill_content):
        """Should support reviewer role."""
        assert "reviewer" in skill_content.lower()

    def test_supports_author_role(self, skill_content):
        """Should support author role."""
        assert "author" in skill_content.lower()

    def test_has_iteration_tracking(self, skill_content):
        """Should track review iterations."""
        assert "iteration" in skill_content.lower()

    def test_handles_stalled_prs(self, skill_content):
        """Should handle stalled PRs."""
        assert "STALLED" in skill_content or "stalled" in skill_content.lower()

    def test_is_level_3(self, skill_content):
        """Should be level 3 workflow."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("level") == 3


class TestPRSkillsIntegration:
    """Integration tests for PR skills working together."""

    def test_composite_composes_atomics(self):
        """Composite skills should compose atomic skills."""
        review_content = read_skill("pr-review")
        assert "pr-read" in review_content
        assert "pr-diff-read" in review_content
        assert "pr-review-submit" in review_content

    def test_workflow_composes_composites(self):
        """Workflow should compose composite skills."""
        workflow_content = read_skill("pr-review-complete")
        assert "pr-review" in workflow_content

    def test_consistent_domain(self):
        """All PR skills should have github domain."""
        for skill_name in ALL_PR_SKILLS:
            content = read_skill(skill_name)
            metadata = extract_metadata(content)
            assert metadata.get("domain") == "github"

    def test_level_hierarchy(self):
        """Skills should follow level hierarchy."""
        for atomic in PR_ATOMIC_SKILLS:
            metadata = extract_metadata(read_skill(atomic))
            assert metadata.get("level") == 1

        for composite in PR_COMPOSITE_SKILLS:
            metadata = extract_metadata(read_skill(composite))
            assert metadata.get("level") == 2

        for workflow in PR_WORKFLOW_SKILLS:
            metadata = extract_metadata(read_skill(workflow))
            assert metadata.get("level") == 3


class TestPRSkillsCompleteness:
    """Tests for completeness of PR skill documentation."""

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_description(self, skill_name):
        """Each skill should have a description."""
        content = read_skill(skill_name)
        assert "## Description" in content

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_metadata(self, skill_name):
        """Each skill should have metadata."""
        content = read_skill(skill_name)
        assert "## Metadata" in content

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_input_schema(self, skill_name):
        """Each skill should have input schema."""
        content = read_skill(skill_name)
        assert "## Input Schema" in content or "inputSchema:" in content

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_output_schema(self, skill_name):
        """Each skill should have output schema."""
        content = read_skill(skill_name)
        assert "## Output Schema" in content or "outputSchema:" in content

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_examples(self, skill_name):
        """Each skill should have examples."""
        content = read_skill(skill_name)
        assert "## Examples" in content or "Example" in content


class TestPRSkillsGitHubIntegration:
    """Tests for GitHub integration coverage."""

    @pytest.mark.parametrize("skill_name", PR_ATOMIC_SKILLS)
    def test_documents_gh_cli(self, skill_name):
        """Atomic skills should document gh CLI usage."""
        content = read_skill(skill_name)
        assert "gh " in content, f"{skill_name} should document gh CLI"

    @pytest.mark.parametrize("skill_name", PR_ATOMIC_SKILLS)
    def test_documents_rest_api(self, skill_name):
        """Atomic skills should document REST API."""
        content = read_skill(skill_name)
        assert "api.github.com" in content or "REST API" in content, \
            f"{skill_name} should document REST API"

    def test_pr_read_documents_mcp(self):
        """pr-read should document MCP server usage."""
        content = read_skill("pr-read")
        assert "MCP" in content


class TestPRSkillsTags:
    """Tests for proper tagging."""

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_github_tag(self, skill_name):
        """All PR skills should have github tag."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        tags = metadata.get("tags", [])
        assert "github" in tags, f"{skill_name} should have github tag"

    @pytest.mark.parametrize("skill_name", ALL_PR_SKILLS)
    def test_has_pull_request_tag(self, skill_name):
        """All PR skills should have pull-request tag."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        tags = metadata.get("tags", [])
        assert "pull-request" in tags, f"{skill_name} should have pull-request tag"
