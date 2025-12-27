"""
Core types for the authentication layer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AuthMethod(Enum):
    """Authentication method used."""
    JWT = "jwt"
    API_KEY = "api_key"
    SERVICE_ACCOUNT = "service_account"
    OAUTH = "oauth"


@dataclass
class SkillAuthContext:
    """
    Authentication context for skill execution.

    Contains user identity, permissions, and metadata needed
    for authorization decisions during skill execution.
    """
    user_id: str
    workspace_id: str
    auth_method: AuthMethod
    scopes: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)

    # Token information
    token_id: Optional[str] = None
    token_expires_at: Optional[datetime] = None

    # Audit metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    # Additional claims/metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if self.token_expires_at is None:
            return False
        return datetime.utcnow() > self.token_expires_at

    def has_scope(self, scope: str) -> bool:
        """Check if context has a specific scope."""
        return scope in self.scopes

    def has_role(self, role: str) -> bool:
        """Check if context has a specific role."""
        return role in self.roles

    def has_any_role(self, roles: List[str]) -> bool:
        """Check if context has any of the specified roles."""
        return any(role in self.roles for role in roles)

    def to_audit_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for audit logging."""
        return {
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "auth_method": self.auth_method.value,
            "scopes": self.scopes,
            "roles": self.roles,
            "token_id": self.token_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
        }


@dataclass
class TokenPair:
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime
    token_type: str = "Bearer"


@dataclass
class APIKeyCredential:
    """API key credential with metadata."""
    api_key_id: str
    api_key_hash: str  # Never store plaintext
    api_secret_hash: str

    # Ownership
    user_id: str
    workspace_id: str

    # Permissions
    scopes: List[str] = field(default_factory=list)

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    # Rotation
    rotation_required: bool = False
    rotation_deadline: Optional[datetime] = None

    # Status
    is_active: bool = True
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """Check if the API key has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the API key is valid for use."""
        return self.is_active and not self.is_expired and self.revoked_at is None


class AuthEventType(Enum):
    """Types of authentication events for audit logging."""
    TOKEN_ISSUED = "token_issued"
    TOKEN_VALIDATED = "token_validated"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"
    API_KEY_CREATED = "api_key_created"
    API_KEY_VALIDATED = "api_key_validated"
    API_KEY_ROTATED = "api_key_rotated"
    API_KEY_REVOKED = "api_key_revoked"
    AUTH_FAILED = "auth_failed"


@dataclass
class AuthEvent:
    """Authentication event for audit logging."""
    event_type: AuthEventType
    timestamp: datetime
    user_id: Optional[str]
    workspace_id: Optional[str]
    auth_method: AuthMethod
    success: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    token_id: Optional[str] = None
    api_key_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "auth_method": self.auth_method.value,
            "success": self.success,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "token_id": self.token_id,
            "api_key_id": self.api_key_id,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class AuthResult:
    """Result of an authentication attempt."""
    success: bool
    context: Optional[SkillAuthContext] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def ok(cls, context: SkillAuthContext) -> "AuthResult":
        """Create a successful auth result."""
        return cls(success=True, context=context)

    @classmethod
    def fail(cls, code: str, message: str) -> "AuthResult":
        """Create a failed auth result."""
        return cls(success=False, error_code=code, error_message=message)


class AuthProvider(ABC):
    """
    Abstract base class for authentication providers.

    Implement this class to add new authentication methods
    (e.g., OAuth, SAML, custom tokens).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for identification."""
        pass

    @property
    @abstractmethod
    def auth_method(self) -> AuthMethod:
        """The authentication method this provider handles."""
        pass

    @abstractmethod
    def can_handle(self, token: str) -> bool:
        """
        Check if this provider can handle the given token.

        Used for auto-detection of auth type.
        """
        pass

    @abstractmethod
    async def validate_token(self, token: str) -> AuthResult:
        """
        Validate a token and return auth context.

        Returns AuthResult with context on success, error on failure.
        """
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[TokenPair]:
        """
        Refresh an access token using a refresh token.

        Returns new token pair or None if refresh fails.
        """
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token.

        Returns True if revocation successful.
        """
        pass
