"""Tests for Level 2 (Composite) portfolio manager skills."""

import pytest
from pathlib import Path
import re

try:
    from skills_ref.validator import validate
    from skills_ref.parser import parse_skill
    SKILLS_REF_AVAILABLE = True
except ImportError:
    SKILLS_REF_AVAILABLE = False


# =============================================================================
# Skill Existence Tests
# =============================================================================

class TestCompositeSkillsExist:
    """Verify all expected composite skills exist."""

    def test_all_composite_skills_present(self, composite_dir, composite_skills):
        """All expected composite skills should have directories."""
        for skill_name in composite_skills:
            skill_path = composite_dir / skill_name
            assert skill_path.exists(), f"Composite skill directory missing: {skill_name}"
            assert skill_path.is_dir(), f"Not a directory: {skill_name}"

    def test_all_composite_skills_have_skill_md(self, composite_dir, composite_skills):
        """All composite skills should have SKILL.md files."""
        for skill_name in composite_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"SKILL.md missing for: {skill_name}"


# =============================================================================
# Skill Validation Tests
# =============================================================================

@pytest.mark.skipif(not SKILLS_REF_AVAILABLE, reason="skills_ref not available")
class TestCompositeSkillsValidate:
    """Validate composite skills pass the validator."""

    @pytest.mark.parametrize("skill_name", [
        "portfolio-summarise",
        "risk-profile-estimate",
        "scenario-analyse",
        "benchmark-compare",
        "suitability-assess",
        "goal-allocation-generate",
        "trade-list-generate",
        "drift-monitor",
        "whatif-simulate",
        "health-report-generate",
        "ips-define",
        "tax-impact-estimate",
    ])
    def test_skill_validates(self, composite_dir, skill_name):
        """Each composite skill should pass validation."""
        skill_path = composite_dir / skill_name
        if skill_path.exists():
            errors = validate(skill_path)
            assert errors == [], f"Validation errors for {skill_name}: {errors}"


# =============================================================================
# Level 2 Property Tests
# =============================================================================

class TestCompositeSkillLevelProperties:
    """Verify Level 2 skills have correct properties."""

    def test_all_composite_are_level_2(self, composite_dir, composite_skills):
        """All composite skills should be level 2."""
        for skill_name in composite_skills:
            skill_path = composite_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                assert "level: 2" in content, f"{skill_name} should be level 2"

    def test_composite_skills_have_operation(self, composite_dir, composite_skills):
        """All composite skills should declare an operation."""
        for skill_name in composite_skills:
            skill_path = composite_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                has_operation = (
                    "operation: READ" in content or
                    "operation: WRITE" in content or
                    "operation: TRANSFORM" in content
                )
                assert has_operation, f"{skill_name} should have operation declared"

    def test_composite_skills_have_composes(self, composite_dir, composite_skills):
        """Composite skills should compose other skills."""
        for skill_name in composite_skills:
            skill_path = composite_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                assert "composes:" in content, f"{skill_name} should compose other skills"


# =============================================================================
# Portfolio Understanding Skills Tests
# =============================================================================

class TestPortfolioSummarise:
    """Tests for portfolio-summarise skill."""

    def test_skill_exists(self, composite_dir):
        """portfolio-summarise skill exists."""
        assert (composite_dir / "portfolio-summarise" / "SKILL.md").exists()

    def test_composes_atomics(self, composite_dir):
        """portfolio-summarise composes atomic skills."""
        content = (composite_dir / "portfolio-summarise" / "SKILL.md").read_text()
        assert "holdings-ingest" in content
        assert "market-data-fetch" in content

    def test_provides_breakdowns(self, composite_dir):
        """portfolio-summarise provides asset class/sector/geography breakdowns."""
        content = (composite_dir / "portfolio-summarise" / "SKILL.md").read_text()
        assert "asset_class" in content or "asset class" in content.lower()
        assert "sector" in content.lower()
        assert "geography" in content.lower() or "geographic" in content.lower()


class TestRiskProfileEstimate:
    """Tests for risk-profile-estimate skill."""

    def test_skill_exists(self, composite_dir):
        """risk-profile-estimate skill exists."""
        assert (composite_dir / "risk-profile-estimate" / "SKILL.md").exists()

    def test_provides_risk_metrics(self, composite_dir):
        """risk-profile-estimate provides comprehensive risk metrics."""
        content = (composite_dir / "risk-profile-estimate" / "SKILL.md").read_text()
        assert "volatility" in content.lower()
        assert "drawdown" in content.lower()
        assert "concentration" in content.lower()

    def test_provides_risk_rating(self, composite_dir):
        """risk-profile-estimate provides a risk rating."""
        content = (composite_dir / "risk-profile-estimate" / "SKILL.md").read_text()
        assert "risk_rating" in content or "risk rating" in content.lower()


