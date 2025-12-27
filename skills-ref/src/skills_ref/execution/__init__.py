"""
Execution Environment Abstraction for AgentSkills Enterprise.

This module provides:
- Environment detection (local, Codespaces, cloud, Docker)
- Environment-aware credential loading
- Capability detection
- Execution context management
"""

from .types import (
    ExecutionEnvironment,
    EnvironmentType,
    EnvironmentCapability,
    SkillRequirements,
    ExecutionContext,
    ExecutionConstraints,
)
from .detector import EnvironmentDetector
from .manager import EnvironmentManager, ExecutionContextBuilder

__all__ = [
    # Types
    "ExecutionEnvironment",
    "EnvironmentType",
    "EnvironmentCapability",
    "SkillRequirements",
    "ExecutionContext",
    "ExecutionConstraints",
    # Detector
    "EnvironmentDetector",
    # Manager
    "EnvironmentManager",
    "ExecutionContextBuilder",
]
