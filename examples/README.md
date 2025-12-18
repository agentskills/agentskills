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
│   └── pdf-save/
│       └── SKILL.md            # Save URL as PDF
│
├── _composite/                  # Level 2: Combined operations
│   └── research/
│       └── SKILL.md            # web-search + pdf-save
│
└── _workflows/                  # Level 3: Complex orchestration
    └── daily-briefing/
        └── SKILL.md            # Orchestrates multiple composites
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

## Creating Your Own

1. **Start with atomics**: Identify the core operations you need
2. **Compose carefully**: Only combine what naturally goes together
3. **Add decision logic**: When you need branching, that's a workflow
4. **Declare dependencies**: Always specify `composes` for clarity

See [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for the full design rationale.
