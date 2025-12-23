# Example Composable Skills

This directory demonstrates the **composable skills architecture** with a complete example from atomic primitives through to a complex workflow.

## The Composition Hierarchy

```
Level 3: _workflows/daily-briefing
              │
              ├── research ────────────────────┐
              │                                │
Level 2: _composite/research                   │
              │                                │
              ├── web-search ──────┐           │
              │                    │           │
Level 1: _atomic/web-search   _atomic/pdf-save │
              │                    │           │
              ▼                    ▼           │
Level 0:  [Perplexity API]    [PDF library]   │
                                              │
              ┌───────────────────────────────┘
              ▼
         [Also uses: calendar-read, email-read, customer-intel]
```

## Directory Structure

```
examples/
├── README.md                    # This file
│
├── _atomic/                     # Level 1: Single operations
│   ├── web-search/
│   │   └── SKILL.md            # Search the web, return citations
│   ├── pdf-save/
│   │   └── SKILL.md            # Save URL as PDF
│   ├── http-request/
│   │   └── SKILL.md            # Make HTTP requests to any URL
│   ├── github-issues-create/
│   │   └── SKILL.md            # Create GitHub issues
│   ├── github-issues-list/
│   │   └── SKILL.md            # List/filter GitHub issues
│   ├── slack-message-send/
│   │   └── SKILL.md            # Send Slack messages
│   └── google-sheets-read/
│       └── SKILL.md            # Read from Google Sheets
│
├── _composite/                  # Level 2: Combined operations
│   ├── research/
│   │   └── SKILL.md            # web-search + pdf-save
│   ├── deep-research/
│   │   └── SKILL.md            # RECURSIVE: follows citation chains
│   ├── data-merge/
│   │   └── SKILL.md            # Merge data from multiple sources
│   ├── email-reply/
│   │   └── SKILL.md            # Context-aware email replies
│   └── issue-triage/
│       └── SKILL.md            # Classify and route GitHub issues
│
└── _workflows/                  # Level 3: Complex orchestration
    ├── daily-briefing/
    │   └── SKILL.md            # Orchestrates multiple composites
    ├── slack-to-issue/
    │   └── SKILL.md            # Convert Slack messages to GitHub issues
    └── notion-sheets-sync/
        └── SKILL.md            # Bidirectional Notion ↔ Sheets sync
```

## How Composition Works

### Level 1: Atomic Skills

Each atomic skill does **ONE thing**:

**web-search** (READ):
```yaml
level: 1
operation: READ
# No composes - wraps primitive (Perplexity API)
```

**pdf-save** (WRITE):
```yaml
level: 1
operation: WRITE
# No composes - wraps primitive (PDF library)
```

### Level 2: Composite Skills

Composite skills **combine** atomics:

**research** (READ):
```yaml
level: 2
operation: READ  # All components are READ-safe
composes:
  - web-search   # Level 1
  - pdf-save     # Level 1 (optional)
```

The `composes` field creates an explicit dependency graph.

### Level 3: Workflow Skills

Workflows **orchestrate** with decision logic:

**daily-briefing** (READ):
```yaml
level: 3
operation: READ
composes:
  - calendar-read    # Level 1
  - email-read       # Level 1
  - research         # Level 2 (!)
  - customer-intel   # Level 2
```

Note how daily-briefing composes both Level 1 and Level 2 skills.

## Benefits Demonstrated

### 1. Reusability

`web-search` is used by:
- `research` (Level 2)
- Any other skill needing web search

Write once, use everywhere.

### 2. Testability

Each level can be tested independently:
```bash
# Test atomic
skills-ref validate examples/_atomic/web-search

# Test composite
skills-ref validate examples/_composite/research

# Test workflow
skills-ref validate examples/_workflows/daily-briefing
```

### 3. Safety Propagation

Operation safety flows upward:
- `web-search` is READ → safe
- `pdf-save` is WRITE → needs confirmation
- `research` is READ because pdf-save is optional
- `daily-briefing` is READ because all required components are READ

### 4. Transparency

The `composes` field shows exactly what each skill uses:
```yaml
# You can see daily-briefing uses research,
# and research uses web-search and pdf-save
```

### 5. Maintainability

Update `web-search` once, and:
- `research` automatically benefits
- `daily-briefing` automatically benefits
- Any other consumer automatically benefits

### 6. Recursion

The `deep-research` example demonstrates **self-recursion** - a skill that composes itself:

```yaml
name: deep-research
composes:
  - deep-research    # Self-recursion!
  - web-search
  - pdf-save
```

This enables:
- **Divide-and-conquer**: Each citation becomes a sub-problem
- **Dynamic parallelisation**: Sub-agents can run concurrently
- **Minimal code**: One definition handles arbitrary depth
- **Context efficiency**: No need for `research-depth-1`, `research-depth-2`, etc.

See `_composite/deep-research/SKILL.md` for the full example

## Try It Out

Validate all examples:
```bash
cd examples
for skill in _atomic/* _composite/* _workflows/*; do
  echo "Validating $skill..."
  skills-ref validate "$skill"
done
```

Generate prompt XML:
```bash
skills-ref to-prompt _atomic/web-search _composite/research _workflows/daily-briefing
```

## n8n-Inspired Atomic Skills

Several atomic skills are inspired by [n8n's node ecosystem](https://n8n.io/), enabling familiar patterns for workflow automation:

| Skill | Operation | n8n Equivalent |
|-------|-----------|----------------|
| `http-request` | READ | HTTP Request node |
| `github-issues-create` | WRITE | GitHub → Issues → Create |
| `github-issues-list` | READ | GitHub → Issues → Get All |
| `slack-message-send` | WRITE | Slack → Message → Send |
| `google-sheets-read` | READ | Google Sheets → Read |

These follow the **MECE decomposition pattern**: each n8n node's resource+operation combinations become separate atomic skills. For example, n8n's GitHub node becomes `github-issues-create`, `github-issues-list`, `github-repos-read`, etc.

See [docs/n8n-node-mapping.md](../docs/n8n-node-mapping.md) for the complete mapping pattern.

## n8n-Inspired Composite Skills (Level 2)

These skills combine multiple atomics, inspired by n8n's data transformation and multi-step nodes:

| Skill | Operation | Pattern |
|-------|-----------|---------|
| `data-merge` | READ | Merge node: combine data from multiple sources |
| `email-reply` | WRITE | Gmail Reply: read thread + send reply |
| `issue-triage` | WRITE | GitHub + AI: classify, label, assign |

Level 2 skills add **intelligence between reads and writes** - the value is in the combination.

## n8n-Inspired Workflows (Level 3)

These workflows demonstrate complex orchestration patterns from popular n8n templates:

| Skill | Operation | n8n Template Equivalent |
|-------|-----------|------------------------|
| `slack-to-issue` | WRITE | "Create Jira issues from Slack messages" |
| `notion-sheets-sync` | WRITE | "Sync Notion database to Google Sheets" |

Level 3 skills have **decision logic, state management, and multi-directional data flow**.

## Creating Your Own

1. **Start with atomics**: Identify the core operations you need
2. **Compose carefully**: Only combine what naturally goes together
3. **Add decision logic**: When you need branching, that's a workflow
4. **Declare dependencies**: Always specify `composes` for clarity

See [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for the full design rationale.
