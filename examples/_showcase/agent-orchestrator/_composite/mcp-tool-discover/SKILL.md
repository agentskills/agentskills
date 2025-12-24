# mcp-tool-discover

Discover tools across all MCP servers with search and filtering.

## Metadata

```yaml
name: mcp-tool-discover
version: 1.0.0
level: 2
type: composite
operation: READ
domain: mcp
```

## Description

Aggregates tools from all configured MCP servers and provides search, filtering,
and ranking capabilities. Maps user intent to available tools using semantic
matching on tool names and descriptions.

## Composes

- `mcp-server-list` (L1) - Enumerate configured servers
- `mcp-tools-list` (L1) - Query tools from each server
- `intent-classify` (L1) - Parse user intent for matching

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Natural language description of desired capability"
    },
    "filters": {
      "type": "object",
      "properties": {
        "servers": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Limit to specific servers"
        },
        "annotations": {
          "type": "object",
          "properties": {
            "readOnly": { "type": "boolean" },
            "idempotent": { "type": "boolean" },
            "destructive": { "type": "boolean" }
          },
          "description": "Filter by tool annotations"
        },
        "name_pattern": {
          "type": "string",
          "description": "Regex pattern for tool names"
        }
      }
    },
    "limit": {
      "type": "integer",
      "default": 10,
      "description": "Maximum tools to return"
    },
    "include_schema": {
      "type": "boolean",
      "default": false,
      "description": "Include full inputSchema in results"
    }
  },
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
          "server": { "type": "string" },
          "name": { "type": "string" },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "relevance_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "annotations": { "type": "object" },
          "inputSchema": { "type": "object" },
          "match_reasons": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Why this tool matched the query"
          }
        },
        "required": ["server", "name", "relevance_score"]
      }
    },
    "total_scanned": {
      "type": "integer",
      "description": "Total tools scanned across all servers"
    },
    "servers_queried": {
      "type": "array",
      "items": { "type": "string" }
    },
    "query_interpretation": {
      "type": "object",
      "properties": {
        "operation_type": {
          "type": "string",
          "enum": ["READ", "WRITE", "TRANSFORM"]
        },
        "domain_hints": {
          "type": "array",
          "items": { "type": "string" }
        },
        "keywords": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  },
  "required": ["tools", "total_scanned", "servers_queried"]
}
```

## Matching Algorithm

1. **Keyword Matching**: Tool name and description contain query terms
2. **Semantic Similarity**: Description meaning aligns with query intent
3. **Domain Alignment**: Tool domain matches query context
4. **Annotation Boost**: Relevant annotations (e.g., readOnly for queries) increase score

## Example

**Input:**
```json
{
  "query": "read a file from disk",
  "filters": {
    "annotations": {
      "readOnly": true
    }
  },
  "limit": 3
}
```

**Output:**
```json
{
  "tools": [
    {
      "server": "filesystem",
      "name": "read_file",
      "description": "Read the complete contents of a file",
      "relevance_score": 0.95,
      "annotations": { "readOnly": true, "idempotent": true },
      "match_reasons": [
        "Name contains 'read' and 'file'",
        "readOnly annotation matches filter"
      ]
    },
    {
      "server": "filesystem",
      "name": "get_file_info",
      "description": "Get metadata about a file",
      "relevance_score": 0.72,
      "annotations": { "readOnly": true },
      "match_reasons": ["Domain match: filesystem operations"]
    },
    {
      "server": "git",
      "name": "read_file",
      "description": "Read file contents from a git repository",
      "relevance_score": 0.68,
      "annotations": { "readOnly": true },
      "match_reasons": ["Name matches query terms"]
    }
  ],
  "total_scanned": 47,
  "servers_queried": ["filesystem", "git", "github", "memory"],
  "query_interpretation": {
    "operation_type": "READ",
    "domain_hints": ["filesystem", "storage"],
    "keywords": ["read", "file", "disk"]
  }
}
```

## Caching Strategy

- Server list: Cached until config file changes
- Tool lists: Cached 5 minutes per server
- Invalidated on `notifications/tools/list_changed`

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_NO_SERVERS | No MCP servers configured |
| MCP_ALL_SERVERS_FAILED | All server queries failed |
| MCP_PARTIAL_RESULTS | Some servers failed (results from others) |

## Notes

- Returns partial results if some servers fail (with warning)
- Use `include_schema: true` only when needed (increases response size)
- Relevance scores are relative within result set, not absolute
- Empty query returns all tools (up to limit), sorted by server