class TestScenarioAnalyse:
    """Tests for scenario-analyse skill."""

    def test_skill_exists(self, composite_dir):
        """scenario-analyse skill exists."""
        assert (composite_dir / "scenario-analyse" / "SKILL.md").exists()

    def test_supports_market_scenarios(self, composite_dir):
        """scenario-analyse supports various market scenarios."""
        content = (composite_dir / "scenario-analyse" / "SKILL.md").read_text()
        # Should support rate and recession scenarios
        assert "rate" in content.lower()
        assert "recession" in content.lower()

    def test_provides_impact_analysis(self, composite_dir):
        """scenario-analyse provides portfolio impact analysis."""
        content = (composite_dir / "scenario-analyse" / "SKILL.md").read_text()
        assert "impact" in content.lower()


class TestBenchmarkCompare:
    """Tests for benchmark-compare skill."""

    def test_skill_exists(self, composite_dir):
        """benchmark-compare skill exists."""
        assert (composite_dir / "benchmark-compare" / "SKILL.md").exists()

    def test_provides_performance_attribution(self, composite_dir):
        """benchmark-compare provides performance attribution."""
        content = (composite_dir / "benchmark-compare" / "SKILL.md").read_text()
        assert "attribution" in content.lower()


# =============================================================================
# Goal Alignment Skills Tests
# =============================================================================

class TestSuitabilityAssess:
    """Tests for suitability-assess skill."""

    def test_skill_exists(self, composite_dir):
        """suitability-assess skill exists."""
        assert (composite_dir / "suitability-assess" / "SKILL.md").exists()

    def test_checks_alignment(self, composite_dir):
        """suitability-assess checks goal/risk alignment."""
        content = (composite_dir / "suitability-assess" / "SKILL.md").read_text()
        assert "alignment" in content.lower() or "suitable" in content.lower()
        assert "risk" in content.lower()
        assert "goal" in content.lower() or "horizon" in content.lower()


class TestGoalAllocationGenerate:
    """Tests for goal-allocation-generate skill."""

    def test_skill_exists(self, composite_dir):
        """goal-allocation-generate skill exists."""
        assert (composite_dir / "goal-allocation-generate" / "SKILL.md").exists()

    def test_generates_allocations(self, composite_dir):
        """goal-allocation-generate generates target allocations."""
        content = (composite_dir / "goal-allocation-generate" / "SKILL.md").read_text()
        assert "allocation" in content.lower()
        assert "goal" in content.lower()


# =============================================================================
# Portfolio Construction Skills Tests
# =============================================================================

class TestTradeListGenerate:
    """Tests for trade-list-generate skill."""

    def test_skill_exists(self, composite_dir):
        """trade-list-generate skill exists."""
        assert (composite_dir / "trade-list-generate" / "SKILL.md").exists()

    def test_generates_trades(self, composite_dir):
        """trade-list-generate generates buy/sell trades."""
        content = (composite_dir / "trade-list-generate" / "SKILL.md").read_text()
        assert "buy" in content.lower()
        assert "sell" in content.lower()

    def test_considers_tax(self, composite_dir):
        """trade-list-generate considers tax implications."""
        content = (composite_dir / "trade-list-generate" / "SKILL.md").read_text()
        assert "tax" in content.lower()

    def test_considers_cost(self, composite_dir):
        """trade-list-generate considers transaction costs."""
        content = (composite_dir / "trade-list-generate" / "SKILL.md").read_text()
        assert "cost" in content.lower() or "commission" in content.lower()


# =============================================================================
# Monitoring Skills Tests
# =============================================================================

class TestDriftMonitor:
    """Tests for drift-monitor skill."""

    def test_skill_exists(self, composite_dir):
        """drift-monitor skill exists."""
        assert (composite_dir / "drift-monitor" / "SKILL.md").exists()

    def test_monitors_drift(self, composite_dir):
        """drift-monitor checks for weight drift."""
        content = (composite_dir / "drift-monitor" / "SKILL.md").read_text()
        assert "drift" in content.lower()
        assert "threshold" in content.lower()

    def test_monitors_concentration(self, composite_dir):
        """drift-monitor checks concentration limits."""
        content = (composite_dir / "drift-monitor" / "SKILL.md").read_text()
        assert "concentration" in content.lower()


