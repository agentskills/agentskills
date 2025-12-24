# mcp-tool-call

Execute a single MCP tool.

## Metadata

```yaml
name: mcp-tool-call
version: 1.0.0
level: 1
type: atomic
operation: WRITE
domain: mcp
```

## Description

Invokes a specific tool on an MCP server via the `tools/call` JSON-RPC method.
Handles argument marshalling, response parsing, and error extraction. This is
the fundamental execution primitive for all MCP tool interactions.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "server": {
      "type": "string",
      "description": "Server name or connection URL"
    },
    "tool": {
      "type": "string",
      "description": "Tool name to invoke"
    },
    "arguments": {
      "type": "object",
      "description": "Tool arguments (must match tool's inputSchema)"
    },
    "timeout_ms": {
      "type": "integer",
      "default": 30000,
      "description": "Timeout in milliseconds"
    },
    "include_metadata": {
      "type": "boolean",
      "default": false,
      "description": "Include timing and request metadata in response"
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
    "success": {
      "type": "boolean",
      "description": "True if tool executed without error"
    },
    "content": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["text", "image", "audio", "resource"]
          },
          "text": { "type": "string" },
          "data": { "type": "string", "description": "Base64 for binary" },
          "mimeType": { "type": "string" },
          "uri": { "type": "string" }
        }
      },
      "description": "Tool output content blocks"
    },
    "structuredContent": {
      "type": "object",
      "description": "Structured JSON result (if outputSchema defined)"
    },
    "isError": {
      "type": "boolean",
      "description": "True if tool returned an error result"
    },
    "error": {
      "type": "object",
      "properties": {
        "code": { "type": "integer" },
        "message": { "type": "string" },
        "data": { "type": "object" }
      },
      "description": "Error details if isError or protocol error"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "server": { "type": "string" },
        "tool": { "type": "string" },
        "duration_ms": { "type": "integer" },
        "request_id": { "type": "string" },
        "timestamp": { "type": "string", "format": "date-time" }
      },
      "description": "Execution metadata (if include_metadata=true)"
    }
  },
  "required": ["success", "content"]
}
```

## JSON-RPC Request

Sends to MCP server:
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": { ... }
  }
}
```

## Content Types

MCP tools can return multiple content types:

| Type | Description | Fields |
|------|-------------|--------|
| `text` | Plain text response | `text` |
| `image` | Base64-encoded image | `data`, `mimeType` |
| `audio` | Base64-encoded audio | `data`, `mimeType` |
| `resource` | URI reference | `uri`, optionally `text` |

## Example

**Input:**
```json
{
  "server": "filesystem",
  "tool": "read_file",
  "arguments": {
    "path": "/home/user/example.txt"
  },
  "include_metadata": true
}
```

**Output (success):**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Hello, World!\nThis is the file content."
    }
  ],
  "isError": false,
  "metadata": {
    "server": "filesystem",
    "tool": "read_file",
    "duration_ms": 12,
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

**Output (tool error):**
```json
{
  "success": false,
  "content": [
    {
      "type": "text",
      "text": "File not found: /home/user/missing.txt"
    }
  ],
  "isError": true,
  "error": {
    "message": "File not found: /home/user/missing.txt"
  }
}
```

## Error Handling

Two error types:

1. **Protocol Errors** (connection/RPC failures):
   - `-32700`: Parse error
   - `-32600`: Invalid request
   - `-32601`: Method not found
   - `-32602`: Invalid params
   - `-32603`: Internal error

2. **Tool Errors** (tool execution failures):
   - `isError: true` in response
   - Content contains error message for LLM self-correction

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_SERVER_NOT_FOUND | Server not configured |
| MCP_TOOL_NOT_FOUND | Tool does not exist on server |
| MCP_INVALID_ARGUMENTS | Arguments don't match inputSchema |
| MCP_EXECUTION_TIMEOUT | Tool exceeded timeout |
| MCP_TOOL_ERROR | Tool returned isError: true |

## Dependencies

- `mcp-server-list` (for server resolution)

## Notes

- Does NOT validate arguments; use `mcp-tool-validate` first for safety
- Does NOT retry on failure; use `mcp-tool-retry` for retry logic
- Use `isError` to distinguish tool failures from protocol errors
- Tool errors are actionable feedback for LLM self-correction
