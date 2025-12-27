"""
Role-Based Access Control (RBAC) for AgentSkills Enterprise.

This module provides:
- Role and permission definitions
- Skill capability classification
- Permission evaluation engine
- Skill composition security validation
"""

from .types import (
    Role,
    Permission,
    PermissionAction,
    ResourceType,
    RiskLevel,
    SkillCapability,
    RBACPolicy,
    AccessDecision,
)
from .manager import PermissionManager, RoleManager
from .policy import PolicyEngine, PolicyRule

__all__ = [
    # Types
    "Role",
    "Permission",
    "PermissionAction",
    "ResourceType",
    "RiskLevel",
    "SkillCapability",
    "RBACPolicy",
    "AccessDecision",
    # Managers
    "PermissionManager",
    "RoleManager",
    # Policy
    "PolicyEngine",
    "PolicyRule",
]
