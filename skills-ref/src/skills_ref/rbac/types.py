"""
Core types for RBAC system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class PermissionAction(Enum):
    """Actions that can be performed on resources."""
    EXECUTE = "execute"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE = "manage"
    APPROVE = "approve"


class ResourceType(Enum):
    """Types of resources that can be protected."""
    SKILL = "skill"
    SECRET = "secret"
    WORKSPACE = "workspace"
    ROLE = "role"
    API_KEY = "api_key"
    AUDIT_LOG = "audit_log"


class RiskLevel(Enum):
    """Risk classification for skills."""
    READ_ONLY = "read_only"     # L1: Safe, no side effects
    WRITE = "write"             # L2: Creates/modifies data
    DESTRUCTIVE = "destructive"  # L3: Deletes data, hard to reverse
    CRITICAL = "critical"        # L4: Financial, legal, production impact

    @classmethod
    def from_operation(cls, operation: str) -> "RiskLevel":
        """Map skill operation to risk level."""
        mapping = {
            "READ": cls.READ_ONLY,
            "WRITE": cls.WRITE,
            "TRANSFORM": cls.READ_ONLY,
        }
        return mapping.get(operation.upper(), cls.WRITE)


class DataClassification(Enum):
    """Data sensitivity classification."""
    PUBLIC = "public"           # Can be shared freely
    INTERNAL = "internal"       # Internal use only
    CONFIDENTIAL = "confidential"  # Need-to-know basis
    RESTRICTED = "restricted"   # Highest sensitivity


@dataclass
class Permission:
    """
    A permission grants ability to perform an action on a resource.

    Format: action:resource_type:resource_id
    Examples:
        - execute:skill:*
        - execute:skill:research
        - read:secret:database_*
        - manage:role:*
    """
    action: PermissionAction
    resource_type: ResourceType
    resource_id: str = "*"  # * means all resources

    # Optional conditions
    conditions: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.action.value}:{self.resource_type.value}:{self.resource_id}"

    @classmethod
    def parse(cls, permission_str: str) -> "Permission":
        """Parse permission string like 'execute:skill:research'."""
        parts = permission_str.split(":", 2)
        if len(parts) < 2:
            raise ValueError(f"Invalid permission format: {permission_str}")

        action = PermissionAction(parts[0])
        resource_type = ResourceType(parts[1])
        resource_id = parts[2] if len(parts) > 2 else "*"

        return cls(action=action, resource_type=resource_type, resource_id=resource_id)

    def matches(self, action: PermissionAction, resource_type: ResourceType, resource_id: str) -> bool:
        """Check if this permission matches the requested access."""
        if self.action != action:
            return False
        if self.resource_type != resource_type:
            return False
        if self.resource_id == "*":
            return True
        if self.resource_id.endswith("*"):
            prefix = self.resource_id[:-1]
            return resource_id.startswith(prefix)
        return self.resource_id == resource_id


@dataclass
class Role:
    """
    A role groups permissions together.

    Roles can inherit from other roles to form a hierarchy.
    """
    id: str
    name: str
    description: str = ""

    # Direct permissions
    permissions: List[Permission] = field(default_factory=list)

    # Inherited roles (role hierarchy)
    inherited_roles: List[str] = field(default_factory=list)

    # Metadata
    is_system_role: bool = False  # Built-in vs custom
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def has_permission(self, permission: Permission) -> bool:
        """Check if role has a specific permission (direct only)."""
        for p in self.permissions:
            if p.matches(permission.action, permission.resource_type, permission.resource_id):
                return True
        return False


@dataclass
class SkillCapability:
    """
    Capability requirements for executing a skill.

    Defines what permissions, roles, and approvals are needed.
    """
    skill_name: str
    risk_level: RiskLevel
    data_classification: DataClassification = DataClassification.INTERNAL

    # Required permissions to execute
    required_permissions: List[str] = field(default_factory=list)

    # Alternative: required roles (any of these)
    required_roles: List[str] = field(default_factory=list)

    # Audit requirements
    audit_required: bool = True
    audit_inputs: bool = False  # Log inputs (careful with PII)
    audit_outputs: bool = False  # Log outputs

    # Approval requirements
    cosign_required: bool = False  # Require approval from another user
    cosign_roles: List[str] = field(default_factory=list)  # Roles that can approve

    # Execution constraints
    allowed_environments: List[str] = field(default_factory=lambda: ["*"])
    allowed_time_windows: List[Dict[str, str]] = field(default_factory=list)
    rate_limit: Optional[Dict[str, int]] = None  # e.g., {"per_hour": 100}

    @classmethod
    def from_skill_definition(cls, skill: Dict[str, Any]) -> "SkillCapability":
        """Create capability from skill definition."""
        operation = skill.get("operation", "READ")
        risk_level = RiskLevel.from_operation(operation)

        # Higher risk for destructive skills
        if skill.get("destructive", False):
            risk_level = RiskLevel.DESTRUCTIVE

        return cls(
            skill_name=skill.get("name", "unknown"),
            risk_level=risk_level,
            required_permissions=skill.get("required_permissions", []),
            required_roles=skill.get("required_roles", []),
            audit_required=skill.get("audit_required", True),
            cosign_required=skill.get("cosign_required", False),
        )


@dataclass
class RBACPolicy:
    """
    Complete RBAC policy for a role.

    Defines what a role can do, with fine-grained constraints.
    """
    role_id: str

    # Skill access
    allowed_skills: List[Dict[str, Any]] = field(default_factory=list)
    denied_skills: List[str] = field(default_factory=list)

    # Skill composition rules
    skill_composition_rules: Optional[Dict[str, Any]] = None

    # Time constraints
    time_window: Optional[Dict[str, str]] = None  # {"start": "09:00", "end": "17:00"}
    allowed_days: List[str] = field(default_factory=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

    # Network constraints
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)

    # Resource limits
    resource_limits: Optional[Dict[str, int]] = None

    def is_skill_allowed(self, skill_name: str) -> bool:
        """Check if a skill is allowed by this policy."""
        # Check denied list first
        if skill_name in self.denied_skills:
            return False

        # Check allowed list
        if not self.allowed_skills:
            return True  # No restrictions

        for allowed in self.allowed_skills:
            if isinstance(allowed, str):
                if allowed == "*" or allowed == skill_name:
                    return True
            elif isinstance(allowed, dict):
                if allowed.get("skill_name") == skill_name:
                    return True
                if allowed.get("skill_name") == "*":
                    return True

        return False


@dataclass
class AccessDecision:
    """Result of an access control decision."""
    allowed: bool
    reason: str
    evaluated_at: datetime = field(default_factory=datetime.utcnow)

    # Which policy/permission granted or denied access
    policy_id: Optional[str] = None
    permission_id: Optional[str] = None

    # For auditing
    user_id: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = None
    action: Optional[PermissionAction] = None

    @classmethod
    def allow(cls, reason: str, **kwargs) -> "AccessDecision":
        return cls(allowed=True, reason=reason, **kwargs)

    @classmethod
    def deny(cls, reason: str, **kwargs) -> "AccessDecision":
        return cls(allowed=False, reason=reason, **kwargs)

    def to_audit_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for audit logging."""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "evaluated_at": self.evaluated_at.isoformat(),
            "policy_id": self.policy_id,
            "permission_id": self.permission_id,
            "user_id": self.user_id,
            "resource_type": self.resource_type.value if self.resource_type else None,
            "resource_id": self.resource_id,
            "action": self.action.value if self.action else None,
        }


