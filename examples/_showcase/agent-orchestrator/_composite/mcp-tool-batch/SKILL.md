# mcp-tool-batch

Execute multiple MCP tools in sequence or parallel.

## Metadata

```yaml
name: mcp-tool-batch
version: 1.0.0
level: 2
type: composite
operation: WRITE
domain: mcp
decorators:
  - batch
  - parallel
```

## Description

Orchestrates execution of multiple MCP tool calls with configurable execution
strategies. Supports sequential execution, parallel execution, and pipeline
patterns where outputs feed into subsequent inputs.

## Composes

- `mcp-tool-call` (L1) - Execute individual tools
- `mcp-tool-retry` (L2) - Retry failed calls
- `conflict-detect` (L2) - Check for conflicting operations

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "calls": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique identifier for this call"
          },
          "server": { "type": "string" },
          "tool": { "type": "string" },
          "arguments": { "type": "object" },
          "depends_on": {
            "type": "array",
            "items": { "type": "string" },
            "description": "IDs of calls that must complete first"
          },
          "argument_refs": {
            "type": "object",
            "description": "Map argument names to outputs from prior calls",
            "additionalProperties": {
              "type": "string",
              "pattern": "^\\$\\{[a-zA-Z0-9_]+\\.[a-zA-Z0-9_.]+\\}$"
            }
          }
        },
        "required": ["id", "server", "tool"]
      },
      "minItems": 1
    },
    "execution": {
      "type": "object",
      "properties": {
        "strategy": {
          "type": "string",
          "enum": ["sequential", "parallel", "auto"],
          "default": "auto",
          "description": "auto infers from dependencies"
        },
        "max_parallel": {
          "type": "integer",
          "default": 5,
          "description": "Max concurrent calls in parallel mode"
        },
        "stop_on_error": {
          "type": "boolean",
          "default": true,
          "description": "Halt batch on first failure"
        },
        "continue_on_error": {
          "type": "boolean",
          "default": false,
          "description": "Continue batch, skip dependent calls"
        }
      }
    },
    "retry_config": {
      "type": "object",
      "description": "Default retry config for all calls (can override per-call)"
    }
  },
  "required": ["calls"],
  "additionalProperties": false
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "True if all calls succeeded"
    },
    "results": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "success": { "type": "boolean" },
          "content": { "type": "array" },
          "structuredContent": { "type": "object" },
          "error": { "type": "object" },
          "duration_ms": { "type": "integer" },
          "skipped": {
            "type": "boolean",
            "description": "True if skipped due to failed dependency"
          }
        }
      },
      "description": "Results keyed by call ID"
    },
    "execution_order": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Order in which calls were executed"
    },
    "total_duration_ms": { "type": "integer" },
    "summary": {
      "type": "object",
      "properties": {
        "total": { "type": "integer" },
        "succeeded": { "type": "integer" },
        "failed": { "type": "integer" },
        "skipped": { "type": "integer" }
      }
    }
  },
  "required": ["success", "results", "summary"]
}
```

## Execution Strategies

### Sequential
Executes calls one at a time in array order (ignoring depends_on).

### Parallel
Executes all independent calls concurrently up to `max_parallel`.

### Auto (default)
Builds dependency graph and executes:
1. All calls with no dependencies run in parallel
2. As each completes, dependent calls become eligible
3. Maximizes parallelism while respecting dependencies

## Argument References

Use `${call_id.path}` syntax to reference prior outputs:

```json
{
  "calls": [
    {
      "id": "read_config",
      "server": "filesystem",
      "tool": "read_file",
      "arguments": { "path": "/app/config.json" }
    },
    {
      "id": "parse_config",
      "server": "custom",
      "tool": "parse_json",
      "depends_on": ["read_config"],
      "argument_refs": {
        "json_string": "${read_config.content[0].text}"
      }
    }
  ]
}
```

## Example

**Input:**
```json
{
  "calls": [
    {
      "id": "list_files",
      "server": "filesystem",
      "tool": "list_directory",
      "arguments": { "path": "/home/user/docs" }
    },
    {
      "id": "read_readme",
      "server": "filesystem",
      "tool": "read_file",
      "arguments": { "path": "/home/user/docs/README.md" }
    },
    {
      "id": "read_license",
      "server": "filesystem",
      "tool": "read_file",
      "arguments": { "path": "/home/user/docs/LICENSE" }
    }
  ],
  "execution": {
    "strategy": "parallel",
    "max_parallel": 3
  }
}
```

**Output:**
```json
{
  "success": true,
  "results": {
    "list_files": {
      "success": true,
      "content": [{ "type": "text", "text": "[\"README.md\", \"LICENSE\", ...]" }],
      "duration_ms": 15
    },
    "read_readme": {
      "success": true,
      "content": [{ "type": "text", "text": "# Project\n..." }],
      "duration_ms": 12
    },
    "read_license": {
      "success": true,
      "content": [{ "type": "text", "text": "MIT License..." }],
      "duration_ms": 10
    }
  },
  "execution_order": ["list_files", "read_readme", "read_license"],
  "total_duration_ms": 18,
  "summary": {
    "total": 3,
    "succeeded": 3,
    "failed": 0,
    "skipped": 0
  }
}
```

## Conflict Detection

When `execution.strategy` is "parallel" or "auto", runs `conflict-detect` to
identify potentially conflicting operations (e.g., writing to same file).
Conflicting calls are serialized automatically.

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_BATCH_PARTIAL | Some calls failed (check results) |
| MCP_BATCH_DEPENDENCY_FAILED | Dependency call failed |
| MCP_BATCH_CYCLE_DETECTED | Circular dependency in depends_on |
| MCP_BATCH_INVALID_REF | Argument reference path invalid |

## Notes

- Use `id` to reference results and build dependencies
- Parallel execution reduces total time for independent operations
- Pipeline patterns enable complex multi-step workflows
- Conflict detection prevents race conditions on shared resources
- Consider using `worktree-isolate` for truly parallel file modifications
