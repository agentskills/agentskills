# Role-Based Access Control (RBAC)

The AgentSkills RBAC module provides fine-grained permission management for skill execution.

## Overview

The RBAC system provides:
- **Roles** with hierarchical permissions
- **Skill capabilities** based on risk levels
- **Policy-based access control** with conditions
- **Permission inheritance** through role hierarchy

## Quick Start

```python
from skills_ref.rbac import (
    RoleManager,
    PermissionManager,
    PolicyEngine,
    DEFAULT_ROLES,
)

# Create managers
role_manager = RoleManager()
permission_manager = PermissionManager(role_manager)

# Load default roles
for role in DEFAULT_ROLES.values():
    role_manager.add_role(role)

# Check if user can execute a skill
can_execute = permission_manager.can_execute_skill(
    user_roles=["developer"],
    skill_name="research-skill",
    risk_level=RiskLevel.LOW,
)
```

## Default Roles

The system includes predefined roles:

| Role | Level | Description |
|------|-------|-------------|
| `admin` | 100 | Full system access |
| `developer` | 50 | Create and execute skills |
| `operator` | 30 | Execute and monitor skills |
| `viewer` | 10 | Read-only access |

```python
from skills_ref.rbac import DEFAULT_ROLES

admin_role = DEFAULT_ROLES["admin"]
print(admin_role.permissions)  # ["*"] - all permissions
print(admin_role.max_risk_level)  # RiskLevel.CRITICAL
```

## Role Management

### Creating Custom Roles

```python
from skills_ref.rbac import Role, RiskLevel

# Create a custom role
analyst_role = Role(
    name="analyst",
    level=25,
    permissions=["skill:read", "skill:execute"],
    max_risk_level=RiskLevel.LOW,
    allowed_skill_levels=[1, 2],  # Atomic and Composite only
    parent_role="viewer",  # Inherits from viewer
)

role_manager.add_role(analyst_role)
```

### Role Hierarchy

```python
# Get effective permissions including inherited
effective_perms = role_manager.get_effective_permissions("analyst")

# Check inheritance chain
ancestors = role_manager.get_role_ancestry("analyst")
# ["analyst", "viewer"]
```

## Permission Checks

### Basic Permission Check

```python
# Check a single permission
has_perm = permission_manager.has_permission(
    user_roles=["developer"],
    permission="skill:execute",
)

# Check multiple permissions (all required)
has_all = permission_manager.has_all_permissions(
    user_roles=["developer"],
    permissions=["skill:execute", "skill:read"],
)

# Check multiple permissions (any required)
has_any = permission_manager.has_any_permission(
    user_roles=["viewer"],
    permissions=["skill:execute", "skill:read"],
)
```

### Skill Authorization

```python
from skills_ref.rbac import SkillCapability, RiskLevel

capability = SkillCapability(
    skill_name="email-send",
    skill_level=2,
    risk_level=RiskLevel.MEDIUM,
    required_permissions=["email:send"],
    required_scopes=["email.write"],
)

decision = permission_manager.authorize_skill(
    user_roles=["developer"],
    user_scopes=["email.write"],
    capability=capability,
)

if decision.allowed:
    print("Access granted")
else:
    print(f"Denied: {decision.reason}")
```

## Policy Engine

The policy engine enables rule-based access control with conditions.

### Creating Policies

```python
from skills_ref.rbac import PolicyEngine, PolicyRule

# Create policy engine
engine = PolicyEngine()

# Add a rule: allow email skills only during business hours
engine.add_rule(PolicyRule(
    id="business-hours-email",
    name="Business Hours Email Access",
    effect="allow",
    resources=["skill:email-*"],
    actions=["execute"],
    conditions={
        "time_of_day": {"gte": "09:00", "lte": "17:00"},
        "day_of_week": {"in": ["monday", "tuesday", "wednesday", "thursday", "friday"]},
    },
))

# Add a deny rule: block high-risk skills for viewers
engine.add_rule(PolicyRule(
    id="block-high-risk-viewers",
    name="Block High Risk for Viewers",
    effect="deny",
    resources=["skill:*"],
    actions=["execute"],
    conditions={
        "role": {"eq": "viewer"},
        "risk_level": {"in": ["high", "critical"]},
    },
    priority=100,  # Higher priority = evaluated first
))
```

