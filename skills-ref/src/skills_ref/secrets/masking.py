"""
Secret masking utilities for safe logging.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Pattern


@dataclass
class MaskingRule:
    """Rule for identifying and masking secrets."""
    name: str
    pattern: Pattern
    replacement: str = "***MASKED***"

    def apply(self, text: str) -> str:
        """Apply masking to text."""
        return self.pattern.sub(self.replacement, text)


# Default patterns for common secrets
DEFAULT_MASKING_RULES = [
    MaskingRule(
        name="jwt",
        pattern=re.compile(r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"),
        replacement="***JWT_TOKEN***",
    ),
    MaskingRule(
        name="api_key_sk",
        pattern=re.compile(r"sk[-_][a-zA-Z0-9]{20,}"),
        replacement="***API_KEY***",
    ),
    MaskingRule(
        name="api_key_pk",
        pattern=re.compile(r"pk[-_][a-zA-Z0-9]{20,}"),
        replacement="***PUB_KEY***",
    ),
    MaskingRule(
        name="aws_access_key",
        pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
        replacement="***AWS_KEY***",
    ),
    MaskingRule(
        name="aws_secret_key",
        pattern=re.compile(r"(?<![a-zA-Z0-9/+=])[a-zA-Z0-9/+=]{40}(?![a-zA-Z0-9/+=])"),
        replacement="***AWS_SECRET***",
    ),
    MaskingRule(
        name="bearer_token",
        pattern=re.compile(r"Bearer\s+[a-zA-Z0-9._-]+"),
        replacement="Bearer ***TOKEN***",
    ),
    MaskingRule(
        name="password_field",
        pattern=re.compile(r'(["\']?password["\']?\s*[=:]\s*)["\']?[^"\'\s,}]+["\']?', re.IGNORECASE),
        replacement=r"\1***PASSWORD***",
    ),
    MaskingRule(
        name="secret_field",
        pattern=re.compile(r'(["\']?secret["\']?\s*[=:]\s*)["\']?[^"\'\s,}]+["\']?', re.IGNORECASE),
        replacement=r"\1***SECRET***",
    ),
    MaskingRule(
        name="token_field",
        pattern=re.compile(r'(["\']?(?:api_key|apikey|auth_token|access_token)["\']?\s*[=:]\s*)["\']?[^"\'\s,}]+["\']?', re.IGNORECASE),
        replacement=r"\1***TOKEN***",
    ),
    MaskingRule(
        name="connection_string_password",
        pattern=re.compile(r"(://[^:]+:)[^@]+(@)"),
        replacement=r"\1***\2",
    ),
]


class SecretMasker:
    """
    Masks secrets in text, logs, and data structures.

    Features:
    - Pattern-based detection
    - Known secret values
    - Recursive data structure masking
    - Customizable rules
    """

    def __init__(
        self,
        rules: Optional[List[MaskingRule]] = None,
        known_secrets: Optional[Set[str]] = None,
    ):
        self.rules = rules or list(DEFAULT_MASKING_RULES)
        self._known_secrets: Set[str] = known_secrets or set()

    def add_known_secret(self, secret: str) -> None:
        """Add a known secret value to mask."""
        if secret and len(secret) >= 4:
            self._known_secrets.add(secret)

    def remove_known_secret(self, secret: str) -> None:
        """Remove a known secret from masking."""
        self._known_secrets.discard(secret)

    def add_rule(self, rule: MaskingRule) -> None:
        """Add a custom masking rule."""
        self.rules.append(rule)

    def mask(self, text: str) -> str:
        """
        Mask secrets in text.

        Applies all rules and known secret masking.
        """
        if not text:
            return text

        result = text

        # Apply pattern rules
        for rule in self.rules:
            result = rule.apply(result)

        # Mask known secrets
        for secret in self._known_secrets:
            if secret in result:
                # Show first 2 and last 2 chars
                masked = f"{secret[:2]}***{secret[-2:]}" if len(secret) > 4 else "****"
                result = result.replace(secret, masked)

        return result

    def mask_dict(
        self,
        data: Dict[str, Any],
        sensitive_keys: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """
        Recursively mask secrets in a dictionary.

        Args:
            data: Dictionary to mask
            sensitive_keys: Additional key names to always mask

        Returns:
            New dictionary with masked values
        """
        default_sensitive = {
            "password", "secret", "token", "api_key", "apikey",
            "access_token", "refresh_token", "private_key",
            "credentials", "auth", "authorization",
        }
        sensitive = default_sensitive | (sensitive_keys or set())

        return self._mask_value(data, sensitive)

    def _mask_value(
        self,
        value: Any,
        sensitive_keys: Set[str],
    ) -> Any:
        """Recursively mask a value."""
        if isinstance(value, dict):
            return {
                k: self._mask_dict_value(k, v, sensitive_keys)
                for k, v in value.items()
            }
        elif isinstance(value, list):
            return [self._mask_value(item, sensitive_keys) for item in value]
        elif isinstance(value, str):
            return self.mask(value)
        else:
            return value

    def _mask_dict_value(
        self,
        key: str,
        value: Any,
        sensitive_keys: Set[str],
    ) -> Any:
        """Mask a dictionary value based on key."""
        key_lower = key.lower()

        # Always mask sensitive keys
        if key_lower in sensitive_keys:
            if isinstance(value, str):
                if len(value) > 4:
                    return f"{value[:2]}***{value[-2:]}"
                return "****"
            elif isinstance(value, dict):
                return {"$masked": True}
            else:
                return "***MASKED***"

        # Recursively process non-sensitive values
        return self._mask_value(value, sensitive_keys)


def mask_secrets(text: str, known_secrets: Optional[List[str]] = None) -> str:
    """
    Convenience function to mask secrets in text.

    Args:
        text: Text to mask
        known_secrets: Optional list of known secret values

    Returns:
        Masked text
    """
    masker = SecretMasker()
    if known_secrets:
        for secret in known_secrets:
            masker.add_known_secret(secret)
    return masker.mask(text)


def mask_for_logging(data: Any) -> Any:
    """
    Prepare data for logging by masking secrets.

    Can handle strings, dicts, lists, and other JSON-serializable types.
    """
    masker = SecretMasker()

    if isinstance(data, str):
        return masker.mask(data)
    elif isinstance(data, dict):
        return masker.mask_dict(data)
    elif isinstance(data, list):
        return [mask_for_logging(item) for item in data]
    else:
        return data


class LoggingFilter:
    """
    Logging filter that masks secrets.

    Use with Python logging:
        handler.addFilter(LoggingFilter(masker))
    """

    def __init__(self, masker: Optional[SecretMasker] = None):
        self.masker = masker or SecretMasker()

    def filter(self, record) -> bool:
        """Filter and mask log record."""
        if hasattr(record, "msg"):
            if isinstance(record.msg, str):
                record.msg = self.masker.mask(record.msg)

        if hasattr(record, "args") and record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    masked_args.append(self.masker.mask(arg))
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)

        return True
