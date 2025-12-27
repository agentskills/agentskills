"""
Configuration schema definitions and validation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ConfigError(Exception):
    """Configuration validation error."""
    pass


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SecretBackendType(str, Enum):
    """Secret backend types."""
    ENV = "env"
    AWS = "aws"
    VAULT = "vault"


class TracingExporterType(str, Enum):
    """Tracing exporter types."""
    CONSOLE = "console"
    JAEGER = "jaeger"
    OTLP = "otlp"


@dataclass
class AuthConfig:
    """Authentication configuration."""
    enabled: bool = True
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 3600
    refresh_token_ttl_seconds: int = 86400 * 7
    api_key_enabled: bool = True
    api_key_header: str = "X-API-Key"
    require_https: bool = True
    allowed_issuers: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """Validate auth configuration."""
        errors = []
        if self.enabled and not self.jwt_secret:
            errors.append("jwt_secret is required when auth is enabled")
        if self.access_token_ttl_seconds < 60:
            errors.append("access_token_ttl_seconds must be at least 60")
        if self.refresh_token_ttl_seconds < self.access_token_ttl_seconds:
            errors.append("refresh_token_ttl_seconds must be >= access_token_ttl_seconds")
        return errors


@dataclass
class RBACConfig:
    """RBAC configuration."""
    enabled: bool = True
    default_role: str = "viewer"
    admin_users: List[str] = field(default_factory=list)
    custom_roles_file: Optional[str] = None
    policy_file: Optional[str] = None
    cache_ttl_seconds: int = 300
    inherit_permissions: bool = True

    def validate(self) -> List[str]:
        """Validate RBAC configuration."""
        errors = []
        if self.cache_ttl_seconds < 0:
            errors.append("cache_ttl_seconds must be >= 0")
        return errors


@dataclass
class SecretsConfig:
    """Secrets management configuration."""
    backend: SecretBackendType = SecretBackendType.ENV
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    mask_in_logs: bool = True
    audit_access: bool = True
    # AWS-specific
    aws_region: Optional[str] = None
    aws_secret_prefix: str = ""
    # Vault-specific
    vault_addr: Optional[str] = None
    vault_token: Optional[str] = None
    vault_mount: str = "secret"

    def validate(self) -> List[str]:
        """Validate secrets configuration."""
        errors = []
        if self.backend == SecretBackendType.AWS and not self.aws_region:
            errors.append("aws_region is required when using AWS backend")
        if self.backend == SecretBackendType.VAULT and not self.vault_addr:
            errors.append("vault_addr is required when using Vault backend")
        if self.cache_ttl_seconds < 0:
            errors.append("cache_ttl_seconds must be >= 0")
        return errors


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: str = "json"
    include_context: bool = True
    include_trace_id: bool = True
    mask_sensitive: bool = True
    output_file: Optional[str] = None
    max_message_length: int = 10000
    sensitive_fields: List[str] = field(default_factory=lambda: [
        "password", "secret", "token", "api_key", "credential"
    ])

    def validate(self) -> List[str]:
        """Validate logging configuration."""
        errors = []
        if self.format not in ["json", "text"]:
            errors.append("format must be 'json' or 'text'")
        if self.max_message_length < 100:
            errors.append("max_message_length must be at least 100")
        return errors


@dataclass
class TracingConfig:
    """Distributed tracing configuration."""
    enabled: bool = True
    service_name: str = "agentskills"
    sample_rate: float = 1.0
    exporter: TracingExporterType = TracingExporterType.CONSOLE
    # Jaeger-specific
    jaeger_endpoint: Optional[str] = None
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    # OTLP-specific
    otlp_endpoint: Optional[str] = None
    propagate_context: bool = True

    def validate(self) -> List[str]:
        """Validate tracing configuration."""
        errors = []
        if self.sample_rate < 0 or self.sample_rate > 1:
            errors.append("sample_rate must be between 0 and 1")
        if self.exporter == TracingExporterType.JAEGER and not self.jaeger_endpoint:
            errors.append("jaeger_endpoint is required when using Jaeger exporter")
        if self.exporter == TracingExporterType.OTLP and not self.otlp_endpoint:
            errors.append("otlp_endpoint is required when using OTLP exporter")
        return errors


@dataclass
class ExecutionConfig:
    """Execution environment configuration."""
    auto_detect_environment: bool = True
    default_timeout_ms: int = 30000
    max_timeout_ms: int = 300000
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    sandbox_enabled: bool = True
    allowed_environments: List[str] = field(default_factory=lambda: [
        "local", "codespaces", "cloud", "docker", "ci"
    ])
    resource_limits: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validate execution configuration."""
        errors = []
        if self.default_timeout_ms < 1000:
            errors.append("default_timeout_ms must be at least 1000")
        if self.max_timeout_ms < self.default_timeout_ms:
            errors.append("max_timeout_ms must be >= default_timeout_ms")
        if self.max_retries < 0:
            errors.append("max_retries must be >= 0")
        if self.retry_backoff_base < 1:
            errors.append("retry_backoff_base must be >= 1")
        return errors


