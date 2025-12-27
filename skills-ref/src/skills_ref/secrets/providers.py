"""
Secret providers for different backends.
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .types import (
    SecretAccessAction,
    SecretAuditEntry,
    SecretBackend,
    SecretRef,
    SecureValue,
)


class SecretProvider(ABC):
    """
    Abstract base class for secret providers.

    Implement this to add new secret backends.
    """

    @property
    @abstractmethod
    def backend(self) -> SecretBackend:
        """The backend type this provider handles."""
        pass

    @abstractmethod
    async def get_secret(
        self,
        path: str,
        version: Optional[str] = None,
        key: Optional[str] = None,
    ) -> Optional[SecureValue]:
        """
        Retrieve a secret by path.

        Args:
            path: Secret path/name
            version: Optional version identifier
            key: Optional key for multi-value secrets

        Returns:
            SecureValue or None if not found
        """
        pass

    @abstractmethod
    async def get_secret_batch(
        self,
        paths: List[str],
    ) -> Dict[str, Optional[SecureValue]]:
        """
        Retrieve multiple secrets at once.

        Returns dict mapping path to SecureValue (or None if not found).
        """
        pass

    async def rotate_secret(
        self,
        path: str,
        new_value: str,
    ) -> bool:
        """
        Rotate a secret to a new value.

        Default implementation returns False (not supported).
        """
        return False

    async def delete_secret(self, path: str) -> bool:
        """
        Delete a secret.

        Default implementation returns False (not supported).
        """
        return False


class EnvSecretProvider(SecretProvider):
    """
    Secret provider using environment variables.

    Simple but suitable for local development and Docker.
    """

    def __init__(
        self,
        prefix: str = "",
        on_audit: Optional[Callable[[SecretAuditEntry], None]] = None,
    ):
        """
        Initialize with optional prefix.

        Args:
            prefix: Prefix for env var names (e.g., "SKILL_" -> "SKILL_API_KEY")
            on_audit: Callback for audit logging
        """
        self.prefix = prefix
        self._on_audit = on_audit

    @property
    def backend(self) -> SecretBackend:
        return SecretBackend.ENV

    async def get_secret(
        self,
        path: str,
        version: Optional[str] = None,
        key: Optional[str] = None,
    ) -> Optional[SecureValue]:
        """Get secret from environment variable."""
        env_name = f"{self.prefix}{path}".upper()
        value = os.environ.get(env_name)

        if value is None:
            self._log_access(path, success=False, error="Secret not found")
            return None

        ref = SecretRef(vault=SecretBackend.ENV, path=path)
        secure_value = SecureValue(ref=ref, value=value)

        self._log_access(path, success=True)
        return secure_value

    async def get_secret_batch(
        self,
        paths: List[str],
    ) -> Dict[str, Optional[SecureValue]]:
        """Get multiple secrets from environment."""
        result = {}
        for path in paths:
            result[path] = await self.get_secret(path)
        return result

    def _log_access(
        self,
        path: str,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Log secret access for audit."""
        if self._on_audit:
            entry = SecretAuditEntry(
                timestamp=datetime.utcnow(),
                action=SecretAccessAction.READ,
                secret_path=path,
                secret_backend=SecretBackend.ENV,
                user_id="system",  # Env access is typically system-level
                success=success,
                error_message=error,
            )
            self._on_audit(entry)


