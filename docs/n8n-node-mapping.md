# n8n Node → Atomic Skill Mapping

This document describes how n8n node definitions map to Level 1 atomic skills, enabling systematic conversion of n8n's ~400 nodes to SKILL.md format.

## Structural Mapping

| n8n Concept | SKILL.md Field | Notes |
|-------------|----------------|-------|
| `displayName` | `name` | Convert to kebab-case |
| `description` | `description` | Direct mapping |
| `group: "input"` | `operation: READ` | n8n "input" = data retrieval |
| `group: "output"` | `operation: WRITE` | n8n "output" = data modification |
| `resource` | Skill name suffix | `github-issues`, `github-repos` |
| `operation` | Skill name suffix | `github-issues-create`, `github-issues-read` |
| `properties[]` | `inputs[]` | Convert INodeProperties to FieldSchema |
| Return data | `outputs[]` | Infer from operation type |
| `credentials` | (external) | Handled by runtime/MCP |

## Operation Mapping

| n8n Operation | SKILL.md Operation | Skill Naming |
|---------------|-------------------|--------------|
| `create` | WRITE | `{service}-{resource}-create` |
| `get` | READ | `{service}-{resource}-read` |
| `getAll` / `getMany` | READ | `{service}-{resource}-list` |
| `update` / `edit` | WRITE | `{service}-{resource}-update` |
| `delete` | WRITE | `{service}-{resource}-delete` |

## Property Type Mapping

| n8n Type | SKILL.md Type | Notes |
|----------|---------------|-------|
| `string` | `string` | Direct |
| `number` | `number` | Direct |
| `boolean` | `boolean` | Direct |
| `options` | `string` with enum | List valid values in description |
| `collection` | Object type | Define custom type |
| `fixedCollection` | Object type | Define custom type |
| `resourceLocator` | `string` | URL, ID, or name |
| `json` | `object` | Or `any` for flexibility |

## Example Conversion

### n8n GitHub Issues Node (Create)

```typescript
// n8n node definition (simplified)
{
  displayName: 'GitHub Issues',
  name: 'githubIssues',
  description: 'Manage GitHub issues',
  properties: [
    {
      displayName: 'Owner',
      name: 'owner',
      type: 'string',
      required: true,
    },
    {
      displayName: 'Repository',
      name: 'repository',
      type: 'string',
      required: true,
    },
    {
      displayName: 'Title',
      name: 'title',
      type: 'string',
      required: true,
    },
    {
      displayName: 'Body',
      name: 'body',
      type: 'string',
    },
  ]
}
```

### Equivalent SKILL.md

```yaml
---
name: github-issues-create
description: Create a new issue in a GitHub repository. Use when the user wants to file a bug report, feature request, or track a task.
level: 1
operation: WRITE

inputs:
  - name: owner
    type: string
    required: true
    description: Repository owner (user or organisation)
  - name: repository
    type: string
    required: true
    description: Repository name
  - name: title
    type: string
    required: true
    description: Issue title
  - name: body
    type: string
    required: false
    description: Issue body (markdown supported)
  - name: labels
    type: string[]
    required: false
    description: Labels to apply to the issue
  - name: assignees
    type: string[]
    required: false
    description: GitHub usernames to assign

outputs:
  - name: issue_number
    type: integer
    description: Created issue number
  - name: issue_url
    type: string
    description: URL to the created issue
  - name: html_url
    type: string
    description: Web URL for the issue
---
```

## MECE Decomposition Pattern

For each n8n node with multiple resources/operations, decompose into atomic skills:

```
n8n: github (node)
  └── resources: [file, issue, release, repository, ...]
      └── operations: [create, get, update, delete, ...]

SKILL.md decomposition:
  └── github-issues-create (Level 1, WRITE)
  └── github-issues-read (Level 1, READ)
  └── github-issues-update (Level 1, WRITE)
  └── github-issues-list (Level 1, READ)
  └── github-repos-read (Level 1, READ)
  └── github-repos-list (Level 1, READ)
  └── github-files-create (Level 1, WRITE)
  └── github-files-read (Level 1, READ)
  ...
```

## Popular n8n Nodes for Priority Conversion

Based on usage data, prioritise these nodes:

| Priority | n8n Node | Atomic Skills |
|----------|----------|---------------|
| 1 | HTTP Request | `http-request` |
| 2 | GitHub | `github-*` (issues, repos, files, releases) |
| 3 | Slack | `slack-*` (messages, channels, users) |
| 4 | Google Sheets | `google-sheets-*` (read, append, update) |
| 5 | Gmail | `gmail-*` (send, read, list) |
| 6 | Notion | `notion-*` (pages, databases, blocks) |
| 7 | Airtable | `airtable-*` (records, tables) |
| 8 | OpenAI | `openai-*` (chat, embeddings, images) |
| 9 | Postgres | `postgres-*` (query, insert, update) |
| 10 | Webhook | `webhook-receive` (trigger skill) |

## Conversion Automation

A conversion script could:

1. Parse n8n node TypeScript definitions
2. Extract resources and operations
3. Generate one SKILL.md per resource+operation combination
4. Infer outputs from API response schemas
5. Apply consistent naming: `{service}-{resource}-{action}`

This enables bootstrapping a comprehensive atomic skills library from n8n's battle-tested node collection.
