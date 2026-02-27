---
title: "Using scripts in skills"
sidebarTitle: "Using scripts"
description: "How to run commands and bundle executable scripts in your skills."
---

Skills can instruct agents to run shell commands and bundle reusable scripts in a `scripts/` directory. This guide covers one-off commands, self-contained scripts with their own dependencies, and how to design script interfaces for agentic use.

## One-off commands

When an existing package already does what you need, you can reference it directly in your `SKILL.md` instructions without a `scripts/` directory. Many ecosystems provide tools that auto-resolve dependencies at runtime.

<Tabs sync={false}>
  <Tab title="uvx">
    [uvx](https://docs.astral.sh/uv/guides/tools/) runs Python packages in isolated environments with aggressive caching. It ships with [uv](https://docs.astral.sh/uv/).

    ```bash
    uvx ruff@0.8.0 check .
    uvx black@24.10.0 .
    ```

    - Not bundled with Python — requires a separate install.
    - Fast. Caches aggressively so repeat runs are near-instant.
  </Tab>
  <Tab title="pipx">
    [pipx](https://pipx.pypa.io/) runs Python packages in isolated environments. Available via OS package managers (`apt install pipx`, `brew install pipx`).

    ```bash
    pipx run 'black==24.10.0' .
    pipx run 'ruff==0.8.0' check .
    ```

    - Not bundled with Python — requires a separate install.
    - A mature alternative to `uvx`. While `uvx` has become the standard recommendation, `pipx` remains a reliable option with broader OS package manager availability.
  </Tab>
  <Tab title="npx">
    [npx](https://docs.npmjs.com/cli/commands/npx) runs npm packages, downloading them on demand. It ships with npm (which ships with Node.js).

    ```bash
    npx eslint@9 --fix .
    npx create-vite@6 my-app
    ```

    - Bundled with Node.js — no extra install needed.
    - Downloads the package, runs it, and caches it for future use.
    - Pin versions with `npx package@version` for reproducibility.
  </Tab>
  <Tab title="bunx">
    [bunx](https://bun.sh/docs/cli/bunx) is Bun's equivalent of `npx`. It ships with [Bun](https://bun.sh/).

    ```bash
    bunx eslint@9 --fix .
    bunx create-vite@6 my-app
    ```

    - Drop-in replacement for `npx` in Bun-based environments.
    - Only appropriate when the user's environment has Bun rather than Node.js.
  </Tab>
  <Tab title="deno run">
    [deno run](https://docs.deno.com/runtime/reference/cli/run/) runs scripts directly from URLs or specifiers. It ships with [Deno](https://deno.com/).

    ```bash
    deno run npm:create-vite@6 my-app
    deno run --allow-read npm:eslint@9 -- --fix .
    ```

    - Permission flags (`--allow-read`, etc.) are required for filesystem/network access.
    - Use `--` to separate Deno flags from the tool's own flags.
  </Tab>
  <Tab title="go run">
    [go run](https://pkg.go.dev/cmd/go#hdr-Compile_and_run_Go_program) compiles and runs Go packages directly. It is built into the `go` command.

    ```bash
    go run golang.org/x/tools/cmd/goimports@v0.28.0 .
    go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.62.0 run
    ```

    - Built into Go — no extra tooling needed.
    - Pin versions or use `@latest` to make the command explicit.
  </Tab>
</Tabs>

**Tips for one-off commands in skills:**

- **Pin versions** (e.g., `npx eslint@9.0.0`) so the command behaves the same over time.
- **State prerequisites** in your `SKILL.md` (e.g., "Requires Node.js 18+") rather than assuming the agent's environment has them. For runtime-level requirements, use the [`compatibility` frontmatter field](/specification#compatibility-field).
- **Move complex commands into scripts.** A one-off command works well when you're invoking a tool with a few flags. When a command grows complex enough that it's hard to get right on the first try, a tested script in `scripts/` is more reliable.

## Referencing scripts from `SKILL.md`

Use **relative paths from the skill directory root** to reference bundled files. The agent resolves these paths automatically — no absolute paths needed.

List available scripts in your `SKILL.md` so the agent knows they exist:

```markdown SKILL.md
## Available scripts

- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data
```

Then instruct the agent to run them:

````markdown SKILL.md
## Workflow

1. Run the validation script:
   ```bash
   bash scripts/validate.sh "$INPUT_FILE"
   ```

2. Process the results:
   ```bash
   python3 scripts/process.py --input results.json
   ```
````

<Note>
The same relative-path convention works in support files like `references/*.md` — script execution paths (in code blocks) are relative to the **skill directory root**, because the agent runs commands from there.
</Note>

## Self-contained scripts

When you need reusable logic, bundle a script in `scripts/` that declares its own dependencies inline. The agent can run the script with a single command — no separate manifest file or install step required.

Several languages support inline dependency declarations:

<Tabs sync={false}>
  <Tab title="Python">
    [PEP 723](https://peps.python.org/pep-0723/) defines a standard format for inline script metadata. Declare dependencies in a TOML block inside `# ///` markers:

    ```python scripts/extract.py
    # /// script
    # dependencies = [
    #   "beautifulsoup4",
    # ]
    # ///

    from bs4 import BeautifulSoup

    html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
    print(BeautifulSoup(html, "html.parser").select_one("p.info").get_text())
    ```

    Run with [uv](https://docs.astral.sh/uv/) (recommended):

    ```bash
    uv run scripts/extract.py
    ```

    `uv run` creates an isolated environment, installs the declared dependencies, and runs the script. [pipx](https://pipx.pypa.io/) (`pipx run scripts/extract.py`) also supports PEP 723.

    - Pin versions with [PEP 508](https://peps.python.org/pep-0508/) specifiers: `"beautifulsoup4>=4.12,<5"`.
    - Use `requires-python` to constrain the Python version.
    - Use `uv lock --script` to create a lockfile for full reproducibility.
  </Tab>
  <Tab title="Deno">
    Deno's `npm:` and `jsr:` import specifiers make every script self-contained by default:

    ```typescript scripts/extract.ts
    #!/usr/bin/env -S deno run

    import * as cheerio from "npm:cheerio@1.0.0";

    const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
    const $ = cheerio.load(html);
    console.log($("p.info").text());
    ```

    ```bash
    deno run scripts/extract.ts
    ```

    - Use `npm:` for npm packages, `jsr:` for Deno-native packages.
    - Version specifiers follow semver: `@1.0.0` (exact), `@^1.0.0` (compatible).
    - Dependencies are cached globally. Use `--reload` to force re-fetch.
    - Packages with native addons (node-gyp) may not work — packages that ship pre-built binaries work best.
  </Tab>
  <Tab title="Bun">
    Bun auto-installs missing packages at runtime when no `node_modules` directory is found. Pin versions directly in the import path:

    ```typescript scripts/extract.ts
    #!/usr/bin/env bun

    import * as cheerio from "cheerio@1.0.0";

    const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
    const $ = cheerio.load(html);
    console.log($("p.info").text());
    ```

    ```bash
    bun run scripts/extract.ts
    ```

    - No `package.json` or `node_modules` needed. TypeScript works natively.
    - Packages are cached globally. First run downloads; subsequent runs are near-instant.
    - If a `node_modules` directory exists anywhere up the directory tree, auto-install is disabled and Bun falls back to standard Node.js resolution.
  </Tab>
  <Tab title="Ruby">
    Bundler ships with Ruby since 2.6. Use `bundler/inline` to declare gems directly in the script:

    ```ruby scripts/extract.rb
    require 'bundler/inline'

    gemfile do
      source 'https://rubygems.org'
      gem 'nokogiri'
    end

    html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
    doc = Nokogiri::HTML(html)
    puts doc.at_css('p.info').text
    ```

    ```bash
    ruby scripts/extract.rb
    ```

    - Pin versions explicitly (`gem 'nokogiri', '~> 1.16'`) — there is no lockfile.
    - An existing `Gemfile` or `BUNDLE_GEMFILE` env var in the working directory can interfere.
  </Tab>
</Tabs>

## Designing scripts for agentic use

When an agent runs your script, it reads stdout and stderr to decide what to do next. A few design choices make scripts dramatically easier for agents to use.

### Avoid interactive prompts

This is a hard requirement of the agent execution environment. Agents operate in non-interactive shells — they cannot respond to TTY prompts, password dialogs, or confirmation menus. A script that blocks on interactive input will hang indefinitely.

Accept all input via command-line flags, environment variables, or stdin:

```
# Bad: hangs waiting for input
$ python scripts/deploy.py
Target environment: _

# Good: clear error with guidance
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

### Document usage with `--help`

`--help` output is the primary way an agent learns your script's interface. Include a brief description, available flags, and usage examples:

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Process input data and produce a summary report.

Options:
  --format FORMAT    Output format: json, csv, table (default: json)
  --output FILE      Write output to FILE instead of stdout
  --verbose          Print progress to stderr

Examples:
  scripts/process.py data.csv
  scripts/process.py --format csv --output report.csv data.csv
```

Keep it concise — the output enters the agent's context window alongside everything else it's working with.

### Write helpful error messages

When an agent gets an error, the message directly shapes its next attempt. An opaque "Error: invalid input" wastes a turn. Instead, say what went wrong, what was expected, and what to try:

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

### Use structured output

Prefer structured formats — JSON, CSV, TSV — over free-form text. Structured formats can be consumed by both the agent and standard tools (`jq`, `cut`, `awk`), making your script composable in pipelines.

```
# Whitespace-aligned — hard to parse programmatically
NAME          STATUS    CREATED
my-service    running   2025-01-15

# Delimited — unambiguous field boundaries
{"name": "my-service", "status": "running", "created": "2025-01-15"}
```

**Separate data from diagnostics:** send structured data to stdout and progress messages, warnings, and other diagnostics to stderr. This lets the agent capture clean, parseable output while still having access to diagnostic information when needed.

### Further considerations

- **Idempotency.** Agents may retry commands. "Create if not exists" is safer than "create and fail on duplicate."
- **Input constraints.** Reject ambiguous input with a clear error rather than guessing. Use enums and closed sets where possible.
- **Dry-run support.** For destructive or stateful operations, a `--dry-run` flag lets the agent preview what will happen.
- **Meaningful exit codes.** Use distinct exit codes for different failure types (not found, invalid arguments, auth failure) and document them in your `--help` output so the agent knows what each code means.
- **Safe defaults.** Consider whether destructive operations should require explicit confirmation flags (`--confirm`, `--force`) or other safeguards appropriate to the risk level.
- **Predictable output size.** Many agent harnesses automatically truncate tool output beyond a threshold (e.g., 10-30K characters), potentially losing critical information. If your script might produce large output, default to a summary or a reasonable limit, and support flags like `--offset` so the agent can request more information when needed. Alternatively, if output is large and not amenable to pagination, require agents to pass an `--output` flag that specifies either an output file or `-` to explicitly opt in to stdout.
