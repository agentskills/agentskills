# cpanel-navigator

> An Agent Skill for navigating and automating cPanel web hosting tasks via browser automation.

## What it does

`cpanel-navigator` teaches AI agents how to operate cPanel (port 2083) and WHM (port 2087) through the browser using the `browser-use` CLI. Instead of manually uploading files or clicking through menus, you describe what you need and the agent handles the navigation.

### Supported tasks

| Task | Example prompt |
|------|---------------|
| Upload files to live server | "Upload bot.php to /public_html/active/poultry/" |
| Browse and manage files | "Open File Manager at /public_html/ and show me what's there" |
| Create a database | "Create a MySQL database called poultry_db in cPanel" |
| Run terminal commands | "Open the cPanel terminal and extract deploy.zip in public_html" |
| Change PHP version | "Switch the site to PHP 8.2 in MultiPHP Manager" |
| Add a cron job | "Schedule a cron job to run bot.php every 5 minutes" |
| Manage DNS records | "Add a CNAME record for mail.example.com" |
| Whitelist an IP in WHM | "Add 203.0.113.10 to the CSF firewall whitelist in WHM" |
| Check service status | "Is Apache running? Check WHM service status" |

## Requirements

- [`browser-use`](https://github.com/browser-use/browser-use) CLI installed and working (`browser-use doctor`)
- cPanel access credentials (username + password)
- cPanel server reachable on port 2083 (IP or hostname)

## Installation

### Claude Code

Copy the skill folder into your global skills directory:

```bash
# Option A: from the zip
unzip cpanel-navigator.zip -d ~/.claude/skills/

# Option B: clone from GitHub (if hosted)
git clone https://github.com/<your-handle>/cpanel-navigator ~/.claude/skills/cpanel-navigator
```

The skill activates automatically when you describe a cPanel task. Trigger phrases include:

- "deploy to cpanel"
- "upload via cpanel file manager"
- "navigate cpanel"
- "cpanel terminal"
- "push to production via cpanel"

### Other agents (Cursor, Gemini CLI, OpenCode, etc.)

This skill follows the open [Agent Skills specification](https://agentskills.io/specification) and works with any compatible agent. Check your agent's documentation for the skills directory location — common paths:

| Agent | Skills directory |
|-------|-----------------|
| Claude Code | `~/.claude/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| OpenCode | `~/.opencode/skills/` |
| Cursor | `.cursor/skills/` (project) |
| Codex | `~/.agents/skills/` |

## Usage

Once installed, describe what you want in plain language:

```
"Log into cPanel at <your-server-ip> with username <your-username> and upload
/var/www/html/project/bot.php to /public_html/active/myapp/"
```

```
"Read the file /home/<your-cpanel-user>/public_html/config.php from cPanel
and show me the database credentials"
```

```
"In WHM, go to CSF firewall and whitelist IP 203.0.113.10"
```

The agent will:
1. Open a browser and navigate to `https://<ip>:2083`
2. Authenticate with your credentials
3. Navigate to the relevant section
4. Complete the task step by step
5. Take a screenshot to confirm success

## Security note

Never hardcode credentials in prompts you share publicly. Pass them interactively or via environment variables. The skill itself contains no credentials.

## File structure

```
cpanel-navigator/
├── SKILL.md                        # Agent instructions (loaded automatically)
├── CPANEL.md                       # This file — human-readable README
└── references/
    └── cpanel-reference.md         # Full URL map, section guide, known quirks
```

## Contributing / Feedback

Found a cPanel section not covered? Open an issue or PR on GitHub, or share on the [Agent Skills Discord](https://discord.gg/MKPE9g8aUy).

## License

MIT — free to use, fork, and adapt.
