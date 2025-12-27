import pytest
from skills_ref.execution.sandbox import ScriptSandbox, ScriptLanguage, SandboxConfig
from skills_ref.execution.mermaid_executor import MermaidExecutor, RenderFormat
from skills_ref.security.controls import SecurityGate, SecurityPolicy
from pathlib import Path

def test_python_sandbox_execution():
    sandbox = ScriptSandbox()
    code = "print('Hello from Sandbox')"
    result = sandbox.execute(code, ScriptLanguage.PYTHON)

    assert result.success
    assert "Hello from Sandbox" in result.stdout
    assert result.execution_time_ms > 0

def test_python_sandbox_timeout():
    # Use short timeout
    config = SandboxConfig(timeout_seconds=1)
    sandbox = ScriptSandbox(config)
    # Use a simple infinite loop instead of time.sleep for more reliable timeout testing
    code = "while True: pass"
    result = sandbox.execute(code, ScriptLanguage.PYTHON)

    assert not result.success
    assert result.error is not None and "timed out" in result.error

def test_python_sandbox_import_restriction():
    config = SandboxConfig(allowed_imports=['math']) # only math allowed
    sandbox = ScriptSandbox(config)
    code = "import os"
    result = sandbox.execute(code, ScriptLanguage.PYTHON)

    assert not result.success
    # Check that os import was blocked (message may vary)
    assert "os" in result.stderr and ("not allowed" in result.stderr or "not in the allowed list" in result.stderr)

def test_mermaid_ascii_fallback():
    # Assume mmdc is not installed in test env, check fallback
    executor = MermaidExecutor()
    code = """graph TD
    A[Start] --> B[End]
    """
    result = executor.execute(code, format=RenderFormat.ASCII)

    assert result.success
    assert result.format == RenderFormat.ASCII
    assert "Start" in result.text_output
    assert "End" in result.text_output
    # Check metadata extraction
    assert len(result.metadata['nodes']) == 2
    assert result.metadata['nodes'][0]['id'] == 'A'

def test_security_controls():
    policy = SecurityPolicy(deny_path_traversal=True, skill_root=Path("/skills"))
    gate = SecurityGate(policy)

    # Path traversal check
    # Note: validate_path checks if resolved path is relative to root.
    # Since /skills doesn't exist, resolve might behave differently or we mock.
    # We can test logic without existing paths if we create tmp root.
    pass

@pytest.fixture
def temp_skill_root(tmp_path):
    root = tmp_path / "skills"
    root.mkdir()
    return root

def test_path_traversal(temp_skill_root, tmp_path):
    policy = SecurityPolicy(deny_path_traversal=True, skill_root=temp_skill_root)
    gate = SecurityGate(policy)

    # Valid path
    valid_path = temp_skill_root / "skill.md"
    valid_path.touch()
    valid, err = gate.validate_path(valid_path)
    assert valid

    # Invalid path (symlink outside)
    target = tmp_path / "outside.txt"
    target.touch()
    link = temp_skill_root / "link"
    link.symlink_to(target)

    valid, err = gate.validate_path(link)
    assert not valid
    assert "Path traversal" in err

def test_content_sanitization():
    gate = SecurityGate(SecurityPolicy(sanitize_html=True))
    content = "Hello <script>alert(1)</script>"
    cleaned = gate.sanitize_content(content)
    assert "<script>" not in cleaned
    assert "Hello" in cleaned
