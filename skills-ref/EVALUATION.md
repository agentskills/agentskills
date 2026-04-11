# Skill Quality Evaluation Framework

## Overview

The Skill Quality Evaluation Framework provides automated assessment of Agent Skills, measuring completeness, clarity, and structure to help maintain high-quality skill documentation.

## Features

### Three Quality Dimensions

1. **Completeness** (0-100)
   - Required metadata present (name, description, license)
   - Adequate content length
   - Code examples provided
   - Tool references documented

2. **Clarity** (0-100)
   - Description length appropriate (20-500 chars)
   - "When to use" guidance included
   - Actionable language (should, must, use)
   - Clear directives for agents

3. **Structure** (0-100)
   - Recommended sections present
   - Well-organized content
   - Proper markdown formatting

### Severity Levels

- **ERROR**: Critical issues preventing skill use
- **WARNING**: Important improvements recommended  
- **INFO**: Optional enhancements for best practices

### Scoring System

- Each dimension scored 0-100
- Errors: -30 points
- Warnings: -15 points
- Info: -5 points
- Overall score: average of three dimensions

## Usage

### CLI

```bash
# Basic evaluation
skills-ref evaluate path/to/skill

# JSON output
skills-ref evaluate path/to/skill --json

# With minimum score threshold (exits with code 1 if below threshold)
skills-ref evaluate path/to/skill --min-score 80
```

### Python API

```python
from pathlib import Path
from skills_ref import evaluate_skill

# Evaluate a skill
result = evaluate_skill(Path("my-skill"))

# Check scores
print(f"Overall: {result.overall_score:.1f}/100")
print(f"Completeness: {result.scores['completeness']:.1f}/100")
print(f"Clarity: {result.scores['clarity']:.1f}/100")
print(f"Structure: {result.scores['structure']:.1f}/100")

# Check for issues
if result.has_errors:
    print("Skill has critical errors!")
elif result.has_warnings:
    print("Skill has warnings to address")

# Iterate through findings
for finding in result.findings:
    print(f"[{finding.severity}] {finding.category}: {finding.message}")
    if finding.suggestion:
        print(f"  → {finding.suggestion}")
```

### Custom Evaluator

```python
from skills_ref.evaluator import SkillEvaluator

# Create custom evaluator
evaluator = SkillEvaluator()

# Customize thresholds
evaluator.min_description_length = 50
evaluator.max_description_length = 300
evaluator.min_content_length = 200

# Add custom required sections
evaluator.recommended_sections.add("## Prerequisites")
evaluator.recommended_sections.add("## Best Practices")

# Evaluate with custom settings
result = evaluator.evaluate(Path("my-skill"))
```

## What Gets Evaluated

### Frontmatter (SKILL.md YAML)

- **name**: Required, kebab-case
- **description**: Required, 20-500 chars, includes "when to use" guidance
- **license**: Recommended
- **compatibility**: Optional
- **allowed-tools**: Optional

### Content

- **Length**: Minimum 100 characters (excluding frontmatter)
- **Examples**: Code blocks or `<example>` tags expected
- **Sections**: Checks for Overview, When to Use, Usage, Examples
- **Language**: Looks for actionable verbs (should, must, use, call)
- **Tool References**: Suggests `allowed-tools` if tools mentioned

## Output Formats

### Human-Readable (Default)

```
============================================================
Skill Quality Evaluation: my-coding-skill
============================================================

Scores:
  Completeness   : 85.0/100
  Clarity        : 90.0/100
  Structure      : 75.0/100
  Overall        : 83.3/100

Findings (3):

  [INFO] completeness: No license specified
    → Add a 'license' field to SKILL.md frontmatter

  [INFO] structure: Missing recommended sections: ## Examples
    → Consider adding these sections for better clarity

  [WARNING] completeness: No code examples or examples found
    → Add examples to demonstrate skill usage
```

### JSON Output

```json
{
  "skill_path": "/path/to/skill",
  "skill_name": "my-coding-skill",
  "scores": {
    "completeness": 85.0,
    "clarity": 90.0,
    "structure": 75.0
  },
  "overall_score": 83.3,
  "findings": [
    {
      "severity": "info",
      "category": "completeness",
      "message": "No license specified",
      "suggestion": "Add a 'license' field to SKILL.md frontmatter"
    }
  ]
}
```

## Integration

### CI/CD Pipeline

```bash
# Fail build if skill score below 75
skills-ref evaluate my-skill --min-score 75 --json > evaluation.json

# Or evaluate all skills in a directory
find skills/ -name "SKILL.md" -exec dirname {} \; | \
  xargs -I {} skills-ref evaluate {} --min-score 75
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

changed_skills=$(git diff --cached --name-only | grep "SKILL.md" | xargs dirname)

for skill in $changed_skills; do
    if ! skills-ref evaluate "$skill" --min-score 70; then
        echo "Skill quality check failed for $skill"
        exit 1
    fi
done
```

### Batch Analysis

```python
from pathlib import Path
from skills_ref import evaluate_skill

skills_dir = Path("skills")
results = []

for skill_path in skills_dir.iterdir():
    if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
        result = evaluate_skill(skill_path)
        results.append({
            "name": result.skill_name,
            "score": result.overall_score,
            "errors": result.has_errors,
            "warnings": result.has_warnings
        })

# Sort by score
results.sort(key=lambda x: x["score"])

print("Skills needing improvement:")
for r in results[:5]:  # Bottom 5
    print(f"  {r['name']}: {r['score']:.1f}/100")
```

## Best Practices

1. **Run evaluation during development** - Catch issues early
2. **Set minimum thresholds** - Enforce quality standards in CI/CD
3. **Address errors first** - Fix critical issues before warnings
4. **Use JSON output for automation** - Easier to parse and integrate
5. **Customize for your needs** - Adjust thresholds and required sections
6. **Iterate based on findings** - Use suggestions to improve skills

## Files Created

- `src/skills_ref/evaluator.py` - Core evaluation logic
- `tests/test_evaluator.py` - Comprehensive test suite
- Updated `src/skills_ref/__init__.py` - Export evaluator classes
- Updated `src/skills_ref/cli.py` - Added `evaluate` command
- Updated `README.md` - Documentation and examples

## API Reference

### Classes

- `SkillEvaluator` - Main evaluator class
- `EvaluationResult` - Container for evaluation results
- `EvaluationFinding` - Individual finding with severity and suggestion
- `Severity` - Enum: ERROR, WARNING, INFO

### Functions

- `evaluate_skill(skill_path: Path) -> EvaluationResult` - Convenience function

### Properties

- `EvaluationResult.has_errors` - Boolean, any ERROR findings
- `EvaluationResult.has_warnings` - Boolean, any WARNING findings
- `EvaluationResult.overall_score` - Float, average of dimension scores
- `EvaluationResult.scores` - Dict[str, float], dimension scores
- `EvaluationResult.findings` - List[EvaluationFinding], all findings

## License

Apache 2.0 (same as the skills-ref library)
