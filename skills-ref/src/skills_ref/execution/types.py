"""
Core types for execution environment abstraction.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..auth.types import SkillAuthContext
from ..secrets.store import SecretStore


class EnvironmentType(Enum):
    """Types of execution environments."""
    LOCAL = "local"
    CODESPACE = "codespace"
    CLOUD = "cloud"
    DOCKER = "docker"
    CI = "ci"
    UNKNOWN = "unknown"


class EnvironmentCapability(Enum):
    """Capabilities an environment may have."""
    FILESYSTEM_READ = "filesystem_read"
    FILESYSTEM_WRITE = "filesystem_write"
    NETWORK_ACCESS = "network_access"
    SUBPROCESS_EXEC = "subprocess_exec"
    GPU_AVAILABLE = "gpu_available"
    SECRETS_ENV = "secrets_env"
    SECRETS_VAULT = "secrets_vault"
    SECRETS_CLOUD = "secrets_cloud"
    BROWSER_AVAILABLE = "browser_available"
    DISPLAY_AVAILABLE = "display_available"


@dataclass
class ExecutionConstraints:
    """Resource constraints for skill execution."""
    max_cpu_seconds: Optional[float] = None  # CPU time limit
    max_memory_mb: Optional[int] = None  # Memory limit
    max_timeout_seconds: Optional[int] = None  # Wall clock timeout
    max_network_requests: Optional[int] = None  # Rate limiting
    max_file_size_mb: Optional[int] = None  # File output limit

    # Network restrictions
    allowed_hosts: List[str] = field(default_factory=list)  # Whitelist
    blocked_hosts: List[str] = field(default_factory=list)  # Blacklist

    # Filesystem restrictions
    allowed_paths: List[str] = field(default_factory=list)
    blocked_paths: List[str] = field(default_factory=list)

    def allows_host(self, host: str) -> bool:
        """Check if a host is allowed."""
        if host in self.blocked_hosts:
            return False
        if self.allowed_hosts and host not in self.allowed_hosts:
            return False
        return True

    def allows_path(self, path: str) -> bool:
        """Check if a path is allowed."""
        for blocked in self.blocked_paths:
            if path.startswith(blocked):
                return False
        if self.allowed_paths:
            for allowed in self.allowed_paths:
                if path.startswith(allowed):
                    return True
            return False
        return True


@dataclass
class ExecutionEnvironment:
    """
    Describes the current execution environment.

    Provides information about capabilities, constraints,
    and configuration for the current runtime.
    """
    type: EnvironmentType
    hostname: str
    working_directory: str

    # Capabilities
    capabilities: Set[EnvironmentCapability] = field(default_factory=set)

    # Constraints
    constraints: ExecutionConstraints = field(default_factory=ExecutionConstraints)

    # Cloud provider info (if applicable)
    cloud_provider: Optional[str] = None  # aws, gcp, azure
    cloud_region: Optional[str] = None

    # Container info (if applicable)
    container_id: Optional[str] = None
    container_image: Optional[str] = None

    # Codespace info (if applicable)
    codespace_name: Optional[str] = None
    github_token_available: bool = False

    # Metadata
    detected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_capability(self, cap: EnvironmentCapability) -> bool:
        """Check if environment has a capability."""
        return cap in self.capabilities

    def has_all_capabilities(self, caps: List[EnvironmentCapability]) -> bool:
        """Check if environment has all specified capabilities."""
        return all(self.has_capability(c) for c in caps)

    def has_any_capability(self, caps: List[EnvironmentCapability]) -> bool:
        """Check if environment has any specified capability."""
        return any(self.has_capability(c) for c in caps)

    def is_local(self) -> bool:
        """Check if running locally."""
        return self.type == EnvironmentType.LOCAL

    def is_cloud(self) -> bool:
        """Check if running in cloud."""
        return self.type == EnvironmentType.CLOUD

    def is_codespace(self) -> bool:
        """Check if running in GitHub Codespace."""
        return self.type == EnvironmentType.CODESPACE

    def is_container(self) -> bool:
        """Check if running in Docker."""
        return self.type == EnvironmentType.DOCKER

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "hostname": self.hostname,
            "working_directory": self.working_directory,
            "capabilities": [c.value for c in self.capabilities],
            "cloud_provider": self.cloud_provider,
            "cloud_region": self.cloud_region,
            "container_id": self.container_id,
            "codespace_name": self.codespace_name,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class SkillRequirements:
    """Requirements for executing a skill."""
    # Environment requirements
    min_environment: EnvironmentType = EnvironmentType.LOCAL
    preferred_environment: Optional[EnvironmentType] = None
    supported_environments: List[EnvironmentType] = field(
        default_factory=lambda: list(EnvironmentType)
    )

    # Required capabilities
    required_capabilities: List[EnvironmentCapability] = field(default_factory=list)

    # Resource requirements
    min_memory_mb: Optional[int] = None
    min_cpu_seconds: Optional[float] = None
    requires_gpu: bool = False

    # Network requirements
    requires_network: bool = False
    required_hosts: List[str] = field(default_factory=list)

    # Filesystem requirements
    requires_filesystem_read: bool = False
    requires_filesystem_write: bool = False
    required_paths: List[str] = field(default_factory=list)

    def is_satisfied_by(self, env: ExecutionEnvironment) -> tuple[bool, List[str]]:
        """
        Check if requirements are satisfied by environment.

        Returns (satisfied, list of unsatisfied requirements).
        """
        unsatisfied = []

        # Check environment type
        if env.type not in self.supported_environments:
            unsatisfied.append(f"Environment type {env.type.value} not supported")

        # Check capabilities
        for cap in self.required_capabilities:
            if not env.has_capability(cap):
                unsatisfied.append(f"Missing capability: {cap.value}")

        # Check network
        if self.requires_network:
            if not env.has_capability(EnvironmentCapability.NETWORK_ACCESS):
                unsatisfied.append("Network access required")

        # Check filesystem
        if self.requires_filesystem_read:
            if not env.has_capability(EnvironmentCapability.FILESYSTEM_READ):
                unsatisfied.append("Filesystem read access required")

        if self.requires_filesystem_write:
            if not env.has_capability(EnvironmentCapability.FILESYSTEM_WRITE):
                unsatisfied.append("Filesystem write access required")

        # Check GPU
        if self.requires_gpu:
            if not env.has_capability(EnvironmentCapability.GPU_AVAILABLE):
                unsatisfied.append("GPU required")

        return len(unsatisfied) == 0, unsatisfied


@dataclass
class ExecutionContext:
    """
    Complete context for skill execution.

    Bundles together environment, auth, secrets, and logging.
    """
    # Environment
    environment: ExecutionEnvironment

    # Authentication
    auth_context: Optional[SkillAuthContext] = None

    # Secrets
    secret_store: Optional[SecretStore] = None

    # Execution metadata
    execution_id: str = ""
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    timeout_at: Optional[datetime] = None

    # Custom data
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def user_id(self) -> Optional[str]:
        """Get user ID from auth context."""
        return self.auth_context.user_id if self.auth_context else None

    @property
    def workspace_id(self) -> Optional[str]:
        """Get workspace ID from auth context."""
        return self.auth_context.workspace_id if self.auth_context else None

    def get_secret(self, name: str) -> Optional[str]:
        """Convenience method to get a secret."""
        if self.secret_store:
            # Note: This is sync wrapper, in practice use await
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.secret_store.get(name))
            except Exception:
                return None
        return None

    def to_logging_context(self) -> Dict[str, Any]:
        """Get context dict for structured logging."""
        return {
            "execution_id": self.execution_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "environment_type": self.environment.type.value,
        }
