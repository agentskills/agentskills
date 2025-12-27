"""
Integration tests for execution environment flow.
"""

import os
import pytest

from skills_ref.execution import (
    EnvironmentDetector,
    EnvironmentManager,
    EnvironmentType,
    EnvironmentCapability,
    ExecutionEnvironment,
    ExecutionContextBuilder,
    ExecutionConstraints,
    SkillRequirements,
)


class TestEnvironmentDetection:
    """Test environment detection."""

    @pytest.fixture
    def detector(self):
        return EnvironmentDetector()

    def test_detect_environment(self, detector):
        """Test basic environment detection."""
        env = detector.detect()

        assert env is not None
        assert env.type in EnvironmentType
        assert isinstance(env.capabilities, set)

    def test_detect_local_environment(self, detector, monkeypatch):
        """Test local environment detection."""
        # Clear environment variables that indicate other environments
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.delenv("CODESPACES", raising=False)
        monkeypatch.delenv("KUBERNETES_SERVICE_HOST", raising=False)

        env = detector.detect()

        # Without indicators, should default to local
        # (unless running in Docker, which is detected by /.dockerenv)

    def test_detect_ci_environment(self, detector, monkeypatch):
        """Test CI environment detection."""
        monkeypatch.setenv("CI", "true")

        env = detector.detect()
        assert env.type == EnvironmentType.CI

    def test_detect_codespaces_environment(self, detector, monkeypatch):
        """Test Codespaces environment detection."""
        monkeypatch.setenv("CODESPACES", "true")

        env = detector.detect()
        assert env.type == EnvironmentType.CODESPACES

    def test_detect_github_actions(self, detector, monkeypatch):
        """Test GitHub Actions detection."""
        monkeypatch.setenv("GITHUB_ACTIONS", "true")

        env = detector.detect()
        assert env.type == EnvironmentType.CI


class TestEnvironmentCapabilities:
    """Test environment capability checking."""

    def test_capability_checking(self):
        """Test checking environment capabilities."""
        env = ExecutionEnvironment(
            type=EnvironmentType.LOCAL,
            name="test-env",
            capabilities={
                EnvironmentCapability.FILESYSTEM,
                EnvironmentCapability.NETWORK,
            },
        )

        assert env.has_capability(EnvironmentCapability.FILESYSTEM)
        assert env.has_capability(EnvironmentCapability.NETWORK)
        assert not env.has_capability(EnvironmentCapability.GPU)

    def test_multiple_capability_check(self):
        """Test checking multiple capabilities."""
        env = ExecutionEnvironment(
            type=EnvironmentType.CLOUD,
            name="cloud-env",
            capabilities={
                EnvironmentCapability.FILESYSTEM,
                EnvironmentCapability.NETWORK,
                EnvironmentCapability.SECRETS,
                EnvironmentCapability.HIGH_MEMORY,
            },
        )

        required = {
            EnvironmentCapability.FILESYSTEM,
            EnvironmentCapability.NETWORK,
        }

        assert required.issubset(env.capabilities)

        # Check missing capability
        required_with_gpu = required | {EnvironmentCapability.GPU}
        assert not required_with_gpu.issubset(env.capabilities)


class TestSkillRequirements:
    """Test skill requirement validation."""

    def test_requirements_satisfied(self):
        """Test when environment satisfies requirements."""
        env = ExecutionEnvironment(
            type=EnvironmentType.DOCKER,
            name="docker-env",
            capabilities={
                EnvironmentCapability.FILESYSTEM,
                EnvironmentCapability.NETWORK,
            },
        )

        requirements = SkillRequirements(
            min_memory_mb=512,
            required_capabilities={EnvironmentCapability.NETWORK},
            allowed_environments=[EnvironmentType.DOCKER, EnvironmentType.CLOUD],
        )

        assert env.satisfies(requirements)

    def test_requirements_not_satisfied_environment(self):
        """Test when environment type not allowed."""
        env = ExecutionEnvironment(
            type=EnvironmentType.LOCAL,
            name="local-env",
            capabilities={EnvironmentCapability.NETWORK},
        )

        requirements = SkillRequirements(
            allowed_environments=[EnvironmentType.DOCKER, EnvironmentType.CLOUD],
        )

        assert not env.satisfies(requirements)

    def test_requirements_not_satisfied_capability(self):
        """Test when capability not available."""
        env = ExecutionEnvironment(
            type=EnvironmentType.DOCKER,
            name="docker-env",
            capabilities={EnvironmentCapability.FILESYSTEM},
        )

        requirements = SkillRequirements(
            required_capabilities={
                EnvironmentCapability.NETWORK,
                EnvironmentCapability.GPU,
            },
        )

        assert not env.satisfies(requirements)


