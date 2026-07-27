# cpanel-navigator

> Agent Skill — automates cPanel and WHM tasks via browser automation

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Agent Skills](https://img.shields.io/badge/Agent_Skills-Compatible-blue)
![Works with Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-orange)

Most developers hate clicking through cPanel. This skill teaches AI agents to do it instead — file uploads, database creation, PHP config, DNS, cron jobs, and more — using `browser-use` or Playwright Python.

---

## What it does

| Task | Example prompt |
|------|----------------|
| Upload a file | `"Upload index.php to /public_html/active/myapp/"` |
| Read a live file | `"Read /public_html/config.php and show me the DB credentials"` |
| Overwrite a file | `"Replace index.php on the server with the local version"` |
| Create a database | `"Create MySQL database myapp_db in cPanel"` |
| Change PHP version | `"Switch the site to PHP 8.2 in MultiPHP Manager"` |
| Add a cron job | `"Schedule checkamount.php to run every 5 minutes"` |
| Add a DNS record | `"Add a CNAME record for mail.example.com"` |
| WHM firewall | `"Whitelist IP 203.0.113.10 in CSF firewall"` |
| Check services | `"Is Apache running? Check WHM service status"` |

---

## Highlights

- **Headless-safe file I/O** — reads and writes files via cPanel's UAPI `Fileman` endpoints inside `page.evaluate()`. No clicking through File Manager UI, no WebSocket terminal issues.
- **Two automation paths** — `browser-use` CLI for simple navigation tasks; Playwright Python for precise UAPI calls and large file operations.
- **Login quirks handled** — email-format username fallback, self-signed cert acceptance, `cpsess` token timing, CSF lockout awareness.
- **WHM support** — covers port 2087 server-admin tasks: firewall, EasyApache, account management, service restarts.
- **Full URL reference** — 30+ cPanel sections mapped, both Jupiter and Paper Lantern themes.

---

## Requirements

- [browser-use](https://github.com/browser-use/browser-use) CLI **or** Python 3 + `uvx` (for the Playwright fallback)
- cPanel account credentials (username + password)
- cPanel server reachable on port 2083

---

## Quick start

### 1. Install

```bash
# From zip
unzip cpanel-navigator.zip -d ~/.claude/skills/

# From GitHub
git clone https://github.com/antonynjagi/cpanel-navigator ~/.claude/skills/cpanel-navigator
```

### 2. Verify browser-use

```bash
browser-use doctor
```

If `browser-use` is unavailable, use the Playwright fallback (no extra install on most systems):

```bash
uvx --with playwright python3 --version
python3 -m playwright install chromium
```

### 3. Use it

The skill activates automatically. Just describe the task:

```
"Log into cPanel at 203.0.113.10 and upload /var/www/html/project/index.php
to /public_html/active/myapp/"
```

```
"Read /public_html/active/myapp/config.php from cPanel"
```

```
"In WHM, whitelist IP 203.0.113.10 in CSF"
```

---

## File structure

```
cpanel-navigator/
├── SKILL.md                     # Agent instructions (auto-loaded)
├── CPANEL.md                    # Human-readable overview
├── README.md                    # This file
└── references/
    └── cpanel-reference.md      # Full URL map, quirks, UAPI reference
```

---

## Agent compatibility

This skill follows the open [Agent Skills specification](https://agentskills.io/specification).

| Agent | Skills directory |
|-------|-----------------|
| Claude Code | `~/.claude/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| OpenCode | `~/.opencode/skills/` |
| Cursor | `.cursor/skills/` (project-local) |
| Codex | `~/.agents/skills/` |

---

## Known limitations

| Issue | Details |
|-------|---------|
| Terminal input silently dropped in headless mode | cPanel's xterm.js WebSocket accepts the connection but drops all keyboard input in headless Chromium. Use the UAPI `save_file_content` approach for all file writes instead. |
| `cpsess` token can lag | Wait 3–4 seconds after `networkidle` before parsing the URL for the session token. |
| Username format varies | Some hosts require `username@domain.com`. If plain username fails, try the email format. |
| CSF auto-blocks repeated failures | Multiple failed logins may get the dev machine IP blocked. Whitelist via WHM → CSF → Allow IP. |

Full quirks list: [`references/cpanel-reference.md`](references/cpanel-reference.md)

---

## Security

Never hardcode credentials in prompts you share publicly. Pass them at runtime or via environment variables. This skill contains no credentials.

---

## Contributing

Found a cPanel section not covered? Open a PR or issue. Feature requests welcome.

Discord: [Agent Skills community](https://discord.gg/MKPE9g8aUy)

---

## License

MIT — free to use, fork, and adapt.
