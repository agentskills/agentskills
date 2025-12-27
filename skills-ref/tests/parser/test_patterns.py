import pytest
from pathlib import Path
from skills_ref.parser.patterns import PATTERNS, PatternType

def test_wikilink_regex():
    pattern = PATTERNS[PatternType.WIKILINK]

    # Test simple link
    match = pattern.match("[[Simple]]")
    assert match
    assert match.group("target") == "Simple"

    # Test link with display
    match = pattern.match("[[Target|Display]]")
    assert match
    assert match.group("target") == "Target"
    assert match.group("display") == "Display"

    # Test link with heading
    match = pattern.match("[[Target#Heading]]")
    assert match
    assert match.group("target") == "Target"
    assert match.group("heading") == "Heading"

    # Test link with block
    match = pattern.match("[[Target^block-id]]")
    assert match
    assert match.group("target") == "Target"
    assert match.group("block") == "block-id"

def test_block_id_regex():
    pattern = PATTERNS[PatternType.BLOCK_ID]

    match = pattern.match("Text ^block-id")
    assert match
    assert match.group("id") == "block-id"

def test_nested_tag_regex():
    pattern = PATTERNS[PatternType.NESTED_TAG]

    match = pattern.match("#tag/nested")
    assert match
    assert match.group("path") == "tag/nested"

def test_callout_regex():
    pattern = PATTERNS[PatternType.CALLOUT]

    match = pattern.match("> [!info] Title")
    assert match
    assert match.group("type") == "info"
    assert match.group("title") == "Title"
