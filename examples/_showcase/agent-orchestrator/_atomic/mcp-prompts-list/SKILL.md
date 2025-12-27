# mcp-prompts-list

Query available prompts from an MCP server.

## Metadata

```yaml
name: mcp-prompts-list
version: 1.0.0
level: 1
type: atomic
operation: READ
domain: mcp
```

## Description

Connects to an MCP server and retrieves its available prompts via the
`prompts/list` JSON-RPC method. Prompts are pre-defined templates that
guide optimal use of the server's tools and resources.

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
    "prompts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Prompt identifier"
          },
          "title": {
            "type": "string",
            "description": "Human-readable title"
          },
          "description": {
            "type": "string",
            "description": "What the prompt helps with"
          },
          "arguments": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "description": { "type": "string" },
                "required": { "type": "boolean" }
              }
            },
            "description": "Template arguments"
          }
        },
        "required": ["name"]
      }
    },
    "server": { "type": "string" },
    "prompt_count": { "type": "integer" },
    "next_cursor": { "type": "string" }
  },
  "required": ["prompts", "server", "prompt_count"]
}
```

## JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prompts/list",
  "params": {
    "cursor": "optional-cursor"
  }
}
```

## Prompt Arguments

Prompts can have arguments that customize their behavior:

```json
{
  "name": "code_review",
  "description": "Review code for issues and improvements",
  "arguments": [
    {
      "name": "language",
      "description": "Programming language",
      "required": true
    },
    {
      "name": "focus",
      "description": "Review focus: security, performance, style",
      "required": false
    }
  ]
}
```

## Example

**Input:**
```json
{
  "server": "everything"
}
```

**Output:**
```json
{
  "prompts": [
    {
      "name": "simple_prompt",
      "title": "Simple Prompt",
      "description": "A basic prompt template"
    },
    {
      "name": "complex_prompt",
      "title": "Complex Prompt",
      "description": "A prompt with arguments",
      "arguments": [
        {
          "name": "temperature",
          "description": "How creative to be (0-1)",
          "required": false
        }
      ]
    }
  ],
  "server": "everything",
  "prompt_count": 2,
  "next_cursor": null
}
```

## Getting Prompt Content

To retrieve the actual prompt template, use `prompts/get`:
```json
{
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "language": "python"
    }
  }
}
```

Returns messages array ready for LLM context.

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_SERVER_NOT_FOUND | Server not configured |
| MCP_PROMPTS_NOT_SUPPORTED | Server doesn't support prompts |
| MCP_CONNECTION_FAILED | Cannot connect to server |

## Dependencies

- `mcp-server-list` (for server resolution)

## Notes

- Not all MCP servers provide prompts; check capabilities first
- Prompts encode best practices for using server's tools/resources
- Subscribe to `notifications/prompts/list_changed` for updates
- Use prompts to ensure optimal tool usage patterns
