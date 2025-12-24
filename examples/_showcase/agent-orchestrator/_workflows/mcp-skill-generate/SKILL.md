# mcp-skill-generate

Generate complete skill definitions from MCP servers.

## Metadata

```yaml
name: mcp-skill-generate
version: 1.0.0
level: 3
type: workflow
operation: WRITE
domain: mcp
```

## Description

End-to-end workflow that discovers MCP servers, queries their capabilities,
and generates a complete skill library. Creates L1 atomic skills for each tool,
L2 composite skills for common patterns, and appropriate decorators for
reliability. Outputs ready-to-use SKILL.md files.

## Composes

- `mcp-server-list` (L1) - Discover configured servers
- `mcp-tools-list` (L1) - Query tools from each server
- `mcp-resources-list` (L1) - Query resources
- `mcp-prompts-list` (L1) - Query prompts for patterns
- `mcp-skill-map` (L2) - Generate skill definitions
- `skill-coherence-check` (L2) - Validate generated skills
- `completion-marker-set` (L1) - Mark generation complete

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "servers": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Specific servers to process (all if empty)"
    },
    "output_dir": {
      "type": "string",
      "description": "Directory to write generated skills"
    },
    "options": {
      "type": "object",
      "properties": {
        "prefix": {
          "type": "string",
          "default": "mcp",
          "description": "Skill name prefix"
        },
        "include_decorators": {
          "type": "boolean",
          "default": true
        },
        "include_composites": {
          "type": "boolean",
          "default": true,
          "description": "Generate L2 composites for common patterns"
        },
        "dry_run": {
          "type": "boolean",
          "default": false,
          "description": "Preview without writing files"
        },
        "overwrite": {
          "type": "boolean",
          "default": false,
          "description": "Overwrite existing skill files"
        }
      }
    },
    "composite_patterns": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "tool_pattern": {
            "type": "string",
            "description": "Regex matching tools to compose"
          },
          "composition": {
            "type": "string",
            "enum": ["sequence", "parallel", "conditional"]
          }
        }
      },
      "description": "Custom composite skill patterns"
    }
  },
  "required": ["output_dir"],
  "additionalProperties": false
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "generated": {
      "type": "object",
      "properties": {
        "atomic": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "server": { "type": "string" },
              "tool": { "type": "string" },
              "path": { "type": "string" },
              "status": {
                "type": "string",
                "enum": ["created", "updated", "skipped", "failed"]
              }
            }
          }
        },
        "composite": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "composes": { "type": "array", "items": { "type": "string" } },
              "path": { "type": "string" },
              "status": { "type": "string" }
            }
          }
        }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "servers_processed": { "type": "integer" },
        "tools_found": { "type": "integer" },
        "skills_created": { "type": "integer" },
        "skills_updated": { "type": "integer" },
        "skills_skipped": { "type": "integer" },
        "errors": { "type": "integer" }
      }
    },
    "validation": {
      "type": "object",
      "properties": {
        "passed": { "type": "boolean" },
        "issues": { "type": "array" }
      }
    },
    "marker": {
      "type": "string",
      "description": "Completion marker path"
    }
  },
  "required": ["success", "generated", "summary"]
}
```

## Workflow States

```
DISCOVER → QUERY → MAP → VALIDATE → WRITE → VERIFY → COMPLETE
```

1. **DISCOVER**: List all configured MCP servers
2. **QUERY**: Fetch tools, resources, prompts from each server
3. **MAP**: Transform tools to skill definitions
4. **VALIDATE**: Run coherence checks on generated skills
5. **WRITE**: Write SKILL.md files to output directory
6. **VERIFY**: Verify files were written correctly
7. **COMPLETE**: Set completion marker

## Auto-Generated Composites

When `include_composites: true`, generates L2 skills for patterns:

| Pattern | Generated Composite |
|---------|---------------------|
| `read_*` + `write_*` | `{server}-read-write` (CRUD pattern) |
| `list_*` + `get_*` | `{server}-browse` (navigation) |
| `create_*` + `update_*` + `delete_*` | `{server}-manage` (lifecycle) |
| `search_*` + `get_*` | `{server}-find` (search-then-fetch) |

## Example

**Input:**
```json
{
  "servers": ["filesystem", "github"],
  "output_dir": "./generated-skills",
  "options": {
    "prefix": "mcp",
    "include_decorators": true,
    "include_composites": true,
    "dry_run": false
  }
}
```

**Output:**
```json
{
  "success": true,
  "generated": {
    "atomic": [
      {
        "name": "mcp-filesystem-read_file",
        "server": "filesystem",
        "tool": "read_file",
        "path": "./generated-skills/_atomic/mcp-filesystem-read_file/SKILL.md",
        "status": "created"
      },
      {
        "name": "mcp-filesystem-write_file",
        "server": "filesystem",
        "tool": "write_file",
        "path": "./generated-skills/_atomic/mcp-filesystem-write_file/SKILL.md",
        "status": "created"
      },
      {
        "name": "mcp-github-create_issue",
        "server": "github",
        "tool": "create_issue",
        "path": "./generated-skills/_atomic/mcp-github-create_issue/SKILL.md",
        "status": "created"
      }
    ],
    "composite": [
      {
        "name": "mcp-filesystem-read-write",
        "composes": ["mcp-filesystem-read_file", "mcp-filesystem-write_file"],
        "path": "./generated-skills/_composite/mcp-filesystem-read-write/SKILL.md",
        "status": "created"
      }
    ]
  },
  "summary": {
    "servers_processed": 2,
    "tools_found": 15,
    "skills_created": 18,
    "skills_updated": 0,
    "skills_skipped": 0,
    "errors": 0
  },
  "validation": {
    "passed": true,
    "issues": []
  },
  "marker": ".cache/automation-markers/mcp-skill-generate-2025-01-15.done"
}
```

## Generated Directory Structure

```
generated-skills/
├── _atomic/
│   ├── mcp-filesystem-read_file/
│   │   └── SKILL.md
│   ├── mcp-filesystem-write_file/
│   │   └── SKILL.md
│   └── mcp-github-create_issue/
│       └── SKILL.md
├── _composite/
│   ├── mcp-filesystem-read-write/
│   │   └── SKILL.md
│   └── mcp-github-issue-workflow/
│       └── SKILL.md
└── README.md  # Index of generated skills
```

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_NO_SERVERS | No servers configured or matched |
| MCP_GENERATION_PARTIAL | Some skills failed to generate |
| MCP_VALIDATION_FAILED | Generated skills have coherence issues |
| MCP_WRITE_FAILED | Could not write skill files |

## Notes

- Run periodically to keep skills in sync with MCP servers
- Use `dry_run: true` to preview before generating
- Idempotent: safe to run multiple times
- Completion marker prevents duplicate runs in automation
- Generated skills include source metadata for traceability
