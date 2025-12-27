# Execution Environments

The AgentSkills execution module provides environment detection, capability management, and execution context handling.

## Overview

The execution system provides:
- **Environment detection**: Automatically detect Local, Docker, CI, Codespaces, Cloud
- **Capability checking**: Verify environment supports required features
- **Execution context**: Manage timeouts, retries, resource limits
- **Middleware integration**: Wrap skill execution with environment handling

## Quick Start

```python
from skills_ref.execution import (
    EnvironmentDetector,
    EnvironmentManager,
    ExecutionContextBuilder,
)

# Detect current environment
detector = EnvironmentDetector()
env = detector.detect()

print(f"Environment: {env.type}")
print(f"Capabilities: {env.capabilities}")

# Create execution context
context = (
    ExecutionContextBuilder()
    .with_timeout(30000)
    .with_retries(3)
    .build()
)
```

## Environment Types

| Type | Detection | Use Case |
|------|-----------|----------|
| `LOCAL` | No container indicators | Development |
| `DOCKER` | `/.dockerenv` exists | Containerised workloads |
| `CODESPACES` | `CODESPACES` env var | GitHub Codespaces |
| `CI` | `CI` or `GITHUB_ACTIONS` env var | CI/CD pipelines |
| `CLOUD` | Cloud provider metadata | Production |

```python
from skills_ref.execution import EnvironmentType

# Check environment type
if env.type == EnvironmentType.DOCKER:
    print("Running in container")
elif env.type == EnvironmentType.CI:
    print("Running in CI pipeline")
```

## Environment Detection

```python
from skills_ref.execution import EnvironmentDetector

detector = EnvironmentDetector()

# Detect environment
env = detector.detect()

# Access properties
print(env.type)           # EnvironmentType.LOCAL
print(env.name)           # "development-macbook"
print(env.capabilities)   # {GPU, NETWORK, FILESYSTEM, ...}

# Check specific capabilities
if env.has_capability(EnvironmentCapability.GPU):
    print("GPU available")

if env.has_capability(EnvironmentCapability.NETWORK):
    print("Network access available")
```

## Environment Capabilities

| Capability | Description |
|------------|-------------|
| `GPU` | GPU/CUDA available |
| `NETWORK` | External network access |
| `FILESYSTEM` | File system read/write |
| `SECRETS` | Secrets manager access |
| `DATABASE` | Database connectivity |
| `HIGH_MEMORY` | >8GB RAM available |
| `HIGH_CPU` | >4 CPU cores available |

```python
from skills_ref.execution import EnvironmentCapability

# Check multiple capabilities
required = {
    EnvironmentCapability.NETWORK,
    EnvironmentCapability.SECRETS,
}

if required.issubset(env.capabilities):
    print("All required capabilities available")
else:
    missing = required - env.capabilities
    print(f"Missing: {missing}")
```

## Skill Requirements

Define what a skill needs from its environment:

```python
from skills_ref.execution import SkillRequirements, EnvironmentCapability

requirements = SkillRequirements(
    min_memory_mb=512,
    min_cpu_cores=2,
    required_capabilities={
        EnvironmentCapability.NETWORK,
        EnvironmentCapability.SECRETS,
    },
    allowed_environments=[
        EnvironmentType.DOCKER,
        EnvironmentType.CLOUD,
    ],
)

# Check if environment satisfies requirements
if env.satisfies(requirements):
    print("Environment is suitable")
else:
    print("Environment doesn't meet requirements")
```

## Execution Context

The execution context carries runtime configuration:

```python
from skills_ref.execution import ExecutionContextBuilder

# Build context with fluent API
context = (
    ExecutionContextBuilder()
    .with_timeout(30000)          # 30 second timeout
    .with_retries(3)              # 3 retry attempts
    .with_backoff(2.0)            # Exponential backoff base
    .with_trace_id("trace-123")   # Distributed tracing
    .with_user_id("user-456")     # User context
    .with_metadata({"key": "value"})
    .build()
)

print(context.timeout_ms)     # 30000
print(context.max_retries)    # 3
print(context.trace_id)       # "trace-123"
```

## Environment Manager

Manages environment lifecycle and skill execution:

