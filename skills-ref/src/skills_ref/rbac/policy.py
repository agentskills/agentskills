"""
Policy Engine for complex RBAC rules.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .types import (
    AccessDecision,
    Permission,
    PermissionAction,
    RBACPolicy,
    ResourceType,
    RiskLevel,
    Role,
    SkillCapability,
)


@dataclass
class PolicyRule:
    """
    A single policy rule.

    Rules are evaluated in order; first match wins.
    """
    id: str
    name: str
    description: str = ""

    # Matching criteria
    roles: List[str] = field(default_factory=list)  # Match any of these roles
    users: List[str] = field(default_factory=list)  # Match any of these users
    skills: List[str] = field(default_factory=list)  # Match any of these skills (supports wildcards)
    actions: List[PermissionAction] = field(default_factory=list)

    # Conditions (all must be true)
    conditions: Dict[str, Any] = field(default_factory=dict)

    # Effect
    effect: str = "allow"  # "allow" or "deny"

    # Priority (lower = higher priority)
    priority: int = 100

    def matches(
        self,
        user_id: str,
        user_roles: List[str],
        skill_name: str,
        action: PermissionAction,
        context: Dict[str, Any],
    ) -> bool:
        """Check if this rule matches the request."""
        # Check user
        if self.users and user_id not in self.users:
            if not self._matches_pattern(user_id, self.users):
                return False

        # Check roles
        if self.roles:
            if not any(r in user_roles for r in self.roles):
                return False

        # Check skills
        if self.skills:
            if not self._matches_pattern(skill_name, self.skills):
                return False

        # Check actions
        if self.actions:
            if action not in self.actions:
                return False

        # Check conditions
        if not self._evaluate_conditions(context):
            return False

        return True

    def _matches_pattern(self, value: str, patterns: List[str]) -> bool:
        """Check if value matches any pattern (supports * wildcards)."""
        for pattern in patterns:
            if pattern == "*":
                return True
            if "*" in pattern:
                regex = pattern.replace("*", ".*")
                if re.match(f"^{regex}$", value):
                    return True
            elif pattern == value:
                return True
        return False

    def _evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate all conditions against context."""
        for condition_key, expected in self.conditions.items():
            actual = context.get(condition_key)

            if isinstance(expected, dict):
                # Complex condition
                op = expected.get("operator", "eq")
                val = expected.get("value")

                if op == "eq" and actual != val:
                    return False
                elif op == "ne" and actual == val:
                    return False
                elif op == "in" and actual not in val:
                    return False
                elif op == "not_in" and actual in val:
                    return False
                elif op == "gt" and not (actual and actual > val):
                    return False
                elif op == "lt" and not (actual and actual < val):
                    return False
                elif op == "contains" and val not in (actual or ""):
                    return False
                elif op == "matches" and not re.match(val, str(actual or "")):
                    return False
            else:
                # Simple equality
                if actual != expected:
                    return False

        return True


