# skills_ref/parser/patterns.py — Regex patterns for Obsidian-flavored Markdown

import re
from dataclasses import dataclass
from typing import Optional, List, Pattern, Tuple
from enum import Enum, auto

class PatternType(Enum):
    WIKILINK = auto()
    BLOCK_ID = auto()
    BLOCK_REFERENCE = auto()
    HEADING_LINK = auto()
    NESTED_TAG = auto()
    CALLOUT = auto()
    FOOTNOTE_REF = auto()
    FOOTNOTE_DEF = auto()
    INLINE_FOOTNOTE = auto()
    MERMAID_BLOCK = auto()
    DATAVIEW_BLOCK = auto()
    DATAVIEW_INLINE = auto()
    TEMPLATER_CMD = auto()
    TEMPLATER_EXEC = auto()

@dataclass(frozen=True)
class ObsidianPattern:
    """Immutable pattern definition with validation."""
    pattern_type: PatternType
    regex: Pattern
    description: str
    capture_groups: Tuple[str, ...]

    def match(self, text: str) -> Optional[re.Match]:
        return self.regex.search(text)

    def find_all(self, text: str) -> List[re.Match]:
        return list(self.regex.finditer(text))

# Pattern Definitions
PATTERNS: dict[PatternType, ObsidianPattern] = {

    PatternType.WIKILINK: ObsidianPattern(
        pattern_type=PatternType.WIKILINK,
        regex=re.compile(
            r'\[\['
            r'(?P<target>[^\]|#^]+)'           # Note name
            r'(?:#(?P<heading>[^\]|^|]+))?'    # Optional heading
            r'(?:\^(?P<block>[^\]|]+))?'       # Optional block ID
            r'(?:\|(?P<display>[^\]]+))?'      # Optional display text
            r'\]\]',
            re.UNICODE
        ),
        description="Wikilink with optional heading, block, and display text",
        capture_groups=('target', 'heading', 'block', 'display')
    ),

    PatternType.BLOCK_ID: ObsidianPattern(
        pattern_type=PatternType.BLOCK_ID,
        regex=re.compile(
            r'(?:^|\s)\^(?P<id>[a-zA-Z0-9_-]+)(?:\s|$)',
            re.MULTILINE
        ),
        description="Block identifier at end of line/paragraph",
        capture_groups=('id',)
    ),

    PatternType.BLOCK_REFERENCE: ObsidianPattern(
        pattern_type=PatternType.BLOCK_REFERENCE,
        regex=re.compile(
            r'\[\[(?P<file>[^\]#^]+)\^(?P<block>[a-zA-Z0-9_-]+)\]\]'
        ),
        description="Reference to specific block in another file",
        capture_groups=('file', 'block')
    ),

    PatternType.NESTED_TAG: ObsidianPattern(
        pattern_type=PatternType.NESTED_TAG,
        regex=re.compile(
            r'(?:^|\s)#(?P<path>(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]+)(?:\s|$)',
            re.UNICODE
        ),
        description="Hierarchical tag with slash-separated path",
        capture_groups=('path',)
    ),

    PatternType.CALLOUT: ObsidianPattern(
        pattern_type=PatternType.CALLOUT,
        regex=re.compile(
            r'^>\s*\[!(?P<type>\w+)\]'
            r'(?P<fold>[+-])?'
            r'(?:\s+(?P<title>.+))?$',
            re.MULTILINE
        ),
        description="Callout block with type, fold state, and optional title",
        capture_groups=('type', 'fold', 'title')
    ),

    PatternType.FOOTNOTE_REF: ObsidianPattern(
        pattern_type=PatternType.FOOTNOTE_REF,
        regex=re.compile(r'\[\^(?P<id>[^\]]+)\](?!\:)'),
        description="Footnote reference in text",
        capture_groups=('id',)
    ),

    PatternType.FOOTNOTE_DEF: ObsidianPattern(
        pattern_type=PatternType.FOOTNOTE_DEF,
        regex=re.compile(
            r'^\[\^(?P<id>[^\]]+)\]:\s*(?P<content>.+)$',
            re.MULTILINE
        ),
        description="Footnote definition",
        capture_groups=('id', 'content')
    ),

    PatternType.INLINE_FOOTNOTE: ObsidianPattern(
        pattern_type=PatternType.INLINE_FOOTNOTE,
        regex=re.compile(r'\^\[(?P<content>[^\]]+)\]'),
        description="Inline footnote with immediate content",
        capture_groups=('content',)
    ),

    PatternType.MERMAID_BLOCK: ObsidianPattern(
        pattern_type=PatternType.MERMAID_BLOCK,
        regex=re.compile(
            r'```mermaid\s*\n(?P<content>.*?)```',
            re.DOTALL
        ),
        description="Mermaid diagram code block",
        capture_groups=('content',)
    ),

    PatternType.DATAVIEW_BLOCK: ObsidianPattern(
        pattern_type=PatternType.DATAVIEW_BLOCK,
        regex=re.compile(
            r'```dataview\s*\n(?P<query>.*?)```',
            re.DOTALL
        ),
        description="Dataview query block",
        capture_groups=('query',)
    ),

    PatternType.DATAVIEW_INLINE: ObsidianPattern(
        pattern_type=PatternType.DATAVIEW_INLINE,
        regex=re.compile(r'`=\s*(?P<expr>[^`]+)`'),
        description="Inline dataview expression",
        capture_groups=('expr',)
    ),

    PatternType.TEMPLATER_CMD: ObsidianPattern(
        pattern_type=PatternType.TEMPLATER_CMD,
        regex=re.compile(r'<%\s*(?P<cmd>[^%*][^%]*)\s*%>'),
        description="Templater output command",
        capture_groups=('cmd',)
    ),

    PatternType.TEMPLATER_EXEC: ObsidianPattern(
        pattern_type=PatternType.TEMPLATER_EXEC,
        regex=re.compile(r'<%\*\s*(?P<code>.*?)\s*%>', re.DOTALL),
        description="Templater execution block",
        capture_groups=('code',)
    ),
}

def extract_all_syntax(text: str) -> dict[PatternType, List[dict]]:
    """Extract all Obsidian syntax elements from text."""
    results = {}
    for ptype, pattern in PATTERNS.items():
        matches = pattern.find_all(text)
        results[ptype] = [
            {name: m.group(name) for name in pattern.capture_groups if m.group(name) is not None}
            for m in matches
        ]
    return results
