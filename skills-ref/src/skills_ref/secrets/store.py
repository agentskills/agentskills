"""
High-level secret store for skill access.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from .types import (
    SecretAccessAction,
    SecretAuditEntry,
    SecretBackend,
    SecretRef,
    SecureValue,
)
from .providers import SecretProvider


class SecretStore:
    """
    High-level API for skills to access secrets.

    Features:
    - Multi-provider support
    - Automatic audit logging
    - Secret validation
    - Typed getters
    """

    def __init__(
        self,
        providers: Dict[SecretBackend, SecretProvider],
        on_audit: Optional[Callable[[SecretAuditEntry], None]] = None,
        user_id: str = "system",
        workspace_id: Optional[str] = None,
    ):
        self.providers = providers
        self._on_audit = on_audit
        self.user_id = user_id
        self.workspace_id = workspace_id

    async def get(
        self,
        name: str,
        backend: SecretBackend = SecretBackend.ENV,
    ) -> str:
        """
        Get a secret value.

        Args:
            name: Secret name/path
            backend: Which backend to use

        Returns:
            Secret value as string

        Raises:
            ValueError: If secret not found
        """
        provider = self.providers.get(backend)
        if provider is None:
            raise ValueError(f"No provider configured for backend: {backend}")

        secret = await provider.get_secret(name)
        if secret is None:
            raise ValueError(f"Secret not found: {name}")

        return secret.value

    async def get_secure(
        self,
        ref: SecretRef,
    ) -> SecureValue:
        """
        Get a secret as SecureValue with metadata.

        Useful when you need access metadata or expiration info.
        """
        provider = self.providers.get(ref.vault)
        if provider is None:
            raise ValueError(f"No provider configured for backend: {ref.vault}")

        secret = await provider.get_secret(ref.path, ref.version, ref.key)
        if secret is None:
            raise ValueError(f"Secret not found: {ref.path}")

        return secret

    def get_ref(
        self,
        path: str,
        backend: SecretBackend = SecretBackend.ENV,
    ) -> SecretRef:
        """
        Get a secret reference without loading.

        Useful for passing secrets between skills without exposing values.
        """
        return SecretRef(vault=backend, path=path)

    async def validate(
        self,
        required_secrets: List[str],
        backend: SecretBackend = SecretBackend.ENV,
    ) -> Dict[str, bool]:
        """
        Validate that required secrets exist.

        Returns dict mapping secret name to exists boolean.
        """
        provider = self.providers.get(backend)
        if provider is None:
            return {name: False for name in required_secrets}

        result = {}
        for name in required_secrets:
            secret = await provider.get_secret(name)
            result[name] = secret is not None

        return result

    async def get_missing(
        self,
        required_secrets: List[str],
        backend: SecretBackend = SecretBackend.ENV,
    ) -> List[str]:
        """Get list of missing secrets."""
        validation = await self.validate(required_secrets, backend)
        return [name for name, exists in validation.items() if not exists]

    # Typed getters for common patterns
    async def get_api_key(
        self,
        name: str = "API_KEY",
        backend: SecretBackend = SecretBackend.ENV,
    ) -> str:
        """Get an API key."""
        return await self.get(name, backend)

    async def get_database_url(
        self,
        name: str = "DATABASE_URL",
        backend: SecretBackend = SecretBackend.ENV,
    ) -> str:
        """Get database connection URL."""
        return await self.get(name, backend)

    async def get_database_password(
        self,
        name: str = "DATABASE_PASSWORD",
        backend: SecretBackend = SecretBackend.ENV,
    ) -> str:
        """Get database password."""
        return await self.get(name, backend)

    async def get_jwt_secret(
        self,
        name: str = "JWT_SECRET",
        backend: SecretBackend = SecretBackend.ENV,
    ) -> str:
        """Get JWT signing secret."""
        return await self.get(name, backend)


class CachedSecretStore(SecretStore):
    """
    Secret store with caching.

    Reduces calls to secret backends for frequently accessed secrets.
    """

    def __init__(
        self,
        providers: Dict[SecretBackend, SecretProvider],
        cache_ttl_seconds: int = 300,  # 5 minutes
        on_audit: Optional[Callable[[SecretAuditEntry], None]] = None,
        user_id: str = "system",
        workspace_id: Optional[str] = None,
    ):
        super().__init__(providers, on_audit, user_id, workspace_id)
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cache: Dict[str, tuple[SecureValue, datetime]] = {}

    async def get_secure(self, ref: SecretRef) -> SecureValue:
        """Get secret with caching."""
        cache_key = f"{ref.vault.value}:{ref.path}:{ref.version}:{ref.key}"

        # Check cache
        if cache_key in self._cache:
            value, cached_at = self._cache[cache_key]
            if datetime.utcnow() - cached_at < self.cache_ttl:
                return value

        # Cache miss - fetch from provider
        value = await super().get_secure(ref)

        # Store in cache
        self._cache[cache_key] = (value, datetime.utcnow())

        return value

    def clear_cache(self) -> None:
        """Clear the secret cache."""
        self._cache.clear()

    def invalidate(self, path: str) -> None:
        """Invalidate a specific secret from cache."""
        keys_to_remove = [k for k in self._cache if f":{path}:" in k]
        for key in keys_to_remove:
            del self._cache[key]


class SecretStoreBuilder:
    """
    Builder for creating secret stores.

    Example:
        store = (SecretStoreBuilder()
            .with_env_provider()
            .with_aws_provider(region="us-east-1")
            .with_caching(ttl_seconds=300)
            .build())
    """

    def __init__(self):
        self._providers: Dict[SecretBackend, SecretProvider] = {}
        self._on_audit = None
        self._user_id = "system"
        self._workspace_id = None
        self._cache_ttl = None

    def with_env_provider(self, prefix: str = "") -> "SecretStoreBuilder":
        """Add environment variable provider."""
        from .providers import EnvSecretProvider
        self._providers[SecretBackend.ENV] = EnvSecretProvider(prefix, self._on_audit)
        return self

    def with_aws_provider(
        self,
        region: Optional[str] = None,
    ) -> "SecretStoreBuilder":
        """Add AWS Secrets Manager provider."""
        from .providers import AWSSecretsManagerProvider
        self._providers[SecretBackend.AWS_SECRETS_MANAGER] = AWSSecretsManagerProvider(
            region, self._on_audit
        )
        return self

    def with_vault_provider(
        self,
        addr: Optional[str] = None,
        token: Optional[str] = None,
    ) -> "SecretStoreBuilder":
        """Add HashiCorp Vault provider."""
        from .providers import HashicorpVaultProvider
        self._providers[SecretBackend.HASHICORP_VAULT] = HashicorpVaultProvider(
            addr, token, on_audit=self._on_audit
        )
        return self

    def with_audit(
        self,
        callback: Callable[[SecretAuditEntry], None],
    ) -> "SecretStoreBuilder":
        """Add audit logging callback."""
        self._on_audit = callback
        return self

    def with_user(
        self,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> "SecretStoreBuilder":
        """Set user context for audit."""
        self._user_id = user_id
        self._workspace_id = workspace_id
        return self

    def with_caching(self, ttl_seconds: int = 300) -> "SecretStoreBuilder":
        """Enable caching with TTL."""
        self._cache_ttl = ttl_seconds
        return self

    def build(self) -> SecretStore:
        """Build the secret store."""
        if self._cache_ttl:
            return CachedSecretStore(
                providers=self._providers,
                cache_ttl_seconds=self._cache_ttl,
                on_audit=self._on_audit,
                user_id=self._user_id,
                workspace_id=self._workspace_id,
            )
        else:
            return SecretStore(
                providers=self._providers,
                on_audit=self._on_audit,
                user_id=self._user_id,
                workspace_id=self._workspace_id,
            )
