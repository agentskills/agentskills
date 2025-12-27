"""
Secrets Management for AgentSkills Enterprise.

This module provides:
- Secret abstraction layer
- Multiple backend support (env, AWS, Vault)
- Automatic masking in logs
- Audit logging for secret access
"""

from .types import (
    SecretRef,
    SecureValue,
    SecretAuditEntry,
    SecretBackend,
    SecretRotationPolicy,
)
from .providers import (
    SecretProvider,
    EnvSecretProvider,
    AWSSecretsManagerProvider,
    HashicorpVaultProvider,
)
from .store import SecretStore, CachedSecretStore
from .masking import SecretMasker, mask_secrets

__all__ = [
    # Types
    "SecretRef",
    "SecureValue",
    "SecretAuditEntry",
    "SecretBackend",
    "SecretRotationPolicy",
    # Providers
    "SecretProvider",
    "EnvSecretProvider",
    "AWSSecretsManagerProvider",
    "HashicorpVaultProvider",
    # Store
    "SecretStore",
    "CachedSecretStore",
    # Masking
    "SecretMasker",
    "mask_secrets",
]
