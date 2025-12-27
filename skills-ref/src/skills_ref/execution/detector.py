"""
Environment detection for different runtime contexts.
"""

import os
import platform
import socket
from datetime import datetime
from typing import Optional, Set

from .types import (
    EnvironmentCapability,
    EnvironmentType,
    ExecutionConstraints,
    ExecutionEnvironment,
)


class EnvironmentDetector:
    """
    Detects the current execution environment.

    Identifies whether running in:
    - Local development machine
    - GitHub Codespaces
    - Docker container
    - Cloud (AWS, GCP, Azure)
    - CI/CD pipeline
    """

    def __init__(self):
        self._cached_env: Optional[ExecutionEnvironment] = None

    def detect(self, force_refresh: bool = False) -> ExecutionEnvironment:
        """
        Detect the current environment.

        Caches result unless force_refresh is True.
        """
        if self._cached_env and not force_refresh:
            return self._cached_env

        env_type = self._detect_type()
        capabilities = self._detect_capabilities()
        constraints = self._detect_constraints(env_type)

        env = ExecutionEnvironment(
            type=env_type,
            hostname=socket.gethostname(),
            working_directory=os.getcwd(),
            capabilities=capabilities,
            constraints=constraints,
            detected_at=datetime.utcnow(),
        )

        # Add type-specific details
        self._enrich_environment(env)

        self._cached_env = env
        return env

    def _detect_type(self) -> EnvironmentType:
        """Detect the environment type."""
        # GitHub Codespaces
        if os.environ.get("CODESPACE_NAME"):
            return EnvironmentType.CODESPACE

        # CI/CD environments
        if any(os.environ.get(v) for v in [
            "CI", "GITHUB_ACTIONS", "GITLAB_CI",
            "JENKINS_URL", "CIRCLECI", "TRAVIS",
        ]):
            return EnvironmentType.CI

        # Docker container
        if self._is_docker():
            return EnvironmentType.DOCKER

        # Cloud environments
        if self._is_aws():
            return EnvironmentType.CLOUD
        if self._is_gcp():
            return EnvironmentType.CLOUD
        if self._is_azure():
            return EnvironmentType.CLOUD

        # Default to local
        return EnvironmentType.LOCAL

    def _is_docker(self) -> bool:
        """Check if running in Docker."""
        # Check for .dockerenv file
        if os.path.exists("/.dockerenv"):
            return True

        # Check cgroup
        try:
            with open("/proc/1/cgroup", "r") as f:
                content = f.read()
                if "docker" in content or "containerd" in content:
                    return True
        except Exception:
            pass

        return False

    def _is_aws(self) -> bool:
        """Check if running in AWS."""
        return any(os.environ.get(v) for v in [
            "AWS_EXECUTION_ENV", "AWS_LAMBDA_FUNCTION_NAME",
            "ECS_CONTAINER_METADATA_URI", "AWS_REGION",
        ])

    def _is_gcp(self) -> bool:
        """Check if running in GCP."""
        return any(os.environ.get(v) for v in [
            "GCP_PROJECT", "GOOGLE_CLOUD_PROJECT",
            "GAE_APPLICATION", "K_SERVICE",
        ])

    def _is_azure(self) -> bool:
        """Check if running in Azure."""
        return any(os.environ.get(v) for v in [
            "AZURE_FUNCTIONS_ENVIRONMENT", "WEBSITE_SITE_NAME",
            "AZURE_CLIENT_ID",
        ])

    def _detect_capabilities(self) -> Set[EnvironmentCapability]:
        """Detect available capabilities."""
        caps = set()

        # Filesystem
        if self._can_read_filesystem():
            caps.add(EnvironmentCapability.FILESYSTEM_READ)
        if self._can_write_filesystem():
            caps.add(EnvironmentCapability.FILESYSTEM_WRITE)

        # Network
        if self._has_network():
            caps.add(EnvironmentCapability.NETWORK_ACCESS)

        # Subprocess
        if self._can_exec_subprocess():
            caps.add(EnvironmentCapability.SUBPROCESS_EXEC)

        # GPU
        if self._has_gpu():
            caps.add(EnvironmentCapability.GPU_AVAILABLE)

        # Secrets backends
        if os.environ:
            caps.add(EnvironmentCapability.SECRETS_ENV)

        if os.environ.get("VAULT_ADDR"):
            caps.add(EnvironmentCapability.SECRETS_VAULT)

        if self._is_aws() or self._is_gcp() or self._is_azure():
            caps.add(EnvironmentCapability.SECRETS_CLOUD)

        # Display
        if os.environ.get("DISPLAY"):
            caps.add(EnvironmentCapability.DISPLAY_AVAILABLE)

        return caps

    def _can_read_filesystem(self) -> bool:
        """Check if we can read the filesystem."""
        try:
            os.listdir("/")
            return True
        except Exception:
            return False

    def _can_write_filesystem(self) -> bool:
        """Check if we can write to filesystem."""
        try:
            test_path = "/tmp/.agentskills_write_test"
            with open(test_path, "w") as f:
                f.write("test")
            os.remove(test_path)
            return True
        except Exception:
            return False

    def _has_network(self) -> bool:
        """Check if network is available."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except Exception:
            return False

    def _can_exec_subprocess(self) -> bool:
        """Check if we can execute subprocesses."""
        try:
            import subprocess
            subprocess.run(
                ["echo", "test"],
                capture_output=True,
                timeout=2,
            )
            return True
        except Exception:
            return False

    def _has_gpu(self) -> bool:
        """Check if GPU is available."""
        # Check NVIDIA
        if os.path.exists("/usr/bin/nvidia-smi"):
            return True

        # Check CUDA
        if os.environ.get("CUDA_VISIBLE_DEVICES"):
            return True

        return False

    def _detect_constraints(self, env_type: EnvironmentType) -> ExecutionConstraints:
        """Detect resource constraints."""
        constraints = ExecutionConstraints()

        # Set defaults based on environment type
        if env_type == EnvironmentType.CI:
            constraints.max_timeout_seconds = 600  # 10 min
            constraints.max_memory_mb = 4096

        elif env_type == EnvironmentType.CLOUD:
            # Check for Lambda-style constraints
            if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                timeout = int(os.environ.get("AWS_LAMBDA_FUNCTION_TIMEOUT", 300))
                memory = int(os.environ.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", 128))
                constraints.max_timeout_seconds = timeout
                constraints.max_memory_mb = memory

        elif env_type == EnvironmentType.DOCKER:
            # Could read cgroup limits here
            pass

        return constraints

    def _enrich_environment(self, env: ExecutionEnvironment) -> None:
        """Add type-specific details to environment."""
        if env.type == EnvironmentType.CODESPACE:
            env.codespace_name = os.environ.get("CODESPACE_NAME")
            env.github_token_available = bool(os.environ.get("GITHUB_TOKEN"))
            env.metadata["github_user"] = os.environ.get("GITHUB_USER")
            env.metadata["github_repository"] = os.environ.get("GITHUB_REPOSITORY")

        elif env.type == EnvironmentType.CLOUD:
            if self._is_aws():
                env.cloud_provider = "aws"
                env.cloud_region = os.environ.get("AWS_REGION")
            elif self._is_gcp():
                env.cloud_provider = "gcp"
                env.cloud_region = os.environ.get("GOOGLE_CLOUD_REGION")
            elif self._is_azure():
                env.cloud_provider = "azure"
                env.cloud_region = os.environ.get("AZURE_REGION")

        elif env.type == EnvironmentType.DOCKER:
            # Try to get container ID from cgroup
            try:
                with open("/proc/self/cgroup", "r") as f:
                    content = f.read()
                    for line in content.split("\n"):
                        if "docker" in line:
                            parts = line.split("/")
                            if parts:
                                env.container_id = parts[-1][:12]
                                break
            except Exception:
                pass

        elif env.type == EnvironmentType.CI:
            if os.environ.get("GITHUB_ACTIONS"):
                env.metadata["ci_provider"] = "github_actions"
                env.metadata["github_workflow"] = os.environ.get("GITHUB_WORKFLOW")
                env.metadata["github_run_id"] = os.environ.get("GITHUB_RUN_ID")
            elif os.environ.get("GITLAB_CI"):
                env.metadata["ci_provider"] = "gitlab_ci"
                env.metadata["gitlab_pipeline_id"] = os.environ.get("CI_PIPELINE_ID")

        # Add platform info
        env.metadata["platform"] = platform.system()
        env.metadata["platform_version"] = platform.version()
        env.metadata["python_version"] = platform.python_version()
