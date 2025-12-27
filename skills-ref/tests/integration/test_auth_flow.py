"""
Integration tests for authentication flow.
"""

import asyncio
import pytest
from datetime import datetime, timedelta

from skills_ref.auth import (
    AuthManager,
    AuthMiddleware,
    JWTAuthProvider,
    APIKeyAuthProvider,
    SkillAuthContext,
    TokenPair,
    require_auth,
)


class TestJWTAuthFlow:
    """Test JWT authentication end-to-end."""

    @pytest.fixture
    def jwt_provider(self):
        return JWTAuthProvider(
            secret_key="test-secret-key-for-testing",
            issuer="test-issuer",
            access_token_ttl=3600,
            refresh_token_ttl=86400,
        )

    @pytest.fixture
    def auth_manager(self, jwt_provider):
        return AuthManager([jwt_provider])

    @pytest.mark.asyncio
    async def test_full_jwt_lifecycle(self, jwt_provider):
        """Test complete JWT lifecycle: create, validate, refresh, revoke."""
        # Create tokens
        tokens = await jwt_provider.create_tokens(
            user_id="user-123",
            scopes=["skill:execute", "skill:read"],
            roles=["developer"],
            metadata={"org_id": "org-456"},
        )

        assert tokens.access_token
        assert tokens.refresh_token

        # Validate access token
        result = await jwt_provider.validate_token(tokens.access_token)
        assert result.success
        assert result.context.user_id == "user-123"
        assert "skill:execute" in result.context.scopes
        assert "developer" in result.context.roles

        # Refresh token
        new_tokens = await jwt_provider.refresh_token(tokens.refresh_token)
        assert new_tokens is not None
        assert new_tokens.access_token != tokens.access_token

        # Validate new token
        result = await jwt_provider.validate_token(new_tokens.access_token)
        assert result.success
        assert result.context.user_id == "user-123"

        # Revoke token
        revoked = await jwt_provider.revoke_token(tokens.access_token)
        assert revoked

    @pytest.mark.asyncio
    async def test_expired_token_handling(self, jwt_provider):
        """Test handling of expired tokens."""
        # Create provider with very short TTL
        short_provider = JWTAuthProvider(
            secret_key="test-secret",
            issuer="test",
            access_token_ttl=1,  # 1 second
        )

        tokens = await short_provider.create_tokens(
            user_id="user-123",
            scopes=["skill:read"],
        )

        # Wait for expiration
        await asyncio.sleep(2)

        # Should fail validation
        result = await short_provider.validate_token(tokens.access_token)
        assert not result.success
        assert result.error_code == "TOKEN_EXPIRED"

    @pytest.mark.asyncio
    async def test_invalid_token_handling(self, jwt_provider):
        """Test handling of invalid tokens."""
        result = await jwt_provider.validate_token("invalid-token")
        assert not result.success
        assert result.error_code == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_auth_manager_provider_selection(self, auth_manager, jwt_provider):
        """Test AuthManager selects correct provider."""
        tokens = await jwt_provider.create_tokens(
            user_id="user-123",
            scopes=["skill:read"],
        )

        # Manager should route to JWT provider
        result = await auth_manager.authenticate(tokens.access_token)
        assert result.success
        assert result.context.user_id == "user-123"


class TestAPIKeyAuthFlow:
    """Test API key authentication end-to-end."""

    @pytest.fixture
    def api_key_provider(self):
        return APIKeyAuthProvider()

    @pytest.fixture
    def auth_manager(self, api_key_provider):
        return AuthManager([api_key_provider])

    @pytest.mark.asyncio
    async def test_api_key_lifecycle(self, api_key_provider):
        """Test complete API key lifecycle."""
        # Register key
        credential = await api_key_provider.register_key(
            key="sk_test_abc123xyz",
            user_id="user-456",
            scopes=["skill:execute"],
            metadata={"environment": "test"},
        )

        assert credential.key_id
        assert credential.user_id == "user-456"

        # Validate key
        result = await api_key_provider.validate_token("sk_test_abc123xyz")
        assert result.success
        assert result.context.user_id == "user-456"
        assert "skill:execute" in result.context.scopes

        # Rotate key
        new_key, new_credential = await api_key_provider.rotate_key(credential.key_id)
        assert new_key != "sk_test_abc123xyz"
        assert new_credential.key_id == credential.key_id

        # Old key should fail
        result = await api_key_provider.validate_token("sk_test_abc123xyz")
        assert not result.success

        # New key should work
        result = await api_key_provider.validate_token(new_key)
        assert result.success

        # Revoke key
        revoked = await api_key_provider.revoke_token(new_key)
        assert revoked

        # Should no longer work
        result = await api_key_provider.validate_token(new_key)
        assert not result.success


