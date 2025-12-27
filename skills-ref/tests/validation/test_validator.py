import pytest
from skills_ref.parser.extended_parser import ExtendedSkillParser
from skills_ref.validation.validator import SkillValidator, Severity

@pytest.fixture
def skill_dir_with_issues(tmp_path):
    d = tmp_path / "test_skill_issues"
    d.mkdir()
    (d / "SKILL.md").write_text("""---
name: InvalidName
description: A test skill with issues
---

# Heading 1

Block with invalid ID ^123

> [!invalid] Callout
> Content

[[MissingLink]]

```
print("No language")
```
""", encoding='utf-8')
    return d

def test_validator(skill_dir_with_issues):
    parser = ExtendedSkillParser(skill_dir_with_issues)
    parse_result = parser.parse()

    validator = SkillValidator()
    result = validator.validate(
        parse_result.properties,
        parse_result.ast,
        parse_result.index,
        parse_result.raw_body
    )

    assert not result.valid

    # Check Frontmatter Name Error
    name_error = next((i for i in result.errors if "lowercase" in i.message), None)
    assert name_error

    # Check Callout Error
    callout_error = next((i for i in result.errors if "Invalid callout type" in i.message), None)
    assert callout_error

    # Check Block ID Warning
    block_warning = next((i for i in result.warnings if "non-standard format" in i.message), None)
    assert block_warning

    # Check Code Block Warning
    code_warning = next((i for i in result.warnings if "missing language" in i.message), None)
    assert code_warning

    # Check Link Warning
    link_warning = next((i for i in result.warnings if "Unresolved link" in i.message), None)
    if not link_warning:
        print("\nWarnings found:", [w.message for w in result.warnings])
        print("Errors found:", [e.message for e in result.errors])
    assert link_warning
