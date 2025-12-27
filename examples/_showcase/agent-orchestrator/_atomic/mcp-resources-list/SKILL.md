# mcp-resources-list

Query available resources from an MCP server.

## Metadata

```yaml
name: mcp-resources-list
version: 1.0.0
level: 1
type: atomic
operation: READ
domain: mcp
```

## Description

Connects to an MCP server and retrieves its available resources via the
`resources/list` JSON-RPC method. Resources are structured data that can be
included in LLM context, such as files, API responses, or knowledge bases.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "server": {
      "type": "string",
      "description": "Server name or connection URL"
    },
    "cursor": {
      "type": "string",
      "description": "Pagination cursor"
    },
    "fetch_all": {
      "type": "boolean",
      "default": true
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
    "resources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "uri": {
            "type": "string",
            "format": "uri",
            "description": "Unique resource identifier"
          },
          "name": {
            "type": "string",
            "description": "Human-readable name"
          },
          "description": {
            "type": "string"
          },
          "mimeType": {
            "type": "string",
            "description": "Content type (e.g., text/plain, application/json)"
          },
          "size": {
            "type": "integer",
            "description": "Size in bytes (if known)"
          },
          "annotations": {
            "type": "object",
            "properties": {
              "audience": { "type": "array", "items": { "type": "string" } }
            }
          }
        },
        "required": ["uri", "name"]
      }
    },
    "server": { "type": "string" },
    "resource_count": { "type": "integer" },
    "next_cursor": { "type": "string" }
  },
  "required": ["resources", "server", "resource_count"]
}
```

## JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/list",
  "params": {
    "cursor": "optional-cursor"
  }
}
```

## Resource URI Schemes

Common URI schemes in MCP resources:

| Scheme | Example | Purpose |
|--------|---------|---------|
| `file://` | `file:///home/user/doc.txt` | Local files |
| `http(s)://` | `https://api.example.com/data` | Web resources |
| `memory://` | `memory://entities/john` | In-memory knowledge |
| Custom | `postgres://db/table` | Server-specific |

## Example

**Input:**
```json
{
  "server": "memory"
}
```

**Output:**
```json
{
  "resources": [
    {
      "uri": "memory://entities",
      "name": "Entity List",
      "description": "All known entities in the knowledge graph",
      "mimeType": "application/json"
    },
    {
      "uri": "memory://relations",
      "name": "Relation List",
      "description": "All relations between entities",
      "mimeType": "application/json"
    }
  ],
  "server": "memory",
  "resource_count": 2,
  "next_cursor": null
}
```

## Related Operations

To read a resource's content, use `resources/read`:
```json
{
  "method": "resources/read",
  "params": {
    "uri": "memory://entities"
  }
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_SERVER_NOT_FOUND | Server not configured |
| MCP_RESOURCES_NOT_SUPPORTED | Server doesn't support resources |
| MCP_CONNECTION_FAILED | Cannot connect to server |

## Dependencies

- `mcp-server-list` (for server resolution)

## Notes

- Not all MCP servers provide resources; check capabilities first
- Resources are read-only context data (unlike tools which execute actions)
- Use resource URIs with `resources/read` to fetch content
- Subscribe to `notifications/resources/list_changed` for updates
