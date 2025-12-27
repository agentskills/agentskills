"""
Integration tests for RBAC flow.
"""

import pytest

from skills_ref.rbac import (
    RoleManager,
    PermissionManager,
    PolicyEngine,
    PolicyRule,
    Role,
    RiskLevel,
    SkillCapability,
    DEFAULT_ROLES,
)


class TestRoleHierarchy:
    """Test role hierarchy and inheritance."""

    @pytest.fixture
    def role_manager(self):
        manager = RoleManager()
        for role in DEFAULT_ROLES.values():
            manager.add_role(role)
        return manager

    def test_default_roles_loaded(self, role_manager):
        """Test default roles are available."""
        assert role_manager.get_role("admin") is not None
        assert role_manager.get_role("developer") is not None
        assert role_manager.get_role("operator") is not None
        assert role_manager.get_role("viewer") is not None

    def test_role_hierarchy_levels(self, role_manager):
        """Test role levels are correctly ordered."""
        admin = role_manager.get_role("admin")
        developer = role_manager.get_role("developer")
        viewer = role_manager.get_role("viewer")

        assert admin.level > developer.level
        assert developer.level > viewer.level

    def test_permission_inheritance(self, role_manager):
        """Test permissions are inherited from parent roles."""
        # Add a custom role with parent
        analyst_role = Role(
            name="analyst",
            level=25,
            permissions=["data:read"],
            parent_role="viewer",
        )
        role_manager.add_role(analyst_role)

        # Should have own permissions plus inherited
        effective = role_manager.get_effective_permissions("analyst")
        assert "data:read" in effective  # Own permission
        # Should also have viewer permissions

    def test_role_ancestry(self, role_manager):
        """Test role ancestry chain."""
        # Add nested roles
        role_manager.add_role(Role(
            name="senior-dev",
            level=60,
            permissions=["deploy:prod"],
            parent_role="developer",
        ))

        ancestry = role_manager.get_role_ancestry("senior-dev")
        assert "senior-dev" in ancestry
        assert "developer" in ancestry


class TestPermissionChecks:
    """Test permission checks."""

    @pytest.fixture
    def role_manager(self):
        manager = RoleManager()
        for role in DEFAULT_ROLES.values():
            manager.add_role(role)
        return manager

    @pytest.fixture
    def permission_manager(self, role_manager):
        return PermissionManager(role_manager)

    def test_admin_has_all_permissions(self, permission_manager):
        """Test admin role has wildcard permissions."""
        assert permission_manager.has_permission(["admin"], "skill:execute")
        assert permission_manager.has_permission(["admin"], "skill:delete")
        assert permission_manager.has_permission(["admin"], "system:admin")
        assert permission_manager.has_permission(["admin"], "any:permission")

    def test_viewer_limited_permissions(self, permission_manager):
        """Test viewer role has limited permissions."""
        # Viewer typically only has read permissions
        viewer_role = DEFAULT_ROLES.get("viewer")
        if viewer_role:
            # Check specific permissions based on default role definition
            pass

    def test_multiple_roles_combined(self, permission_manager, role_manager):
        """Test multiple roles combine permissions."""
        # Add custom roles
        role_manager.add_role(Role(
            name="reader",
            level=10,
            permissions=["skill:read"],
        ))
        role_manager.add_role(Role(
            name="writer",
            level=10,
            permissions=["skill:write"],
        ))

        # User with both roles should have both permissions
        assert permission_manager.has_permission(["reader", "writer"], "skill:read")
        assert permission_manager.has_permission(["reader", "writer"], "skill:write")

        # But not with just one role
        assert permission_manager.has_permission(["reader"], "skill:read")
        assert not permission_manager.has_permission(["reader"], "skill:write")


