"""Tests for Level 1 (Atomic) portfolio manager skills."""

import pytest
from pathlib import Path

try:
    from skills_ref.validator import validate
    from skills_ref.parser import parse_skill
    SKILLS_REF_AVAILABLE = True
except ImportError:
    SKILLS_REF_AVAILABLE = False


# =============================================================================
# Skill Existence Tests
# =============================================================================

class TestAtomicSkillsExist:
    """Verify all expected atomic skills exist."""

    def test_all_atomic_skills_present(self, atomic_dir, atomic_skills):
        """All expected atomic skills should have directories."""
        for skill_name in atomic_skills:
            skill_path = atomic_dir / skill_name
            assert skill_path.exists(), f"Atomic skill directory missing: {skill_name}"
            assert skill_path.is_dir(), f"Not a directory: {skill_name}"

    def test_all_atomic_skills_have_skill_md(self, atomic_dir, atomic_skills):
        """All atomic skills should have SKILL.md files."""
        for skill_name in atomic_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"SKILL.md missing for: {skill_name}"


# =============================================================================
# Skill Validation Tests
# =============================================================================

@pytest.mark.skipif(not SKILLS_REF_AVAILABLE, reason="skills_ref not available")
class TestAtomicSkillsValidate:
    """Validate atomic skills pass the validator."""

    @pytest.mark.parametrize("skill_name", [
        "holdings-ingest",
        "market-data-fetch",
        "constraint-validate",
        "risk-metrics-calculate",
        "trade-order-execute",
        "alert-send",
    ])
    def test_skill_validates(self, atomic_dir, skill_name):
        """Each atomic skill should pass validation."""
        skill_path = atomic_dir / skill_name
        errors = validate(skill_path)
        assert errors == [], f"Validation errors for {skill_name}: {errors}"


# =============================================================================
# Skill Property Tests
# =============================================================================

class TestHoldingsIngest:
    """Tests specific to holdings-ingest skill."""

    def test_skill_exists(self, atomic_dir):
        """holdings-ingest skill exists."""
        assert (atomic_dir / "holdings-ingest" / "SKILL.md").exists()

    def test_skill_content(self, atomic_dir):
        """holdings-ingest has required content."""
        content = (atomic_dir / "holdings-ingest" / "SKILL.md").read_text()
        assert "name: holdings-ingest" in content
        assert "level: 1" in content
        assert "operation: READ" in content
        # Should handle multiple data sources
        assert "csv" in content.lower()
        assert "api" in content.lower()
        # Should output normalized holdings
        assert "security_id" in content
        assert "quantity" in content


class TestMarketDataFetch:
    """Tests specific to market-data-fetch skill."""

    def test_skill_exists(self, atomic_dir):
        """market-data-fetch skill exists."""
        assert (atomic_dir / "market-data-fetch" / "SKILL.md").exists()

    def test_skill_content(self, atomic_dir):
        """market-data-fetch has required content."""
        content = (atomic_dir / "market-data-fetch" / "SKILL.md").read_text()
        assert "name: market-data-fetch" in content
        assert "level: 1" in content
        assert "operation: READ" in content
        # Should support multiple data types
        assert "price" in content.lower()
        assert "history" in content.lower()
        assert "fundamentals" in content.lower()


class TestConstraintValidate:
    """Tests specific to constraint-validate skill."""

    def test_skill_exists(self, atomic_dir):
        """constraint-validate skill exists."""
        assert (atomic_dir / "constraint-validate" / "SKILL.md").exists()

    def test_skill_content(self, atomic_dir):
        """constraint-validate has required content."""
        content = (atomic_dir / "constraint-validate" / "SKILL.md").read_text()
        assert "name: constraint-validate" in content
        assert "level: 1" in content
        assert "operation: READ" in content
        # Should check various constraints
        assert "position" in content.lower()
        assert "sector" in content.lower()
        assert "concentration" in content.lower()


class TestRiskMetricsCalculate:
    """Tests specific to risk-metrics-calculate skill."""

    def test_skill_exists(self, atomic_dir):
        """risk-metrics-calculate skill exists."""
        assert (atomic_dir / "risk-metrics-calculate" / "SKILL.md").exists()

    def test_skill_content(self, atomic_dir):
        """risk-metrics-calculate has required content."""
        content = (atomic_dir / "risk-metrics-calculate" / "SKILL.md").read_text()
        assert "name: risk-metrics-calculate" in content
        assert "level: 1" in content
        assert "operation: READ" in content
        # Should calculate standard risk metrics
        assert "volatility" in content.lower()
        assert "var" in content.lower() or "VaR" in content
        assert "drawdown" in content.lower()
        assert "sharpe" in content.lower()


