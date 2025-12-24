# mcp-skill-map

Map MCP tools to skill definitions.

## Metadata

```yaml
name: mcp-skill-map
version: 1.0.0
level: 2
type: composite
operation: TRANSFORM
domain: mcp
```

## Description

Transforms MCP tool definitions into the agentskills SKILL.md format. Automatically
generates metadata, input/output schemas, examples, and dependency declarations
based on the tool's JSON-RPC definition and annotations.

## Composes

- `mcp-tools-list` (L1) - Get tool definitions
- `mcp-prompts-list` (L1) - Get related prompts for examples
- `skill-registry-read` (L1) - Check for existing skill mappings

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "server": {
      "type": "string",
      "description": "MCP server name"
    },
    "tools": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Specific tools to map (all if empty)"
    },
    "prefix": {
      "type": "string",
      "default": "mcp",
      "description": "Prefix for generated skill names"
    },
    "include_decorators": {
      "type": "boolean",
      "default": true,
      "description": "Add reliability decorator suggestions"
    },
    "output_format": {
      "type": "string",
      "enum": ["markdown", "yaml", "json"],
      "default": "markdown"
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
    "skills": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Generated skill name (prefix-server-tool)"
          },
          "source_tool": {
            "type": "string"
          },
          "source_server": {
            "type": "string"
          },
          "definition": {
            "type": "string",
            "description": "SKILL.md content or YAML/JSON"
          },
          "suggested_decorators": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "decorator": { "type": "string" },
                "reason": { "type": "string" },
                "config": { "type": "object" }
              }
            }
          },
          "operation_type": {
            "type": "string",
            "enum": ["READ", "WRITE", "TRANSFORM"]
          }
        },
        "required": ["name", "source_tool", "source_server", "definition"]
      }
    },
    "server": { "type": "string" },
    "tools_mapped": { "type": "integer" },
    "existing_mappings": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Tools that already have skill mappings"
    }
  },
  "required": ["skills", "server", "tools_mapped"]
}
```

## Mapping Rules

### Operation Type Inference

| Annotation | Mapped Operation |
|------------|------------------|
| `readOnly: true` | READ |
| `destructive: true` | WRITE |
| `idempotent: true` (no destructive) | READ or TRANSFORM |
| No annotations | Infer from name/description |

### Decorator Suggestions

| Condition | Suggested Decorator |
|-----------|---------------------|
| Network operation | `@retry(max=3, backoff=exponential)` |
| Destructive action | `@confirm(prompt="Are you sure?")` |
| Long-running | `@timeout(seconds=60)` |
| Rate-limited API | `@ratelimit(calls=10, period=60)` |
| Idempotent | `@cache(ttl=300)` |
| Not idempotent | `@no_cache` |

### Name Generation

Pattern: `{prefix}-{server}-{tool_name}`
- `mcp-filesystem-read_file`
- `mcp-github-create_issue`
- `mcp-memory-add_entity`

## Example

**Input:**
```json
{
  "server": "filesystem",
  "tools": ["read_file"],
  "include_decorators": true
}
```

**Output:**
```json
{
  "skills": [
    {
      "name": "mcp-filesystem-read_file",
      "source_tool": "read_file",
      "source_server": "filesystem",
      "definition": "# mcp-filesystem-read_file\n\nRead file contents via MCP filesystem server.\n\n## Metadata\n\n```yaml\nname: mcp-filesystem-read_file\nversion: 1.0.0\nlevel: 1\ntype: atomic\noperation: READ\ndomain: filesystem\nsource:\n  type: mcp\n  server: filesystem\n  tool: read_file\n```\n\n## Description\n\nRead the complete contents of a file from the file system.\n\n## Input Schema\n\n```json\n{\n  \"type\": \"object\",\n  \"properties\": {\n    \"path\": {\n      \"type\": \"string\",\n      \"description\": \"Path to the file to read\"\n    }\n  },\n  \"required\": [\"path\"]\n}\n```\n\n## Decorators\n\n```yaml\ndecorators:\n  - name: cache\n    config:\n      ttl: 300\n      key: \"file:{path}\"\n  - name: retry\n    config:\n      max_attempts: 2\n      on: [\"MCP_CONNECTION_FAILED\"]\n```\n\n## Notes\n\n- Automatically generated from MCP tool definition\n- Original annotations: readOnly=true, idempotent=true\n",
      "suggested_decorators": [
        {
          "decorator": "@cache",
          "reason": "Tool is idempotent and read-only",
          "config": { "ttl": 300 }
        },
        {
          "decorator": "@retry",
          "reason": "Network operation may fail transiently",
          "config": { "max_attempts": 2 }
        }
      ],
      "operation_type": "READ"
    }
  ],
  "server": "filesystem",
  "tools_mapped": 1,
  "existing_mappings": []
}
```

## Template Structure

Generated SKILL.md includes:
1. **Metadata block** with MCP source reference
2. **Description** from tool description
3. **Input Schema** from tool inputSchema
4. **Output Schema** inferred or from outputSchema
5. **Decorators** based on annotations
6. **Notes** with original MCP metadata

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_SERVER_NOT_FOUND | Server not configured |
| MCP_TOOL_NOT_FOUND | Specified tool doesn't exist |
| SKILL_ALREADY_EXISTS | Skill mapping already exists (warning) |

## Notes

- Does not write files; returns definitions for review
- Use with `skill-compose` workflow to persist mappings
- Decorators are suggestions; review before applying
- Existing mappings are skipped unless `force: true`
