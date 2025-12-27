"""
Configuration Management for AgentSkills Enterprise.

This module provides:
- Configuration schema validation
- Environment-specific defaults
- Dynamic configuration loading
- Feature flags and toggles
"""

from .schema import (
    ConfigSchema,
    AuthConfig,
    RBACConfig,
    SecretsConfig,
    LoggingConfig,
    TracingConfig,
    ExecutionConfig,
    validate_config,
)
from .defaults import (
    get_default_config,
    EnvironmentDefaults,
    DEVELOPMENT_DEFAULTS,
    PRODUCTION_DEFAULTS,
    TESTING_DEFAULTS,
)
from .loader import (
    ConfigLoader,
    EnvConfigLoader,
    FileConfigLoader,
    CompositeConfigLoader,
)

__all__ = [
    # Schema
    "ConfigSchema",
    "AuthConfig",
    "RBACConfig",
    "SecretsConfig",
    "LoggingConfig",
    "TracingConfig",
    "ExecutionConfig",
    "validate_config",
    # Defaults
    "get_default_config",
    "EnvironmentDefaults",
    "DEVELOPMENT_DEFAULTS",
    "PRODUCTION_DEFAULTS",
    "TESTING_DEFAULTS",
    # Loader
    "ConfigLoader",
    "EnvConfigLoader",
    "FileConfigLoader",
    "CompositeConfigLoader",
]
