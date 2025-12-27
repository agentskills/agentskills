"""
Core types for secrets management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SecretBackend(Enum):
    """Supported secret backends."""
    ENV = "env"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    HASHICORP_VAULT = "hashicorp_vault"
    AZURE_KEYVAULT = "azure_keyvault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"


class SecretRotationPolicy(Enum):
    """Secret rotation policies."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"


@dataclass
class SecretRef:
    """
    Reference to a secret without loading it.

    Used to pass secrets around without exposing values.
    The actual value is only loaded when needed.
    """
    vault: SecretBackend
    path: str
    version: Optional[str] = None
    key: Optional[str] = None  # For secrets with multiple keys

    # Rotation policy
    rotation_policy: SecretRotationPolicy = SecretRotationPolicy.NONE
    rotation_deadline: Optional[datetime] = None

    def __str__(self) -> str:
        return f"SecretRef({self.vault.value}:{self.path})"

    def __repr__(self) -> str:
        return f"SecretRef(vault={self.vault.value}, path={self.path}, version={self.version})"

    @classmethod
    def from_env(cls, name: str) -> "SecretRef":
        """Create reference to environment variable."""
        return cls(vault=SecretBackend.ENV, path=name)

    @classmethod
    def from_aws(cls, secret_id: str, version: Optional[str] = None) -> "SecretRef":
        """Create reference to AWS Secrets Manager secret."""
        return cls(vault=SecretBackend.AWS_SECRETS_MANAGER, path=secret_id, version=version)

    @classmethod
    def from_vault(cls, path: str, key: Optional[str] = None) -> "SecretRef":
        """Create reference to HashiCorp Vault secret."""
        return cls(vault=SecretBackend.HASHICORP_VAULT, path=path, key=key)


@dataclass
class SecureValue:
    """
    A secret value with metadata.

    The value is stored but should never be logged or serialized.
    Use `masked` property for safe display.
    """
    ref: SecretRef
    value: str  # The actual secret value

    # Metadata
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    accessed_at: datetime = field(default_factory=datetime.utcnow)

    # Audit trail
    access_log: List[str] = field(default_factory=list)

    @property
    def masked(self) -> str:
        """Get masked version safe for logging."""
        if not self.value:
            return "***EMPTY***"
        if len(self.value) <= 4:
            return "****"
        return f"{self.value[:2]}***{self.value[-2:]}"

    @property
    def is_expired(self) -> bool:
        """Check if secret has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def __str__(self) -> str:
        """Never expose value in string representation."""
        return f"SecureValue(ref={self.ref}, masked={self.masked})"

    def __repr__(self) -> str:
        """Never expose value in repr."""
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict WITHOUT the actual value."""
        return {
            "ref": str(self.ref),
            "masked": self.masked,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accessed_at": self.accessed_at.isoformat(),
            "is_expired": self.is_expired,
        }


class SecretAccessAction(Enum):
    """Types of secret access for audit logging."""
    READ = "read"
    ROTATE = "rotate"
    CREATE = "create"
    DELETE = "delete"
    REVOKE = "revoke"


@dataclass
class SecretAuditEntry:
    """Audit log entry for secret access."""
    timestamp: datetime
    action: SecretAccessAction
    secret_path: str
    secret_backend: SecretBackend

    # Who accessed
    user_id: str
    workspace_id: Optional[str] = None

    # Context
    skill_name: Optional[str] = None
    skill_execution_id: Optional[str] = None

    # Result
    success: bool = True
    error_message: Optional[str] = None

    # Request context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/logging."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "secret_path": self.secret_path,
            "secret_backend": self.secret_backend.value,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "skill_name": self.skill_name,
            "skill_execution_id": self.skill_execution_id,
            "success": self.success,
            "error_message": self.error_message,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }


# Common secret patterns for validation
SECRET_PATTERNS = {
    "api_key": r"^(sk|pk|api)[-_][a-zA-Z0-9]{20,}$",
    "jwt": r"^eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+$",
    "aws_access_key": r"^AKIA[0-9A-Z]{16}$",
    "aws_secret_key": r"^[a-zA-Z0-9/+=]{40}$",
    "password": r".{8,}",  # At least 8 characters
}