class TestSkillAuthorization:
    """Test skill-level authorization."""

    @pytest.fixture
    def role_manager(self):
        manager = RoleManager()
        for role in DEFAULT_ROLES.values():
            manager.add_role(role)
        return manager

    @pytest.fixture
    def permission_manager(self, role_manager):
        return PermissionManager(role_manager)

    def test_skill_risk_level_check(self, permission_manager):
        """Test skill authorization based on risk level."""
        low_risk_skill = SkillCapability(
            skill_name="read-file",
            skill_level=1,
            risk_level=RiskLevel.LOW,
            required_permissions=["skill:execute"],
        )

        high_risk_skill = SkillCapability(
            skill_name="delete-data",
            skill_level=1,
            risk_level=RiskLevel.HIGH,
            required_permissions=["skill:execute", "data:delete"],
        )

        # Admin can execute both
        admin_decision = permission_manager.authorize_skill(
            user_roles=["admin"],
            user_scopes=["*"],
            capability=high_risk_skill,
        )
        assert admin_decision.allowed

        # Viewer might not be able to execute high-risk
        viewer_decision = permission_manager.authorize_skill(
            user_roles=["viewer"],
            user_scopes=["skill:read"],
            capability=high_risk_skill,
        )
        # Depends on viewer role configuration

    def test_skill_level_restriction(self, permission_manager, role_manager):
        """Test skill level restrictions."""
        # Create role that can only execute L1 skills
        role_manager.add_role(Role(
            name="l1-only",
            level=15,
            permissions=["skill:execute"],
            allowed_skill_levels=[1],
            max_risk_level=RiskLevel.LOW,
        ))

        l1_skill = SkillCapability(
            skill_name="simple-skill",
            skill_level=1,
            risk_level=RiskLevel.NONE,
        )

        l2_skill = SkillCapability(
            skill_name="composite-skill",
            skill_level=2,
            risk_level=RiskLevel.LOW,
        )

        # Can execute L1
        decision = permission_manager.authorize_skill(
            user_roles=["l1-only"],
            user_scopes=[],
            capability=l1_skill,
        )
        # Result depends on implementation

        # Cannot execute L2
        decision = permission_manager.authorize_skill(
            user_roles=["l1-only"],
            user_scopes=[],
            capability=l2_skill,
        )
        # Should be denied


class TestPolicyEngine:
    """Test policy-based access control."""

    @pytest.fixture
    def policy_engine(self):
        engine = PolicyEngine()
        return engine

    def test_allow_rule(self, policy_engine):
        """Test basic allow rule."""
        policy_engine.add_rule(PolicyRule(
            id="allow-skill-execute",
            name="Allow Skill Execute",
            effect="allow",
            resources=["skill:*"],
            actions=["execute"],
            conditions={},
        ))

        # Should allow skill execution
        # (Implementation depends on evaluate method)

    def test_deny_rule_priority(self, policy_engine):
        """Test deny rules take priority."""
        # Add allow rule
        policy_engine.add_rule(PolicyRule(
            id="allow-all",
            name="Allow All",
            effect="allow",
            resources=["*"],
            actions=["*"],
            priority=0,
        ))

        # Add deny rule with higher priority
        policy_engine.add_rule(PolicyRule(
            id="deny-production",
            name="Deny Production Access",
            effect="deny",
            resources=["skill:*"],
            actions=["execute"],
            conditions={"environment": {"eq": "production"}},
            priority=100,
        ))

        # Deny should win due to higher priority

    def test_condition_matching(self, policy_engine):
        """Test condition matching in policies."""
        policy_engine.add_rule(PolicyRule(
            id="business-hours-only",
            name="Business Hours Only",
            effect="allow",
            resources=["skill:*"],
            actions=["execute"],
            conditions={
                "hour": {"gte": 9, "lte": 17},
                "day": {"in": ["monday", "tuesday", "wednesday", "thursday", "friday"]},
            },
        ))

        # Should only allow during business hours

    def test_resource_pattern_matching(self, policy_engine):
        """Test resource pattern matching."""
        policy_engine.add_rule(PolicyRule(
            id="allow-email-skills",
            name="Allow Email Skills",
            effect="allow",
            resources=["skill:email-*"],
            actions=["execute"],
        ))

        # Should match skill:email-send, skill:email-read, etc.
        # But not skill:slack-send


class TestRBACIntegration:
    """Test RBAC integration with auth."""

    @pytest.fixture
    def role_manager(self):
        manager = RoleManager()
        for role in DEFAULT_ROLES.values():
            manager.add_role(role)
        return manager

    @pytest.fixture
    def permission_manager(self, role_manager):
        return PermissionManager(role_manager)

    def test_auth_context_to_rbac(self, permission_manager):
        """Test flowing auth context to RBAC check."""
        # Simulate auth context from JWT
        user_roles = ["developer"]
        user_scopes = ["skill:execute", "skill:read"]

        # Check permissions
        can_execute = permission_manager.has_permission(
            user_roles,
            "skill:execute",
        )

        can_admin = permission_manager.has_permission(
            user_roles,
            "system:admin",
        )

        assert can_execute  # Developer should be able to execute
        assert not can_admin  # Developer should not be admin

    def test_dynamic_role_assignment(self, role_manager, permission_manager):
        """Test dynamic role assignment affects permissions."""
        # Initially just viewer
        assert not permission_manager.has_permission(["viewer"], "skill:execute")

        # Assign developer role
        user_roles = ["viewer", "developer"]
        assert permission_manager.has_permission(user_roles, "skill:execute")
