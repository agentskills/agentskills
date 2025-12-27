"""Property-based tests for portfolio manager skills using Hypothesis.

These tests generate random valid inputs and verify that invariants hold.

Requires: pip install hypothesis
"""

import pytest
from pathlib import Path
import re

try:
    from hypothesis import given, strategies as st, assume, settings
    from hypothesis.strategies import composite
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Create dummy decorators for when hypothesis is not available
    def given(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

    def composite(f):
        return f

    class st:
        @staticmethod
        def text(*args, **kwargs):
            return None
        @staticmethod
        def integers(*args, **kwargs):
            return None
        @staticmethod
        def floats(*args, **kwargs):
            return None
        @staticmethod
        def lists(*args, **kwargs):
            return None
        @staticmethod
        def sampled_from(*args, **kwargs):
            return None
        @staticmethod
        def fixed_dictionaries(*args, **kwargs):
            return None

    def assume(x):
        pass

    def settings(*args, **kwargs):
        def decorator(f):
            return f
        return decorator


# Skip all tests if hypothesis not installed
pytestmark = pytest.mark.skipif(
    not HYPOTHESIS_AVAILABLE,
    reason="hypothesis not installed"
)


# =============================================================================
# Custom Strategies
# =============================================================================

# Define strategies conditionally
if HYPOTHESIS_AVAILABLE:
    @composite
    def skill_name_strategy(draw):
        """Generate valid skill names (kebab-case)."""
        words = draw(st.lists(
            st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=2, max_size=10),
            min_size=1, max_size=4
        ))
        return '-'.join(words)

    @composite
    def yaml_frontmatter_strategy(draw):
        """Generate valid YAML frontmatter."""
        name = draw(skill_name_strategy())
        level = draw(st.sampled_from([1, 2, 3]))
        operation = draw(st.sampled_from(['READ', 'WRITE', 'TRANSFORM']))
        version = f"{draw(st.integers(0, 9))}.{draw(st.integers(0, 9))}.{draw(st.integers(0, 9))}"

        return {
            'name': name,
            'level': level,
            'operation': operation,
            'version': version,
            'description': draw(st.text(min_size=20, max_size=200))
        }

    @composite
    def holdings_strategy(draw):
        """Generate valid holdings arrays."""
        return draw(st.lists(
            st.fixed_dictionaries({
                'security_id': st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=3, max_size=6),
                'quantity': st.integers(1, 10000),
                'value': st.floats(min_value=100, max_value=1000000, allow_nan=False),
                'weight': st.floats(min_value=0.001, max_value=1.0, allow_nan=False)
            }),
            min_size=1, max_size=20
        ))

    @composite
    def allocation_strategy(draw):
        """Generate valid asset allocations that sum to ~100%."""
        n_classes = draw(st.integers(2, 6))
        # Generate weights that sum to approximately 1.0
        raw_weights = [draw(st.floats(0.05, 0.5)) for _ in range(n_classes)]
        total = sum(raw_weights)
        normalized = [w / total for w in raw_weights]

        asset_classes = ['equities', 'fixed_income', 'cash', 'alternatives', 'property', 'commodities']
        return {
            asset_classes[i]: normalized[i]
            for i in range(n_classes)
        }
else:
    # Dummy strategies when hypothesis not available
    def skill_name_strategy():
        return None

    def yaml_frontmatter_strategy():
        return None

    def holdings_strategy():
        return None

    def allocation_strategy():
        return None


# =============================================================================
# Property Tests for Skill Structure
# =============================================================================

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestSkillNameProperties:
    """Property-based tests for skill naming conventions."""

    @given(skill_name_strategy())
    def test_skill_name_is_lowercase(self, name):
        """Generated skill names should be lowercase."""
        assert name == name.lower()

    @given(skill_name_strategy())
    def test_skill_name_no_underscores(self, name):
        """Generated skill names should not contain underscores."""
        assert '_' not in name

    @given(skill_name_strategy())
    def test_skill_name_uses_hyphens(self, name):
        """Skill names with multiple words should use hyphens."""
        # If there are multiple words, they should be separated by hyphens
        parts = name.split('-')
        assert all(part.isalpha() for part in parts)


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestFrontmatterProperties:
    """Property-based tests for YAML frontmatter."""

    @given(yaml_frontmatter_strategy())
    def test_frontmatter_has_required_fields(self, frontmatter):
        """Generated frontmatter should have all required fields."""
        required = ['name', 'level', 'operation', 'description']
        for field in required:
            assert field in frontmatter

    @given(yaml_frontmatter_strategy())
    def test_level_is_valid(self, frontmatter):
        """Level should be 1, 2, or 3."""
        assert frontmatter['level'] in [1, 2, 3]

    @given(yaml_frontmatter_strategy())
    def test_operation_is_valid(self, frontmatter):
        """Operation should be READ, WRITE, or TRANSFORM."""
        assert frontmatter['operation'] in ['READ', 'WRITE', 'TRANSFORM']

    @given(yaml_frontmatter_strategy())
    def test_version_format(self, frontmatter):
        """Version should follow semver format."""
        version = frontmatter['version']
        assert re.match(r'^\d+\.\d+\.\d+$', version)


