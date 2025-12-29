# TypeScript Composition Guide

Type-safe skill composition with compile-time validation.

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

## API

### Types

| Type | Description |
|------|-------------|
| `Skill<TInput, TOutput>` | Base interface for typed skills |
| `InputOf<S>` | Extract input type from a skill |
| `OutputOf<S>` | Extract output type from a skill |
| `CanCompose<S1, S2>` | Check if two skills can be composed |

### Functions

```typescript
// Sequential: A → B
const workflow = compose(skillA, skillB);

// Pipeline: A → B → C
const pipeline = pipe(skillA, skillB, skillC);

// Parallel: Same input, merged outputs
const enriched = parallel(fetchProfile, fetchSettings);
```

## Skill Levels

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| 1 | Atomic | Single operation (READ or WRITE) | `email-read`, `slack-post` |
| 2 | Composite | Combines atomics | `research` = web-search + pdf-save |
| 3 | Workflow | Orchestration with decision logic | `daily-briefing` |

## Operation Types

| Operation | Description | Confirmation |
|-----------|-------------|--------------|
| `READ` | Fetches data, no side effects | Never required |
| `WRITE` | Modifies external state | Recommended |
| `TRANSFORM` | Local computation only | Never required |

## Examples

- [file-read](../examples/_atomic/file-read/) - L1 atomic skill
- [research](../examples/_composite/research/) - L2 composite skill
- [daily-briefing](../examples/_workflows/daily-briefing/) - L3 workflow
