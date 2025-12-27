"""
Environment-specific default configurations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from .schema import (
    AuthConfig,
    ConfigSchema,
    ExecutionConfig,
    FeatureFlags,
    LoggingConfig,
    LogLevel,
    RBACConfig,
    SecretBackendType,
    SecretsConfig,
    TracingConfig,
    TracingExporterType,
)


class Environment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class EnvironmentDefaults:
    """Environment-specific defaults container."""
    environment: Environment
    config: ConfigSchema
    description: str


# Development defaults - relaxed security, verbose logging
DEVELOPMENT_DEFAULTS = EnvironmentDefaults(
    environment=Environment.DEVELOPMENT,
    description="Development environment with relaxed security and verbose logging",
    config=ConfigSchema(
        auth=AuthConfig(
            enabled=True,
            jwt_secret="dev-secret-change-in-production",
            require_https=False,
            access_token_ttl_seconds=86400,  # 24 hours for dev convenience
            refresh_token_ttl_seconds=86400 * 30,  # 30 days
        ),
        rbac=RBACConfig(
            enabled=True,
            default_role="developer",  # More permissive default
            cache_ttl_seconds=60,  # Short cache for testing changes
        ),
        secrets=SecretsConfig(
            backend=SecretBackendType.ENV,
            cache_enabled=True,
            cache_ttl_seconds=60,
            mask_in_logs=True,
            audit_access=False,  # Reduce noise in dev
        ),
        logging=LoggingConfig(
            level=LogLevel.DEBUG,
            format="text",  # Human-readable in dev
            include_context=True,
            include_trace_id=True,
            mask_sensitive=True,
        ),
        tracing=TracingConfig(
            enabled=True,
            service_name="agentskills-dev",
            sample_rate=1.0,  # Trace everything in dev
            exporter=TracingExporterType.CONSOLE,
        ),
        execution=ExecutionConfig(
            auto_detect_environment=True,
            default_timeout_ms=60000,  # Longer timeout for debugging
            max_retries=1,  # Fail fast in dev
            sandbox_enabled=False,  # No sandbox in dev
        ),
        features=FeatureFlags(
            enable_skill_composition=True,
            enable_skill_versioning=True,
            enable_lessons_system=True,
            enable_higher_order_skills=True,
            enable_distributed_execution=False,
            enable_cost_tracking=False,  # No cost tracking in dev
            enable_audit_logging=False,  # Reduce noise in dev
        ),
    ),
)


# Testing defaults - fast, deterministic, isolated
TESTING_DEFAULTS = EnvironmentDefaults(
    environment=Environment.TESTING,
    description="Testing environment optimized for fast, deterministic tests",
    config=ConfigSchema(
        auth=AuthConfig(
            enabled=False,  # Disable auth in unit tests
            jwt_secret="test-secret",
            require_https=False,
        ),
        rbac=RBACConfig(
            enabled=False,  # Disable RBAC in unit tests
            default_role="admin",  # Full access for tests
            cache_ttl_seconds=0,  # No caching in tests
        ),
        secrets=SecretsConfig(
            backend=SecretBackendType.ENV,
            cache_enabled=False,  # No caching in tests
            mask_in_logs=False,  # See full values in test output
            audit_access=False,
        ),
        logging=LoggingConfig(
            level=LogLevel.WARNING,  # Reduce noise
            format="text",
            include_context=False,
            include_trace_id=False,
        ),
        tracing=TracingConfig(
            enabled=False,  # Disable tracing in tests
            sample_rate=0,
        ),
        execution=ExecutionConfig(
            auto_detect_environment=False,
            default_timeout_ms=5000,  # Short timeout for tests
            max_retries=0,  # No retries in tests
            sandbox_enabled=False,
        ),
        features=FeatureFlags(
            enable_skill_composition=True,
            enable_skill_versioning=True,
            enable_lessons_system=True,
            enable_higher_order_skills=True,
            enable_distributed_execution=False,
            enable_cost_tracking=False,
            enable_audit_logging=False,
        ),
    ),
)


# Staging defaults - production-like with more visibility
STAGING_DEFAULTS = EnvironmentDefaults(
    environment=Environment.STAGING,
    description="Staging environment - production-like with enhanced observability",
    config=ConfigSchema(
        auth=AuthConfig(
            enabled=True,
            require_https=True,
            access_token_ttl_seconds=3600,
            refresh_token_ttl_seconds=86400 * 7,
        ),
        rbac=RBACConfig(
            enabled=True,
            default_role="viewer",
            cache_ttl_seconds=180,
        ),
        secrets=SecretsConfig(
            backend=SecretBackendType.ENV,  # Can upgrade to AWS/Vault
            cache_enabled=True,
            cache_ttl_seconds=180,
            mask_in_logs=True,
            audit_access=True,
        ),
        logging=LoggingConfig(
            level=LogLevel.DEBUG,  # More verbose than prod
            format="json",
            include_context=True,
            include_trace_id=True,
            mask_sensitive=True,
        ),
        tracing=TracingConfig(
            enabled=True,
            service_name="agentskills-staging",
            sample_rate=1.0,  # Trace everything in staging
            exporter=TracingExporterType.JAEGER,
        ),
        execution=ExecutionConfig(
            auto_detect_environment=True,
            default_timeout_ms=30000,
            max_retries=2,
            sandbox_enabled=True,
        ),
        features=FeatureFlags(
            enable_skill_composition=True,
            enable_skill_versioning=True,
            enable_lessons_system=True,
            enable_higher_order_skills=True,
            enable_distributed_execution=False,
            enable_cost_tracking=True,
            enable_audit_logging=True,
        ),
    ),
)


# Production defaults - secure, performant, observable
PRODUCTION_DEFAULTS = EnvironmentDefaults(
    environment=Environment.PRODUCTION,
    description="Production environment with full security and observability",
    config=ConfigSchema(
        auth=AuthConfig(
            enabled=True,
            require_https=True,
            access_token_ttl_seconds=3600,  # 1 hour
            refresh_token_ttl_seconds=86400 * 7,  # 7 days
        ),
        rbac=RBACConfig(
            enabled=True,
            default_role="viewer",  # Minimal default permissions
            cache_ttl_seconds=300,
        ),
        secrets=SecretsConfig(
            backend=SecretBackendType.AWS,  # Use managed secrets
            cache_enabled=True,
            cache_ttl_seconds=300,
            mask_in_logs=True,
            audit_access=True,
        ),
        logging=LoggingConfig(
            level=LogLevel.INFO,
            format="json",
            include_context=True,
            include_trace_id=True,
            mask_sensitive=True,
        ),
        tracing=TracingConfig(
            enabled=True,
            service_name="agentskills",
            sample_rate=0.1,  # Sample 10% in production
            exporter=TracingExporterType.OTLP,
        ),
        execution=ExecutionConfig(
            auto_detect_environment=True,
            default_timeout_ms=30000,
            max_retries=3,
            sandbox_enabled=True,
        ),
        features=FeatureFlags(
            enable_skill_composition=True,
            enable_skill_versioning=True,
            enable_lessons_system=True,
            enable_higher_order_skills=True,
            enable_distributed_execution=True,
            enable_cost_tracking=True,
            enable_audit_logging=True,
        ),
    ),
)


# Registry of all defaults
_DEFAULTS_REGISTRY: Dict[Environment, EnvironmentDefaults] = {
    Environment.DEVELOPMENT: DEVELOPMENT_DEFAULTS,
    Environment.TESTING: TESTING_DEFAULTS,
    Environment.STAGING: STAGING_DEFAULTS,
    Environment.PRODUCTION: PRODUCTION_DEFAULTS,
}


def get_default_config(
    environment: Optional[str] = None,
) -> ConfigSchema:
    """
    Get default configuration for an environment.

    Args:
        environment: Environment name (development, testing, staging, production)
                    If None, auto-detects from AGENTSKILLS_ENV environment variable

    Returns:
        ConfigSchema with environment-appropriate defaults
    """
    import os

    if environment is None:
        environment = os.environ.get("AGENTSKILLS_ENV", "development")

    try:
        env = Environment(environment.lower())
    except ValueError:
        # Unknown environment, default to development
        env = Environment.DEVELOPMENT

    return _DEFAULTS_REGISTRY[env].config


def get_environment_description(environment: str) -> str:
    """Get description of an environment's defaults."""
    try:
        env = Environment(environment.lower())
        return _DEFAULTS_REGISTRY[env].description
    except (ValueError, KeyError):
        return "Unknown environment"


def list_environments() -> Dict[str, str]:
    """List all available environments with descriptions."""
    return {
        env.value: defaults.description
        for env, defaults in _DEFAULTS_REGISTRY.items()
    }