class TestExecutionContext:
    """Test execution context building."""

    def test_context_builder(self):
        """Test building execution context."""
        context = (
            ExecutionContextBuilder()
            .with_timeout(30000)
            .with_retries(3)
            .with_backoff(2.0)
            .with_trace_id("trace-123")
            .with_user_id("user-456")
            .with_metadata({"key": "value"})
            .build()
        )

        assert context.timeout_ms == 30000
        assert context.max_retries == 3
        assert context.backoff_base == 2.0
        assert context.trace_id == "trace-123"
        assert context.user_id == "user-456"
        assert context.metadata["key"] == "value"

    def test_context_with_constraints(self):
        """Test context with execution constraints."""
        constraints = ExecutionConstraints(
            max_duration_ms=60000,
            max_memory_mb=1024,
            max_retries=5,
            sandbox=True,
        )

        context = (
            ExecutionContextBuilder()
            .with_constraints(constraints)
            .build()
        )

        assert context.constraints.max_duration_ms == 60000
        assert context.constraints.sandbox is True

    def test_context_defaults(self):
        """Test context has sensible defaults."""
        context = ExecutionContextBuilder().build()

        assert context.timeout_ms > 0
        assert context.max_retries >= 0


class TestEnvironmentManager:
    """Test environment manager."""

    @pytest.fixture
    def manager(self):
        return EnvironmentManager()

    @pytest.fixture
    def test_env(self):
        return ExecutionEnvironment(
            type=EnvironmentType.LOCAL,
            name="test-env",
            capabilities={
                EnvironmentCapability.FILESYSTEM,
                EnvironmentCapability.NETWORK,
            },
        )

    def test_register_environment(self, manager, test_env):
        """Test registering an environment."""
        manager.register_environment(test_env)

        assert manager.get_environment(test_env.name) == test_env

    def test_can_execute_check(self, manager, test_env):
        """Test can_execute check."""
        manager.register_environment(test_env)

        # Requirements that can be satisfied
        requirements = SkillRequirements(
            required_capabilities={EnvironmentCapability.NETWORK},
            allowed_environments=[EnvironmentType.LOCAL],
        )

        can_run = manager.can_execute(
            skill_requirements=requirements,
            environment=test_env,
        )

        assert can_run

    def test_cannot_execute_check(self, manager, test_env):
        """Test can_execute returns false for unsatisfied requirements."""
        manager.register_environment(test_env)

        # Requirements that cannot be satisfied
        requirements = SkillRequirements(
            required_capabilities={EnvironmentCapability.GPU},
        )

        can_run = manager.can_execute(
            skill_requirements=requirements,
            environment=test_env,
        )

        assert not can_run


class TestExecutionFlow:
    """Test full execution flow through environment system."""

    @pytest.fixture
    def detector(self):
        return EnvironmentDetector()

    @pytest.fixture
    def manager(self):
        return EnvironmentManager()

    def test_full_execution_flow(self, detector, manager):
        """Test complete execution flow."""
        # Detect environment
        env = detector.detect()
        assert env is not None

        # Register environment
        manager.register_environment(env)

        # Build execution context
        context = (
            ExecutionContextBuilder()
            .with_timeout(5000)
            .with_retries(1)
            .with_trace_id("test-trace")
            .build()
        )

        assert context.trace_id == "test-trace"

        # Check if skill can execute
        requirements = SkillRequirements(
            min_memory_mb=256,
            required_capabilities=set(),  # No specific requirements
        )

        can_run = manager.can_execute(requirements, env)
        assert can_run  # Should be able to run with no specific requirements

    def test_environment_specific_context(self, detector):
        """Test creating context specific to environment."""
        env = detector.detect()

        # Adjust context based on environment
        if env.type == EnvironmentType.CI:
            timeout = 60000  # Longer timeout for CI
            retries = 3
        elif env.type == EnvironmentType.LOCAL:
            timeout = 30000
            retries = 1
        else:
            timeout = 45000
            retries = 2

        context = (
            ExecutionContextBuilder()
            .with_timeout(timeout)
            .with_retries(retries)
            .build()
        )

        assert context.timeout_ms > 0
        assert context.max_retries >= 0
