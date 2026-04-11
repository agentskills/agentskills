# skills-ref

Reference library for Agent Skills.

> [!IMPORTANT]
> This library is intended for demonstration purposes only. It is not meant to be used in production.

## Installation

### macOS / Linux

Using pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Or using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
source .venv/bin/activate
```

### Windows

Using pip (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Using pip (Command Prompt):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .
```

Or using [uv](https://docs.astral.sh/uv/):

```powershell
uv sync
.venv\Scripts\Activate.ps1
```

After installation, the `skills-ref` executable will be available on your `PATH` (within the activated virtual environment).

## Usage

### CLI

```bash
# Validate a skill
skills-ref validate path/to/skill

# Read skill properties (outputs JSON)
skills-ref read-properties path/to/skill

# Generate <available_skills> XML for agent prompts
skills-ref to-prompt path/to/skill-a path/to/skill-b

# Evaluate skill quality
skills-ref evaluate path/to/skill

# Evaluate with JSON output
skills-ref evaluate path/to/skill --json

# Evaluate with minimum score threshold
skills-ref evaluate path/to/skill --min-score 80
```

### Python API

```python
from pathlib import Path
from skills_ref import validate, read_properties, to_prompt, evaluate_skill

# Validate a skill directory
problems = validate(Path("my-skill"))
if problems:
    print("Validation errors:", problems)

# Read skill properties
props = read_properties(Path("my-skill"))
print(f"Skill: {props.name} - {props.description}")

# Generate prompt for available skills
prompt = to_prompt([Path("skill-a"), Path("skill-b")])
print(prompt)

# Evaluate skill quality
result = evaluate_skill(Path("my-skill"))
print(f"Overall score: {result.overall_score:.1f}/100")
print(f"Scores: {result.scores}")
for finding in result.findings:
    print(f"  [{finding.severity}] {finding.message}")
```

## Agent Prompt Integration

Use `to-prompt` to generate the suggested `<available_skills>` XML block for your agent's system prompt. This format is recommended for Anthropic's models, but Skill Clients may choose to format it differently based on the model being used.

```xml
<available_skills>
<skill>
<name>
my-skill
</name>
<description>
What this skill does and when to use it
</description>
<location>
/path/to/my-skill/SKILL.md
</location>
</skill>
</available_skills>
```

The `<location>` element tells the agent where to find the full skill instructions.

## Skill Quality Evaluation

The evaluation framework assesses skills across three dimensions:

- **Completeness**: Has required content, examples, and metadata
- **Clarity**: Clear, concise descriptions with actionable guidance
- **Structure**: Well-organized with recommended sections

### Evaluation Metrics

Each skill receives scores (0-100) for:
- Completeness
- Clarity  
- Structure
- Overall (average of the three)

### Findings

The evaluator provides actionable findings at three severity levels:
- **ERROR**: Critical issues that prevent skill use
- **WARNING**: Important improvements recommended
- **INFO**: Optional enhancements for best practices

### Example Output

```
============================================================
Skill Quality Evaluation: my-skill
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

## License

Apache 2.0
