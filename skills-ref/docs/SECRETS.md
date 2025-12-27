# Secrets Management

The AgentSkills secrets module provides secure secret storage, retrieval, and automatic masking.

## Overview

The secrets system provides:
- **Multiple backends**: Environment variables, AWS Secrets Manager, HashiCorp Vault
- **Automatic masking**: Prevents secrets from appearing in logs
- **Caching**: Reduces API calls with configurable TTL
- **Audit logging**: Tracks all secret access

## Quick Start

```python
from skills_ref.secrets import (
    SecretStore,
    EnvSecretProvider,
    SecretMasker,
)

# Create a secret store with environment provider
provider = EnvSecretProvider()
store = SecretStore(provider)

# Get a secret
api_key = await store.get("OPENAI_API_KEY")
print(api_key.expose())  # Exposes the actual value

# The secret value is protected
print(api_key)  # Prints: SecureValue(****)
```

## Secret Providers

### Environment Variables

```python
from skills_ref.secrets import EnvSecretProvider

provider = EnvSecretProvider(
    prefix="AGENTSKILLS_",  # Only load vars with this prefix
)

# Gets AGENTSKILLS_API_KEY from environment
secret = await provider.get("API_KEY")
```

### AWS Secrets Manager

```python
from skills_ref.secrets import AWSSecretsManagerProvider

provider = AWSSecretsManagerProvider(
    region="us-east-1",
    prefix="agentskills/",  # Secret path prefix
)

# Gets secret from AWS Secrets Manager at "agentskills/api-key"
secret = await provider.get("api-key")
```

### HashiCorp Vault

```python
from skills_ref.secrets import HashicorpVaultProvider

provider = HashicorpVaultProvider(
    addr="https://vault.example.com:8200",
    token="hvs.xxxxx",
    mount="secret",
    path_prefix="agentskills/",
)

# Gets secret from Vault at "secret/data/agentskills/api-key"
secret = await provider.get("api-key")
```

## SecureValue

The `SecureValue` class protects secrets from accidental exposure:

```python
from skills_ref.secrets import SecureValue

# Create a secure value
secret = SecureValue("my-secret-value")

# Safe operations
print(secret)        # SecureValue(****)
str(secret)          # "SecureValue(****)"
repr(secret)         # "SecureValue(****)"

# Explicit exposure required
actual_value = secret.expose()

# Check if value exists
if secret:
    print("Secret is set")

# Compare (timing-safe)
if secret == another_secret:
    print("Secrets match")
```

## Secret Store

The `SecretStore` provides a unified interface for secret management:

```python
from skills_ref.secrets import SecretStore, SecretStoreBuilder

# Using builder pattern
store = (
    SecretStoreBuilder()
    .with_env_provider()
    .with_caching(ttl_seconds=300)
    .with_masking()
    .with_audit_logging()
    .build()
)

# Get a secret
api_key = await store.get("OPENAI_API_KEY")

# Get with default
db_password = await store.get("DB_PASSWORD", default="local-dev-password")

# Check if secret exists
exists = await store.exists("SOME_SECRET")

# List available secrets (names only)
names = await store.list()
```

## Cached Secret Store

```python
from skills_ref.secrets import CachedSecretStore

cached_store = CachedSecretStore(
    provider=provider,
    ttl_seconds=300,  # Cache for 5 minutes
)

# First call fetches from provider
secret1 = await cached_store.get("API_KEY")

# Second call returns cached value
secret2 = await cached_store.get("API_KEY")

# Force refresh
secret3 = await cached_store.get("API_KEY", refresh=True)

# Clear entire cache
cached_store.clear_cache()
```

## Secret Masking

Automatically mask secrets in logs and outputs:

```python
from skills_ref.secrets import SecretMasker, mask_secrets

# Create masker
masker = SecretMasker()

# Register secrets to mask
masker.register("sk-abc123")
masker.register("my-password")

# Mask a string
text = "Using API key sk-abc123 to connect"
masked = masker.mask(text)
print(masked)  # "Using API key ******** to connect"

# Mask a dictionary (deep)
data = {
    "api_key": "sk-abc123",
    "nested": {"password": "my-password"},
}
masked_data = masker.mask_dict(data)
```

