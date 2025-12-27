import pytest
from skills_ref.parser.extended_parser import ExtendedSkillParser
from skills_ref.navigation.block_navigator import BlockNavigator, SkillRegistry
from skills_ref.navigation.progressive_loader import ProgressiveLoader, LoadingStrategy, LoadRequest

@pytest.fixture
def skill_dir_nav(tmp_path):
    d = tmp_path / "test_skill_nav"
    d.mkdir()
    (d / "SKILL.md").write_text("""---
name: nav-skill
description: Navigation Test
---

# Introduction ^intro-block

This is the introduction.

## Section A

Content A.

### Subsection A.1 ^a1

Content A.1.

## Section B

Content B.
""", encoding='utf-8')
    return d

@pytest.fixture
def registry(skill_dir_nav):
    parser = ExtendedSkillParser(skill_dir_nav)
    result = parser.parse()
    reg = SkillRegistry()
    reg.register("nav-skill", result)
    return reg

def test_block_navigation(registry):
    navigator = BlockNavigator(registry)

    # Test valid block navigation
    res = navigator.navigate("nav-skill:^intro-block")
    assert res.found
    assert "Introduction" in res.content
    assert res.context.section_path == ["introduction"] # anchor is slugified

    res = navigator.navigate("nav-skill:^a1")
    assert res.found
    assert "Subsection A.1" in res.content or "Content A.1" in getattr(res.node, 'raw', '') # Check logic

def test_heading_navigation(registry):
    navigator = BlockNavigator(registry)

    # Test section navigation
    res = navigator.navigate("nav-skill:#section-a")
    assert res.found
    assert "Content A" in res.content
    assert "Content A.1" in res.content # Includes children

    # Test nested path?
    # My implementation assumes path segments match anchors in tree.
    # "section-a/subsection-a-1"
    # Wait, my slug generation logic: "Subsection A.1" -> "subsection-a1"

    res = navigator.navigate("nav-skill:#section-a/subsection-a1")
    assert res.found
    assert "Content A.1" in res.content

def test_progressive_loader(registry):
    loader = ProgressiveLoader(registry)

    # Test Full Load
    req = LoadRequest("nav-skill", LoadingStrategy.FULL)
    res = loader.load(req)
    assert res.token_count > 0
    assert not res.truncated
    assert "*" in res.sections_loaded

    # Test Heading Only
    req = LoadRequest("nav-skill", LoadingStrategy.HEADING_ONLY, depth=2)
    res = loader.load(req)
    assert "# Introduction" in res.content
    assert "## Section A" in res.content
    assert "## Section B" in res.content
    # Depth 2 means H1, H2. H3 might be excluded?
    # H3 is level 3. Depth 2 < 3 is false?
    # Logic: if current_depth < depth.
    # Root is depth 0?
    # traverse(root, 0).
    # H1 (Introduction) at depth 0. 0 < 2 -> recurse 1.
    # H2 (Section A) at depth 1. 1 < 2 -> recurse 2.
    # H3 (Subsection A.1) at depth 2. 2 < 2 False.
    # So H3 should NOT be in content.
    assert "### Subsection A.1" not in res.content

    # Test Section Load
    req = LoadRequest("nav-skill", LoadingStrategy.SECTION, target="section-a")
    res = loader.load(req)
    assert "Content A" in res.content
    assert "Content A.1" in res.content
