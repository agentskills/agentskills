"""
Authentication & Authorization Layer for AgentSkills Enterprise.

This module provides:
- JWT token validation and refresh
- API key authentication
- Multi-provider authentication management
- Audit logging for auth events
"""

from .types import (
    SkillAuthContext,
    AuthProvider,
    APIKeyCredential,
    TokenPair,
    AuthEvent,
    AuthResult,
)
from .providers import JWTAuthProvider, APIKeyAuthProvider
from .manager import AuthManager

__all__ = [
    # Types
    "SkillAuthContext",
    "AuthProvider",
    "APIKeyCredential",
    "TokenPair",
    "AuthEvent",
    "AuthResult",
    # Providers
    "JWTAuthProvider",
    "APIKeyAuthProvider",
    # Manager
    "AuthManager",
]
