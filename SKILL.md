---
name: cpanel-navigator
description: Automates cPanel web hosting control panel tasks via browser automation. Use when the user needs to upload files to a live server, manage databases, configure PHP settings, create email accounts, manage DNS records, access the in-browser terminal, or perform any operation inside a cPanel or WHM interface. Triggers on phrases like "deploy to cpanel", "upload via cpanel file manager", "create database in cpanel", "cpanel terminal", "navigate cpanel", or "push to production via cpanel".
allowed-tools: Bash
---

# cPanel Navigator

Automate cPanel (port 2083) and WHM (port 2087) tasks using the `browser-use` CLI. Covers authentication, File Manager uploads, database management, PHP configuration, email accounts, DNS, and the in-browser Terminal.

Read `references/cpanel-reference.md` for the full section URL map, theme differences, and known quirks.

## Prerequisites

**Option A — browser-use CLI (recommended)**
```bash
browser-use doctor    # Verify browser-use is installed and working
```

**Option B — Playwright Python (fallback, no extra install on most systems)**
```bash
uvx --with playwright python3 --version   # verify uvx is available
python3 -m playwright install chromium    # install browser once
```

Use Option B when `browser-use` is not available or when you need direct `page.evaluate()` calls for UAPI operations (see *UAPI via Session Token* below).

## Authentication

cPanel runs HTTPS on port 2083. Always connect via IP or the real hostname — not a domain that may point locally via `/etc/hosts`.

**Username format:** Some cPanel accounts require the full email format `username@domain.com` rather than just `username`. If plain username returns "login is invalid", try the email format.

```bash
# 1. Open the login page
browser-use open "https://<ip-or-hostname>:2083"

# 2. Inspect the login form
browser-use state

# 3. Fill credentials and submit
browser-use input <user-index> "cpanel-username"
browser-use input <pass-index> "password"
browser-use click <login-button-index>

# 4. Confirm successful login
browser-use wait text "cPanel"
browser-use screenshot
```

After login, all cPanel URLs contain a session token in the form `cpsess<TOKEN>`. Extract it once and reuse for direct navigation:

```bash
browser-use eval "window.location.href"
# → https://<ip>:2083/cpsess1234567890/frontend/jupiter/index.html
#                          ^^^^^^^^^^^^ this is the token
```

Self-signed certificate warnings: headless Chromium accepts them automatically. If `--headed` mode is required, ask the user to accept the cert manually first.

## File Manager — Upload Files

The most frequent deployment task.

```bash
# Option A: Navigate to File Manager, then upload
browser-use open "https://<ip>:2083/cpsess<TOKEN>/frontend/jupiter/filemanager/index.html?dir=/home/user/public_html/target/"
browser-use wait selector ".filemanager"
browser-use state

# Click the Upload toolbar button
browser-use click <upload-button-index>

# In the upload panel, find the file input and attach the local file
browser-use state
browser-use upload <file-input-index> "/absolute/local/path/to/file.php"
browser-use wait text "100%"
browser-use screenshot
```

**For multiple files:** zip them locally, upload the zip, then extract via the File Manager context menu or the Terminal.

```bash
# Zip locally before uploading
# (run this in Bash, not browser-use)
zip -j /tmp/deploy.zip /path/to/file1.php /path/to/file2.php
```

Then upload `/tmp/deploy.zip` via File Manager, right-click it → Extract.

## File Manager — Edit a File In-Place

```bash
browser-use open "https://<ip>:2083/cpsess<TOKEN>/frontend/jupiter/filemanager/index.html?dir=/home/user/public_html/"
browser-use state

# Right-click the target file
browser-use rightclick <file-row-index>
browser-use state   # Context menu appears — find "Edit" or "Code Editor"
browser-use click <edit-index>

# Wait for editor to load, then type new content
browser-use wait selector ".code-editor"
```

For large or binary files, uploading is more reliable than in-browser editing.

## cPanel Terminal (In-Browser Shell)

> ⚠️ **Headless limitation:** The Terminal uses a WebSocket-backed xterm.js session. In headless Chromium the WebSocket handshake completes but **keyboard input is silently swallowed** — commands never reach the shell. The terminal page appears to load but nothing executes.
>
> **Use the UAPI approach below instead** for all file read/write/delete operations. Reserve the in-browser Terminal for cases where a headed (`--headed`) browser session is available and the user can confirm the terminal is interactive.

```bash
browser-use open "https://<ip>:2083/cpsess<TOKEN>/frontend/jupiter/terminal/index.html"
browser-use wait selector ".xterm"
browser-use click <terminal-index>
browser-use type "ls /home/user/public_html/\n"
browser-use screenshot
```

Intended uses when running headed:
- Extracting uploaded zip files: `unzip /home/user/public_html/deploy.zip -d /home/user/public_html/target/`
- Running PHP/Composer: `php composer.phar install`
- Checking logs: `tail -n 50 /home/user/public_html/error_log`
- Setting permissions: `chmod 644 /home/user/public_html/config.php`

