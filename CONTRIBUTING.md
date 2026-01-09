# Contributing to Agent Skills

Thank you for your interest in contributing to Agent Skills! This document provides guidelines and instructions for contributing to this repository.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Repository Structure](#repository-structure)
- [Contributing Documentation](#contributing-documentation)
- [Contributing to skills-ref](#contributing-to-skills-ref)
- [Creating Example Skills](#creating-example-skills)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Getting Help](#getting-help)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Ways to Contribute

There are several ways you can contribute to Agent Skills:

| Contribution Type | Description | Difficulty |
|-------------------|-------------|------------|
| Documentation | Improve guides, fix typos, add examples | Easy |
| Example Skills | Create well-documented example skills | Easy-Medium |
| Bug Reports | Report issues with the specification or tools | Easy |
| skills-ref SDK | Improve the Python reference library | Medium |
| Specification | Propose changes to the Agent Skills format | Advanced |

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentskills.git
   cd agentskills
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** following the guidelines below
5. **Push to your fork** and create a pull request

## Repository Structure

```
agentskills/
├── README.md              # Project overview
├── CONTRIBUTING.md        # This file
├── LICENSE                # CC BY 4.0 license
├── docs/                  # Documentation site (Mintlify)
│   ├── home.mdx
│   ├── what-are-skills.mdx
│   ├── specification.mdx
│   ├── integrate-skills.mdx
│   └── docs.json          # Navigation configuration
└── skills-ref/            # Python reference library
    ├── src/
    ├── tests/
    └── pyproject.toml
```

## Contributing Documentation

Documentation lives in the `docs/` directory and uses [Mintlify](https://mintlify.com/) for the documentation site at [agentskills.io](https://agentskills.io).

### Adding a New Page

1. Create a new `.mdx` file in `docs/`:
   ```mdx
   ---
   title: "Your Page Title"
   description: "A brief description of the page content."
   ---

   Your content here...
   ```

2. Add the page to `docs/docs.json` navigation:
   ```json
   {
     "navigation": {
       "pages": [
         "home",
         "what-are-skills",
         "specification",
         "integrate-skills",
         "your-new-page"
       ]
     }
   }
   ```

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Use tables for comparing options or listing fields
- Add tips and notes using Mintlify components:
  ```mdx
  <Tip>Helpful tip here</Tip>
  <Note>Important note here</Note>
  <Warning>Warning message here</Warning>
  ```

## Contributing to skills-ref

The `skills-ref/` directory contains the Python reference library for working with skills.

### Setup Development Environment

```bash
cd skills-ref

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run tests
uv run pytest
```

### Adding Features

1. Add your code in `src/`
2. Write tests in `tests/`
3. Update the README if adding new CLI commands
4. Ensure all tests pass before submitting

### CLI Commands

The skills-ref CLI currently supports:
- `skills-ref validate <path>` - Validate a skill directory
- `skills-ref to-prompt <path>...` - Generate XML for agent prompts

When adding new commands, follow the existing patterns and include help text.

## Creating Example Skills

Example skills help others understand how to write effective skills. To contribute an example:

### Skill Structure

```
your-skill/
├── SKILL.md              # Required: metadata + instructions
├── scripts/              # Optional: executable code
│   └── example.py
├── references/           # Optional: additional docs
│   └── REFERENCE.md
└── assets/               # Optional: templates, resources
    └── template.txt
```

### SKILL.md Template

```yaml
---
name: your-skill-name
description: Clear description of what this skill does and when to use it.
license: Apache-2.0
metadata:
  author: your-name
  version: "1.0"
---

# Your Skill Name

## When to Use This Skill

Describe the scenarios where this skill is helpful...

## Instructions

Step-by-step instructions for the agent...

## Examples

### Example 1: Basic Usage

Show input and expected output...

## Edge Cases

Document any special cases or limitations...
```

### Skill Guidelines

- Keep `SKILL.md` under 500 lines; move details to `references/`
- Write clear, actionable instructions
- Include examples of inputs and outputs
- Document edge cases and limitations
- Test your skill with an agent before submitting

## Pull Request Process

1. **Ensure your changes are complete** and follow the style guidelines
2. **Update documentation** if your changes affect user-facing features
3. **Run tests** if modifying skills-ref:
   ```bash
   cd skills-ref && uv run pytest
   ```
4. **Create a pull request** with:
   - A clear title describing the change
   - A description explaining what and why
   - Links to any related issues

### PR Title Format

Use a descriptive title that summarizes the change:
- `docs: Add troubleshooting guide`
- `skills-ref: Add init command for scaffolding`
- `spec: Clarify metadata field constraints`
- `example: Add code-review skill`

### Review Process

- A maintainer will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Style Guidelines

### Markdown/MDX

- Use ATX-style headers (`#`, `##`, `###`)
- Include blank lines before and after code blocks
- Use fenced code blocks with language identifiers
- Keep lines under 100 characters when practical

### Python (skills-ref)

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for public functions
- Keep functions focused and testable

### YAML (SKILL.md frontmatter)

- Use lowercase for field names
- Quote strings that contain special characters
- Keep descriptions concise but informative

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/agentskills/agentskills/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/agentskills/agentskills/issues)
- **Documentation**: Visit [agentskills.io](https://agentskills.io)

## License

By contributing to Agent Skills, you agree that your contributions will be licensed under the [CC BY 4.0 License](LICENSE).

---

Thank you for contributing to Agent Skills!
