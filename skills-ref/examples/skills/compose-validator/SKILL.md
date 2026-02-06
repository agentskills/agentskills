---
name: compose-validator
description: Validate that two skills can be composed together based on their input/output types. Use this before chaining skills to fail fast and avoid silent errors.
composition:
  inputs:
    - skill-reference
  outputs:
    - composition-result
---

# compose-validator

Validate that two skills can be composed together by checking their input/output type compatibility. Use this skill before executing a chain to catch type mismatches early rather than failing silently at runtime.

## When to Use

Use this skill when you need to:
- Verify a skill chain will work before executing it
- Debug why a composition is failing
- Validate a planned workflow before running expensive operations
- Prevent silent failures and hallucinated data from type mismatches

## Why This Matters

Without validation, an LLM might:
1. Chain `slack-search` → `slack-summarize` (incompatible - missing `slack-read`)
2. Get no output or malformed data
3. Hallucinate results to "be helpful"
4. User gets incorrect information

With validation:
1. LLM calls `compose-validator` first
2. Gets clear error: "message-refs is not compatible with message-content input"
3. LLM adjusts the plan (adds `slack-read` in between)
4. No wasted API calls, no hallucination

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| source | string | Yes | - | Source skill name or path |
| target | string | Yes | - | Target skill name or path |
| json | flag | No | false | Output as JSON |

## Running

```bash
# Check valid chain: slack-search → slack-read
python scripts/run.py --source slack-search --target slack-read

# Check invalid chain: slack-search → slack-summarize (missing middle step)
python scripts/run.py --source slack-search --target slack-summarize --json
```

## Output Format

Returns a `composition-result` containing:
- `valid` - Boolean indicating if composition is valid
- `source` - Source skill name
- `target` - Target skill name
- `reason` - Human-readable explanation
- `matched_type` - The type that matched (if valid)

### Example: Valid Composition
```json
{
  "valid": true,
  "source": "slack-search",
  "target": "slack-read",
  "reason": "Compatible: slack-search outputs [message-refs] which slack-read accepts",
  "matched_type": "message-refs"
}
```

### Example: Invalid Composition
```json
{
  "valid": false,
  "source": "slack-search",
  "target": "slack-summarize",
  "reason": "Type mismatch: slack-search outputs [message-refs] but slack-summarize expects [message-content]"
}
```

## Real-World Example: Slack Deep Search Pipeline

The `slack-deep-search` skill demonstrates proper composition:

```
slack-search (outputs: message-refs)
      ↓
slack-read (inputs: message-refs, outputs: message-content)
      ↓
slack-summarize (inputs: message-content, outputs: search-summary)
```

Validate the full chain:
```bash
skills-ref compose ./slack-search ./slack-read
# ✓ slack-search → slack-read (message-refs)

skills-ref compose ./slack-read ./slack-summarize
# ✓ slack-read → slack-summarize (message-content)
```

## Composition

**Consumes:**
- `skill-reference` - Names or paths of skills to validate

**Produces:**
- `composition-result` - Validation result with compatibility details

## Authentication

**None required.** This skill only reads SKILL.md metadata files.

## Safety

- **Operation:** READ
- **Side effects:** None
- **Confirmation required:** No