class AWSSecretsManagerProvider(SecretProvider):
    """
    Secret provider using AWS Secrets Manager.

    Requires boto3 and AWS credentials.
    """

    def __init__(
        self,
        region_name: Optional[str] = None,
        on_audit: Optional[Callable[[SecretAuditEntry], None]] = None,
    ):
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self._on_audit = on_audit
        self._client = None

    @property
    def backend(self) -> SecretBackend:
        return SecretBackend.AWS_SECRETS_MANAGER

    def _get_client(self):
        """Lazy initialization of AWS client."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    "secretsmanager",
                    region_name=self.region_name
                )
            except ImportError:
                raise ImportError("boto3 is required for AWS Secrets Manager")
        return self._client

    async def get_secret(
        self,
        path: str,
        version: Optional[str] = None,
        key: Optional[str] = None,
    ) -> Optional[SecureValue]:
        """Get secret from AWS Secrets Manager."""
        try:
            client = self._get_client()

            kwargs = {"SecretId": path}
            if version:
                kwargs["VersionId"] = version

            response = client.get_secret_value(**kwargs)

            # Handle string or binary secret
            if "SecretString" in response:
                value = response["SecretString"]
            else:
                import base64
                value = base64.b64decode(response["SecretBinary"]).decode()

            # If key specified, parse JSON and extract key
            if key:
                import json
                data = json.loads(value)
                value = data.get(key, "")

            ref = SecretRef(
                vault=SecretBackend.AWS_SECRETS_MANAGER,
                path=path,
                version=version,
                key=key,
            )

            created_at = response.get("CreatedDate")
            secure_value = SecureValue(
                ref=ref,
                value=value,
                created_at=created_at,
            )

            self._log_access(path, success=True)
            return secure_value

        except Exception as e:
            self._log_access(path, success=False, error=str(e))
            return None

    async def get_secret_batch(
        self,
        paths: List[str],
    ) -> Dict[str, Optional[SecureValue]]:
        """Get multiple secrets from AWS."""
        # AWS supports batch retrieval
        result = {}
        for path in paths:
            result[path] = await self.get_secret(path)
        return result

    async def rotate_secret(
        self,
        path: str,
        new_value: str,
    ) -> bool:
        """Trigger secret rotation in AWS."""
        try:
            client = self._get_client()
            client.update_secret(SecretId=path, SecretString=new_value)
            self._log_access(path, success=True, action=SecretAccessAction.ROTATE)
            return True
        except Exception as e:
            self._log_access(path, success=False, error=str(e), action=SecretAccessAction.ROTATE)
            return False

    def _log_access(
        self,
        path: str,
        success: bool,
        error: Optional[str] = None,
        action: SecretAccessAction = SecretAccessAction.READ,
    ) -> None:
        """Log secret access for audit."""
        if self._on_audit:
            entry = SecretAuditEntry(
                timestamp=datetime.utcnow(),
                action=action,
                secret_path=path,
                secret_backend=SecretBackend.AWS_SECRETS_MANAGER,
                user_id="system",
                success=success,
                error_message=error,
            )
            self._on_audit(entry)


class HashicorpVaultProvider(SecretProvider):
    """
    Secret provider using HashiCorp Vault.

    Supports multiple auth methods and dynamic secrets.
    """

    def __init__(
        self,
        vault_addr: Optional[str] = None,
        token: Optional[str] = None,
        namespace: Optional[str] = None,
        on_audit: Optional[Callable[[SecretAuditEntry], None]] = None,
    ):
        self.vault_addr = vault_addr or os.environ.get("VAULT_ADDR", "http://localhost:8200")
        self.token = token or os.environ.get("VAULT_TOKEN")
        self.namespace = namespace or os.environ.get("VAULT_NAMESPACE")
        self._on_audit = on_audit
        self._client = None

    @property
    def backend(self) -> SecretBackend:
        return SecretBackend.HASHICORP_VAULT

    def _get_client(self):
        """Lazy initialization of Vault client."""
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(
                    url=self.vault_addr,
                    token=self.token,
                    namespace=self.namespace,
                )
            except ImportError:
                raise ImportError("hvac is required for HashiCorp Vault")
        return self._client

    async def get_secret(
        self,
        path: str,
        version: Optional[str] = None,
        key: Optional[str] = None,
    ) -> Optional[SecureValue]:
        """Get secret from Vault."""
        try:
            client = self._get_client()

            # Read from KV v2 (default)
            response = client.secrets.kv.v2.read_secret_version(
                path=path,
                version=int(version) if version else None,
            )

            data = response.get("data", {}).get("data", {})

            if key:
                value = data.get(key, "")
            else:
                # If no key, serialize entire data
                import json
                value = json.dumps(data) if len(data) > 1 else list(data.values())[0]

            ref = SecretRef(
                vault=SecretBackend.HASHICORP_VAULT,
                path=path,
                version=version,
                key=key,
            )

            metadata = response.get("data", {}).get("metadata", {})
            created_at = metadata.get("created_time")
            if created_at:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            secure_value = SecureValue(
                ref=ref,
                value=value,
                created_at=created_at,
            )

            self._log_access(path, success=True)
            return secure_value

        except Exception as e:
            self._log_access(path, success=False, error=str(e))
            return None

    async def get_secret_batch(
        self,
        paths: List[str],
    ) -> Dict[str, Optional[SecureValue]]:
        """Get multiple secrets from Vault."""
        result = {}
        for path in paths:
            result[path] = await self.get_secret(path)
        return result

    async def rotate_secret(
        self,
        path: str,
        new_value: str,
    ) -> bool:
        """Update secret in Vault (creates new version)."""
        try:
            client = self._get_client()

            # Parse new_value as JSON if possible
            try:
                import json
                data = json.loads(new_value)
            except:
                data = {"value": new_value}

            client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
            )

            self._log_access(path, success=True, action=SecretAccessAction.ROTATE)
            return True

        except Exception as e:
            self._log_access(path, success=False, error=str(e), action=SecretAccessAction.ROTATE)
            return False

    def _log_access(
        self,
        path: str,
        success: bool,
        error: Optional[str] = None,
        action: SecretAccessAction = SecretAccessAction.READ,
    ) -> None:
        """Log secret access for audit."""
        if self._on_audit:
            entry = SecretAuditEntry(
                timestamp=datetime.utcnow(),
                action=action,
                secret_path=path,
                secret_backend=SecretBackend.HASHICORP_VAULT,
                user_id="system",
                success=success,
                error_message=error,
            )
            self._on_audit(entry)
