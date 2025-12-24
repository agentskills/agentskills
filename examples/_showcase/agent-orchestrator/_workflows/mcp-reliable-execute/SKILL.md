# mcp-reliable-execute

Full reliability wrapper for MCP tool execution.

## Metadata

```yaml
name: mcp-reliable-execute
version: 1.0.0
level: 3
type: workflow
operation: WRITE
domain: mcp
decorators:
  - validate
  - retry
  - timeout
  - log
  - fallback
```

## Description

Production-grade workflow for executing MCP tools with comprehensive reliability
features. Combines input validation, retry with backoff, timeout handling,
detailed logging, fallback strategies, and circuit breaker patterns into a
single orchestrated execution.

## Composes

- `mcp-tool-validate` (L2) - Pre-validate arguments
- `mcp-tool-retry` (L2) - Execute with retry logic
- `mcp-tools-list` (L1) - Check tool annotations
- `completion-marker-set` (L1) - Mark execution for idempotency

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "server": {
      "type": "string",
      "description": "MCP server name"
    },
    "tool": {
      "type": "string",
      "description": "Tool to execute"
    },
    "arguments": {
      "type": "object",
      "description": "Tool arguments"
    },
    "reliability": {
      "type": "object",
      "properties": {
        "validate": {
          "type": "boolean",
          "default": true,
          "description": "Pre-validate arguments"
        },
        "retry": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": true },
            "max_attempts": { "type": "integer", "default": 3 },
            "backoff": { "type": "string", "default": "exponential" }
          }
        },
        "timeout_ms": {
          "type": "integer",
          "default": 30000
        },
        "circuit_breaker": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "failure_threshold": { "type": "integer", "default": 5 }
          }
        },
        "fallback": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "strategy": {
              "type": "string",
              "enum": ["cache", "default_value", "alternative_tool", "error"],
              "default": "error"
            },
            "cache_key": { "type": "string" },
            "default_value": { "type": "object" },
            "alternative": {
              "type": "object",
              "properties": {
                "server": { "type": "string" },
                "tool": { "type": "string" }
              }
            }
          }
        },
        "idempotency": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "key": { "type": "string", "description": "Unique execution key" },
            "ttl_seconds": { "type": "integer", "default": 3600 }
          }
        }
      }
    },
    "logging": {
      "type": "object",
      "properties": {
        "level": {
          "type": "string",
          "enum": ["none", "errors", "all"],
          "default": "errors"
        },
        "include_arguments": {
          "type": "boolean",
          "default": false,
          "description": "Include arguments in logs (may contain sensitive data)"
        },
        "destination": {
          "type": "string",
          "default": "stderr"
        }
      }
    }
  },
  "required": ["server", "tool"],
  "additionalProperties": false
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "content": { "type": "array" },
    "structuredContent": { "type": "object" },
    "isError": { "type": "boolean" },
    "error": { "type": "object" },
    "reliability_report": {
      "type": "object",
      "properties": {
        "validation": {
          "type": "object",
          "properties": {
            "performed": { "type": "boolean" },
            "passed": { "type": "boolean" },
            "errors": { "type": "array" },
            "coerced": { "type": "boolean" }
          }
        },
        "execution": {
          "type": "object",
          "properties": {
            "attempts": { "type": "integer" },
            "total_duration_ms": { "type": "integer" },
            "final_attempt_duration_ms": { "type": "integer" }
          }
        },
        "fallback": {
          "type": "object",
          "properties": {
            "triggered": { "type": "boolean" },
            "strategy_used": { "type": "string" },
            "reason": { "type": "string" }
          }
        },
        "circuit_breaker": {
          "type": "object",
          "properties": {
            "state": { "type": "string" },
            "failures_count": { "type": "integer" }
          }
        },
        "idempotency": {
          "type": "object",
          "properties": {
            "cached_result": { "type": "boolean" },
            "marker_key": { "type": "string" }
          }
        }
      }
    },
    "logs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "timestamp": { "type": "string" },
          "level": { "type": "string" },
          "message": { "type": "string" },
          "metadata": { "type": "object" }
        }
      }
    }
  },
  "required": ["success", "content", "reliability_report"]
}
```

## Workflow States

```
VALIDATE → EXECUTE → [RETRY] → [FALLBACK] → COMPLETE
           ↓          ↑
      CIRCUIT_CHECK ──┘