class TestTradeOrderExecute:
    """Tests specific to trade-order-execute skill."""

    def test_skill_exists(self, atomic_dir):
        """trade-order-execute skill exists."""
        assert (atomic_dir / "trade-order-execute" / "SKILL.md").exists()

    def test_skill_content(self, atomic_dir):
        """trade-order-execute has required content."""
        content = (atomic_dir / "trade-order-execute" / "SKILL.md").read_text()
        assert "name: trade-order-execute" in content
        assert "level: 1" in content
        assert "operation: WRITE" in content
        # Should require approval for execution
        assert "requires_approval" in content.lower() or "approval" in content.lower()
        # Should support order types
        assert "market" in content.lower()
        assert "limit" in content.lower()


class TestAlertSend:
    """Tests specific to alert-send skill."""

    def test_skill_exists(self, atomic_dir):
        """alert-send skill exists."""
        assert (atomic_dir / "alert-send" / "SKILL.md").exists()

    def test_skill_content(self, atomic_dir):
        """alert-send has required content."""
        content = (atomic_dir / "alert-send" / "SKILL.md").read_text()
        assert "name: alert-send" in content
        assert "level: 1" in content
        assert "operation: WRITE" in content
        # Should support multiple channels
        assert "email" in content.lower()
        assert "slack" in content.lower() or "push" in content.lower()


# =============================================================================
# Level 1 Property Tests
# =============================================================================

class TestAtomicSkillLevelProperties:
    """Verify Level 1 skills have correct properties."""

    def test_all_atomic_are_level_1(self, atomic_dir, atomic_skills):
        """All atomic skills should be level 1."""
        for skill_name in atomic_skills:
            content = (atomic_dir / skill_name / "SKILL.md").read_text()
            assert "level: 1" in content, f"{skill_name} should be level 1"

    def test_atomic_skills_have_operation(self, atomic_dir, atomic_skills):
        """All atomic skills should declare an operation."""
        for skill_name in atomic_skills:
            content = (atomic_dir / skill_name / "SKILL.md").read_text()
            has_operation = (
                "operation: READ" in content or
                "operation: WRITE" in content or
                "operation: TRANSFORM" in content
            )
            assert has_operation, f"{skill_name} should have operation declared"

    def test_atomic_skills_have_no_composes(self, atomic_dir, atomic_skills):
        """Atomic skills should not compose other skills."""
        for skill_name in atomic_skills:
            content = (atomic_dir / skill_name / "SKILL.md").read_text()
            # composes should not be in the YAML frontmatter
            # Allow "composes" in documentation but not as a field
            lines = content.split("---")[1] if "---" in content else ""
            assert "composes:" not in lines or "composes: []" in lines, \
                f"{skill_name} is L1 and should not compose other skills"


# =============================================================================
# Input/Output Schema Tests
# =============================================================================

class TestAtomicSkillSchemas:
    """Verify atomic skills have well-defined schemas."""

    def test_holdings_ingest_has_output_schema(self, atomic_dir):
        """holdings-ingest should define output schema."""
        content = (atomic_dir / "holdings-ingest" / "SKILL.md").read_text()
        assert "output" in content.lower()
        assert "holdings" in content.lower()

    def test_market_data_fetch_has_output_schema(self, atomic_dir):
        """market-data-fetch should define output schema."""
        content = (atomic_dir / "market-data-fetch" / "SKILL.md").read_text()
        assert "output" in content.lower()
        assert "quotes" in content.lower() or "price" in content.lower()

    def test_risk_metrics_has_output_schema(self, atomic_dir):
        """risk-metrics-calculate should define output schema."""
        content = (atomic_dir / "risk-metrics-calculate" / "SKILL.md").read_text()
        assert "output" in content.lower()
        assert "volatility" in content.lower()

    def test_trade_execute_has_input_schema(self, atomic_dir):
        """trade-order-execute should define input schema."""
        content = (atomic_dir / "trade-order-execute" / "SKILL.md").read_text()
        assert "input" in content.lower()
        assert "order" in content.lower()