```python
from skills_ref.execution import EnvironmentManager

manager = EnvironmentManager()

# Register environment
manager.register_environment(env)

# Check if skill can run
can_run = manager.can_execute(
    skill_requirements=requirements,
    environment=env,
)

# Execute with context
result = await manager.execute(
    skill=my_skill,
    inputs={"query": "test"},
    context=context,
)
```

## Execution Middleware

Wrap skill execution with environment handling:

```python
from skills_ref.execution import ExecutionMiddleware

middleware = ExecutionMiddleware(
    manager=manager,
    default_timeout_ms=30000,
    default_retries=3,
)

# Execute skill through middleware
result = await middleware.execute(
    skill=my_skill,
    inputs=inputs,
    context=context,
)

# Middleware handles:
# - Environment validation
# - Timeout enforcement
# - Retry logic
# - Error handling
# - Context propagation
```

## Execution Constraints

Set limits on skill execution:

```python
from skills_ref.execution import ExecutionConstraints

constraints = ExecutionConstraints(
    max_duration_ms=60000,    # 1 minute max
    max_memory_mb=1024,       # 1GB memory limit
    max_retries=5,            # Maximum retries
    allowed_hosts=["api.example.com"],  # Network allowlist
    blocked_hosts=["evil.com"],         # Network blocklist
    sandbox=True,             # Run in sandbox
)

context = (
    ExecutionContextBuilder()
    .with_constraints(constraints)
    .build()
)
```

## Resource Limits

```python
from skills_ref.execution import ResourceLimits

limits = ResourceLimits(
    memory_mb=512,
    cpu_percent=50,        # 50% of available CPU
    disk_mb=100,           # 100MB disk space
    network_bandwidth_kbps=1000,
)

# Apply to execution
context = (
    ExecutionContextBuilder()
    .with_resource_limits(limits)
    .build()
)
```

## Configuration

Configure via environment variables:

```bash
# Auto-detection
AGENTSKILLS_EXECUTION__AUTO_DETECT_ENVIRONMENT=true

# Timeouts
AGENTSKILLS_EXECUTION__DEFAULT_TIMEOUT_MS=30000
AGENTSKILLS_EXECUTION__MAX_TIMEOUT_MS=300000

# Retries
AGENTSKILLS_EXECUTION__MAX_RETRIES=3
AGENTSKILLS_EXECUTION__RETRY_BACKOFF_BASE=2.0

# Sandboxing
AGENTSKILLS_EXECUTION__SANDBOX_ENABLED=true

# Allowed environments
AGENTSKILLS_EXECUTION__ALLOWED_ENVIRONMENTS=["local", "docker", "cloud"]
```

## Integration Example

```python
from skills_ref.execution import (
    EnvironmentDetector,
    EnvironmentManager,
    ExecutionContextBuilder,
    ExecutionMiddleware,
)
from skills_ref.auth import require_auth

# Setup
detector = EnvironmentDetector()
env = detector.detect()
manager = EnvironmentManager()
manager.register_environment(env)
middleware = ExecutionMiddleware(manager)

@require_auth(auth_manager)
async def execute_skill(auth_context, skill_name: str, inputs: dict):
    # Build execution context
    context = (
        ExecutionContextBuilder()
        .with_timeout(30000)
        .with_retries(3)
        .with_user_id(auth_context.user_id)
        .with_trace_id(auth_context.trace_id)
        .build()
    )

    # Execute through middleware
    result = await middleware.execute(
        skill=get_skill(skill_name),
        inputs=inputs,
        context=context,
    )

    return result
```

## Error Handling

```python
from skills_ref.execution import (
    EnvironmentError,
    TimeoutError,
    ResourceLimitError,
    CapabilityError,
)

try:
    result = await middleware.execute(skill, inputs, context)
except TimeoutError as e:
    print(f"Skill timed out after {e.duration_ms}ms")
except ResourceLimitError as e:
    print(f"Resource limit exceeded: {e.resource} = {e.value}")
except CapabilityError as e:
    print(f"Missing capability: {e.capability}")
except EnvironmentError as e:
    print(f"Environment error: {e}")
```

## Best Practices

1. **Detect early**: Detect environment at startup, not per-request
2. **Define requirements**: Explicitly state skill requirements
3. **Use constraints**: Set reasonable limits to prevent runaway execution
4. **Handle failures**: Implement proper error handling for environment issues
5. **Test environments**: Test skills in all target environments
6. **Monitor resources**: Track resource usage in production
