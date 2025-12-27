"""
RBAC Managers for permission and role management.
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any, Callable, Dict, List, Optional, Set

from .types import (
    AccessDecision,
    DataClassification,
    DEFAULT_ROLES,
    Permission,
    PermissionAction,
    RBACPolicy,
    ResourceType,
    RiskLevel,
    Role,
    SkillCapability,
)


class RoleManager:
    """
    Manages role definitions and hierarchy.

    Features:
    - CRUD for roles
    - Role hierarchy with inheritance
    - Default system roles
    """

    def __init__(self, roles: Optional[Dict[str, Role]] = None):
        # Start with default roles
        self._roles: Dict[str, Role] = dict(DEFAULT_ROLES)
        if roles:
            self._roles.update(roles)

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get a role by ID."""
        return self._roles.get(role_id)

    def get_all_roles(self) -> List[Role]:
        """Get all defined roles."""
        return list(self._roles.values())

    def create_role(
        self,
        role_id: str,
        name: str,
        description: str = "",
        permissions: Optional[List[Permission]] = None,
        inherited_roles: Optional[List[str]] = None,
    ) -> Role:
        """Create a new role."""
        if role_id in self._roles:
            raise ValueError(f"Role {role_id} already exists")

        role = Role(
            id=role_id,
            name=name,
            description=description,
            permissions=permissions or [],
            inherited_roles=inherited_roles or [],
        )
        self._roles[role_id] = role
        return role

    def update_role(self, role_id: str, **updates) -> Optional[Role]:
        """Update a role."""
        role = self._roles.get(role_id)
        if role is None:
            return None

        if role.is_system_role:
            raise ValueError(f"Cannot modify system role: {role_id}")

        for key, value in updates.items():
            if hasattr(role, key):
                setattr(role, key, value)

        role.updated_at = datetime.utcnow()
        return role

    def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        role = self._roles.get(role_id)
        if role is None:
            return False

        if role.is_system_role:
            raise ValueError(f"Cannot delete system role: {role_id}")

        del self._roles[role_id]
        return True

    def get_effective_permissions(self, role_id: str, visited: Optional[Set[str]] = None) -> List[Permission]:
        """
        Get all permissions for a role, including inherited ones.

        Follows role hierarchy recursively.
        """
        visited = visited or set()
        if role_id in visited:
            return []  # Prevent circular inheritance
        visited.add(role_id)

        role = self._roles.get(role_id)
        if role is None:
            return []

        # Start with direct permissions
        permissions = list(role.permissions)

        # Add inherited permissions
        for inherited_id in role.inherited_roles:
            inherited = self.get_effective_permissions(inherited_id, visited)
            permissions.extend(inherited)

        return permissions

    def is_role_hierarchy_valid(self, role_id: str) -> bool:
        """Check if role hierarchy has no circular dependencies."""
        def check_circular(rid: str, visited: Set[str]) -> bool:
            if rid in visited:
                return False  # Circular
            visited.add(rid)

            role = self._roles.get(rid)
            if role is None:
                return True

            for inherited in role.inherited_roles:
                if not check_circular(inherited, visited.copy()):
                    return False

            return True

        return check_circular(role_id, set())