class TestWhatifSimulate:
    """Tests for whatif-simulate skill."""

    def test_skill_exists(self, composite_dir):
        """whatif-simulate skill exists."""
        assert (composite_dir / "whatif-simulate" / "SKILL.md").exists()

    def test_simulates_changes(self, composite_dir):
        """whatif-simulate simulates portfolio changes."""
        content = (composite_dir / "whatif-simulate" / "SKILL.md").read_text()
        assert "add" in content.lower() or "remove" in content.lower()
        assert "impact" in content.lower()


# =============================================================================
# Tax & Planning Skills Tests
# =============================================================================

class TestTaxImpactEstimate:
    """Tests for tax-impact-estimate skill."""

    def test_skill_exists(self, composite_dir):
        """tax-impact-estimate skill exists."""
        assert (composite_dir / "tax-impact-estimate" / "SKILL.md").exists()

    def test_estimates_cgt(self, composite_dir):
        """tax-impact-estimate estimates capital gains tax."""
        content = (composite_dir / "tax-impact-estimate" / "SKILL.md").read_text()
        assert "capital" in content.lower() or "cgt" in content.lower()
        assert "gain" in content.lower()

    def test_supports_lot_selection(self, composite_dir):
        """tax-impact-estimate supports lot selection strategies."""
        content = (composite_dir / "tax-impact-estimate" / "SKILL.md").read_text()
        assert "lot" in content.lower()
        assert "fifo" in content.lower() or "hifo" in content.lower()


# =============================================================================
# Policy Skills Tests
# =============================================================================

class TestIpsDefine:
    """Tests for ips-define skill."""

    def test_skill_exists(self, composite_dir):
        """ips-define skill exists."""
        assert (composite_dir / "ips-define" / "SKILL.md").exists()

    def test_defines_ips(self, composite_dir):
        """ips-define creates Investment Policy Statement."""
        content = (composite_dir / "ips-define" / "SKILL.md").read_text()
        assert "investment policy" in content.lower() or "IPS" in content

    def test_requires_approval(self, composite_dir):
        """ips-define requires approval for changes."""
        content = (composite_dir / "ips-define" / "SKILL.md").read_text()
        assert "requires_approval" in content.lower() or "approval" in content.lower()


# =============================================================================
# Reporting Skills Tests
# =============================================================================

class TestHealthReportGenerate:
    """Tests for health-report-generate skill."""

    def test_skill_exists(self, composite_dir):
        """health-report-generate skill exists."""
        assert (composite_dir / "health-report-generate" / "SKILL.md").exists()

    def test_generates_shareable_report(self, composite_dir):
        """health-report-generate creates shareable summary."""
        content = (composite_dir / "health-report-generate" / "SKILL.md").read_text()
        assert "report" in content.lower()
        assert "summary" in content.lower() or "share" in content.lower()

    def test_includes_key_sections(self, composite_dir):
        """health-report-generate includes key sections."""
        content = (composite_dir / "health-report-generate" / "SKILL.md").read_text()
        assert "performance" in content.lower()
        assert "risk" in content.lower()
        assert "goal" in content.lower() or "action" in content.lower()


# =============================================================================
# Composition Chain Tests
# =============================================================================

class TestCompositionChains:
    """Test that composite skills correctly chain atomic skills."""

    def test_portfolio_summarise_chain(self, composite_dir, atomic_dir):
        """portfolio-summarise should compose available atomics."""
        content = (composite_dir / "portfolio-summarise" / "SKILL.md").read_text()
        # Extract composes list
        assert "holdings-ingest" in content
        assert "market-data-fetch" in content

    def test_trade_list_chain(self, composite_dir):
        """trade-list-generate should reference constraint validation."""
        content = (composite_dir / "trade-list-generate" / "SKILL.md").read_text()
        # Should reference constraint checking
        assert "constraint" in content.lower()

    def test_drift_monitor_chain(self, composite_dir):
        """drift-monitor should compose alert-send for notifications."""
        content = (composite_dir / "drift-monitor" / "SKILL.md").read_text()
        assert "alert" in content.lower()
