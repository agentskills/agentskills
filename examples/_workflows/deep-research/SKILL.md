---
name: deep-research
description: Workflow that recursively researches a topic by following citation chains. Spawns sub-agents to explore related topics in parallel, building comprehensive understanding through orchestrated recursion.
level: 3
operation: READ
composes:
  - deep-research
  - research
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
deep-research (Level 3, READ)
├── deep-research     # Self-recursion for citation chains
└── research          # Level 2 composite (web-search + pdf-save)
```

This follows the MECE principle: at each level, there's only one skill for a given capability. `deep-research` orchestrates recursion, while `research` handles the actual search-and-save operation.

## How It Works

```
1. RESEARCH
   └── Use research skill to search and optionally archive sources

2. FOR EACH citation (up to max_depth):
   └── RECURSE: Invoke deep-research on the citation topic
       └── This spawns a sub-agent that performs steps 1-3
       └── Sub-agents can run in parallel

3. SYNTHESISE
   └── Combine findings from all recursion levels
   └── Flag contradictions between sources
```

Note: `research` internally handles both web-search and pdf-save, so `deep-research` only needs to orchestrate the recursion.

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
├── research → finds papers on sparse attention, linear attention
├── deep-research("sparse attention mechanisms")      # Recursion depth 1
│   ├── research → finds Longformer, BigBird papers
│   ├── deep-research("Longformer architecture")      # Recursion depth 2
│   │   └── research → specific implementation details
│   └── [research handles archiving internally]
├── deep-research("linear attention complexity")      # Recursion depth 1
│   ├── research → finds Performer, Linear Transformer
│   └── [research handles archiving internally]
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
- The skill is READ-only because research (and its pdf-save dependency) writes locally, not to external systems
- Contradictions between sources are automatically flagged for human review
- This is a Level 3 workflow because recursion is a form of orchestration (deciding when to recurse, when to stop)
