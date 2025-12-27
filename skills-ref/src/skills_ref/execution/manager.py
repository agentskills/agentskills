"""
Execution environment and context management.
"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..auth.types import SkillAuthContext
from ..secrets.store import SecretStore, SecretStoreBuilder
from ..secrets.types import SecretBackend
from .detector import EnvironmentDetector
from .types import (
    EnvironmentCapability,
    EnvironmentType,
    ExecutionContext,
    ExecutionEnvironment,
    SkillRequirements,
)


class EnvironmentManager:
    """
    Manages execution environments and contexts.

    Features:
    - Environment detection
    - Skill requirement validation
    - Execution context preparation
    - Environment-aware secret loading
    """

    def __init__(
        self,
        detector: Optional[EnvironmentDetector] = None,
    ):
        self.detector = detector or EnvironmentDetector()
        self._current_env: Optional[ExecutionEnvironment] = None

    def get_current_environment(self, force_refresh: bool = False) -> ExecutionEnvironment:
        """Get the current execution environment."""
        if self._current_env is None or force_refresh:
            self._current_env = self.detector.detect(force_refresh)
        return self._current_env

    def can_execute_skill(
        self,
        requirements: SkillRequirements,
        environment: Optional[ExecutionEnvironment] = None,
    ) -> tuple[bool, List[str]]:
        """
        Check if a skill can be executed in the current/given environment.

        Returns (can_execute, list of unsatisfied requirements).
        """
        env = environment or self.get_current_environment()
        return requirements.is_satisfied_by(env)

    def prepare_context(
        self,
        auth_context: Optional[SkillAuthContext] = None,
        secret_store: Optional[SecretStore] = None,
        timeout_seconds: Optional[int] = None,
        **metadata,
    ) -> ExecutionContext:
        """
        Prepare an execution context for skill execution.

        Automatically configures secrets based on environment.
        """
        env = self.get_current_environment()

        # Auto-configure secret store if not provided
        if secret_store is None:
            secret_store = self._create_secret_store(env)

        # Calculate timeout
        timeout_at = None
        if timeout_seconds:
            timeout_at = datetime.utcnow() + timedelta(seconds=timeout_seconds)
        elif env.constraints.max_timeout_seconds:
            timeout_at = datetime.utcnow() + timedelta(
                seconds=env.constraints.max_timeout_seconds
            )

        return ExecutionContext(
            environment=env,
            auth_context=auth_context,
            secret_store=secret_store,
            execution_id=secrets.token_hex(8),
            timeout_at=timeout_at,
            metadata=metadata,
        )

    def get_available_environments(self) -> List[ExecutionEnvironment]:
        """
        Get list of available environments.

        For now, returns only current environment.
        In future, could query remote environments.
        """
        return [self.get_current_environment()]

    def validate_requirements(
        self,
        requirements: SkillRequirements,
    ) -> Dict[str, Any]:
        """
        Validate skill requirements against current environment.

        Returns detailed validation result.
        """
        env = self.get_current_environment()
        satisfied, unsatisfied = requirements.is_satisfied_by(env)

        return {
            "satisfied": satisfied,
            "environment_type": env.type.value,
            "requirements": {
                "environment_type": requirements.min_environment.value,
                "required_capabilities": [c.value for c in requirements.required_capabilities],
                "requires_network": requirements.requires_network,
                "requires_filesystem_read": requirements.requires_filesystem_read,
                "requires_filesystem_write": requirements.requires_filesystem_write,
                "requires_gpu": requirements.requires_gpu,
            },
            "available_capabilities": [c.value for c in env.capabilities],
            "unsatisfied": unsatisfied,
        }

    def _create_secret_store(self, env: ExecutionEnvironment) -> SecretStore:
        """Create a secret store appropriate for the environment."""
        builder = SecretStoreBuilder()

        # Always add env provider
        if env.has_capability(EnvironmentCapability.SECRETS_ENV):
            builder.with_env_provider()

        # Add cloud providers based on environment
        if env.has_capability(EnvironmentCapability.SECRETS_CLOUD):
            if env.cloud_provider == "aws":
                builder.with_aws_provider(env.cloud_region)
            # Add GCP, Azure providers as needed

        # Add Vault if available
        if env.has_capability(EnvironmentCapability.SECRETS_VAULT):
            builder.with_vault_provider()

        return builder.with_caching(ttl_seconds=300).build()


class ExecutionContextBuilder:
    """
    Builder for creating execution contexts.

    Example:
        context = (ExecutionContextBuilder()
            .with_auth(auth_context)
            .with_secrets(secret_store)
            .with_timeout(30)
            .with_trace_id(trace_id)
            .build())
    """

    def __init__(self, environment_manager: Optional[EnvironmentManager] = None):
        self._env_manager = environment_manager or EnvironmentManager()
        self._auth_context: Optional[SkillAuthContext] = None
        self._secret_store: Optional[SecretStore] = None
        self._timeout_seconds: Optional[int] = None
        self._trace_id: Optional[str] = None
        self._span_id: Optional[str] = None
        self._metadata: Dict[str, Any] = {}

    def with_auth(self, auth_context: SkillAuthContext) -> "ExecutionContextBuilder":
        """Set authentication context."""
        self._auth_context = auth_context
        return self

    def with_secrets(self, secret_store: SecretStore) -> "ExecutionContextBuilder":
        """Set secret store."""
        self._secret_store = secret_store
        return self

    def with_timeout(self, seconds: int) -> "ExecutionContextBuilder":
        """Set execution timeout."""
        self._timeout_seconds = seconds
        return self

    def with_trace_id(self, trace_id: str) -> "ExecutionContextBuilder":
        """Set trace ID for distributed tracing."""
        self._trace_id = trace_id
        return self

    def with_span_id(self, span_id: str) -> "ExecutionContextBuilder":
        """Set span ID for distributed tracing."""
        self._span_id = span_id
        return self

    def with_metadata(self, **kwargs) -> "ExecutionContextBuilder":
        """Add metadata to context."""
        self._metadata.update(kwargs)
        return self

    def build(self) -> ExecutionContext:
        """Build the execution context."""
        context = self._env_manager.prepare_context(
            auth_context=self._auth_context,
            secret_store=self._secret_store,
            timeout_seconds=self._timeout_seconds,
            **self._metadata,
        )

        if self._trace_id:
            context.trace_id = self._trace_id
        if self._span_id:
            context.span_id = self._span_id

        return context


class ExecutionMiddleware:
    """
    Middleware for managing skill execution context.

    Handles:
    - Environment validation
    - Context preparation
    - Resource cleanup
    """

    def __init__(self, environment_manager: EnvironmentManager):
        self.env_manager = environment_manager

    async def before(
        self,
        skill_name: str,
        requirements: SkillRequirements,
        auth_context: Optional[SkillAuthContext],
    ) -> ExecutionContext:
        """
        Prepare for skill execution.

        Validates requirements and creates context.
        """
        # Validate requirements
        can_execute, unsatisfied = self.env_manager.can_execute_skill(requirements)
        if not can_execute:
            raise RuntimeError(
                f"Cannot execute skill {skill_name}: {', '.join(unsatisfied)}"
            )

        # Prepare context
        context = self.env_manager.prepare_context(
            auth_context=auth_context,
            skill_name=skill_name,
        )

        return context

    async def after(
        self,
        context: ExecutionContext,
        result: Any,
    ) -> None:
        """Cleanup after successful execution."""
        # Could log metrics, clean up resources, etc.
        pass

    async def on_error(
        self,
        context: ExecutionContext,
        error: Exception,
    ) -> None:
        """Handle execution error."""
        # Could log error, clean up resources, etc.
        pass
