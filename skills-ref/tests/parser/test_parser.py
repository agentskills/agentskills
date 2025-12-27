import pytest
from pathlib import Path
from skills_ref.parser.extended_parser import ExtendedSkillParser
from skills_ref.types.ast import HeadingNode, CodeBlockNode

# Mock directory structure
@pytest.fixture
def skill_dir(tmp_path):
    d = tmp_path / "test_skill"
    d.mkdir()
    (d / "SKILL.md").write_text("""---
name: test-skill
description: A test skill
---

# Heading 1

Paragraph with [[link]].

## Heading 2 ^block-id

```python
print("hello")
```

> [!info] Callout
> Content
""", encoding='utf-8')
    return d

def test_parser_end_to_end(skill_dir):
    parser = ExtendedSkillParser(skill_dir)
    result = parser.parse()

    assert result.properties.name == "test-skill"
    assert len(result.ast) > 0

    # Check Heading 1
    h1 = result.ast[0]
    assert isinstance(h1, HeadingNode)
    assert h1.text == "Heading 1"
    assert h1.level == 1

    # Check block ID extraction
    # Find heading 2 (nested under H1)
    h2 = next(n for n in h1.children if isinstance(n, HeadingNode) and n.text == "Heading 2")
    assert h2.block_id == "block-id"

    # Check code block (nested under H2)
    cb = next(n for n in h2.children if isinstance(n, CodeBlockNode))
    assert cb.language == "python"
    assert cb.is_executable == True

    # Check index
    assert "block-id" in result.index.block_registry
    assert result.index.block_registry["block-id"].node == h2
