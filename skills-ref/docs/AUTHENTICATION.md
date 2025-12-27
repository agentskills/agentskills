# Authentication

The AgentSkills authentication module provides flexible, secure authentication for skill execution.

## Overview

The authentication system supports multiple authentication methods:
- **JWT (JSON Web Tokens)** - For stateless authentication with refresh tokens
- **API Keys** - For machine-to-machine authentication

## Quick Start

```python
from skills_ref.auth import (
    AuthManager,
    JWTAuthProvider,
    APIKeyAuthProvider,
)

# Create providers
jwt_provider = JWTAuthProvider(
    secret_key="your-secret-key",
    issuer="agentskills",
)

api_key_provider = APIKeyAuthProvider(
    api_keys={"sk_live_abc123": "user-1"},
)

# Create manager
auth_manager = AuthManager([jwt_provider, api_key_provider])

# Authenticate a token
result = await auth_manager.authenticate(token)
if result.success:
    print(f"Authenticated: {result.context.user_id}")
```

## JWT Authentication

### Generating Tokens

```python
from skills_ref.auth import JWTAuthProvider, SkillAuthContext

provider = JWTAuthProvider(
    secret_key="your-secret-key",
    issuer="agentskills",
    access_token_ttl=3600,      # 1 hour
    refresh_token_ttl=604800,   # 7 days
)

# Create token for a user
tokens = await provider.create_tokens(
    user_id="user-123",
    scopes=["skill:execute", "skill:read"],
    roles=["developer"],
    metadata={"org_id": "org-456"},
)

print(tokens.access_token)   # JWT access token
print(tokens.refresh_token)  # JWT refresh token
```

### Validating Tokens

```python
result = await provider.validate_token(access_token)

if result.success:
    context = result.context
    print(f"User: {context.user_id}")
    print(f"Scopes: {context.scopes}")
    print(f"Roles: {context.roles}")
else:
    print(f"Error: {result.error_code} - {result.error_message}")
```

### Refreshing Tokens

```python
new_tokens = await provider.refresh_token(refresh_token)
if new_tokens:
    print(f"New access token: {new_tokens.access_token}")
```

## API Key Authentication

### Creating API Keys

```python
from skills_ref.auth import APIKeyAuthProvider

provider = APIKeyAuthProvider()

# Register an API key
credential = await provider.register_key(
    key="sk_live_your_api_key",
    user_id="user-123",
    scopes=["skill:execute"],
    metadata={"environment": "production"},
)

print(f"Key ID: {credential.key_id}")
```

### Validating API Keys

```python
result = await provider.validate_token("sk_live_your_api_key")

if result.success:
    print(f"Authenticated user: {result.context.user_id}")
```

### Rotating Keys

```python
# Rotate an existing key
new_key, credential = await provider.rotate_key("old_key_id")
print(f"New key: {new_key}")  # Provide this to the user
```

## Auth Manager

The `AuthManager` orchestrates multiple authentication providers:

```python
from skills_ref.auth import AuthManager, AuthMiddleware

# Create manager with multiple providers
auth_manager = AuthManager([jwt_provider, api_key_provider])

# The manager auto-detects which provider to use based on token format
result = await auth_manager.authenticate(token)
```

## Middleware Integration

### Request Authentication

```python
from skills_ref.auth import AuthMiddleware

middleware = AuthMiddleware(auth_manager)

# Authenticate a request
result = await middleware.authenticate_request(
    authorization_header="Bearer eyJ...",  # or None
    api_key_header="sk_live_...",           # or None
    ip_address="192.168.1.1",
    user_agent="MyApp/1.0",
)
```

### Decorator Pattern

```python
from skills_ref.auth import require_auth

@require_auth(
    auth_manager,
    required_scopes=["skill:execute"],
    required_roles=["developer"],
)
async def execute_skill(context: SkillAuthContext, skill_name: str):
    # context is automatically injected with authenticated user
    print(f"Executing for user: {context.user_id}")
```

## Configuration

Configure authentication via environment variables:

```bash
# JWT settings
AGENTSKILLS_AUTH__ENABLED=true
AGENTSKILLS_AUTH__JWT_SECRET=your-super-secret-key
AGENTSKILLS_AUTH__JWT_ALGORITHM=HS256
AGENTSKILLS_AUTH__ACCESS_TOKEN_TTL_SECONDS=3600
AGENTSKILLS_AUTH__REFRESH_TOKEN_TTL_SECONDS=604800

# API key settings
AGENTSKILLS_AUTH__API_KEY_ENABLED=true
AGENTSKILLS_AUTH__API_KEY_HEADER=X-API-Key

# Security
AGENTSKILLS_AUTH__REQUIRE_HTTPS=true
```

## Security Best Practices

1. **Use strong secrets**: Generate JWT secrets with `secrets.token_urlsafe(32)`
2. **Rotate secrets**: Implement secret rotation for production
3. **Short-lived tokens**: Use short access token TTLs (1 hour recommended)
4. **Secure transmission**: Always use HTTPS in production
5. **Validate claims**: Check issuer, audience, and expiration
6. **Rate limit**: Implement rate limiting on auth endpoints

## Error Handling

```python
from skills_ref.auth import AuthResult

result = await auth_manager.authenticate(token)

if not result.success:
    match result.error_code:
        case "TOKEN_EXPIRED":
            # Refresh token or re-authenticate
            pass
        case "INVALID_TOKEN":
            # Bad token format or signature
            pass
        case "NO_PROVIDER":
            # No provider can handle this token type
            pass
        case _:
            print(f"Auth error: {result.error_message}")
```

## Events and Auditing

The auth system emits events for auditing:

```python
def on_auth_event(event: AuthEvent):
    print(f"Auth event: {event.event_type.value}")
    print(f"User: {event.user_id}")
    print(f"Success: {event.success}")

auth_manager = AuthManager(
    providers=[jwt_provider],
    on_auth_event=on_auth_event,
)
```

Event types:
- `LOGIN` - Successful authentication
- `LOGOUT` - Token revocation
- `TOKEN_REFRESH` - Token refreshed
- `TOKEN_EXPIRED` - Token expiration detected
- `AUTH_FAILED` - Authentication failure
