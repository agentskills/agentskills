# mcp-tool-validate

Validate tool arguments against schema before execution.

## Metadata

```yaml
name: mcp-tool-validate
version: 1.0.0
level: 2
type: composite
operation: READ
domain: mcp
decorators:
  - validate
```

## Description

Pre-validates MCP tool arguments against the tool's inputSchema before execution.
Catches invalid parameters early, provides detailed error messages, and suggests
corrections. Prevents wasted API calls and improves error recovery.

## Composes

- `mcp-tools-list` (L1) - Retrieve tool's inputSchema

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
      "description": "Tool to validate arguments for"
    },
    "arguments": {
      "type": "object",
      "description": "Arguments to validate"
    },
    "strict": {
      "type": "boolean",
      "default": true,
      "description": "Reject extra properties not in schema"
    },
    "coerce_types": {
      "type": "boolean",
      "default": false,
      "description": "Attempt to coerce types (e.g., '42' → 42)"
    },
    "suggest_fixes": {
      "type": "boolean",
      "default": true,
      "description": "Suggest corrections for invalid arguments"
    }
  },
  "required": ["server", "tool", "arguments"],
  "additionalProperties": false
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "valid": {
      "type": "boolean",
      "description": "True if arguments pass validation"
    },
    "arguments": {
      "type": "object",
      "description": "Validated (and possibly coerced) arguments"
    },
    "errors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "JSON path to invalid field (e.g., 'config.timeout')"
          },
          "message": {
            "type": "string",
            "description": "Human-readable error message"
          },
          "code": {
            "type": "string",
            "enum": [
              "MISSING_REQUIRED",
              "INVALID_TYPE",
              "INVALID_FORMAT",
              "OUT_OF_RANGE",
              "PATTERN_MISMATCH",
              "EXTRA_PROPERTY",
              "INVALID_ENUM"
            ]
          },
          "expected": {
            "type": "string",
            "description": "What was expected"
          },
          "received": {
            "type": "string",
            "description": "What was received"
          },
          "suggestion": {
            "type": "string",
            "description": "Suggested fix"
          }
        },
        "required": ["path", "message", "code"]
      }
    },
    "warnings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "message": { "type": "string" },
          "code": { "type": "string" }
        }
      },
      "description": "Non-blocking issues (e.g., deprecated fields)"
    },
    "schema_used": {
      "type": "object",
      "description": "The inputSchema used for validation"
    }
  },
  "required": ["valid", "arguments", "errors"]
}
```

## Validation Rules

### Type Checking
```
string, number, integer, boolean, array, object, null
```

### String Constraints
- `minLength`, `maxLength`
- `pattern` (regex)
- `format` (email, uri, date-time, etc.)

### Number Constraints
- `minimum`, `maximum`
- `exclusiveMinimum`, `exclusiveMaximum`
- `multipleOf`

### Array Constraints
- `minItems`, `maxItems`
- `uniqueItems`
- `items` (element schema)

### Object Constraints
- `required`
- `additionalProperties`
- `properties`, `patternProperties`

## Example

**Input:**
```json
{
  "server": "github",
  "tool": "create_issue",
  "arguments": {
    "owner": "anthropics",
    "repo": "claude",
    "title": "",
    "labels": "bug",
    "assignees": ["alice", "bob", 123]
  },
  "suggest_fixes": true
}
```

**Output:**
```json
{
  "valid": false,
  "arguments": {
    "owner": "anthropics",
    "repo": "claude",
    "title": "",
    "labels": "bug",
    "assignees": ["alice", "bob", 123]
  },
  "errors": [
    {
      "path": "title",
      "message": "Title must not be empty",
      "code": "INVALID_FORMAT",
      "expected": "non-empty string",
      "received": "\"\"",
      "suggestion": "Provide a descriptive issue title"
    },
    {
      "path": "labels",
      "message": "Labels must be an array of strings",
      "code": "INVALID_TYPE",
      "expected": "array",
      "received": "string",
      "suggestion": "Use [\"bug\"] instead of \"bug\""
    },
    {
      "path": "assignees[2]",
      "message": "Assignee must be a string username",
      "code": "INVALID_TYPE",
      "expected": "string",
      "received": "number (123)",
      "suggestion": "Use the username string, not user ID"
    }
  ],
  "warnings": [],
  "schema_used": {
    "type": "object",
    "properties": {
      "owner": { "type": "string" },
      "repo": { "type": "string" },
      "title": { "type": "string", "minLength": 1 },
      "body": { "type": "string" },
      "labels": { "type": "array", "items": { "type": "string" } },
      "assignees": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["owner", "repo", "title"]
  }
}
```

## Type Coercion

When `coerce_types: true`:

| From | To | Example |
|------|----|---------|
| String | Number | `"42"` → `42` |
| String | Boolean | `"true"` → `true` |
| Number | String | `42` → `"42"` |
| Single value | Array | `"x"` → `["x"]` |

Coercion only applies to compatible conversions and updates `arguments` in output.

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_TOOL_NOT_FOUND | Tool doesn't exist on server |
| MCP_SCHEMA_MISSING | Tool has no inputSchema |
| VALIDATION_FAILED | One or more validation errors |

## Notes

- Always validate before calling tools with complex schemas
- Use with `mcp-tool-retry` to avoid retrying invalid input errors
- Coercion can help with LLM-generated arguments (strings instead of numbers)
- Suggestions help LLMs self-correct invalid arguments
- Cache schemas to avoid repeated `mcp-tools-list` calls
