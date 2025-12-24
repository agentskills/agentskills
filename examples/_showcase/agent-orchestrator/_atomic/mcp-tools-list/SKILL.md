# mcp-tools-list

Query available tools from an MCP server.

## Metadata

```yaml
name: mcp-tools-list
version: 1.0.0
level: 1
type: atomic
operation: READ
domain: mcp
```

## Description

Connects to an MCP server and retrieves its available tools via the `tools/list`
JSON-RPC method. Supports pagination for servers with many tools. Returns tool
definitions including names, descriptions, and input schemas.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "server": {
      "type": "string",
      "description": "Server name (from mcp-server-list) or connection URL"
    },
    "cursor": {
      "type": "string",
      "description": "Pagination cursor for fetching next page"
    },
    "fetch_all": {
      "type": "boolean",
      "default": true,
      "description": "Automatically fetch all pages"
    }
  },
  "required": ["server"],
  "additionalProperties": false
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "tools": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Tool identifier (1-128 chars)"
          },
          "title": {
            "type": "string",
            "description": "Human-readable display name"
          },
          "description": {
            "type": "string",
            "description": "What the tool does"
          },
          "inputSchema": {
            "type": "object",
            "description": "JSON Schema for tool parameters"
          },
          "outputSchema": {
            "type": "object",
            "description": "Optional JSON Schema for results"
          },
          "annotations": {
            "type": "object",
            "properties": {
              "audience": {
                "type": "array",
                "items": { "type": "string" }
              },
              "idempotent": { "type": "boolean" },
              "destructive": { "type": "boolean" },
              "readOnly": { "type": "boolean" },
              "openWorld": { "type": "boolean" }
            },
            "description": "Behavioral metadata"
          }
        },
        "required": ["name", "inputSchema"]
      }
    },
    "server": {
      "type": "string"
    },
    "tool_count": {
      "type": "integer"
    },
    "next_cursor": {
      "type": "string",
      "description": "Cursor for next page (null if no more pages)"
    }
  },
  "required": ["tools", "server", "tool_count"]
}
```

## JSON-RPC Request

Sends to MCP server:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {
    "cursor": "optional-cursor"
  }
}
```

## Tool Annotations

MCP tools can include annotations describing their behavior:

| Annotation | Meaning |
|------------|---------|
| `readOnly: true` | Tool only reads data, no side effects |
| `destructive: true` | Tool may delete or modify data irreversibly |
| `idempotent: true` | Safe to retry; same result on repeated calls |
| `openWorld: true` | Tool interacts with external systems |

## Example

**Input:**
```json
{
  "server": "filesystem"
}
```

**Output:**
```json
{
  "tools": [
    {
      "name": "read_file",
      "description": "Read the complete contents of a file from the file system",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "Path to the file to read"
          }
        },
        "required": ["path"]
      },
      "annotations": {
        "readOnly": true,
        "idempotent": true
      }
    },
    {
      "name": "write_file",
      "description": "Create a new file or overwrite an existing file",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "content": { "type": "string" }
        },
        "required": ["path", "content"]
      },
      "annotations": {
        "destructive": true
      }
    },
    {
      "name": "list_directory",
      "description": "List all files and directories in a given path",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": { "type": "string" }
        },
        "required": ["path"]
      },
      "annotations": {
        "readOnly": true,
        "idempotent": true
      }
    }
  ],
  "server": "filesystem",
  "tool_count": 3,
  "next_cursor": null
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_SERVER_NOT_FOUND | Server not in configuration |
| MCP_CONNECTION_FAILED | Cannot connect to server |
| MCP_PROTOCOL_ERROR | Invalid JSON-RPC response |
| MCP_TIMEOUT | Server did not respond in time |

## Dependencies

- `mcp-server-list` (to resolve server name to connection details)

## Notes

- Caches tool list for 5 minutes by default (configurable)
- Subscribes to `notifications/tools/list_changed` for cache invalidation
- Use annotations to determine safe retry behavior
