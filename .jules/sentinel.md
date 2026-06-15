## 2025-06-07 - [Prompt XML Injection]
**Vulnerability:** In prompt generation (`prompt.py`), `skill_md_path` was interpolated directly into an XML element without being escaped. An attacker who controls directory names could include tags like `</location><skill><name>malicious</name>...` to inject fake agent instructions or prompt escape commands.
**Learning:** Even internal file paths must be considered potentially tainted if they include portions controlled by external users/inputs (such as downloaded skill repositories).
**Prevention:** Always use `html.escape()` or dedicated XML building tools to serialize paths, names, and descriptions when constructing LLM prompts using XML.

## 2025-06-08 - [Unbounded File Read DoS & Stack Trace Leak]
**Vulnerability:** In `parser.py` and `validator.py`, the CLI utility read files using `Path.read_text()` without limits or proper exception handling. Maliciously crafted files (e.g., massive size, invalid encoding, or unreadable permissions) could cause a DoS (Out of Memory) or crash the CLI, leaking internal Python stack traces to the user/attacker via `OSError` or `UnicodeDecodeError`.
**Learning:** `Path.read_text()` is dangerous for reading external user-supplied files because it loads everything into memory and doesn't handle OS-level errors securely. CLI applications must fail gracefully and not leak their internal execution context to external users.
**Prevention:** Use bounded file reads with `open()`, set explicit read limits (e.g., 1MB), and catch low-level exceptions like `OSError` and `UnicodeDecodeError` to return sanitized error messages.
## 2025-06-09 - [Path Leakage in Error Handling]
**Vulnerability:** Path leakage via `OSError` messages and `skill_dir` representations exposing internal server structure in error output.
**Learning:** Exception handling for missing or unreadable files can unintentionally leak full system paths if the raw exception or absolute path is formatted into user-facing output.
**Prevention:** Sanitize error messages by relying solely on the final path component (`skill_dir.name`) and restricting error string representation to safe subsets like `e.strerror`.
## 2026-06-11 - [Unhandled OSError and Symlink Loop Path Leakage]
**Vulnerability:** Unhandled `OSError` (such as `PermissionError`) during initial filesystem checks (`exists()`, `is_dir()`) and `RuntimeError` from symlink loops inside `resolve()` could crash the CLI, leaking the internal Python stack trace and exact absolute server paths to the user.
**Learning:** Even simple operations like `Path.exists()` can raise exceptions like `PermissionError` on restricted parent directories, and `Path.resolve()` can hit a `RuntimeError` from a symlink loop. If these aren't caught and sanitized at the application boundaries, internal context is leaked.
**Prevention:** Wrap all path I/O operations (including exists/is_dir) and resolution in `try...except (OSError, RuntimeError)` blocks. Fail gracefully at CLI entry points by catching generic `Exception` to prevent any stray tracebacks, and use `.name` for safe error reflections.
## 2024-05-24 - Information Leakage via Error Messages
**Vulnerability:** Information leakage where internal system paths or stack traces were exposed via `str(e)` on `RuntimeError` during path operations in `src/skills_ref/parser.py` and `src/skills_ref/validator.py`.
**Learning:** `RuntimeError` during file system operations can contain sensitive internal paths or stack traces that shouldn't be exposed to external users. This occurred because `str(e)` was directly used to construct the user-facing error message.
**Prevention:** Avoid using `str(e)` directly on exceptions like `RuntimeError` from path operations; use `path.name` or generic fallback messages like "Symlink loop or unresolvable path" instead. Strictly sanitize error and exception messages.
