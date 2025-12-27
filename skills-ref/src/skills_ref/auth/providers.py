"""
Authentication providers for JWT and API key authentication.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from .types import (
    APIKeyCredential,
    AuthEvent,
    AuthEventType,
    AuthMethod,
    AuthProvider,
    AuthResult,
    SkillAuthContext,
    TokenPair,
)


@dataclass
class JWTConfig:
    """Configuration for JWT authentication."""
    secret: str
    algorithm: str = "HS256"
    access_token_expiry_seconds: int = 3600  # 1 hour
    refresh_token_expiry_seconds: int = 604800  # 7 days
    issuer: Optional[str] = None
    audience: Optional[str] = None


class JWTAuthProvider(AuthProvider):
    """
    JWT-based authentication provider.

    Supports:
    - Token validation with expiration checking
    - Token refresh with rotation
    - Token revocation via blacklist
    - Configurable expiration and algorithms
    """

    def __init__(
        self,
        config: JWTConfig,
        revoked_tokens: Optional[set] = None,
        on_auth_event: Optional[Callable[[AuthEvent], None]] = None,
    ):
        self.config = config
        self._revoked_tokens: set = revoked_tokens or set()
        self._on_auth_event = on_auth_event

    @property
    def name(self) -> str:
        return "jwt"

    @property
    def auth_method(self) -> AuthMethod:
        return AuthMethod.JWT

    def can_handle(self, token: str) -> bool:
        """Check if token looks like a JWT (three base64 parts)."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False
            # Try to decode header
            header = self._decode_base64(parts[0])
            header_data = json.loads(header)
            return "alg" in header_data and "typ" in header_data
        except Exception:
            return False

    async def validate_token(self, token: str) -> AuthResult:
        """Validate JWT token and extract auth context."""
        try:
            # Check if revoked
            if token in self._revoked_tokens:
                self._emit_event(AuthEventType.TOKEN_INVALID, success=False,
                                error_message="Token has been revoked")
                return AuthResult.fail("TOKEN_REVOKED", "Token has been revoked")

            # Decode and verify
            payload = self._verify_and_decode(token)
            if payload is None:
                self._emit_event(AuthEventType.TOKEN_INVALID, success=False,
                                error_message="Invalid token signature")
                return AuthResult.fail("INVALID_SIGNATURE", "Invalid token signature")

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                self._emit_event(AuthEventType.TOKEN_EXPIRED, success=False,
                                user_id=payload.get("sub"),
                                error_message="Token has expired")
                return AuthResult.fail("TOKEN_EXPIRED", "Token has expired")

            # Check issuer
            if self.config.issuer and payload.get("iss") != self.config.issuer:
                return AuthResult.fail("INVALID_ISSUER", "Invalid token issuer")

            # Check audience
            if self.config.audience:
                aud = payload.get("aud")
                if isinstance(aud, list):
                    if self.config.audience not in aud:
                        return AuthResult.fail("INVALID_AUDIENCE", "Invalid token audience")
                elif aud != self.config.audience:
                    return AuthResult.fail("INVALID_AUDIENCE", "Invalid token audience")

            # Build auth context
            context = SkillAuthContext(
                user_id=payload.get("sub", ""),
                workspace_id=payload.get("workspace_id", ""),
                auth_method=AuthMethod.JWT,
                scopes=payload.get("scopes", []),
                roles=payload.get("roles", []),
                token_id=payload.get("jti"),
                token_expires_at=datetime.utcfromtimestamp(exp) if exp else None,
                metadata=payload.get("metadata", {}),
            )

            self._emit_event(
                AuthEventType.TOKEN_VALIDATED,
                success=True,
                user_id=context.user_id,
                workspace_id=context.workspace_id,
                token_id=context.token_id,
            )

            return AuthResult.ok(context)

        except Exception as e:
            self._emit_event(AuthEventType.AUTH_FAILED, success=False,
                            error_message=str(e))
            return AuthResult.fail("VALIDATION_ERROR", str(e))

    async def refresh_token(self, refresh_token: str) -> Optional[TokenPair]:
        """Refresh access token using refresh token."""
        try:
            payload = self._verify_and_decode(refresh_token)
            if payload is None:
                return None

            # Check if it's a refresh token
            if payload.get("token_type") != "refresh":
                return None

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                return None

            # Generate new token pair
            return self._generate_token_pair(
                user_id=payload.get("sub", ""),
                workspace_id=payload.get("workspace_id", ""),
                scopes=payload.get("scopes", []),
                roles=payload.get("roles", []),
                metadata=payload.get("metadata", {}),
            )
        except Exception:
            return None

    async def revoke_token(self, token: str) -> bool:
        """Add token to revocation list."""
        self._revoked_tokens.add(token)
        self._emit_event(AuthEventType.TOKEN_REVOKED, success=True)
        return True

    def generate_tokens(
        self,
        user_id: str,
        workspace_id: str,
        scopes: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TokenPair:
        """Generate a new access/refresh token pair."""
        return self._generate_token_pair(
            user_id=user_id,
            workspace_id=workspace_id,
            scopes=scopes or [],
            roles=roles or [],
            metadata=metadata or {},
        )

    def _generate_token_pair(
        self,
        user_id: str,
        workspace_id: str,
        scopes: List[str],
        roles: List[str],
        metadata: Dict[str, Any],
    ) -> TokenPair:
        """Generate access and refresh token pair."""
        now = datetime.utcnow()
        access_expires = now + timedelta(seconds=self.config.access_token_expiry_seconds)
        refresh_expires = now + timedelta(seconds=self.config.refresh_token_expiry_seconds)

        # Common claims
        base_claims = {
            "sub": user_id,
            "workspace_id": workspace_id,
            "scopes": scopes,
            "roles": roles,
            "metadata": metadata,
            "iat": int(now.timestamp()),
        }

        if self.config.issuer:
            base_claims["iss"] = self.config.issuer
        if self.config.audience:
            base_claims["aud"] = self.config.audience

        # Access token
        access_claims = {
            **base_claims,
            "jti": secrets.token_urlsafe(16),
            "exp": int(access_expires.timestamp()),
            "token_type": "access",
        }
        access_token = self._encode(access_claims)

        # Refresh token
        refresh_claims = {
            **base_claims,
            "jti": secrets.token_urlsafe(16),
            "exp": int(refresh_expires.timestamp()),
            "token_type": "refresh",
        }
        refresh_token = self._encode(refresh_claims)

        self._emit_event(
            AuthEventType.TOKEN_ISSUED,
            success=True,
            user_id=user_id,
            workspace_id=workspace_id,
            token_id=access_claims["jti"],
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires,
            refresh_expires_at=refresh_expires,
        )

    def _encode(self, payload: Dict[str, Any]) -> str:
        """Encode payload as JWT."""
        header = {"alg": self.config.algorithm, "typ": "JWT"}
        header_b64 = self._encode_base64(json.dumps(header))
        payload_b64 = self._encode_base64(json.dumps(payload))

        message = f"{header_b64}.{payload_b64}"
        signature = self._sign(message)
        signature_b64 = self._encode_base64(signature)

        return f"{message}.{signature_b64}"

    def _verify_and_decode(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify signature and decode JWT payload."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts
            message = f"{header_b64}.{payload_b64}"

            # Verify signature
            expected_signature = self._sign(message)
            actual_signature = self._decode_base64(signature_b64)

            if not hmac.compare_digest(expected_signature, actual_signature):
                return None

            # Decode payload
            payload = json.loads(self._decode_base64(payload_b64))
            return payload

        except Exception:
            return None

    def _sign(self, message: str) -> bytes:
        """Create HMAC signature."""
        return hmac.new(
            self.config.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()

    def _encode_base64(self, data: str | bytes) -> str:
        """Encode to URL-safe base64 without padding."""
        if isinstance(data, str):
            data = data.encode()
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    def _decode_base64(self, data: str) -> bytes:
        """Decode URL-safe base64 with padding restoration."""
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def _emit_event(
        self,
        event_type: AuthEventType,
        success: bool,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        token_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Emit an auth event for logging."""
        if self._on_auth_event:
            event = AuthEvent(
                event_type=event_type,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                workspace_id=workspace_id,
                auth_method=AuthMethod.JWT,
                success=success,
                token_id=token_id,
                error_message=error_message,
            )
            self._on_auth_event(event)


@dataclass
class APIKeyConfig:
    """Configuration for API key authentication."""
    hash_algorithm: str = "sha256"


class APIKeyAuthProvider(AuthProvider):
    """
    API key-based authentication provider.

    Supports:
    - HMAC-SHA256 key verification
    - Key rotation tracking
    - Usage auditing
    - Automatic expiration
    """

    def __init__(
        self,
        config: Optional[APIKeyConfig] = None,
        key_store: Optional[Dict[str, APIKeyCredential]] = None,
        on_auth_event: Optional[Callable[[AuthEvent], None]] = None,
    ):
        self.config = config or APIKeyConfig()
        self._key_store: Dict[str, APIKeyCredential] = key_store or {}
        self._on_auth_event = on_auth_event

    @property
    def name(self) -> str:
        return "api_key"

    @property
    def auth_method(self) -> AuthMethod:
        return AuthMethod.API_KEY

    def can_handle(self, token: str) -> bool:
        """Check if token looks like an API key (key:secret format or just key)."""
        # API keys typically don't have JWT structure
        if "." in token and token.count(".") == 2:
            return False  # Likely JWT
        return True

    async def validate_token(self, token: str) -> AuthResult:
        """Validate API key and return auth context."""
        try:
            # Parse key:secret format
            if ":" in token:
                api_key, api_secret = token.split(":", 1)
            else:
                api_key = token
                api_secret = ""

            # Look up key
            credential = self._key_store.get(api_key)
            if credential is None:
                self._emit_event(AuthEventType.AUTH_FAILED, success=False,
                                error_message="API key not found")
                return AuthResult.fail("KEY_NOT_FOUND", "API key not found")

            # Check if valid
            if not credential.is_valid:
                if credential.revoked_at:
                    return AuthResult.fail("KEY_REVOKED", "API key has been revoked")
                if credential.is_expired:
                    return AuthResult.fail("KEY_EXPIRED", "API key has expired")
                return AuthResult.fail("KEY_INACTIVE", "API key is inactive")

            # Verify secret (if provided)
            if api_secret:
                secret_hash = self._hash_secret(api_secret)
                if not hmac.compare_digest(secret_hash, credential.api_secret_hash):
                    self._emit_event(AuthEventType.AUTH_FAILED, success=False,
                                    api_key_id=api_key,
                                    error_message="Invalid API secret")
                    return AuthResult.fail("INVALID_SECRET", "Invalid API secret")

            # Update last used
            credential.last_used_at = datetime.utcnow()

            # Build auth context
            context = SkillAuthContext(
                user_id=credential.user_id,
                workspace_id=credential.workspace_id,
                auth_method=AuthMethod.API_KEY,
                scopes=credential.scopes,
                token_id=credential.api_key_id,
                token_expires_at=credential.expires_at,
            )

            self._emit_event(
                AuthEventType.API_KEY_VALIDATED,
                success=True,
                user_id=credential.user_id,
                workspace_id=credential.workspace_id,
                api_key_id=credential.api_key_id,
            )

            return AuthResult.ok(context)

        except Exception as e:
            self._emit_event(AuthEventType.AUTH_FAILED, success=False,
                            error_message=str(e))
            return AuthResult.fail("VALIDATION_ERROR", str(e))

    async def refresh_token(self, refresh_token: str) -> Optional[TokenPair]:
        """API keys don't support refresh. Returns None."""
        return None

    async def revoke_token(self, token: str) -> bool:
        """Revoke an API key."""
        # Parse key from token
        api_key = token.split(":")[0] if ":" in token else token

        credential = self._key_store.get(api_key)
        if credential is None:
            return False

        credential.is_active = False
        credential.revoked_at = datetime.utcnow()

        self._emit_event(
            AuthEventType.API_KEY_REVOKED,
            success=True,
            user_id=credential.user_id,
            workspace_id=credential.workspace_id,
            api_key_id=credential.api_key_id,
        )

        return True

    def create_api_key(
        self,
        user_id: str,
        workspace_id: str,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> tuple[str, str, APIKeyCredential]:
        """
        Create a new API key.

        Returns (api_key, api_secret, credential).
        The api_secret is only returned once and should be stored securely.
        """
        api_key = f"sk_{secrets.token_urlsafe(24)}"
        api_secret = secrets.token_urlsafe(32)

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        credential = APIKeyCredential(
            api_key_id=api_key,
            api_key_hash=self._hash_secret(api_key),
            api_secret_hash=self._hash_secret(api_secret),
            user_id=user_id,
            workspace_id=workspace_id,
            scopes=scopes or [],
            expires_at=expires_at,
        )

        self._key_store[api_key] = credential

        self._emit_event(
            AuthEventType.API_KEY_CREATED,
            success=True,
            user_id=user_id,
            workspace_id=workspace_id,
            api_key_id=api_key,
        )

        return api_key, api_secret, credential

    def rotate_api_key(self, api_key: str) -> Optional[tuple[str, str, APIKeyCredential]]:
        """
        Rotate an API key.

        Creates a new key with same permissions and revokes the old one.
        Returns (new_api_key, new_api_secret, new_credential) or None.
        """
        old_credential = self._key_store.get(api_key)
        if old_credential is None:
            return None

        # Create new key with same permissions
        new_key, new_secret, new_credential = self.create_api_key(
            user_id=old_credential.user_id,
            workspace_id=old_credential.workspace_id,
            scopes=old_credential.scopes,
        )

        # Revoke old key
        old_credential.is_active = False
        old_credential.revoked_at = datetime.utcnow()
        old_credential.revoked_reason = "Rotated"

        self._emit_event(
            AuthEventType.API_KEY_ROTATED,
            success=True,
            user_id=old_credential.user_id,
            workspace_id=old_credential.workspace_id,
            api_key_id=api_key,
            metadata={"new_key_id": new_key},
        )

        return new_key, new_secret, new_credential

    def _hash_secret(self, secret: str) -> str:
        """Hash a secret using configured algorithm."""
        return hashlib.sha256(secret.encode()).hexdigest()

    def _emit_event(
        self,
        event_type: AuthEventType,
        success: bool,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit an auth event for logging."""
        if self._on_auth_event:
            event = AuthEvent(
                event_type=event_type,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                workspace_id=workspace_id,
                auth_method=AuthMethod.API_KEY,
                success=success,
                api_key_id=api_key_id,
                error_message=error_message,
                metadata=metadata or {},
            )
            self._on_auth_event(event)
