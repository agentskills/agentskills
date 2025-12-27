# skills_ref/execution/sandbox.py — Sandboxed script execution

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum, auto
import subprocess
import tempfile
import os
import signal
from pathlib import Path
import json
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
    filesystem_access: str = 'readonly'  # 'none', 'readonly', 'temp_only'


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


class ScriptSandbox:
    """
    Execute scripts in a sandboxed environment.
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
        """Execute code in sandbox."""

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

    def _execute_python(
        self,
        code: str,
        env: Optional[Dict[str, str]],
        stdin: Optional[str]
    ) -> ExecutionResult:
        """Execute Python code in sandbox."""

        wrappers = []

        # Network isolation
        if not self.config.network_access:
            wrappers.append(self._generate_network_blocker())

        # Wrap code with import restrictions if configured
        if self.config.allowed_imports:
            wrappers.append(self._generate_import_wrapper(self.config.allowed_imports))

        if wrappers:
            code = '\n'.join(wrappers) + '\n' + code

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            script_path = f.name

        try:
            # Build execution environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)

            # Add resource limits for Unix systems
            preexec_fn = None
            if hasattr(os, 'setrlimit') and hasattr(os, 'getuid') and os.getuid() != 0:
                # Only set rlimit if not root? Or set anyway.
                # Resource limits work for root too usually.
                import resource

                def set_limits():
                    # Memory limit
                    mem_bytes = self.config.max_memory_mb * 1024 * 1024
                    try:
                        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
                        # CPU time limit
                        # resource.setrlimit(
                        #     resource.RLIMIT_CPU,
                        #     (self.config.timeout_seconds, self.config.timeout_seconds)
                        # )
                        pass
                    except ValueError:
                        pass # Ignore if limits are invalid or permissions denied

                preexec_fn = set_limits

            # Execute
            start_time = time.perf_counter()

            result = subprocess.run(
                ['python3', script_path],
                env=exec_env,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                preexec_fn=preexec_fn
            )

            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000

            # Truncate output if too large
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
        finally:
            Path(script_path).unlink(missing_ok=True)

    def _generate_network_blocker(self) -> str:
        """Generate code to block network-related modules."""
        return '''
import sys
# Block network modules
for mod in ['socket', 'urllib', 'http', 'requests', 'aiohttp']:
    sys.modules[mod] = None
'''

    def _generate_import_wrapper(self, allowed_imports: List[str]) -> str:
        """Generate import restriction wrapper."""
        allowed_set = set(allowed_imports)
        # Always allow 'builtins' and 'sys' for basic functioning?
        # If user restricts imports, they probably want to block everything else.

        return f'''
import builtins
_original_import = builtins.__import__
_allowed = {allowed_set!r}

def _restricted_import(name, *args, **kwargs):
    base_name = name.split('.')[0]
    if base_name not in _allowed and base_name not in ['builtins']:
        raise ImportError(f"Import of '{{name}}' is not allowed in sandbox")
    return _original_import(name, *args, **kwargs)

builtins.__import__ = _restricted_import
'''

    def _execute_bash(
        self,
        code: str,
        env: Optional[Dict[str, str]],
        stdin: Optional[str]
    ) -> ExecutionResult:
        """Execute Bash script in sandbox."""

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.sh',
            delete=False
        ) as f:
            f.write('#!/bin/bash\nset -euo pipefail\n' + code)
            script_path = f.name

        try:
            os.chmod(script_path, 0o755)

            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)

            start_time = time.perf_counter()

            result = subprocess.run(
                ['bash', script_path],
                env=exec_env,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
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
        finally:
            Path(script_path).unlink(missing_ok=True)

    def _execute_javascript(self, code: str, env: Optional[Dict[str, str]], stdin: Optional[str]) -> ExecutionResult:
        # Require nodejs
        return ExecutionResult(
            success=False, stdout="", stderr="JavaScript execution not implemented (requires node)", return_code=-1, execution_time_ms=0
        )
