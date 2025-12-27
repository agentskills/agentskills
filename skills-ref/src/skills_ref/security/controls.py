# skills_ref/security/controls.py — Security control implementations

from dataclasses import dataclass, field
from typing import Optional, Set, List, Tuple
from pathlib import Path
import os
import re


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    # Execution controls
    allow_script_execution: bool = False
    allowed_languages: Set[str] = field(default_factory=set)
    max_execution_time_seconds: int = 30
    max_memory_mb: int = 512

    # Filesystem controls
    skill_root: Optional[Path] = None
    allowed_paths: Set[Path] = field(default_factory=set)
    deny_path_traversal: bool = True

    # Network controls
    allow_network: bool = False
    allowed_hosts: Set[str] = field(default_factory=set)

    # Content controls
    max_skill_size_bytes: int = 10_000_000  # 10MB
    max_body_tokens: int = 5000
    sanitize_html: bool = True


class SecurityGate:
    """
    Security gate for skill operations.

    Enforces:
    1. Path normalization and jail
    2. Execution allowlisting
    3. Resource limits
    4. Content sanitization
    """

    def __init__(self, policy: SecurityPolicy):
        self.policy = policy

    def validate_path(self, path: Path) -> Tuple[bool, Optional[str]]:
        """Validate path is within allowed boundaries."""
        try:
            # Resolve to absolute path
            # We assume path exists? If not, resolve() might fail on strict systems, but usually works.
            # But if path doesn't exist, we can't check relative_to properly if it relies on symlink resolution.
            # We'll use os.path.abspath logic via Path.resolve().
            resolved = path.resolve()

            # Check for path traversal
            if self.policy.deny_path_traversal:
                if self.policy.skill_root:
                    try:
                        resolved.relative_to(self.policy.skill_root.resolve())
                    except ValueError:
                        return False, f"Path traversal detected: {path}"

            # Check against allowed paths
            if self.policy.allowed_paths:
                allowed = False
                for allowed_path in self.policy.allowed_paths:
                    try:
                        resolved.relative_to(allowed_path.resolve())
                        allowed = True
                        break
                    except ValueError:
                        continue

                if not allowed:
                    return False, f"Path not in allowed set: {path}"

            return True, None

        except Exception as e:
            return False, f"Path validation error: {e}"

    def validate_execution(
        self,
        language: str,
        code: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate code execution is allowed."""

        if not self.policy.allow_script_execution:
            return False, "Script execution is disabled"

        if self.policy.allowed_languages:
            if language.lower() not in self.policy.allowed_languages:
                return False, f"Language not allowed: {language}"

        # Check for dangerous patterns
        dangerous_patterns = [
            (r'os\.system', "Direct system calls not allowed"),
            (r'subprocess\.', "Subprocess calls not allowed"),
            (r'eval\s*\(', "eval() not allowed"),
            (r'exec\s*\(', "exec() not allowed"),
            (r'__import__', "Dynamic imports not allowed"),
            (r'open\s*\(', "File operations not allowed"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, code):
                return False, message

        return True, None

    def sanitize_content(self, content: str) -> str:
        """Sanitize content for safe inclusion."""
        if not self.policy.sanitize_html:
            return content

        # Remove potentially dangerous HTML

        # Remove script tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Remove on* event handlers
        content = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)

        # Remove javascript: URLs
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)

        return content

    def check_size(self, content: bytes) -> Tuple[bool, Optional[str]]:
        """Check content size against limits."""
        size = len(content)

        if size > self.policy.max_skill_size_bytes:
            return False, f"Content exceeds size limit: {size} > {self.policy.max_skill_size_bytes}"

        return True, None