class PolicyEngine:
    """
    Evaluates RBAC policies for access decisions.

    Features:
    - Rule-based policy evaluation
    - Priority ordering
    - Condition evaluation
    - Policy caching
    - Policy loading from JSON/YAML
    """

    def __init__(
        self,
        rules: Optional[List[PolicyRule]] = None,
        default_effect: str = "deny",
    ):
        self._rules: List[PolicyRule] = sorted(
            rules or [],
            key=lambda r: r.priority
        )
        self._default_effect = default_effect
        self._cache: Dict[str, AccessDecision] = {}
        self._cache_ttl: int = 60  # seconds

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a rule and re-sort by priority."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority)
        self._cache.clear()

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        for i, rule in enumerate(self._rules):
            if rule.id == rule_id:
                del self._rules[i]
                self._cache.clear()
                return True
        return False

    def evaluate(
        self,
        user_id: str,
        user_roles: List[str],
        skill_name: str,
        action: PermissionAction,
        context: Optional[Dict[str, Any]] = None,
    ) -> AccessDecision:
        """
        Evaluate policies for an access request.

        Returns the first matching rule's decision,
        or default deny if no rules match.
        """
        context = context or {}

        # Check cache
        cache_key = self._cache_key(user_id, skill_name, action)
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        # Evaluate rules in priority order
        for rule in self._rules:
            if rule.matches(user_id, user_roles, skill_name, action, context):
                if rule.effect == "allow":
                    decision = AccessDecision.allow(
                        f"Allowed by policy rule: {rule.name}",
                        policy_id=rule.id,
                        user_id=user_id,
                        resource_type=ResourceType.SKILL,
                        resource_id=skill_name,
                        action=action,
                    )
                else:
                    decision = AccessDecision.deny(
                        f"Denied by policy rule: {rule.name}",
                        policy_id=rule.id,
                        user_id=user_id,
                        resource_type=ResourceType.SKILL,
                        resource_id=skill_name,
                        action=action,
                    )

                self._cache[cache_key] = decision
                return decision

        # No matching rule - use default
        decision = AccessDecision.deny(
            "No matching policy rule (default deny)",
            user_id=user_id,
            resource_type=ResourceType.SKILL,
            resource_id=skill_name,
            action=action,
        ) if self._default_effect == "deny" else AccessDecision.allow(
            "No matching policy rule (default allow)",
            user_id=user_id,
            resource_type=ResourceType.SKILL,
            resource_id=skill_name,
            action=action,
        )

        self._cache[cache_key] = decision
        return decision

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Load policies from dictionary."""
        rules = data.get("rules", [])
        for rule_data in rules:
            # Convert action strings to enums
            actions = [
                PermissionAction(a) if isinstance(a, str) else a
                for a in rule_data.get("actions", [])
            ]

            rule = PolicyRule(
                id=rule_data.get("id", f"rule_{len(self._rules)}"),
                name=rule_data.get("name", "Unnamed Rule"),
                description=rule_data.get("description", ""),
                roles=rule_data.get("roles", []),
                users=rule_data.get("users", []),
                skills=rule_data.get("skills", []),
                actions=actions,
                conditions=rule_data.get("conditions", {}),
                effect=rule_data.get("effect", "allow"),
                priority=rule_data.get("priority", 100),
            )
            self.add_rule(rule)

    def load_from_json(self, json_str: str) -> None:
        """Load policies from JSON string."""
        data = json.loads(json_str)
        self.load_from_dict(data)

    def export_to_dict(self) -> Dict[str, Any]:
        """Export policies to dictionary."""
        return {
            "rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "roles": rule.roles,
                    "users": rule.users,
                    "skills": rule.skills,
                    "actions": [a.value for a in rule.actions],
                    "conditions": rule.conditions,
                    "effect": rule.effect,
                    "priority": rule.priority,
                }
                for rule in self._rules
            ],
            "default_effect": self._default_effect,
        }

    def clear_cache(self) -> None:
        """Clear the decision cache."""
        self._cache.clear()

    def _cache_key(
        self,
        user_id: str,
        skill_name: str,
        action: PermissionAction,
    ) -> str:
        """Generate cache key for decision."""
        return f"{user_id}:{skill_name}:{action.value}"


# Example policy configuration
EXAMPLE_POLICY = {
    "rules": [
        {
            "id": "admin_full_access",
            "name": "Admin Full Access",
            "description": "Administrators have full access to all skills",
            "roles": ["admin"],
            "skills": ["*"],
            "actions": ["execute", "read", "write", "delete", "manage"],
            "effect": "allow",
            "priority": 10,
        },
        {
            "id": "developer_read_write",
            "name": "Developer Read/Write",
            "description": "Developers can execute non-destructive skills",
            "roles": ["developer"],
            "skills": ["*"],
            "actions": ["execute", "read", "write"],
            "conditions": {
                "risk_level": {"operator": "not_in", "value": ["destructive", "critical"]}
            },
            "effect": "allow",
            "priority": 20,
        },
        {
            "id": "viewer_read_only",
            "name": "Viewer Read Only",
            "description": "Viewers can only execute read-only skills",
            "roles": ["viewer"],
            "skills": ["*"],
            "actions": ["execute", "read"],
            "conditions": {
                "risk_level": {"operator": "eq", "value": "read_only"}
            },
            "effect": "allow",
            "priority": 30,
        },
        {
            "id": "deny_production_delete",
            "name": "Deny Production Delete",
            "description": "Block delete operations in production",
            "roles": ["*"],
            "skills": ["*"],
            "actions": ["delete"],
            "conditions": {
                "environment": {"operator": "eq", "value": "production"}
            },
            "effect": "deny",
            "priority": 5,  # High priority
        },
    ],
    "default_effect": "deny",
}