### Default Masking Rules

The masker includes rules for common patterns:

```python
from skills_ref.secrets import DEFAULT_MASKING_RULES

# Automatically masks:
# - API keys (sk-*, api_*, Bearer *, etc.)
# - Passwords in URLs (user:password@host)
# - Common secret patterns (secret=, token=, etc.)
# - AWS credentials (AKIA*, aws_secret_access_key)
# - Private keys (-----BEGIN * PRIVATE KEY-----)
```

### Custom Masking Rules

```python
from skills_ref.secrets import MaskingRule

# Create custom rule
rule = MaskingRule(
    name="custom-pattern",
    pattern=r"custom-secret-\w+",
    replacement="[CUSTOM-SECRET]",
)

masker.add_rule(rule)
```

## Audit Logging

Track all secret access:

```python
from skills_ref.secrets import SecretStore

def on_secret_access(entry):
    print(f"Secret accessed: {entry.secret_name}")
    print(f"By: {entry.accessor_id}")
    print(f"At: {entry.timestamp}")
    print(f"Action: {entry.action}")

store = SecretStore(
    provider=provider,
    on_access=on_secret_access,
)
```

## Configuration

Configure via environment variables:

```bash
# Backend type: env, aws, vault
AGENTSKILLS_SECRETS__BACKEND=env

# Caching
AGENTSKILLS_SECRETS__CACHE_ENABLED=true
AGENTSKILLS_SECRETS__CACHE_TTL_SECONDS=300

# Masking
AGENTSKILLS_SECRETS__MASK_IN_LOGS=true

# Audit
AGENTSKILLS_SECRETS__AUDIT_ACCESS=true

# AWS Secrets Manager
AGENTSKILLS_SECRETS__AWS_REGION=us-east-1
AGENTSKILLS_SECRETS__AWS_SECRET_PREFIX=agentskills/

# HashiCorp Vault
AGENTSKILLS_SECRETS__VAULT_ADDR=https://vault.example.com:8200
AGENTSKILLS_SECRETS__VAULT_TOKEN=hvs.xxxxx
AGENTSKILLS_SECRETS__VAULT_MOUNT=secret
```

## Integration with Skills

```python
from skills_ref.secrets import SecretStore
from skills_ref.core import SkillDefinition

class EmailSkill:
    def __init__(self, secret_store: SecretStore):
        self.secrets = secret_store

    async def execute(self, inputs: dict) -> dict:
        # Get API key securely
        api_key = await self.secrets.get("SENDGRID_API_KEY")

        # Use the exposed value for API call
        response = await send_email(
            api_key=api_key.expose(),
            to=inputs["to"],
            subject=inputs["subject"],
        )

        return {"status": "sent"}
```

## Best Practices

1. **Never log secrets**: Always use `SecureValue` and masking
2. **Short TTLs in production**: Use shorter cache TTLs for sensitive secrets
3. **Rotate regularly**: Implement secret rotation
4. **Audit access**: Enable audit logging in production
5. **Use managed services**: Prefer AWS Secrets Manager or Vault over env vars in production
6. **Encrypt at rest**: Ensure backend storage is encrypted

## Secret Rotation

```python
from skills_ref.secrets import AWSSecretsManagerProvider

provider = AWSSecretsManagerProvider(
    region="us-east-1",
    enable_rotation=True,
    rotation_check_interval=3600,  # Check hourly
)

# Provider automatically handles rotation
# Old values remain valid during rotation window
```

## Error Handling

```python
from skills_ref.secrets import SecretNotFoundError, SecretAccessError

try:
    secret = await store.get("MISSING_SECRET")
except SecretNotFoundError:
    print("Secret not found")
except SecretAccessError as e:
    print(f"Access error: {e}")
```