@dataclass
class FeatureFlags:
    """Feature toggles."""
    enable_skill_composition: bool = True
    enable_skill_versioning: bool = True
    enable_lessons_system: bool = True
    enable_higher_order_skills: bool = True
    enable_distributed_execution: bool = False
    enable_cost_tracking: bool = True
    enable_audit_logging: bool = True


@dataclass
class ConfigSchema:
    """Complete configuration schema."""
    auth: AuthConfig = field(default_factory=AuthConfig)
    rbac: RBACConfig = field(default_factory=RBACConfig)
    secrets: SecretsConfig = field(default_factory=SecretsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    tracing: TracingConfig = field(default_factory=TracingConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)

    def validate(self) -> List[str]:
        """Validate complete configuration."""
        errors = []
        errors.extend([f"auth: {e}" for e in self.auth.validate()])
        errors.extend([f"rbac: {e}" for e in self.rbac.validate()])
        errors.extend([f"secrets: {e}" for e in self.secrets.validate()])
        errors.extend([f"logging: {e}" for e in self.logging.validate()])
        errors.extend([f"tracing: {e}" for e in self.tracing.validate()])
        errors.extend([f"execution: {e}" for e in self.execution.validate()])
        return errors

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigSchema":
        """Create configuration from dictionary."""
        return cls(
            auth=_dict_to_dataclass(AuthConfig, data.get("auth", {})),
            rbac=_dict_to_dataclass(RBACConfig, data.get("rbac", {})),
            secrets=_dict_to_dataclass(SecretsConfig, data.get("secrets", {})),
            logging=_dict_to_dataclass(LoggingConfig, data.get("logging", {})),
            tracing=_dict_to_dataclass(TracingConfig, data.get("tracing", {})),
            execution=_dict_to_dataclass(ExecutionConfig, data.get("execution", {})),
            features=_dict_to_dataclass(FeatureFlags, data.get("features", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        from dataclasses import asdict
        return asdict(self)


def _dict_to_dataclass(cls, data: Dict[str, Any]):
    """Convert dictionary to dataclass, handling enums."""
    import dataclasses
    field_types = {f.name: f.type for f in dataclasses.fields(cls)}
    kwargs = {}

    for key, value in data.items():
        if key in field_types:
            field_type = field_types[key]
            # Handle enum conversion
            if hasattr(field_type, "__origin__"):
                # Skip complex types like List, Optional
                kwargs[key] = value
            elif isinstance(field_type, type) and issubclass(field_type, Enum):
                kwargs[key] = field_type(value) if isinstance(value, str) else value
            else:
                kwargs[key] = value

    return cls(**kwargs)


def validate_config(config: ConfigSchema) -> None:
    """
    Validate configuration and raise on errors.

    Raises:
        ConfigError: If configuration is invalid
    """
    errors = config.validate()
    if errors:
        raise ConfigError(f"Configuration validation failed: {'; '.join(errors)}")