### Evaluating Policies

```python
from skills_ref.rbac import EvaluationContext

context = EvaluationContext(
    user_id="user-123",
    roles=["developer"],
    resource="skill:email-send",
    action="execute",
    environment={
        "time_of_day": "14:30",
        "day_of_week": "wednesday",
        "risk_level": "medium",
    },
)

decision = engine.evaluate(context)

if decision.allowed:
    print(f"Access granted by rule: {decision.matching_rule}")
else:
    print(f"Access denied: {decision.reason}")
```

### Policy Conditions

Supported condition operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `{"role": {"eq": "admin"}}` |
| `neq` | Not equals | `{"status": {"neq": "disabled"}}` |
| `in` | In list | `{"day": {"in": ["sat", "sun"]}}` |
| `nin` | Not in list | `{"env": {"nin": ["production"]}}` |
| `gt`, `gte` | Greater than (or equal) | `{"level": {"gte": 50}}` |
| `lt`, `lte` | Less than (or equal) | `{"risk": {"lt": 3}}` |
| `contains` | String contains | `{"skill": {"contains": "email"}}` |
| `matches` | Regex match | `{"name": {"matches": "^test-.*"}}` |

## Risk Levels

Skills have associated risk levels:

| Level | Value | Examples |
|-------|-------|----------|
| `NONE` | 0 | Read-only operations |
| `LOW` | 1 | Local file operations |
| `MEDIUM` | 2 | External API calls |
| `HIGH` | 3 | Financial transactions |
| `CRITICAL` | 4 | System modifications |

```python
from skills_ref.rbac import RiskLevel

# Check if role can handle risk level
max_allowed = role_manager.get_max_risk_level(["operator"])
if RiskLevel.HIGH <= max_allowed:
    print("Can execute high-risk skills")
```

## Configuration

Configure RBAC via environment variables:

```bash
# Enable/disable RBAC
AGENTSKILLS_RBAC__ENABLED=true

# Default role for new users
AGENTSKILLS_RBAC__DEFAULT_ROLE=viewer

# Admin users (bypass all checks)
AGENTSKILLS_RBAC__ADMIN_USERS=["admin-user-id"]

# Permission cache TTL
AGENTSKILLS_RBAC__CACHE_TTL_SECONDS=300

# Inherit permissions from parent roles
AGENTSKILLS_RBAC__INHERIT_PERMISSIONS=true

# Custom roles file
AGENTSKILLS_RBAC__CUSTOM_ROLES_FILE=/path/to/roles.yaml
```

## Custom Roles File (YAML)

```yaml
roles:
  data-analyst:
    level: 35
    parent: viewer
    permissions:
      - skill:read
      - skill:execute
      - data:read
    max_risk_level: medium
    allowed_skill_levels: [1, 2]

  automation-operator:
    level: 40
    parent: operator
    permissions:
      - skill:execute
      - workflow:trigger
      - schedule:manage
    max_risk_level: high
    allowed_skills:
      - "automation-*"
      - "workflow-*"
```

## Best Practices

1. **Principle of Least Privilege**: Start with minimal permissions, add as needed
2. **Use Role Hierarchy**: Inherit from base roles to reduce duplication
3. **Separate by Risk**: Create roles aligned with risk tolerance
4. **Audit Access**: Log all authorization decisions
5. **Regular Review**: Periodically review role assignments
6. **Policy Testing**: Test policies before deploying to production

## Integration Example

```python
from skills_ref.auth import AuthManager, require_auth
from skills_ref.rbac import PermissionManager, RoleManager

role_manager = RoleManager()
permission_manager = PermissionManager(role_manager)

@require_auth(auth_manager, required_scopes=["skill:execute"])
async def execute_skill(context, skill_name: str, inputs: dict):
    # Check RBAC permissions
    decision = permission_manager.authorize_skill(
        user_roles=context.roles,
        user_scopes=context.scopes,
        capability=skill.capability,
    )

    if not decision.allowed:
        raise PermissionError(decision.reason)

    # Execute skill
    return await skill.execute(inputs)
```
