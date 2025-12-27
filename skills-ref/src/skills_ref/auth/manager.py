"""
Authentication Manager - Orchestrates multiple auth providers.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .types import (
    AuthEvent,
    AuthEventType,
    AuthMethod,
    AuthProvider,
    AuthResult,
    SkillAuthContext,
    TokenPair,
)


class AuthManager:
    """
    Orchestrates authentication across multiple providers.

    Features:
    - Auto-detects auth type from token format
    - Supports multiple auth providers simultaneously
    - Handles token lifecycle (validate, refresh, revoke)
    - Emits events for audit logging
    """

    def __init__(
        self,
        providers: List[AuthProvider],
        on_auth_event: Optional[Callable[[AuthEvent], None]] = None,
    ):
        """
        Initialize with list of auth providers.

        Providers are checked in order for token handling.
        """
        self.providers: Dict[str, AuthProvider] = {p.name: p for p in providers}
        self._provider_list = providers
        self._on_auth_event = on_auth_event

    async def authenticate(
        self,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthResult:
        """
        Authenticate a token using the appropriate provider.

        Auto-detects the provider from token format.
        Enriches the auth context with request metadata.
        """
        # Find provider that can handle this token
        provider = self._find_provider(token)
        if provider is None:
            return AuthResult.fail(
                "NO_PROVIDER",
                "No authentication provider found for this token type"
            )

        # Validate with provider
        result = await provider.validate_token(token)

        # Enrich context with request metadata
        if result.success and result.context:
            result.context.ip_address = ip_address
            result.context.user_agent = user_agent

        return result

    async def refresh(self, refresh_token: str) -> Optional[TokenPair]:
        """
        Refresh an access token.

        Tries each provider until one succeeds.
        """
        for provider in self._provider_list:
            if provider.can_handle(refresh_token):
                result = await provider.refresh_token(refresh_token)
                if result:
                    return result
        return None

    async def revoke(self, token: str) -> bool:
        """
        Revoke a token.

        Tries each provider until one succeeds.
        """
        for provider in self._provider_list:
            if provider.can_handle(token):
                success = await provider.revoke_token(token)
                if success:
                    return True
        return False

    def get_provider(self, name: str) -> Optional[AuthProvider]:
        """Get a specific provider by name."""
        return self.providers.get(name)

    def add_provider(self, provider: AuthProvider) -> None:
        """Add a new auth provider."""
        self.providers[provider.name] = provider
        self._provider_list.append(provider)

    def remove_provider(self, name: str) -> Optional[AuthProvider]:
        """Remove a provider by name."""
        provider = self.providers.pop(name, None)
        if provider:
            self._provider_list = [p for p in self._provider_list if p.name != name]
        return provider

    def _find_provider(self, token: str) -> Optional[AuthProvider]:
        """Find a provider that can handle this token."""
        for provider in self._provider_list:
            if provider.can_handle(token):
                return provider
        return None


class AuthMiddleware:
    """
    Middleware for authenticating skill execution requests.

    Use this to wrap skill execution with authentication checks.
    """

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager

    async def authenticate_request(
        self,
        authorization_header: Optional[str] = None,
        api_key_header: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthResult:
        """
        Authenticate an incoming request.

        Checks Authorization header first, then API key header.
        """
        # Try Authorization header (Bearer token)
        if authorization_header:
            token = self._extract_bearer_token(authorization_header)
            if token:
                return await self.auth_manager.authenticate(
                    token, ip_address, user_agent
                )

        # Try API key header
        if api_key_header:
            return await self.auth_manager.authenticate(
                api_key_header, ip_address, user_agent
            )

        return AuthResult.fail("NO_CREDENTIALS", "No authentication credentials provided")

    def _extract_bearer_token(self, header: str) -> Optional[str]:
        """Extract token from Bearer header."""
        if header.lower().startswith("bearer "):
            return header[7:].strip()
        return None


def require_auth(
    auth_manager: AuthManager,
    required_scopes: Optional[List[str]] = None,
    required_roles: Optional[List[str]] = None,
):
    """
    Decorator for requiring authentication on skill execution.

    Usage:
        @require_auth(auth_manager, required_scopes=["skill:execute"])
        async def execute_skill(context: SkillAuthContext, skill: SkillDefinition):
            ...
    """
    def decorator(func):
        async def wrapper(token: str, *args, **kwargs):
            # Authenticate
            result = await auth_manager.authenticate(token)
            if not result.success:
                raise PermissionError(f"Authentication failed: {result.error_message}")

            context = result.context

            # Check scopes
            if required_scopes:
                for scope in required_scopes:
                    if not context.has_scope(scope):
                        raise PermissionError(f"Missing required scope: {scope}")

            # Check roles
            if required_roles:
                if not context.has_any_role(required_roles):
                    raise PermissionError(f"Missing required role: {required_roles}")

            # Call function with auth context
            return await func(context, *args, **kwargs)

        return wrapper
    return decorator
