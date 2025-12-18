# Agent Skills

[Agent Skills](https://agentskills.io) are a simple, open format for giving agents new capabilities and expertise.

Skills are folders of instructions, scripts, and resources that agents can discover and use to perform better at specific tasks. Write once, use everywhere.

## The Problem: Non-Deterministic Tool Selection

As teams rapidly develop MCP servers and agent skills, a critical problem emerges: **flat, unstructured skill definitions lead to unpredictable agent behaviour**.

### Why Flat Skills Fail at Scale

When multiple developers create skills independently, they inevitably build overlapping functionality with subtly different implementations. Without a formal composition hierarchy, these skills violate **MECE principles** (Mutually Exclusive, Collectively Exhaustive):

| Problem | Consequence |
|---------|-------------|
| **Overlapping skills** | Multiple skills can handle the same request, but with different approaches |
| **Non-deterministic selection** | LLMs may choose different tools for identical prompts across runs |
| **Cascading inconsistency** | A skill chosen on Monday may not be chosen on Tuesday |
| **Unpredictable permutations** | With N overlapping skills, there are N! possible execution paths |

**The result:** Agent systems that appear to "have a mind of their own" - unsuitable for applications requiring real-world reliability, predictability, and determinism.

### What Trustworthy Agents Require

Production-grade agent systems must be:

- **Predictable**: The same input should produce the same tool selection
- **Deterministic**: Execution paths should be reproducible and auditable
- **Reliable**: Behaviour that worked yesterday should work tomorrow
- **Trustworthy**: Users must be confident the agent will "just do the right thing"

Flat skill definitions cannot guarantee these properties because they provide no mechanism for:
- Defining canonical implementations of common operations
- Expressing skill dependencies and composition relationships
- Ensuring teams build on shared primitives rather than duplicating logic

### The Context Window Problem

There is an additional dimension to this challenge: **LLMs have finite context windows, yet we are experiencing an explosion of available tools**.

When an agent must choose between dozens of flat, potentially overlapping skills:
- The LLM must hold all tool definitions in context simultaneously
- Similar descriptions create ambiguity about which tool to select
- Reasoning complexity grows combinatorially with the number of options
- Context budget consumed by tool definitions cannot be used for actual work

Composable skills address this by providing **small, contained, unambiguous primitives** that the LLM can reason about clearly. Instead of choosing between 50 overlapping tools, the agent selects from a curated set of atomic operations - and composition handles the rest deterministically.

## The Solution: Composable Skills

Composable skills introduce a **hierarchical architecture** that enforces MECE principles through explicit composition:

```
Level 3: Workflows        Complex multi-step processes with decision logic
    ↑ composes
Level 2: Composites       Combined operations for common patterns
    ↑ composes
Level 1: Atomics          Single-purpose operations (READ or WRITE)
    ↑ wraps
Level 0: Primitives       Raw scripts, APIs, or tools
```

### How Composition Solves Non-Determinism

| Principle | Implementation |
|-----------|----------------|
| **Single responsibility** | Level 1 atomics do ONE thing - no overlap possible |
| **Explicit dependencies** | `composes` field declares exactly which skills are used |
| **Canonical paths** | Higher-level skills compose lower-level ones, not alternatives |
| **Auditable structure** | Dependency graph is visible and verifiable |

When a team agrees that `research` composes `web-search` + `pdf-save`, there is no ambiguity about which tools will be invoked. The LLM selects `research`, and the composition is deterministic.

### New Frontmatter Fields

Three optional fields enable composition:

```yaml
---
name: research
description: Research a topic with web search and source verification.
level: 2              # Composition tier (1=Atomic, 2=Composite, 3=Workflow)
operation: READ       # Safety classification (READ/WRITE/TRANSFORM)
composes:             # Explicit dependencies
  - web-search
  - pdf-save
---
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Predictability** | Composition graph determines execution path |
| **Determinism** | Same skill selection yields same tool invocations |
| **Simpler reasoning** | LLMs choose from small, unambiguous atomics instead of many overlapping tools |
| **Context efficiency** | Fewer tool definitions needed; composition replaces enumeration |
| **Team coordination** | Shared atomics prevent duplicate implementations |
| **Reusability** | Write atomic skills once, compose everywhere |
| **Testability** | Each level can be tested and verified independently |
| **Safety** | Clear READ/WRITE separation; safety propagates upward |
| **Transparency** | `composes` field makes dependencies explicit and auditable |

## Getting Started

- [Documentation](https://agentskills.io) - Guides and tutorials
- [Specification](https://agentskills.io/specification) - Format details
- [Architecture](docs/architecture.mdx) - Composability design rationale
- [Example Skills](https://github.com/anthropics/skills) - See what's possible

This repo contains the specification, documentation, and reference SDK.

## Quick Reference

### Skill Levels

| Level | Name | Purpose | Example |
|-------|------|---------|---------|
| 1 | Atomic | Single operation | `email-read`, `pdf-save` |
| 2 | Composite | Combined operations | `research`, `customer-intel` |
| 3 | Workflow | Complex orchestration | `daily-synthesis` |

### Operation Types

| Operation | Safety | Confirmation |
|-----------|--------|--------------|
| `READ` | Safe | Never required |
| `WRITE` | Side effects | Recommended |
| `TRANSFORM` | Local only | Never required |

### Directory Structure (Recommended)

```
skills/
├── _atomic/              # Level 1: Canonical single operations
│   ├── email-read/
│   ├── web-search/
│   └── pdf-save/
├── _composite/           # Level 2: Composed from atomics
│   ├── research/
│   └── customer-intel/
└── _workflows/           # Level 3: Complex orchestration
    └── daily-synthesis/
```

## Backwards Compatibility

The composability extension is fully backwards-compatible. Skills without `level`, `operation`, or `composes` fields continue to work unchanged. Teams can adopt composability incrementally.

## About

Agent Skills is an open format maintained by [Anthropic](https://anthropic.com) and open to contributions from the community.
