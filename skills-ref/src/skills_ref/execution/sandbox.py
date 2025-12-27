# skills_ref/execution/sandbox.py — Sandboxed script execution with hardened security

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum, auto
import subprocess
import tempfile
import os
import shutil
from pathlib import Path
import time


class ScriptLanguage(Enum):
    """Supported script languages."""
    PYTHON = auto()
    BASH = auto()
    JAVASCRIPT = auto()


@dataclass
class SandboxConfig:
    """Sandbox configuration."""
    timeout_seconds: int = 30
    max_memory_mb: int = 512
    max_output_bytes: int = 1_000_000
    allowed_imports: List[str] = field(default_factory=list)
    network_access: bool = False
    filesystem_access: str = 'none'  # 'none', 'readonly', 'temp_only'


@dataclass
class ExecutionResult:
    """Result of sandboxed execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float
    memory_used_mb: Optional[float] = None
    error: Optional[str] = None


# Comprehensive list of dangerous patterns to block
DANGEROUS_PATTERNS = [
    # System execution
    'os.system', 'os.popen', 'os.spawn', 'os.exec',
    'subprocess.', 'commands.',
    # Dynamic code execution
    'eval(', 'exec(', 'compile(',
    # Import manipulation
    '__import__', 'importlib',
    # File system access (when restricted)
    'open(', 'file(',
    # Dangerous builtins
    '__builtins__', '__loader__', '__spec__',
    # Pickle (code execution via deserialization)
    'pickle.', 'cPickle.',
    # Code/marshal modules
    'marshal.', 'code.',
    # ctypes (can call arbitrary C functions)
    'ctypes.',
    # Multiprocessing (can spawn processes)
    'multiprocessing.',
]

# Network-related modules to block
NETWORK_MODULES = [
    'socket', 'ssl', 'urllib', 'urllib2', 'urllib3',
    'http', 'httplib', 'http.client', 'http.server',
    'ftplib', 'smtplib', 'poplib', 'imaplib', 'nntplib',
    'telnetlib', 'xmlrpc', 'requests', 'aiohttp', 'httpx',
    'asyncio',  # Can be used for network I/O
]


class ScriptSandbox:
    """
    Execute scripts in a hardened sandboxed environment.

    Security measures:
    1. Code scanning for dangerous patterns
    2. Import restrictions via custom import hook
    3. Network isolation via module blocking
    4. Resource limits (memory, CPU time, output size)
    5. Filesystem isolation via temp directories
    6. Timeout enforcement
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()

    def execute(
        self,
        code: str,
        language: ScriptLanguage,
        env: Optional[Dict[str, str]] = None,
        stdin: Optional[str] = None
    ) -> ExecutionResult:
        """Execute code in sandbox after security validation."""

        # Pre-execution security scan
        scan_result = self._scan_code(code, language)
        if scan_result:
            return ExecutionResult(
                success=False,
                stdout='',
                stderr='',
                return_code=-1,
                execution_time_ms=0,
                error=f"Security violation: {scan_result}"
            )

        if language == ScriptLanguage.PYTHON:
            return self._execute_python(code, env, stdin)
        elif language == ScriptLanguage.BASH:
            return self._execute_bash(code, env, stdin)
        elif language == ScriptLanguage.JAVASCRIPT:
            return self._execute_javascript(code, env, stdin)
        else:
            return ExecutionResult(
                success=False,
                stdout='',
                stderr='',
                return_code=-1,
                execution_time_ms=0,
                error=f"Unsupported language: {language}"
            )

    def _scan_code(self, code: str, language: ScriptLanguage) -> Optional[str]:
        """Scan code for dangerous patterns. Returns error message if found."""

        if language == ScriptLanguage.PYTHON:
            for pattern in DANGEROUS_PATTERNS:
                if pattern in code:
                    return f"Blocked pattern detected: {pattern}"

        elif language == ScriptLanguage.BASH:
            # Block dangerous bash commands
            dangerous_bash = [
                'curl ', 'wget ', 'nc ', 'netcat ',
                '/dev/tcp/', '/dev/udp/',
                'eval ', '$(', '`',  # Command substitution
                'rm -rf', 'dd if=', 'mkfs.',
                ':(){', 'fork',  # Fork bombs
                '/etc/passwd', '/etc/shadow',
                'chmod 777', 'chmod +s',
            ]
            for pattern in dangerous_bash:
                if pattern in code:
                    return f"Blocked bash pattern: {pattern}"

        return None

    def _execute_python(
        self,
        code: str,
        env: Optional[Dict[str, str]],
        stdin: Optional[str]
    ) -> ExecutionResult:
        """Execute Python code in hardened sandbox."""

        # Build the sandboxed code with security wrappers
        sandboxed_code = self._build_python_sandbox(code)

        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / 'script.py'
            script_path.write_text(sandboxed_code, encoding='utf-8')

            try:
                # Build minimal execution environment
                exec_env = self._build_safe_env(temp_dir)
                if env:
                    # Only allow safe environment variables
                    for key, value in env.items():
                        if key.startswith('SANDBOX_'):
                            exec_env[key] = value

                # Build preexec function for resource limits
                preexec_fn = self._build_preexec_fn()

                start_time = time.perf_counter()

                result = subprocess.run(
                    ['python3', '-I', str(script_path)],  # -I for isolated mode
                    env=exec_env,
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    preexec_fn=preexec_fn,
                    cwd=temp_dir  # Restrict working directory
                )

                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000

                stdout = result.stdout[:self.config.max_output_bytes]
                stderr = result.stderr[:self.config.max_output_bytes]

                return ExecutionResult(
                    success=result.returncode == 0,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=result.returncode,
                    execution_time_ms=execution_time_ms
                )

            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    stdout='',
                    stderr='',
                    return_code=-1,
                    execution_time_ms=self.config.timeout_seconds * 1000,
                    error=f"Execution timed out after {self.config.timeout_seconds}s"
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    stdout='',
                    stderr='',
                    return_code=-1,
                    execution_time_ms=0,
                    error=str(e)
                )

    def _build_python_sandbox(self, user_code: str) -> str:
        """Build sandboxed Python code with security wrappers."""

        # Generate list of blocked modules
        blocked_modules = NETWORK_MODULES if not self.config.network_access else []

        # Generate allowed imports set
        allowed_set = set(self.config.allowed_imports) if self.config.allowed_imports else None

        sandbox_wrapper = f'''
import sys
import builtins

# === SECURITY LAYER 1: Block dangerous modules at import time ===
_blocked_modules = {blocked_modules!r}
_allowed_modules = {allowed_set!r}

_original_import = builtins.__import__

def _secure_import(name, globals=None, locals=None, fromlist=(), level=0):
    base_module = name.split('.')[0]

    # Block network modules
    if base_module in _blocked_modules:
        raise ImportError(f"Module '{{name}}' is blocked for security reasons")

    # Block submodules of blocked modules
    for blocked in _blocked_modules:
        if name.startswith(blocked + '.'):
            raise ImportError(f"Module '{{name}}' is blocked for security reasons")

    # If allowlist is specified, only allow those modules
    if _allowed_modules is not None:
        if base_module not in _allowed_modules and base_module not in ('builtins', 'sys'):
            raise ImportError(f"Module '{{name}}' is not in the allowed list")

    return _original_import(name, globals, locals, fromlist, level)

builtins.__import__ = _secure_import

# === SECURITY LAYER 2: Pre-block network modules in sys.modules ===
class _BlockedModule:
    def __getattr__(self, name):
        raise ImportError("This module is blocked for security reasons")
    def __call__(self, *args, **kwargs):
        raise ImportError("This module is blocked for security reasons")

for _mod in _blocked_modules:
    sys.modules[_mod] = _BlockedModule()

# === SECURITY LAYER 3: Disable dangerous builtins ===
_original_open = builtins.open
def _restricted_open(*args, **kwargs):
    raise PermissionError("File operations are disabled in sandbox")

if {self.config.filesystem_access == 'none'!r}:
    builtins.open = _restricted_open

# === SECURITY LAYER 4: Clean up dangerous references ===
del _original_import
del _original_open

# === USER CODE BELOW ===
'''
        return sandbox_wrapper + user_code

    def _build_safe_env(self, temp_dir: str) -> Dict[str, str]:
        """Build a minimal safe environment for subprocess."""
        safe_env = {
            'PATH': '/usr/bin:/bin',
            'HOME': temp_dir,
            'TMPDIR': temp_dir,
            'TEMP': temp_dir,
            'TMP': temp_dir,
            'LANG': 'C.UTF-8',
            'LC_ALL': 'C.UTF-8',
            # Prevent Python from reading user site packages
            'PYTHONNOUSERSITE': '1',
            'PYTHONDONTWRITEBYTECODE': '1',
        }
        return safe_env

    def _build_preexec_fn(self):
        """Build preexec function for resource limits."""
        max_memory = self.config.max_memory_mb

        def set_limits():
            try:
                import resource
                # Memory limit
                mem_bytes = max_memory * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
                # Limit number of processes/threads
                resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
                # Limit file size
                resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
            except (ValueError, OSError):
                pass  # Ignore if limits can't be set

        return set_limits

    def _execute_bash(
        self,
        code: str,
        env: Optional[Dict[str, str]],
        stdin: Optional[str]
    ) -> ExecutionResult:
        """Execute Bash script in restricted sandbox."""

        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / 'script.sh'

            # Build restricted bash script
            restricted_code = self._build_bash_sandbox(code, temp_dir)
            script_path.write_text(restricted_code, encoding='utf-8')
            os.chmod(script_path, 0o755)

            try:
                exec_env = self._build_safe_env(temp_dir)
                if env:
                    for key, value in env.items():
                        if key.startswith('SANDBOX_'):
                            exec_env[key] = value

                start_time = time.perf_counter()

                result = subprocess.run(
                    ['bash', '--restricted', str(script_path)],  # --restricted mode
                    env=exec_env,
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    preexec_fn=self._build_preexec_fn(),
                    cwd=temp_dir
                )

                end_time = time.perf_counter()

                return ExecutionResult(
                    success=result.returncode == 0,
                    stdout=result.stdout[:self.config.max_output_bytes],
                    stderr=result.stderr[:self.config.max_output_bytes],
                    return_code=result.returncode,
                    execution_time_ms=(end_time - start_time) * 1000
                )

            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    stdout='',
                    stderr='',
                    return_code=-1,
                    execution_time_ms=self.config.timeout_seconds * 1000,
                    error=f"Execution timed out after {self.config.timeout_seconds}s"
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    stdout='',
                    stderr='',
                    return_code=-1,
                    execution_time_ms=0,
                    error=str(e)
                )

    def _build_bash_sandbox(self, code: str, temp_dir: str) -> str:
        """Build sandboxed bash script."""
        return f'''#!/bin/bash
set -euo pipefail

# Restrict PATH to minimal commands
export PATH="/usr/bin:/bin"

# Disable dangerous commands by making them no-ops
curl() {{ echo "curl is disabled" >&2; return 1; }}
wget() {{ echo "wget is disabled" >&2; return 1; }}
nc() {{ echo "nc is disabled" >&2; return 1; }}
netcat() {{ echo "netcat is disabled" >&2; return 1; }}
ssh() {{ echo "ssh is disabled" >&2; return 1; }}
scp() {{ echo "scp is disabled" >&2; return 1; }}
rsync() {{ echo "rsync is disabled" >&2; return 1; }}
export -f curl wget nc netcat ssh scp rsync

# Change to temp directory
cd "{temp_dir}"

# User code below
{code}
'''

    def _execute_javascript(
        self,
        code: str,
        env: Optional[Dict[str, str]],
        stdin: Optional[str]
    ) -> ExecutionResult:
        """Execute JavaScript - currently disabled for security."""
        return ExecutionResult(
            success=False,
            stdout="",
            stderr="JavaScript execution is disabled for security reasons",
            return_code=-1,
            execution_time_ms=0,
            error="JavaScript execution not implemented"
        )
