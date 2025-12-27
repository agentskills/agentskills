# mcp-server-list

Discover available MCP servers from configuration.

## Metadata

```yaml
name: mcp-server-list
version: 1.0.0
level: 1
type: atomic
operation: READ
domain: mcp
```

## Description

Reads MCP server configuration to discover available servers. Parses configuration
files (claude_desktop_config.json, mcp-servers.json, or environment-based config)
to enumerate all configured MCP servers with their connection details.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "config_path": {
      "type": "string",
      "description": "Path to MCP config file. If not provided, searches standard locations."
    },
    "filter": {
      "type": "object",
      "properties": {
        "transport": {
          "type": "string",
          "enum": ["stdio", "sse", "streamable-http"],
          "description": "Filter by transport type"
        },
        "name_pattern": {
          "type": "string",
          "description": "Regex pattern to match server names"
        }
      }
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
    "servers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Server identifier"
          },
          "transport": {
            "type": "string",
            "enum": ["stdio", "sse", "streamable-http"]
          },
          "command": {
            "type": "string",
            "description": "For stdio: command to execute"
          },
          "args": {
            "type": "array",
            "items": { "type": "string" },
            "description": "For stdio: command arguments"
          },
          "url": {
            "type": "string",
            "description": "For SSE/HTTP: server URL"
          },
          "env": {
            "type": "object",
            "description": "Environment variables for the server"
          },
          "status": {
            "type": "string",
            "enum": ["configured", "running", "stopped", "error"]
          }
        },
        "required": ["name", "transport"]
      }
    },
    "config_source": {
      "type": "string",
      "description": "Path to config file that was read"
    },
    "server_count": {
      "type": "integer"
    }
  },
  "required": ["servers", "config_source", "server_count"]
}
```

## Standard Config Locations

Searches in order:
1. Provided `config_path`
2. `~/.config/claude/claude_desktop_config.json`
3. `./mcp-servers.json`
4. `./.claude/mcp-servers.json`
5. Environment variable `MCP_CONFIG_PATH`

## Example

**Input:**
```json
{
  "filter": {
    "transport": "stdio"
  }
}
```

**Output:**
```json
{
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed"],
      "status": "configured"
    },
    {
      "name": "github",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "***"
      },
      "status": "configured"
    }
  ],
  "config_source": "~/.config/claude/claude_desktop_config.json",
  "server_count": 2
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| MCP_CONFIG_NOT_FOUND | No configuration file found |
| MCP_CONFIG_PARSE_ERROR | Configuration file is malformed |
| MCP_CONFIG_INVALID | Configuration schema validation failed |

## Dependencies

None (atomic skill)

## Notes

- Masks sensitive environment variables (tokens, keys) in output
- Does not start or connect to servers; only reads configuration
- Use `mcp-tools-list` to query a specific server's capabilities
