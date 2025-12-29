# Agent Skills

Composable, type-safe skills for AI agents. Write once, use everywhere.

## Quick Start

```typescript
import { Skill, compose } from 'agentskills';

// Define skills with typed inputs and outputs
const fetchUser: Skill<{ userId: string }, { user: User }> = {
  name: 'fetch-user',
  async execute({ userId }) {
    return { user: await db.users.find(userId) };
  }
};

const sendEmail: Skill<{ user: User }, { sent: boolean }> = {
  name: 'send-email',
  async execute({ user }) {
    await email.send(user.email, 'Welcome!');
    return { sent: true };
  }
};

// Compose them - type-checked at compile time
const onboard = compose(fetchUser, sendEmail);

// This fails to compile - types don't match:
// compose(sendEmail, fetchUser);  // Error!
```

## Install

```bash
npm install agentskills
```

## Why Composable Skills?

When teams create AI agent tools independently, they build overlapping functionality with incompatible interfaces. One skill outputs `{ priority: "high" }`, another expects `{ priority: 1 }`. These mismatches cause runtime crashes.

Composable skills catch these errors at **compile time**.

## Skill Levels

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| 1 | Atomic | Single operation (READ or WRITE) | `email-read`, `slack-post` |
| 2 | Composite | Combines atomics | `research` = web-search + pdf-save |
| 3 | Workflow | Orchestration with decision logic | `daily-briefing` |

## YAML Format

Skills are folders with a `SKILL.md` file:

```yaml
---
name: research
description: Research a topic with web search and source verification.
level: 2
operation: READ
composes:
  - web-search
  - pdf-save
inputs:
  - name: query
    type: string
    required: true
outputs:
  - name: answer
    type: string
  - name: sources
    type: array
---

## Instructions

1. Search the web for the query
2. Save relevant sources as PDFs
3. Synthesise findings into an answer
```

## TypeScript API

```typescript
import { Skill, compose, pipe, parallel } from 'agentskills';

// Sequential: A → B
const workflow = compose(skillA, skillB);

// Pipeline: A → B → C
const pipeline = pipe(skillA, skillB, skillC);

// Parallel: Same input, merged outputs
const enriched = parallel(fetchProfile, fetchSettings);
```

## Operation Types

| Operation | Description | Confirmation |
|-----------|-------------|--------------|
| `READ` | Fetches data, no side effects | Never required |
| `WRITE` | Modifies external state | Recommended |
| `TRANSFORM` | Local computation only | Never required |

## Directory Structure

```
skills/
├── _atomic/       # Level 1: Single operations
│   ├── email-read/
│   └── web-search/
├── _composite/    # Level 2: Composed from atomics
│   └── research/
└── _workflows/    # Level 3: Complex orchestration
    └── daily-briefing/
```

## Examples

- [file-read](./examples/_atomic/file-read/) - L1 atomic skill
- [research](./examples/_composite/research/) - L2 composite skill
- [daily-briefing](./examples/_workflows/daily-briefing/) - L3 workflow

## Documentation

| Topic | Link |
|-------|------|
| Specification | [docs/specification.mdx](./docs/specification.mdx) |
| Type System | [docs/type-system.mdx](./docs/type-system.mdx) |
| Getting Started | [docs/getting-started-guide.mdx](./docs/getting-started-guide.mdx) |
| MCP Integration | [docs/mcp-interop.mdx](./docs/mcp-interop.mdx) |

## Backwards Compatibility

Skills without `level`, `operation`, or `composes` fields continue to work unchanged.

## License

MIT
