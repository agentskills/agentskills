# mcp-tool-retry

Execute MCP tool with configurable retry logic.

## Metadata

```yaml
name: mcp-tool-retry
version: 1.0.0
level: 2
type: composite
operation: WRITE
domain: mcp
decorators:
  - retry
  - timeout
```

## Description

Wraps MCP tool execution with robust retry logic. Supports exponential backoff,
jitter, conditional retries based on error types, and circuit breaker patterns.
Essential for reliable automation with external MCP servers.

## Composes

- `mcp-tool-call` (L1) - Execute the tool
- `mcp-tools-list` (L1) - Check tool annotations for retry safety

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
    "retry_config": {
      "type": "object",
      "properties": {
        "max_attempts": {
          "type": "integer",
          "default": 3,
          "minimum": 1,
          "maximum": 10
        },
        "backoff": {
          "type": "string",
          "enum": ["none", "linear", "exponential"],
          "default": "exponential"
        },
        "initial_delay_ms": {
          "type": "integer",
          "default": 1000
        },
        "max_delay_ms": {
          "type": "integer",
          "default": 30000
        },
        "jitter": {
          "type": "boolean",
          "default": true,
          "description": "Add random jitter to prevent thundering herd"
        },
        "retry_on": {
          "type": "array",
          "items": { "type": "string" },
          "default": ["MCP_CONNECTION_FAILED", "MCP_TIMEOUT"],
          "description": "Error codes to retry on"
        },
        "no_retry_on": {
          "type": "array",
          "items": { "type": "string" },
          "default": ["MCP_INVALID_ARGUMENTS", "MCP_TOOL_NOT_FOUND"],
          "description": "Error codes to never retry"
        }
      }
    },
    "timeout_ms": {
      "type": "integer",
      "default": 30000,
      "description": "Per-attempt timeout"
    },
    "circuit_breaker": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean", "default": false },
        "failure_threshold": { "type": "integer", "default": 5 },
        "reset_timeout_ms": { "type": "integer", "default": 60000 }
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
    "retry_info": {
      "type": "object",
      "properties": {
        "attempts": {
          "type": "integer",
          "description": "Total attempts made"
        },
        "retried": {
          "type": "boolean",
          "description": "Whether any retries occurred"
        },
        "total_duration_ms": {
          "type": "integer"
        },
        "attempt_history": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "attempt": { "type": "integer" },
              "duration_ms": { "type": "integer" },
              "error_code": { "type": "string" },
              "retryable": { "type": "boolean" }
            }
          }
        },
        "circuit_breaker_state": {
          "type": "string",
          "enum": ["closed", "open", "half-open"]
        }
      }
    }
  },
  "required": ["success", "content", "retry_info"]
}
```

## Backoff Strategies

### Exponential (default)
```
delay = min(initial_delay * 2^attempt, max_delay) + jitter
```
Example: 1s → 2s → 4s → 8s → 16s → 30s (capped)

### Linear
```
delay = min(initial_delay * attempt, max_delay) + jitter
```
Example: 1s → 2s → 3s → 4s → 5s

### None
Immediate retry (use with caution)

## Retry Safety

Before retrying, checks tool annotations:

| Annotation | Retry Behavior |
|------------|----------------|
| `idempotent: true` | Safe to retry freely |
| `destructive: true` | Only retry on connection errors |
| No annotation | Conservative retry (connection only) |

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
  "retry_config": {
    "max_attempts": 3,
    "backoff": "exponential",
    "initial_delay_ms": 1000
  }
}
```

**Output (after 1 retry):**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "{\"title\": \"Feature request\", \"state\": \"open\", ...}"
    }
  ],
  "isError": false,
  "retry_info": {
    "attempts": 2,
    "retried": true,
    "total_duration_ms": 2450,
    "attempt_history": [
      {
        "attempt": 1,
        "duration_ms": 350,
        "error_code": "MCP_TIMEOUT",
        "retryable": true
      },
      {
        "attempt": 2,
        "duration_ms": 120,
        "error_code": null,
        "retryable": false
      }
    ]
  }
}
```

## Circuit Breaker

When enabled, tracks failure rate:

1. **Closed** (normal): Requests flow through
2. **Open** (failing): Requests fail fast without calling server
3. **Half-Open** (testing): Allow one request to test recovery

Prevents cascading failures when MCP server is unhealthy.

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_RETRY_EXHAUSTED | All retry attempts failed |
| MCP_CIRCUIT_OPEN | Circuit breaker is open |
| MCP_NON_RETRYABLE | Error is in no_retry_on list |

## Notes

- Always check `idempotent` annotation before aggressive retry
- Use circuit breaker for long-running automation
- Jitter prevents multiple clients retrying simultaneously
- Log all retry attempts for debugging
- Consider using `mcp-tool-validate` before retry to catch input errors early