class TestAuthMiddleware:
    """Test authentication middleware."""

    @pytest.fixture
    def jwt_provider(self):
        return JWTAuthProvider(
            secret_key="test-secret",
            issuer="test",
        )

    @pytest.fixture
    def api_key_provider(self):
        return APIKeyAuthProvider()

    @pytest.fixture
    def auth_manager(self, jwt_provider, api_key_provider):
        return AuthManager([jwt_provider, api_key_provider])

    @pytest.fixture
    def middleware(self, auth_manager):
        return AuthMiddleware(auth_manager)

    @pytest.mark.asyncio
    async def test_bearer_token_auth(self, middleware, jwt_provider):
        """Test Bearer token authentication."""
        tokens = await jwt_provider.create_tokens(
            user_id="user-123",
            scopes=["skill:read"],
        )

        result = await middleware.authenticate_request(
            authorization_header=f"Bearer {tokens.access_token}",
            ip_address="192.168.1.1",
            user_agent="TestClient/1.0",
        )

        assert result.success
        assert result.context.user_id == "user-123"
        assert result.context.ip_address == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_api_key_header_auth(self, middleware, api_key_provider):
        """Test API key header authentication."""
        await api_key_provider.register_key(
            key="sk_test_xyz789",
            user_id="user-789",
            scopes=["skill:execute"],
        )

        result = await middleware.authenticate_request(
            api_key_header="sk_test_xyz789",
            ip_address="10.0.0.1",
        )

        assert result.success
        assert result.context.user_id == "user-789"

    @pytest.mark.asyncio
    async def test_no_credentials(self, middleware):
        """Test request with no credentials."""
        result = await middleware.authenticate_request()

        assert not result.success
        assert result.error_code == "NO_CREDENTIALS"


class TestRequireAuthDecorator:
    """Test require_auth decorator."""

    @pytest.fixture
    def jwt_provider(self):
        return JWTAuthProvider(
            secret_key="test-secret",
            issuer="test",
        )

    @pytest.fixture
    def auth_manager(self, jwt_provider):
        return AuthManager([jwt_provider])

    @pytest.mark.asyncio
    async def test_decorator_with_valid_token(self, auth_manager, jwt_provider):
        """Test decorator allows valid tokens."""
        tokens = await jwt_provider.create_tokens(
            user_id="user-123",
            scopes=["skill:execute", "skill:read"],
            roles=["developer"],
        )

        @require_auth(auth_manager, required_scopes=["skill:execute"])
        async def protected_function(context: SkillAuthContext, data: str):
            return f"Hello {context.user_id}: {data}"

        result = await protected_function(tokens.access_token, "test data")
        assert result == "Hello user-123: test data"

    @pytest.mark.asyncio
    async def test_decorator_with_missing_scope(self, auth_manager, jwt_provider):
        """Test decorator rejects missing scopes."""
        tokens = await jwt_provider.create_tokens(
            user_id="user-123",
            scopes=["skill:read"],  # Missing skill:execute
        )

        @require_auth(auth_manager, required_scopes=["skill:execute"])
        async def protected_function(context: SkillAuthContext):
            return "success"

        with pytest.raises(PermissionError) as exc_info:
            await protected_function(tokens.access_token)

        assert "Missing required scope" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_decorator_with_missing_role(self, auth_manager, jwt_provider):
        """Test decorator rejects missing roles."""
        tokens = await jwt_provider.create_tokens(
            user_id="user-123",
            roles=["viewer"],  # Not admin
        )

        @require_auth(auth_manager, required_roles=["admin"])
        async def admin_function(context: SkillAuthContext):
            return "admin action"

        with pytest.raises(PermissionError) as exc_info:
            await admin_function(tokens.access_token)

        assert "Missing required role" in str(exc_info.value)


class TestMultiProviderAuth:
    """Test authentication with multiple providers."""

    @pytest.mark.asyncio
    async def test_fallback_between_providers(self):
        """Test AuthManager tries providers in order."""
        jwt_provider = JWTAuthProvider(
            secret_key="jwt-secret",
            issuer="test",
        )
        api_key_provider = APIKeyAuthProvider()

        auth_manager = AuthManager([jwt_provider, api_key_provider])

        # Create JWT token
        jwt_tokens = await jwt_provider.create_tokens(
            user_id="jwt-user",
            scopes=["skill:read"],
        )

        # Register API key
        await api_key_provider.register_key(
            key="sk_api_key",
            user_id="api-user",
            scopes=["skill:execute"],
        )

        # JWT should work
        result = await auth_manager.authenticate(jwt_tokens.access_token)
        assert result.success
        assert result.context.user_id == "jwt-user"

        # API key should work
        result = await auth_manager.authenticate("sk_api_key")
        assert result.success
        assert result.context.user_id == "api-user"

        # Unknown token should fail
        result = await auth_manager.authenticate("unknown-token")
        assert not result.success