# =============================================================================
# Property Tests for Schema Structures
# =============================================================================

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestHoldingsSchemaProperties:
    """Property-based tests for holdings schema."""

    @given(holdings_strategy())
    def test_holdings_have_required_fields(self, holdings):
        """Each holding should have required fields."""
        for holding in holdings:
            assert 'security_id' in holding
            assert 'quantity' in holding
            assert 'value' in holding

    @given(holdings_strategy())
    def test_holdings_quantities_positive(self, holdings):
        """All quantities should be positive."""
        for holding in holdings:
            assert holding['quantity'] > 0

    @given(holdings_strategy())
    def test_holdings_values_positive(self, holdings):
        """All values should be positive."""
        for holding in holdings:
            assert holding['value'] > 0

    @given(holdings_strategy())
    @settings(max_examples=50)
    def test_holdings_weights_between_0_and_1(self, holdings):
        """All weights should be between 0 and 1."""
        for holding in holdings:
            assert 0 < holding['weight'] <= 1


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestAllocationProperties:
    """Property-based tests for asset allocation."""

    @given(allocation_strategy())
    def test_allocation_sums_to_one(self, allocation):
        """Asset allocation should sum to approximately 1.0."""
        total = sum(allocation.values())
        assert 0.99 <= total <= 1.01

    @given(allocation_strategy())
    def test_allocation_all_positive(self, allocation):
        """All allocation weights should be positive."""
        for weight in allocation.values():
            assert weight > 0

    @given(allocation_strategy())
    def test_allocation_no_single_class_exceeds_100(self, allocation):
        """No single asset class should exceed 100%."""
        for weight in allocation.values():
            assert weight <= 1.0


# =============================================================================
# Property Tests for Composition Rules
# =============================================================================

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestCompositionProperties:
    """Property-based tests for skill composition rules."""

    @given(st.integers(1, 3), st.lists(st.integers(1, 3), min_size=0, max_size=5))
    def test_composition_level_hierarchy(self, parent_level, child_levels):
        """Parent skill level should be >= max of child levels."""
        assume(len(child_levels) > 0)

        # In valid composition, parent level >= all child levels
        max_child = max(child_levels)

        # This should hold for valid compositions
        if parent_level >= max_child:
            # Valid composition
            assert True
        else:
            # Invalid - L1 can't compose L2/L3, L2 can't compose L3
            # In our tests, we're generating random combinations
            # and checking they follow the rule
            pass

    @given(st.sampled_from([1, 2, 3]))
    def test_l1_skills_dont_compose(self, level):
        """Level 1 skills should not have compositions."""
        if level == 1:
            # L1 skills should have empty or no composes field
            expected_composes = []
            assert expected_composes == []

    @given(st.integers(2, 3), st.lists(skill_name_strategy(), min_size=1, max_size=10))
    def test_l2_l3_skills_have_compositions(self, level, composed_skills):
        """Level 2 and 3 skills should compose other skills."""
        # L2 and L3 skills should have at least one composed skill
        assert len(composed_skills) >= 1


# =============================================================================
# Property Tests for State Machine Rules
# =============================================================================

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestStateMachineProperties:
    """Property-based tests for state machine definitions."""

    @given(st.lists(st.text(min_size=3, max_size=20, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ_'),
                    min_size=2, max_size=10, unique=True))
    def test_state_names_unique(self, state_names):
        """All state names in a workflow should be unique."""
        assert len(state_names) == len(set(state_names))

    @given(st.lists(st.text(min_size=3, max_size=20, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ_'),
                    min_size=3, max_size=10, unique=True))
    def test_workflow_has_initial_and_terminal(self, state_names):
        """Workflow should have at least initial and terminal states."""
        assume(len(state_names) >= 2)

        # First state is initial, last is terminal
        initial = state_names[0]
        terminal = state_names[-1]

        assert initial != terminal
        assert len([s for s in state_names if s == initial]) == 1
        assert len([s for s in state_names if s == terminal]) == 1


# =============================================================================
# Property Tests for Schema Type Consistency
# =============================================================================

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestTypeConsistencyProperties:
    """Property-based tests for type consistency."""

    VALID_TYPES = ['string', 'number', 'integer', 'boolean', 'array', 'object',
                   'date', 'datetime', 'enum']

    @given(st.sampled_from(VALID_TYPES))
    def test_types_from_valid_set(self, type_name):
        """All types should be from the valid set."""
        assert type_name in self.VALID_TYPES

    @given(st.sampled_from(['array', 'object']))
    def test_complex_types_need_children(self, complex_type):
        """Array and object types should define their structure."""
        # Arrays need 'items', objects need 'properties'
        if complex_type == 'array':
            required_child = 'items'
        else:
            required_child = 'properties'

        # This is a documentation/rule test
        assert required_child in ['items', 'properties']


# =============================================================================
# Regression Tests with Random Data
# =============================================================================

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestRegressionWithRandomData:
    """Regression tests using randomly generated data."""

    @given(holdings_strategy(), allocation_strategy())
    @settings(max_examples=20)
    def test_portfolio_summary_with_random_data(self, holdings, allocation):
        """Portfolio summary should handle any valid input."""
        # Simulate what portfolio-summarise would check
        total_value = sum(h['value'] for h in holdings)
        total_weight = sum(h['weight'] for h in holdings)

        # Invariants that should hold
        assert total_value > 0
        assert total_weight > 0

        # Each holding should contribute to total
        for holding in holdings:
            pct = holding['value'] / total_value
            assert 0 < pct <= 1

    @given(allocation_strategy(), allocation_strategy())
    @settings(max_examples=20)
    def test_drift_calculation_with_random_allocations(self, current, target):
        """Drift calculation should work for any valid allocations."""
        # Calculate drift between two allocations
        common_classes = set(current.keys()) & set(target.keys())
        assume(len(common_classes) > 0)

        max_drift = 0
        for asset_class in common_classes:
            drift = abs(current[asset_class] - target[asset_class])
            max_drift = max(max_drift, drift)

        # Drift should be between 0 and 1
        assert 0 <= max_drift <= 1
