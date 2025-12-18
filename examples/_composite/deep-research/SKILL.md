---
name: deep-research
description: Recursively research a topic by following citation chains. Spawns sub-agents to explore related topics in parallel, building comprehensive understanding with minimal code.
level: 2
operation: READ
composes:
  - deep-research
  - web-search
  - pdf-save
license: Apache-2.0
---

# Deep Research

Recursive research that follows citation chains to build comprehensive understanding of a topic.

## Why This Skill Uses Recursion

This skill demonstrates **self-recursion** - a powerful pattern where a skill composes itself. This is explicitly allowed because it enables:

| Benefit | Application |
|---------|-------------|
| **Divide-and-conquer** | Each citation becomes a sub-problem researched independently |
| **Dynamic parallelisation** | Sub-agents can research citations concurrently |
| **Minimal code** | One skill definition handles arbitrary depth |
| **Context efficiency** | No need to define `research-depth-1`, `research-depth-2`, etc. |

## Composition Graph

```
deep-research (Level 2, READ)
├── deep-research     # Self-recursion for citation chains
├── web-search        # Initial search and citation discovery
└── pdf-save          # Archive sources at each level
```

## How It Works

```
1. SEARCH
   └── Use web-search to find initial answer + citations

2. FOR EACH citation (up to max_depth):
   └── RECURSE: Invoke deep-research on the citation topic
       └── This spawns a sub-agent that performs steps 1-3
       └── Sub-agents can run in parallel

3. ARCHIVE (if save_sources = true)
   └── Use pdf-save to preserve sources at each level

4. SYNTHESISE
   └── Combine findings from all recursion levels
   └── Flag contradictions between sources
```

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | The research question |
| `max_depth` | integer | No | `2` | Maximum recursion depth |
| `max_citations` | integer | No | `3` | Max citations to follow per level |
| `save_sources` | boolean | No | `false` | Archive all sources as PDFs |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Synthesised findings from all levels |
| `tree` | object | Hierarchical structure of research paths |
| `sources` | list | All sources with depth annotations |
| `contradictions` | list | Conflicts found between sources |

## Usage Example

```
Deep research "how do transformer attention mechanisms handle long-range dependencies" with max_depth=2 and save sources
```

**Execution trace:**

```
deep-research("transformer attention long-range dependencies")
├── web-search → finds papers on sparse attention, linear attention
├── deep-research("sparse attention mechanisms")      # Recursion depth 1
│   ├── web-search → finds Longformer, BigBird papers
│   ├── deep-research("Longformer architecture")      # Recursion depth 2
│   │   └── web-search → specific implementation details
│   └── pdf-save → archive sparse attention sources
├── deep-research("linear attention complexity")      # Recursion depth 1
│   ├── web-search → finds Performer, Linear Transformer
│   └── pdf-save → archive linear attention sources
└── SYNTHESISE all findings
```

## Why Recursion Beats Iteration

Without recursion, you would need:
- `research-shallow` (depth 0)
- `research-medium` (depth 1)
- `research-deep` (depth 2)
- ...and so on

With recursion, **one skill definition** handles any depth, controlled at runtime. This follows the functional programming principle that recursion is a fundamental control structure, not a special case.

## Parallelisation

Because each recursive call is independent, agent runtimes can execute them in parallel:

```
                    deep-research(query)
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    deep-research    deep-research    deep-research
      (citation1)      (citation2)      (citation3)
           │               │               │
        [parallel]      [parallel]      [parallel]
```

This natural parallelism emerges from the recursive structure without explicit threading code.

## Notes

- Recursion depth is bounded by `max_depth` to prevent infinite loops
- Each level inherits the same parameters unless overridden
- The skill is READ-only because pdf-save writes locally, not to external systems
- Contradictions between sources are automatically flagged for human review