```

1. **VALIDATE**: Check arguments against inputSchema
2. **CIRCUIT_CHECK**: Verify circuit breaker allows execution
3. **EXECUTE**: Call the tool with timeout
4. **RETRY**: On transient failure, retry with backoff
5. **FALLBACK**: If all retries fail, apply fallback strategy
6. **COMPLETE**: Return result with reliability report

## Fallback Strategies

| Strategy | Behavior |
|----------|----------|
| `cache` | Return last successful result for same inputs |
| `default_value` | Return configured default |
| `alternative_tool` | Try a different server/tool |
| `error` | Propagate the error (default) |

## Example

**Input:**
```json
{
  "server": "github",
  "tool": "get_issue",
  "arguments": {
    "owner": "anthropics",
    "repo": "claude",
    "issue_number": 123
  },
  "reliability": {
    "validate": true,
    "retry": {
      "enabled": true,
      "max_attempts": 3,
      "backoff": "exponential"
    },
    "timeout_ms": 10000,
    "fallback": {
      "enabled": true,
      "strategy": "cache"
    },
    "idempotency": {
      "enabled": true,
      "key": "github-issue-123"
    }
  },
  "logging": {
    "level": "all"
  }
}
```

**Output (success after retry):**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "{\"number\": 123, \"title\": \"Feature request\", \"state\": \"open\"}"
    }
  ],
  "isError": false,
  "reliability_report": {
    "validation": {
      "performed": true,
      "passed": true,
      "errors": [],
      "coerced": false
    },
    "execution": {
      "attempts": 2,
      "total_duration_ms": 2340,
      "final_attempt_duration_ms": 245
    },
    "fallback": {
      "triggered": false
    },
    "circuit_breaker": {
      "state": "closed",
      "failures_count": 0
    },
    "idempotency": {
      "cached_result": false,
      "marker_key": "github-issue-123-2025-01-15"
    }
  },
  "logs": [
    {
      "timestamp": "2025-01-15T10:30:00.000Z",
      "level": "info",
      "message": "Starting reliable execution",
      "metadata": { "server": "github", "tool": "get_issue" }
    },
    {
      "timestamp": "2025-01-15T10:30:00.015Z",
      "level": "info",
      "message": "Validation passed"
    },
    {
      "timestamp": "2025-01-15T10:30:02.100Z",
      "level": "warn",
      "message": "Attempt 1 failed, retrying",
      "metadata": { "error": "MCP_TIMEOUT", "next_delay_ms": 1000 }
    },
    {
      "timestamp": "2025-01-15T10:30:02.345Z",
      "level": "info",
      "message": "Attempt 2 succeeded"
    }
  ]
}
```

## Decorator Stack

Execution wraps through decorators in order:

```
@log → @idempotency → @circuit_breaker → @timeout → @retry → @validate → tool_call
```

Each decorator can short-circuit the chain (e.g., idempotency returns cached result).

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_VALIDATION_FAILED | Arguments invalid |
| MCP_CIRCUIT_OPEN | Circuit breaker tripped |
| MCP_ALL_RETRIES_FAILED | Exhausted all attempts |
| MCP_FALLBACK_FAILED | Fallback strategy also failed |
| MCP_TIMEOUT | Execution exceeded timeout |

## Notes

- Use for production automation requiring high reliability
- Idempotency prevents duplicate executions in retry scenarios
- Circuit breaker protects against cascading failures
- Fallback ensures graceful degradation
- Logs provide audit trail for debugging
- Consider using `worktree-isolate` for destructive operations