## UAPI via Session Token (Preferred for File Operations)

Once logged in via Playwright, the session cookie is active and the browser can call cPanel's UAPI directly with `fetch()` — **no separate API token needed**. This is more reliable than clicking through the File Manager UI and works in headless mode.

```python
# Full Playwright Python pattern — use this when browser-use terminal fails
import asyncio
from playwright.async_api import async_playwright

async def cpanel_session(host, username, password):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(ignore_https_errors=True)
        page = await ctx.new_page()

        # Login
        await page.goto(f"https://{host}:2083", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.fill('#user', username)
        await page.fill('#pass', password)
        await page.evaluate("document.querySelector('#login_form').submit()")
        await page.wait_for_load_state("networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # Extract session token
        url = page.url
        token = next(p for p in url.split("/") if p.startswith("cpsess"))

        # Read a file
        result = await page.evaluate("""
            async ([token, dir_path, fname]) => {
                const body = new URLSearchParams({dir: dir_path, file: fname}).toString();
                const r = await fetch(`/${token}/execute/Fileman/get_file_content`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: body
                });
                return await r.json();
            }
        """, [token, "/home/user/public_html", "config.php"])

        if result.get('status') == 1:
            print(result['data']['content'])

        # Write / overwrite a file
        new_content = "<?php // updated content"
        await page.evaluate("""
            async ([token, dir_path, fname, content]) => {
                const body = new URLSearchParams({dir: dir_path, file: fname, content: content}).toString();
                const r = await fetch(`/${token}/execute/Fileman/save_file_content`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: body
                });
                return await r.json();
            }
        """, [token, "/home/user/public_html", "config.php", new_content])

        await browser.close()

asyncio.run(cpanel_session("<ip>", "<username>", "<password>"))
```

Run with:
```bash
uvx --with playwright python3 cpanel_task.py
```

**Available UAPI Fileman endpoints** (all via POST to `/<token>/execute/Fileman/<endpoint>`):

| Endpoint | Parameters | Purpose |
|----------|-----------|---------|
| `get_file_content` | `dir`, `file` | Read file contents |
| `save_file_content` | `dir`, `file`, `content` | Write / overwrite file |
| `list_files` | `dir` | List directory contents |
| `create_directory` | `path` | Create a directory |

## MySQL Databases

```bash
browser-use open "https://<ip>:2083/cpsess<TOKEN>/frontend/jupiter/sql/index.html"
browser-use state

# Create a new database
browser-use input <new-db-name-index> "dbname"
browser-use click <create-db-button-index>

# Create a user
browser-use scroll down
browser-use input <new-user-index> "dbuser"
browser-use input <new-pass-index> "dbpassword"
browser-use click <create-user-button-index>

# Assign user to database
browser-use scroll down
browser-use select <user-dropdown-index> "cpanelusername_dbuser"
browser-use select <db-dropdown-index> "cpanelusername_dbname"
browser-use click <add-user-to-db-button-index>
```

## PHP Version (MultiPHP Manager)

```bash
browser-use open "https://<ip>:2083/cpsess<TOKEN>/frontend/jupiter/multiphp_manager/index.html"
browser-use state
# Select the domain row, choose version from dropdown, click Apply
```

## WHM (Server-Level Admin — Port 2087)

WHM is for root/reseller operations. Same browser-use workflow, different port.

```bash
browser-use open "https://<ip>:2087"
# Authenticate as root or reseller
```

Common WHM paths (read `references/cpanel-reference.md` for full list):
- CSF Firewall: Plugins > ConfigServer Security & Firewall
- IP whitelist: CSF > Allow IP
- PHP global config: Software > EasyApache 4
- Service status: Server Status > Service Status

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Redirected to login mid-session | Session expired — re-authenticate, extract new `cpsess` token |
| Upload stuck at 0% | Check file size limit in PHP INI Editor; use UAPI `save_file_content` for programmatic writes |
| Terminal loads but commands do nothing | **Expected in headless mode** — WebSocket input is silently dropped; use UAPI `save_file_content` instead |
| Terminal shows "WebSocket error" | cPanel Terminal service is disabled in WHM → Service Configuration; use UAPI as alternative |
| `browser-use state` shows no elements | Page still loading — add `browser-use wait text "cPanel"` before state |
| Self-signed cert error in `--headed` | User must click "Advanced" → "Proceed" once; headless mode handles it automatically |
| Login redirects to wrong URL | Some servers use email-format username (`user@domain.com`) — try both formats |
| `cpsess` token not found in URL | Wait an extra 2–3 seconds after `networkidle` before parsing the URL |

```bash
# If browser session breaks
browser-use close
browser-use open "https://<ip>:2083"
```
