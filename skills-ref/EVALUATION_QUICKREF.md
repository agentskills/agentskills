# Evaluation Framework - Quick Reference

## Installation

```bash
cd skills-ref
uv sync  # or: pip install -e .
```

## Quick Start

```bash
# Evaluate a skill
skills-ref evaluate path/to/skill

# With quality threshold
skills-ref evaluate path/to/skill --min-score 80

# JSON output
skills-ref evaluate path/to/skill --json
```

## Python Quick Start

```python
from pathlib import Path
from skills_ref import evaluate_skill

result = evaluate_skill(Path("my-skill"))
print(f"Score: {result.overall_score:.1f}/100")
```

## Quality Dimensions

| Dimension | What it measures |
|-----------|------------------|
| **Completeness** | Metadata, content length, examples, license |
| **Clarity** | Description quality, "when to use" guidance, actionable language |
| **Structure** | Recommended sections, organization |

## Severity Levels

| Level | Impact | Points Deducted |
|-------|--------|----------------|
| **ERROR** | Critical - prevents skill use | -30 |
| **WARNING** | Important - should fix | -15 |
| **INFO** | Optional - best practice | -5 |

## Common Findings

### Completeness

- ❌ `SKILL.md file not found` (ERROR)
- ⚠️ `No code examples or examples found` (WARNING)
- ℹ️ `No license specified` (INFO)
- ⚠️ `Content is too short` (WARNING)

### Clarity

- ⚠️ `Description is too short/long` (WARNING)
- ℹ️ `Description doesn't clearly indicate when to use` (INFO)
- ℹ️ `Content may lack actionable guidance` (INFO)

### Structure

- ℹ️ `Missing recommended sections` (INFO)

## Recommended Sections

Good skills should include:

```markdown
## Overview
Brief introduction to what the skill does

## When to Use
Clear guidance on when agents should invoke this skill

## Usage
How to use the skill effectively

## Examples
Code examples or usage examples
```

## Score Interpretation

| Score | Quality Level | Action |
|-------|---------------|--------|
| 90-100 | Excellent | Maintain quality |
| 75-89 | Good | Minor improvements |
| 60-74 | Fair | Address warnings |
| 0-59 | Poor | Major revision needed |

## CLI Exit Codes

- `0` - Skill passes evaluation
- `1` - Errors found or score below `--min-score`

## Integration Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
skills-ref evaluate changed_skill --min-score 70 || exit 1
```

### CI/CD

```yaml
# .github/workflows/quality.yml
- name: Evaluate Skills
  run: |
    for skill in skills/*; do
      skills-ref evaluate "$skill" --min-score 75
    done
```

### Python Script

```python
# evaluate_all.py
from pathlib import Path
from skills_ref import evaluate_skill

for skill in Path("skills").iterdir():
    if (skill / "SKILL.md").exists():
        result = evaluate_skill(skill)
        if result.overall_score < 75:
            print(f"⚠️  {skill.name}: {result.overall_score:.1f}/100")
```

## Customization

```python
from skills_ref.evaluator import SkillEvaluator

evaluator = SkillEvaluator()

# Adjust thresholds
evaluator.min_description_length = 50
evaluator.max_description_length = 300
evaluator.min_content_length = 200

# Add required sections
evaluator.recommended_sections.add("## Prerequisites")

result = evaluator.evaluate(Path("my-skill"))
```

## Troubleshooting

### "SKILL.md file not found"
- Ensure the file exists and is named exactly `SKILL.md` (case-sensitive)

### "Failed to parse skill properties"
- Check YAML frontmatter syntax
- Ensure frontmatter is wrapped in `---`

### Low completeness score
- Add code examples
- Include license field
- Expand content to minimum length

### Low clarity score
- Improve description (20-500 chars)
- Add "when to use" guidance
- Use actionable language (should, must, use)

### Low structure score
- Add recommended sections
- Improve markdown formatting

## Further Reading

- Full documentation: `EVALUATION.md`
- Main README: `README.md`
- Tests: `tests/test_evaluator.py`