# Default roles
DEFAULT_ROLES = {
    "admin": Role(
        id="admin",
        name="Administrator",
        description="Full access to all resources",
        permissions=[
            Permission(PermissionAction.MANAGE, ResourceType.SKILL, "*"),
            Permission(PermissionAction.MANAGE, ResourceType.SECRET, "*"),
            Permission(PermissionAction.MANAGE, ResourceType.WORKSPACE, "*"),
            Permission(PermissionAction.MANAGE, ResourceType.ROLE, "*"),
            Permission(PermissionAction.MANAGE, ResourceType.API_KEY, "*"),
            Permission(PermissionAction.READ, ResourceType.AUDIT_LOG, "*"),
        ],
        is_system_role=True,
    ),
    "developer": Role(
        id="developer",
        name="Developer",
        description="Execute skills, manage own API keys",
        permissions=[
            Permission(PermissionAction.EXECUTE, ResourceType.SKILL, "*"),
            Permission(PermissionAction.READ, ResourceType.SECRET, "*"),
            Permission(PermissionAction.MANAGE, ResourceType.API_KEY, "own"),
        ],
        is_system_role=True,
    ),
    "viewer": Role(
        id="viewer",
        name="Viewer",
        description="Read-only access",
        permissions=[
            Permission(PermissionAction.EXECUTE, ResourceType.SKILL, "*"),
            Permission(PermissionAction.READ, ResourceType.SECRET, "*"),
        ],
        is_system_role=True,
    ),
    "service_account": Role(
        id="service_account",
        name="Service Account",
        description="Automated service access",
        permissions=[
            Permission(PermissionAction.EXECUTE, ResourceType.SKILL, "*"),
            Permission(PermissionAction.READ, ResourceType.SECRET, "*"),
        ],
        is_system_role=True,
    ),
}
