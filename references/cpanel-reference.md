# cPanel Reference — URL Map & Section Guide

## URL Structure

```
https://<host>:2083/cpsess<TOKEN>/frontend/<theme>/<section>/index.html
```

- `<host>` — IP address or hostname (never a domain with a local /etc/hosts override)
- `<TOKEN>` — numeric session token, changes every login
- `<theme>` — `jupiter` (cPanel 96+) or `paper_lantern` (older installs)

WHM (server admin) uses port `2087` with path `/cgi-bin/webhost/` or direct module paths.

---

## cPanel Sections (Jupiter theme)

| Section | URL path | Purpose |
|---------|----------|---------|
| Home dashboard | `cpanel/index.html` | Main overview |
| File Manager | `filemanager/index.html` | Browse, upload, edit, extract files |
| MySQL Databases | `sql/index.html` | Create databases, users, assign permissions |
| MySQL Wizard | `sql/wizard.html` | Guided DB + user creation |
| phpMyAdmin | `sql/phpmyadmin.html` or external port | Database GUI |
| Email Accounts | `mail/index.html` | Create/delete mailboxes |
| Forwarders | `mail/forwarders.html` | Email forwarding rules |
| PHP Version | `multiphp_manager/index.html` | Per-domain PHP version |
| PHP INI Editor | `multiphp_ini_editor/index.html` | Edit php.ini values |
| Cron Jobs | `cron/index.html` | Scheduled tasks |
| SSL/TLS | `ssl/index.html` | Manage certificates |
| AutoSSL | `autossl/index.html` | Let's Encrypt automation |
| Subdomains | `subdomain/index.html` | Create/remove subdomains |
| Addon Domains | `addon/index.html` | Add hosted domains |
| DNS Zone Editor | `zone_editor/index.html` | A, CNAME, MX, TXT records |
| Error Pages | `errorpages/index.html` | Custom 404/500 pages |
| Redirects | `redirects/index.html` | 301/302 URL redirects |
| Terminal | `terminal/index.html` | In-browser shell |
| Git Version Control | `git/index.html` | Manage git repos |
| Node.js | `nodejs_selector/index.html` | Node.js app manager |
| Python | `python_selector/index.html` | Python app manager |
| Backup | `backup/index.html` | Manual backup/restore |
| Backup Wizard | `backup_wizard/index.html` | Guided backup |
| Disk Usage | `diskusage/index.html` | Storage breakdown |
| Logs | `logs/index.html` | Access/error log viewer |
| IP Blocker | `ipblock/index.html` | Block IPs at server level |
| Hotlink Protection | `hotlink/index.html` | Prevent image leeching |
| Password & Security | `passwd/index.html` | Change cPanel password |
| Two-Factor Auth | `twofa/index.html` | 2FA settings |
| API Tokens | `api_tokens/index.html` | Generate API access tokens |

---

## WHM Sections (Port 2087)

| Section | Path | Purpose |
|---------|------|---------|
| Home | `/` | Server overview |
| Account List | `scripts/listaccts` | View all cPanel accounts |
| Create Account | `scripts/createacct` | New hosting account |
| CSF Firewall | `cgi/configserver/csf.cgi` | ConfigServer firewall (if installed) |
| EasyApache 4 | `cgi/easyapache4/index.cgi` | Global PHP/Apache config |
| Service Status | `scripts/srvstatus` | Apache, MySQL, FTP status |
| Restart Services | `scripts/restartsrv_httpd` | Restart Apache |
| WHM API | `json-api/` | Programmatic access |

---

## File Manager Query Parameters

```
?dir=/home/user/public_html/subfolder/    # Open at a specific directory
?fileop=upload                             # Jump directly to upload panel
```

---

## Theme Detection

To detect which theme is active after login:

```bash
browser-use eval "window.location.href"
# If URL contains /jupiter/ → new theme
# If URL contains /paper_lantern/ → legacy theme
```

Both themes have the same section structure; only the URL path prefix differs.

---

## Common File Paths on cPanel Servers

| Path | Purpose |
|------|---------|
| `/home/<user>/public_html/` | Main web root |
| `/home/<user>/public_html/active/<project>/` | Subdirectory apps |
| `/home/<user>/logs/` | Access and error logs |
| `/home/<user>/.htaccess` | Apache overrides |
| `/home/<user>/tmp/` | Temp files |
| `/home3/<user>/public_html/` | Alternate partition (some hosts) |
| `/etc/apache2/` | Apache config (WHM only) |

---

## File Size Limits

Default cPanel PHP upload limits (check with `phpinfo()` or PHP INI Editor):
- `upload_max_filesize`: 256M (varies)
- `post_max_size`: 256M (varies)
- `max_execution_time`: 300s

To upload files larger than the limit: use File Manager's native upload (bypasses PHP), or zip + extract via Terminal.

---

## API Token Authentication (No Browser Required)

For scripted operations, generate an API token in cPanel → API Tokens, then:

```bash
curl -u "user:token" "https://<ip>:2083/execute/Fileman/list_files?dir=/public_html/"
```

This uses the UAPI (Unified API) — faster than browser automation for file listing, backup, and database operations when credentials are available.

---

## Known Quirks

1. **Session tokens expire** after a period of inactivity — re-login if getting 401 or redirect to login
2. **File Manager UI is slow** for 10+ files — use UAPI `save_file_content` in a loop instead of clicking through the UI
3. **Paper Lantern was deprecated** in cPanel 11.96; older hosts may still use it
4. **Jupiter theme uses React** — some elements load asynchronously; use `browser-use wait selector` before `state`
5. **Terminal WebSocket fails in headless Chromium** — the xterm.js terminal connects but keyboard input is silently dropped in headless mode; commands never execute. Use UAPI `save_file_content` / `get_file_content` for all file operations instead. Only use the terminal in `--headed` mode with a visible browser window.
6. **phpMyAdmin session is separate** — logging into cPanel does not auto-authenticate phpMyAdmin on some hosts
7. **CSF blocks repeated login failures** — after multiple failed attempts, the dev machine IP may be auto-blocked; whitelist via WHM → CSF → Allow IP
8. **Username format varies by host** — some cPanel accounts require `username@domain.com` (email format); if plain `username` fails with "login is invalid", try the email format
9. **`cpsess` token may not appear immediately** — wait 3–4 seconds after `networkidle` before parsing `window.location.href`; the redirect sometimes lags

## UAPI via Session Token

The most reliable approach for file operations in headless mode. After browser login, the session cookie is active — call UAPI endpoints directly with `fetch()` inside `page.evaluate()`, no separate API token required.

```
POST /<cpsessTOKEN>/execute/Fileman/get_file_content
     dir=/home/user/public_html  file=config.php

POST /<cpsessTOKEN>/execute/Fileman/save_file_content
     dir=/home/user/public_html  file=config.php  content=<file-contents>

POST /<cpsessToken>/execute/Fileman/list_files
     dir=/home/user/public_html

POST /<cpsessToken>/execute/Fileman/create_directory
     path=/home/user/public_html/newdir
```

Response shape: `{ "status": 1, "data": { ... } }` on success; `"status": 0` on error.

See `SKILL.md` → *UAPI via Session Token* for a complete Playwright Python implementation.
