# Validate agentskills action

A GitHub Action that validates [agentskills](https://agentskills.io) directories to ensure `SKILL.md` files conform to the [specification](https://agentskills.io/specification).

## Features

- Discovers all `SKILL.md` files in specified paths
- Validates frontmatter metadata against the [agentskills specification](https://agentskills.io/specification)
- Outputs GitHub annotations for validation errors (visible in PR diffs and Checks)
- Provides detailed JSON error output for programmatic use
- Configurable failure behavior

## Usage

```yaml
- name: Validate agentskills
  uses: agentskills/agentskills/.github/actions/validate-skills@main
  with:
    paths: '.'
    fail-on-error: 'true'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `paths` | Space-separated paths to search for agentskills | No | `.` |
| `fail-on-error` | Fail the action if any validation errors are found | No | `true` |

## Outputs

| Output | Description |
|--------|-------------|
| `agentskills-found` | Number of agentskills directories found |
| `agentskills-valid` | Number of valid agentskills |
| `agentskills-invalid` | Number of invalid agentskills |
| `errors` | JSON array of validation errors |

## Example workflows

### Validate on pull requests

```yaml
name: Validate agentskills

on:
  pull_request:
    paths:
      - '**/SKILL.md'
      - '**/skill.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate agentskills
        uses: agentskills/agentskills/.github/actions/validate-skills@main
```

### Validate with summary

```yaml
name: Validate agentskills

on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate agentskills
        id: validate
        uses: agentskills/agentskills/.github/actions/validate-skills@main
        with:
          paths: 'skills'
          fail-on-error: 'true'

      - name: Summary
        if: always()
        run: |
          echo "## Validation results" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| Metric | Count |" >> $GITHUB_STEP_SUMMARY
          echo "|--------|-------|" >> $GITHUB_STEP_SUMMARY
          echo "| Found | ${{ steps.validate.outputs.agentskills-found }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Valid | ${{ steps.validate.outputs.agentskills-valid }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Invalid | ${{ steps.validate.outputs.agentskills-invalid }} |" >> $GITHUB_STEP_SUMMARY
```

### Non-blocking validation

```yaml
- name: Validate agentskills
  id: validate
  uses: agentskills/agentskills/.github/actions/validate-skills@main
  with:
    fail-on-error: 'false'

- name: Check results
  run: |
    if [ "${{ steps.validate.outputs.agentskills-invalid }}" -gt 0 ]; then
      echo "::warning::Found invalid agentskills, but continuing..."
    fi
```

## Validation rules

The action validates that each `SKILL.md` conforms to the [agentskills specification](https://agentskills.io/specification).

### Required fields

- `name`: 1-64 characters, lowercase alphanumeric + hyphens, must match directory name
- `description`: 1-1024 characters, describes what the skill does and when to use it

### Optional fields

- `license`: License name or reference
- `compatibility`: Max 500 characters, environment requirements
- `metadata`: Key-value mapping for additional data
- `allowed-tools`: Space-delimited list of pre-approved tools

### Name rules

- Must be lowercase
- Cannot start or end with hyphen
- Cannot contain consecutive hyphens (`--`)
- Must match the parent directory name

See the [full specification](https://agentskills.io/specification) for complete details.

## Error output format

The `errors` output is a JSON array:

```json
[
  {
    "directory": "skills/my-skill",
    "name": "my-skill",
    "errors": [
      "Skill name 'MySkill' must be lowercase",
      "Directory name 'my-skill' must match skill name 'MySkill'"
    ]
  }
]
```

## Requirements

- Runs on `ubuntu-latest` (or any runner with Python 3.11+ and bash)
- Uses [uv](https://github.com/astral-sh/uv) for Python package management
- Requires `jq` for JSON processing (pre-installed on GitHub runners)

## License

See [LICENSE](../../../LICENSE) in the root of this repository.
