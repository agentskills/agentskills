# Content Validation for Agent Skills

This guide explains how to validate the content of Agent Skills for compliance with security and privacy policies using [PromptLint](https://github.com/youcommit/promptlint).

## Overview

While the `skills-ref` library validates the **structure** of SKILL.md files (frontmatter format, required fields, naming conventions), content validation ensures that skill instructions don't accidentally contain:

- **PII (Personally Identifiable Information)**: Email addresses, phone numbers, SSNs, credit card numbers
- **Secrets**: API keys, AWS keys, JWT tokens
- **Internal Information**: Internal hostnames, IP addresses, project codenames

## Why Content Validation Matters

Agent Skills are often shared publicly or across organizations. Before distributing a skill, you should verify that:

1. No sensitive data was accidentally included in examples
2. No internal URLs or hostnames are exposed
3. No API keys or credentials are embedded in scripts
4. No PII from test data remains in the skill content

## Using PromptLint for Content Validation

### Installation

```bash
npm install -g promptlint
```

### Basic Usage

Scan a skill directory for policy violations:

```bash
promptlint scan ./my-skill
```

Scan all skills in a directory:

```bash
promptlint scan ./skills
```

### Setting Up a Policy File

Create a policy file for Agent Skills validation:

```bash
promptlint init --output agentskills-policy.yml
```

Example policy configuration for Agent Skills:

```yaml
version: 1

policies:
  # PII Detection
  - id: pii-email
    description: "Detect email addresses in skill content"
    severity: warn
    match:
      type: built_in
      detector: email
    actions:
      - type: annotate
      - type: suggest_redact

  - id: pii-phone
    description: "Detect phone numbers in skill content"
    severity: warn
    match:
      type: built_in
      detector: phone
    actions:
      - type: annotate

  # Secrets Detection
  - id: secrets-api-key
    description: "Block skills containing API keys"
    severity: error
    match:
      type: built_in
      detector: api_key
    actions:
      - type: block
      - type: message
        text: "Remove API keys before publishing skills"

  - id: secrets-aws-key
    description: "Block skills containing AWS keys"
    severity: error
    match:
      type: built_in
      detector: aws_key
    actions:
      - type: block

  - id: secrets-jwt
    description: "Block skills containing JWT tokens"
    severity: error
    match:
      type: built_in
      detector: jwt
    actions:
      - type: block

  # Internal Information
  - id: no-internal-hostnames
    description: "Block internal hostnames"
    severity: error
    match:
      type: regex
      pattern: "(?:\\.internal\\.|corp\\.|intranet\\.)"
    actions:
      - type: block
      - type: message
        text: "Remove internal hostnames before publishing"
```

### CI/CD Integration

Add content validation to your GitHub Actions workflow:

```yaml
name: Validate Skills

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      # Structure validation with skills-ref
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install skills-ref
        run: pip install skills-ref
      
      - name: Validate skill structure
        run: skills-ref validate ./my-skill
      
      # Content validation with PromptLint
      - name: Install PromptLint
        run: npm install -g promptlint
      
      - name: Validate skill content
        run: promptlint scan ./my-skill --fail-on error
```

### Output Formats

PromptLint supports multiple output formats:

```bash
# Human-readable text (default)
promptlint scan ./my-skill

# JSON for programmatic processing
promptlint scan ./my-skill --format json

# SARIF for GitHub Code Scanning
promptlint scan ./my-skill --format sarif > results.sarif
```

## Validation Workflow

The recommended validation workflow for Agent Skills:

1. **Structure Validation** (skills-ref)
   - Validates SKILL.md frontmatter format
   - Checks required fields (name, description)
   - Verifies naming conventions

2. **Content Validation** (PromptLint)
   - Scans for PII and secrets
   - Checks for internal information
   - Enforces custom policies

3. **Manual Review**
   - Review flagged content
   - Verify examples are appropriate
   - Check for sensitive business logic

## Built-in Detectors

PromptLint includes these built-in detectors:

| Detector | Description |
|----------|-------------|
| `email` | Email addresses |
| `phone` | Phone numbers (US format) |
| `ssn` | US Social Security Numbers |
| `credit_card` | Credit card numbers |
| `ipv4` | IPv4 addresses |
| `ipv6` | IPv6 addresses |
| `url` | URLs |
| `api_key` | Common API key patterns |
| `aws_key` | AWS access keys |
| `jwt` | JWT tokens |

## Best Practices

1. **Run validation before publishing**: Always validate skills before sharing publicly
2. **Use CI/CD**: Automate validation in your build pipeline
3. **Custom policies**: Add organization-specific rules for internal terms
4. **Review warnings**: Even warnings should be reviewed before publishing
5. **Test with real data carefully**: Use synthetic data in examples when possible

## Related Resources

- [PromptLint Documentation](https://github.com/youcommit/promptlint)
