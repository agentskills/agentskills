---
title: "Agent Skills vs AGENTS.md vs MCP"
sidebarTitle: "Comparison Guide"
description: "Understanding the differences between Agent Skills, AGENTS.md, and the Model Context Protocol (MCP)."
---

The AI agent ecosystem has several standards and formats that serve different purposes. This guide clarifies the differences between Agent Skills, AGENTS.md, and the Model Context Protocol (MCP) to help you choose the right approach for your needs.

## Quick Overview

| Standard | Purpose | Scope | Maintained By |
|----------|---------|-------|---------------|
| **Agent Skills** | Teach agents new capabilities with reusable skill packages | Cross-agent, capability-focused | [Anthropic](https://anthropic.com) (open standard) |
| **AGENTS.md** | Provide project-specific instructions for coding agents | Repository-focused, coding workflows | [Agentic AI Foundation](https://aaif.io) (Linux Foundation) |
| **MCP** | Connect AI applications to external data sources and tools | Integration-focused, runtime connections | [Anthropic](https://anthropic.com) (open standard) |

## Detailed Feature Comparison

| Feature | Agent Skills | AGENTS.md | MCP |
|---------|--------------|-----------|-----|
| **What it provides** | Procedural knowledge | Project-specific instructions | Tool connectivity |
| **Persistence** | Across conversations | Within repository | Continuous connection |
| **Contains** | Instructions + code + assets | Markdown instructions | Tool definitions + data access |
| **When it loads** | Dynamically, as needed | When agent works in repo | Always available |
| **Can include code** | Yes | No | Yes (server-side) |
| **Best for** | Specialized expertise | Coding workflows | Data access |
| **Architecture** | Structured framework with progressive disclosure | Lightweight convention (simple Markdown) | Client-server protocol |
| **Ecosystem** | Open standard, multi-agent support | Open convention, multi-agent support | Open standard, multi-agent support |

## Agent Skills

Agent Skills are folders of instructions, scripts, and resources that agents can discover and use to perform specific tasks more accurately and efficiently. Think of skills as specialized "training manuals" that give agents expertise in specific domains—from working with Excel spreadsheets to following your organization's brand guidelines.

### How Skills Work

Skills use **progressive disclosure** to keep agents efficient:

1. **Discovery (~100 tokens)**: When working on tasks, agents first scan Skill metadata (names and descriptions) to identify relevant matches
2. **Activation (<5k tokens)**: If a Skill matches, the agent loads the full instructions from the SKILL.md file
3. **Execution (as needed)**: If the Skill includes executable code or reference files, those load only when required

This architecture means you can have many Skills available without overwhelming the agent's context window. The agent accesses exactly what it needs, when it needs it.

### Key Characteristics

Skills use a `SKILL.md` file with YAML frontmatter containing metadata (name, description) followed by Markdown instructions. They can bundle executable code, templates, and reference materials, making them suitable for complex, multi-step tasks that need to be performed consistently.

### When to Use Agent Skills

Choose Skills when you need agents to perform specialized tasks consistently and efficiently:

| Use Case | Example |
|----------|---------|
| **Organizational workflows** | Brand guidelines, compliance procedures, document templates |
| **Domain expertise** | Excel formulas, PDF manipulation, data analysis |
| **Personal preferences** | Note-taking systems, coding patterns, research methods |
| **Repeatable procedures** | Security review processes, code formatting standards |

### Example Structure

```
pdf-processing/
├── SKILL.md          # Instructions + metadata
├── scripts/          # Executable code
├── references/       # Documentation
└── assets/           # Templates, resources
```

### Example SKILL.md

```yaml
---
name: brand-guidelines
description: Apply company brand standards to documents and presentations. Use when creating marketing materials, presentations, or any customer-facing content.
---

# Brand Guidelines

## Color Palette
- Primary: #1a73e8
- Secondary: #34a853
- Accent: #ea4335

## Typography
- Headlines: Inter Bold
- Body: Inter Regular

## When to Apply
Use these guidelines when Claude creates presentations, documents, or any visual content for external audiences.
```

## AGENTS.md

AGENTS.md is a simple, open format for guiding coding agents, used by over 60,000 open-source projects. Think of it as a README specifically written for AI agents rather than humans—a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project.

### How AGENTS.md Works

AGENTS.md complements README.md by containing the extra, sometimes detailed context coding agents need: build steps, tests, and conventions that might clutter a README or aren't relevant to human contributors. The format is intentionally kept separate to:

- Give agents a clear, predictable place for instructions
- Keep READMEs concise and focused on human contributors
- Provide precise, agent-focused guidance that complements existing documentation

### Key Characteristics

| Aspect | Description |
|--------|-------------|
| **Format** | Standard Markdown with no required schema |
| **Location** | Root of repository (or nested in monorepos) |
| **Precedence** | Nearest file to edited code takes precedence |
| **Flexibility** | Any headings or structure you prefer |

### When to Use AGENTS.md

Use AGENTS.md when you want to standardize how AI coding agents interact with your repository:

| Use Case | Example |
|----------|---------|
| **Build instructions** | `pnpm install`, `pnpm dev`, `pnpm test` |
| **Code style rules** | TypeScript strict mode, single quotes, no semicolons |
| **PR conventions** | Title format, required checks, commit message style |
| **Testing requirements** | How to run tests, coverage expectations |
| **Security considerations** | Sensitive areas, required reviews |

### Example Content

```markdown
# AGENTS.md

## Setup commands
- Install deps: `pnpm install`
- Start dev server: `pnpm dev`
- Run tests: `pnpm test`

## Code style
- TypeScript strict mode
- Single quotes, no semicolons
- Use functional patterns where possible

## Testing instructions
- Run `pnpm turbo run test --filter <project_name>` for package tests
- Fix any test or type errors until the whole suite is green
- Add or update tests for the code you change

## PR instructions
- Title format: [component] Description
- Always run `pnpm lint` and `pnpm test` before committing
```

### Monorepo Support

For large monorepos, place additional AGENTS.md files inside each package. Agents automatically read the nearest file in the directory tree, so the closest one takes precedence and every subproject can ship tailored instructions.

## Model Context Protocol (MCP)

MCP is an open-source standard for connecting AI applications to external systems where data lives—content repositories, business tools, databases, and development environments. Think of it like a USB-C port for AI: a standardized way to connect AI applications to data sources, tools, and workflows.

### How MCP Works

MCP provides a standardized way to connect AI applications to your tools and data sources. Instead of building custom integrations for each data source, you build against a single protocol:

```
AI Application (Client)
        ↓
    MCP Protocol
        ↓
MCP Server (exposes tools/data)
        ↓
External System (database, API, etc.)
```

MCP servers expose data and capabilities; MCP clients (like Claude, ChatGPT) connect to these servers. The connection is continuous and bidirectional, enabling real-time data access and actions.

### Key Characteristics

| Aspect | Description |
|--------|-------------|
| **Architecture** | Client-server protocol |
| **Connection** | Continuous, bidirectional |
| **Scope** | External systems integration |
| **Capability** | Data access + tool execution |

### When to Use MCP

Choose MCP when you need AI applications to access external data or perform actions in real-time:

| Use Case | Example |
|----------|---------|
| **Access external data** | Google Drive, Slack, GitHub, databases |
| **Use business tools** | CRM systems, project management platforms |
| **Connect to dev environments** | Local files, IDEs, version control |
| **Integrate custom systems** | Your proprietary tools and data sources |

## Choosing the Right Approach

These standards are complementary rather than competing. Here's a decision framework:

### When to Use What

| Scenario | Recommended Approach |
|----------|---------------------|
| Teaching agents *how* to do something | **Agent Skills** |
| Telling agents *what* to do in your codebase | **AGENTS.md** |
| Giving agents *access* to tools and data | **MCP** |
| Repeating the same instructions across conversations | **Agent Skills** |
| Standardizing agent behavior in a repository | **AGENTS.md** |
| Connecting to external APIs or databases | **MCP** |

### Key Differences Summarized

| Question | Agent Skills | AGENTS.md | MCP |
|----------|--------------|-----------|-----|
| **What does it teach?** | How to perform tasks | What to do in this project | How to access external systems |
| **Where does it live?** | Skill directories (anywhere) | Repository root | MCP servers |
| **When is it loaded?** | On-demand when relevant | When working in the repo | Always connected |
| **Is it portable?** | Yes, across projects | No, project-specific | Yes, across applications |
| **Does it execute code?** | Yes, bundled scripts | No | Yes, server-side tools |

### Combining Approaches

Many projects benefit from using multiple standards together:

- **Skills + MCP**: A skill might reference MCP servers for accessing external data while performing its task. MCP connects Claude to data; Skills teach Claude what to do with that data.

- **Skills + AGENTS.md**: An AGENTS.md file might mention available skills that agents should use for certain tasks. Skills provide portable expertise; AGENTS.md provides project-specific context.

- **All three together**: Use MCP for connectivity, Skills for procedural knowledge, and AGENTS.md for project-specific instructions.

### Example: Research Agent Workflow

Here's how all three can work together:

1. **Project context (AGENTS.md)**: Defines how to work with the repository, coding standards, and PR conventions
2. **MCP connections**: Connect to Google Drive for documents, GitHub for code, web search for real-time information
3. **Skills**: Provide analytical frameworks like competitive analysis procedures, data visualization standards, or report formatting guidelines

## Adoption

### Agent Skills

Supported by Claude Code, Cursor, VS Code, GitHub, OpenAI Codex, Amp, Goose, Letta, OpenCode, and others. See the [home page](/) for the full list.

### AGENTS.md

Supported by OpenAI Codex, Cursor, VS Code, Devin, Gemini CLI, GitHub Copilot, Amp, Goose, Windsurf, Factory, Warp, Zed, RooCode, and many others. The format is stewarded by the Agentic AI Foundation under the Linux Foundation.

### MCP

Supported by Claude, ChatGPT, and a growing ecosystem of AI applications. MCP servers exist for databases (PostgreSQL, SQLite), productivity tools (Google Drive, Slack, Notion), development tools (Git, Sentry), and more.

## Common Questions

### Skills vs. AGENTS.md: When to use what?

**Use AGENTS.md when** you're giving project-specific instructions that apply only to a particular repository. AGENTS.md is reactive—agents read it when working in your codebase.

**Use Skills when** you have procedures or expertise that you'll need repeatedly across different projects. Skills are proactive—agents know when to apply them—and persistent across conversations.

### Skills vs. MCP: When to use what?

**Use MCP when** you need to *access* data or *connect* to external systems. MCP is about connectivity.

**Use Skills when** you need to explain *how* to use data or follow procedures. Skills are about procedural knowledge.

**Use them together when** you need both: MCP for the connection, Skills for the expertise on what to do with that data.

### Can I use all three together?

Yes! They're designed to be complementary:
- MCP provides the data connections
- Skills provide the procedural expertise
- AGENTS.md provides the project-specific context

## Further Reading

- [What are skills?](/what-are-skills) - Deep dive into Agent Skills
- [Agent Skills Specification](/specification) - Technical format details
- [Integrate skills into your agent](/integrate-skills) - Implementation guide
- [AGENTS.md](https://agents.md) - Official AGENTS.md documentation
- [Model Context Protocol](https://modelcontextprotocol.io) - Official MCP documentation
- [Skills Explained (Claude Blog)](https://claude.com/blog/skills-explained) - How Skills compares to prompts, Projects, MCP, and subagents