class PermissionManager:
    """
    Evaluates permissions and access decisions.

    Features:
    - Permission checking with hierarchy
    - Skill execution authorization
    - Skill composition validation
    - Time-based and resource-based constraints
    """

    def __init__(
        self,
        role_manager: RoleManager,
        policies: Optional[Dict[str, RBACPolicy]] = None,
        on_access_decision: Optional[Callable[[AccessDecision], None]] = None,
    ):
        self.role_manager = role_manager
        self._policies: Dict[str, RBACPolicy] = policies or {}
        self._on_access_decision = on_access_decision

        # User -> roles mapping
        self._user_roles: Dict[str, List[str]] = {}

    def assign_role(self, user_id: str, role_id: str) -> None:
        """Assign a role to a user."""
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
        if role_id not in self._user_roles[user_id]:
            self._user_roles[user_id].append(role_id)

    def revoke_role(self, user_id: str, role_id: str) -> bool:
        """Revoke a role from a user."""
        if user_id not in self._user_roles:
            return False
        if role_id in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_id)
            return True
        return False

    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles assigned to a user."""
        return self._user_roles.get(user_id, [])

    def has_permission(
        self,
        user_id: str,
        action: PermissionAction,
        resource_type: ResourceType,
        resource_id: str = "*",
    ) -> AccessDecision:
        """
        Check if user has permission for an action.

        Evaluates all user roles and their inherited permissions.
        """
        roles = self.get_user_roles(user_id)
        if not roles:
            return AccessDecision.deny(
                "No roles assigned to user",
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
            )

        for role_id in roles:
            permissions = self.role_manager.get_effective_permissions(role_id)
            for perm in permissions:
                if perm.matches(action, resource_type, resource_id):
                    decision = AccessDecision.allow(
                        f"Granted by role {role_id}",
                        user_id=user_id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        permission_id=str(perm),
                    )
                    self._emit_decision(decision)
                    return decision

        decision = AccessDecision.deny(
            "No matching permission found",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        self._emit_decision(decision)
        return decision

    def can_execute_skill(
        self,
        user_id: str,
        skill_capability: SkillCapability,
        context: Optional[Dict[str, Any]] = None,
    ) -> AccessDecision:
        """
        Check if user can execute a skill.

        Evaluates:
        - Required permissions
        - Required roles
        - Risk level constraints
        - Time windows
        - Environment constraints
        """
        context = context or {}

        # Check basic execute permission
        perm_check = self.has_permission(
            user_id,
            PermissionAction.EXECUTE,
            ResourceType.SKILL,
            skill_capability.skill_name,
        )
        if not perm_check.allowed:
            return perm_check

        # Check required roles
        if skill_capability.required_roles:
            user_roles = set(self.get_user_roles(user_id))
            required = set(skill_capability.required_roles)
            if not user_roles & required:
                return AccessDecision.deny(
                    f"Missing required role: {skill_capability.required_roles}",
                    user_id=user_id,
                    resource_type=ResourceType.SKILL,
                    resource_id=skill_capability.skill_name,
                )

        # Check risk level restrictions
        user_roles = self.get_user_roles(user_id)
        if skill_capability.risk_level in [RiskLevel.DESTRUCTIVE, RiskLevel.CRITICAL]:
            # Only admin can execute destructive/critical skills
            if "admin" not in user_roles:
                return AccessDecision.deny(
                    f"Risk level {skill_capability.risk_level.value} requires admin role",
                    user_id=user_id,
                    resource_type=ResourceType.SKILL,
                    resource_id=skill_capability.skill_name,
                )

        # Check cosign requirement
        if skill_capability.cosign_required:
            approver = context.get("approved_by")
            if not approver or approver == user_id:
                return AccessDecision.deny(
                    "Skill requires approval from another user",
                    user_id=user_id,
                    resource_type=ResourceType.SKILL,
                    resource_id=skill_capability.skill_name,
                )

        # Check time window (if configured)
        if skill_capability.allowed_time_windows:
            if not self._is_within_time_window(skill_capability.allowed_time_windows):
                return AccessDecision.deny(
                    "Skill execution not allowed at this time",
                    user_id=user_id,
                    resource_type=ResourceType.SKILL,
                    resource_id=skill_capability.skill_name,
                )

        # Check environment (if configured)
        environment = context.get("environment", "*")
        if skill_capability.allowed_environments != ["*"]:
            if environment not in skill_capability.allowed_environments:
                return AccessDecision.deny(
                    f"Skill not allowed in environment: {environment}",
                    user_id=user_id,
                    resource_type=ResourceType.SKILL,
                    resource_id=skill_capability.skill_name,
                )

        return AccessDecision.allow(
            "All checks passed",
            user_id=user_id,
            resource_type=ResourceType.SKILL,
            resource_id=skill_capability.skill_name,
        )

    def validate_skill_composition(
        self,
        user_id: str,
        skills: List[SkillCapability],
    ) -> AccessDecision:
        """
        Validate that a user can execute a skill chain.

        Checks:
        - Permission for each skill
        - No circular dependencies
        - Compatible risk levels in chain
        - Separation of duties
        """
        if not skills:
            return AccessDecision.allow("Empty skill chain")

        # Check each skill individually
        for skill in skills:
            decision = self.can_execute_skill(user_id, skill)
            if not decision.allowed:
                return decision

        # Check separation of duties
        sod_violations = self._check_separation_of_duties(user_id, skills)
        if sod_violations:
            return AccessDecision.deny(
                f"Separation of duties violation: {sod_violations}",
                user_id=user_id,
            )

        # Check risk level escalation
        max_risk = max(s.risk_level.value for s in skills)
        user_roles = self.get_user_roles(user_id)
        if max_risk in ["destructive", "critical"] and "admin" not in user_roles:
            return AccessDecision.deny(
                f"Skill chain contains {max_risk} operations requiring admin",
                user_id=user_id,
            )

        return AccessDecision.allow(
            f"Skill composition validated ({len(skills)} skills)",
            user_id=user_id,
        )

    def set_policy(self, role_id: str, policy: RBACPolicy) -> None:
        """Set policy for a role."""
        self._policies[role_id] = policy

    def get_policy(self, role_id: str) -> Optional[RBACPolicy]:
        """Get policy for a role."""
        return self._policies.get(role_id)

    def _check_separation_of_duties(
        self,
        user_id: str,
        skills: List[SkillCapability],
    ) -> List[str]:
        """
        Check for separation of duties violations.

        Returns list of violations (empty if none).
        """
        violations = []

        # Example SoD rules (in practice, these would be configurable)
        conflicting_pairs = [
            ("approve_payment", "process_payment"),
            ("create_user", "grant_admin"),
            ("delete_backup", "restore_backup"),
        ]

        skill_names = {s.skill_name for s in skills}
        for skill_a, skill_b in conflicting_pairs:
            if skill_a in skill_names and skill_b in skill_names:
                violations.append(f"Cannot execute both {skill_a} and {skill_b}")

        return violations

    def _is_within_time_window(self, windows: List[Dict[str, str]]) -> bool:
        """Check if current time is within allowed windows."""
        now = datetime.now().time()

        for window in windows:
            start_str = window.get("start", "00:00")
            end_str = window.get("end", "23:59")

            start = time.fromisoformat(start_str)
            end = time.fromisoformat(end_str)

            if start <= now <= end:
                return True

        return False

    def _emit_decision(self, decision: AccessDecision) -> None:
        """Emit access decision for logging."""
        if self._on_access_decision:
            self._on_access_decision(decision)


class RBACMiddleware:
    """
    Middleware for enforcing RBAC on skill execution.
    """

    def __init__(self, permission_manager: PermissionManager):
        self.permission_manager = permission_manager

    def authorize(
        self,
        user_id: str,
        skill_capability: SkillCapability,
        context: Optional[Dict[str, Any]] = None,
    ) -> AccessDecision:
        """Authorize skill execution."""
        return self.permission_manager.can_execute_skill(
            user_id, skill_capability, context
        )

    def authorize_chain(
        self,
        user_id: str,
        skills: List[SkillCapability],
    ) -> AccessDecision:
        """Authorize skill chain execution."""
        return self.permission_manager.validate_skill_composition(user_id, skills)
