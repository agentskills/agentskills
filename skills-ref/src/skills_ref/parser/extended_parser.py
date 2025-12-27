# skills_ref/parser/extended_parser.py — Extended parser for Obsidian-flavored Markdown

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum, auto
import re
from pathlib import Path

from ..types.core import SkillProperties, SourcePosition, LineColumn, ValidationResult
from ..types.ast import (
    ASTNode, HeadingNode, ParagraphNode, CodeBlockNode,
    CalloutNode, TableNode, WikiLinkInline, InlineNode,
    TextNode, TagInlineNode, FootnoteRefNode,
    TagNode, HorizontalRuleNode, BlockquoteNode,
    FrontmatterNode
)
from ..types.index import SemanticIndex
from ..errors import ParseError
from .patterns import PATTERNS, PatternType
from .index_builder import SemanticIndexBuilder


class ParserState(Enum):
    """Parser state machine states."""
    NORMAL = auto()
    IN_CODE_BLOCK = auto()
    IN_FRONTMATTER = auto()
    IN_CALLOUT = auto()
    IN_TABLE = auto()
    IN_LIST = auto()


@dataclass
class ParserContext:
    """Mutable context during parsing."""
    state: ParserState = ParserState.NORMAL
    current_code_fence: Optional[str] = None
    code_language: Optional[str] = None
    code_buffer: List[str] = field(default_factory=list)
    callout_buffer: List[str] = field(default_factory=list)
    callout_type: Optional[str] = None
    callout_title: Optional[str] = None
    callout_fold: Optional[str] = None
    table_buffer: List[str] = field(default_factory=list)
    current_heading_stack: List[HeadingNode] = field(default_factory=list)
    line_number: int = 0
    column: int = 0


@dataclass
class ExtendedParseResult:
    """Complete result from extended parsing."""
    properties: SkillProperties
    ast: List[ASTNode]
    index: SemanticIndex
    validation: ValidationResult
    raw_body: str


class ExtendedSkillParser:
    """
    Extended parser for SKILL.md files supporting Obsidian-flavored Markdown.
    """

    def __init__(self, skill_directory: Path):
        self.skill_dir = skill_directory
        self.skill_md_path = self._find_skill_md()
        self.index_builder = SemanticIndexBuilder()

    def _find_skill_md(self) -> Path:
        """Locate SKILL.md (case-insensitive)."""
        if self.skill_dir.is_file():
             return self.skill_dir

        for name in ['SKILL.md', 'skill.md']:
            path = self.skill_dir / name
            if path.exists():
                return path
        raise ParseError(f"No SKILL.md found in {self.skill_dir}")

    def parse(self) -> ExtendedParseResult:
        """Execute complete parse with AST, index, and validation."""
        content = self.skill_md_path.read_text(encoding='utf-8')

        # Phase 1: Extract frontmatter
        properties, body, body_start_line = self._parse_frontmatter(content)

        # Phase 2: Parse body into AST
        ast = self._parse_body(body, body_start_line)

        # Phase 3: Build semantic index
        index = self.index_builder.build(ast)

        # Phase 4: Validate (Placeholder - Validator implemented in next phase)
        validation = ValidationResult()

        return ExtendedParseResult(
            properties=properties,
            ast=ast,
            index=index,
            validation=validation,
            raw_body=body
        )

    def _parse_frontmatter(self, content: str) -> Tuple[SkillProperties, str, int]:
        """Extract and parse YAML frontmatter."""
        if not content.startswith('---'):
            raise ParseError("SKILL.md must start with YAML frontmatter (---)")

        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ParseError("Frontmatter not properly closed with ---")

        yaml_content = parts[1].strip()
        body = parts[2].lstrip('\n')

        # Count lines in frontmatter to get body start line
        # parts[0] is empty string before first ---
        frontmatter_lines = parts[1].count('\n') + 2
        # Add 1 if there was a newline after second --- before body starts
        # The split might consume newlines.

        # Simple YAML parsing (using strictyaml or similar as per existing deps)
        try:
            import strictyaml
            parsed = strictyaml.load(yaml_content).data
        except ImportError:
            import yaml
            parsed = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ParseError(f"Invalid YAML frontmatter: {e}")

        properties = SkillProperties(
            name=parsed.get('name', ''),
            description=parsed.get('description', ''),
            license=parsed.get('license'),
            compatibility=parsed.get('compatibility'),
            metadata=parsed.get('metadata'),
            allowed_tools=parsed.get('allowed-tools', '').split() if isinstance(parsed.get('allowed-tools'), str) else parsed.get('allowed-tools')
        )

        return properties, body, frontmatter_lines + 1

    def _parse_body(self, body: str, start_line: int) -> List[ASTNode]:
        """Parse markdown body into AST with full Obsidian syntax support."""
        lines = body.split('\n')
        ctx = ParserContext(line_number=start_line - 1)
        root_nodes: List[ASTNode] = []

        # Helper to append node to correct parent (nested under heading)
        def append_node(node: ASTNode):
            if isinstance(node, HeadingNode):
                # Manage stack
                while ctx.current_heading_stack and ctx.current_heading_stack[-1].level >= node.level:
                    ctx.current_heading_stack.pop()

                if ctx.current_heading_stack:
                    ctx.current_heading_stack[-1].children.append(node)
                else:
                    root_nodes.append(node)

                ctx.current_heading_stack.append(node)
            else:
                # Non-heading node
                if ctx.current_heading_stack:
                    ctx.current_heading_stack[-1].children.append(node)
                else:
                    root_nodes.append(node)

        i = 0
        while i < len(lines):
            line = lines[i]
            ctx.line_number = start_line + i

            # Special handling for implicit block endings
            if ctx.state == ParserState.IN_CALLOUT:
                # If line doesn't start with >, end the callout
                if not (line.strip() == '' or line.lstrip().startswith('>')):
                    # Flush callout
                    ctx.state = ParserState.NORMAL
                    callout_body = '\n'.join(ctx.callout_buffer)
                    children = self._parse_fragment(callout_body, ctx.line_number - len(ctx.callout_buffer))
                    node = CalloutNode(
                        type='callout',
                        callout_type=ctx.callout_type,
                        title=ctx.callout_title,
                        fold_state=ctx.callout_fold,
                        children=children,
                        position=SourcePosition(
                            start=LineColumn(ctx.line_number - len(ctx.callout_buffer), 0, 0),
                            end=LineColumn(ctx.line_number, 0, 0)
                        ),
                        raw=""
                    )
                    append_node(node)
                    ctx.callout_buffer = []
                    # Don't increment i, process this line in NORMAL state
                    continue

            node = self._process_line(line, ctx)
            if node:
                append_node(node)

            i += 1

        # Flush any pending buffers
        pending = self._flush_buffers(ctx)
        for node in pending:
            append_node(node)

        return root_nodes

    def _process_line(self, line: str, ctx: ParserContext) -> Optional[ASTNode]:
        """Process single line based on current parser state."""

        # State: Inside code block
        if ctx.state == ParserState.IN_CODE_BLOCK:
            return self._process_code_block_line(line, ctx)

        # State: Inside callout
        if ctx.state == ParserState.IN_CALLOUT:
            return self._process_callout_line(line, ctx)

        # State: Inside table
        if ctx.state == ParserState.IN_TABLE:
            return self._process_table_line(line, ctx)

        # State: Normal - detect new constructs
        return self._process_normal_line(line, ctx)

    def _process_normal_line(self, line: str, ctx: ParserContext) -> Optional[ASTNode]:
        """Process line in normal state, detecting construct starts."""

        # Check for code fence start
        code_match = re.match(r'^(\s*)(`{3,}|~{3,})(\w*)?(.*)$', line)
        if code_match:
            ctx.state = ParserState.IN_CODE_BLOCK
            ctx.current_code_fence = code_match.group(2)
            ctx.code_language = code_match.group(3) or None
            ctx.code_buffer = []
            return None

        # Check for callout start
        callout_match = PATTERNS[PatternType.CALLOUT].regex.match(line)
        if callout_match:
            ctx.state = ParserState.IN_CALLOUT
            ctx.callout_type = callout_match.group('type').lower()
            ctx.callout_title = callout_match.group('title')
            ctx.callout_fold = callout_match.group('fold')
            ctx.callout_buffer = []
            return None

        # Check for table start
        if '|' in line and re.match(r'^\s*\|', line):
            # Simple check, improved later
            ctx.state = ParserState.IN_TABLE
            ctx.table_buffer = [line]
            return None

        # Check for block ID at end of line (BEFORE heading check to strip it)
        block_id = None
        block_match = PATTERNS[PatternType.BLOCK_ID].regex.search(line)
        if block_match:
            block_id = block_match.group('id')
            line = line[:block_match.start()].rstrip()

        # Check for heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            return self._create_heading_node(
                level=len(heading_match.group(1)),
                text=heading_match.group(2),
                line=ctx.line_number,
                block_id=block_id
            )

        # Regular paragraph
        if line.strip():
            return self._create_paragraph_node(line, ctx.line_number, block_id)

        # Empty line - ignore or return None
        return None

    def _process_code_block_line(self, line: str, ctx: ParserContext) -> Optional[ASTNode]:
        """Process line inside code block."""
        # Check for end fence
        # It must match the length of the opening fence or be longer?
        # Usually >= length of opening fence.
        # But for simplicity, strict match of fence string or startswith?
        # Obsidian requires matching fence length or more.
        if line.strip().startswith(ctx.current_code_fence):
            # End of code block
            ctx.state = ParserState.NORMAL
            return self._create_code_block_node(
                language=ctx.code_language,
                content='\n'.join(ctx.code_buffer),
                line=ctx.line_number - len(ctx.code_buffer) - 1
            )
        else:
            ctx.code_buffer.append(line)
            return None

    def _process_callout_line(self, line: str, ctx: ParserContext) -> Optional[ASTNode]:
        # We assume _parse_body handles the exit condition now
        # So we just accumulate
        content = re.sub(r'^>\s?', '', line)
        ctx.callout_buffer.append(content)
        return None

    def _process_table_line(self, line: str, ctx: ParserContext) -> Optional[ASTNode]:
        if '|' in line:
            ctx.table_buffer.append(line)
            return None
        else:
            ctx.state = ParserState.NORMAL
            # Create table node
            node = self._create_table_node(ctx.table_buffer, ctx.line_number - len(ctx.table_buffer))
            ctx.table_buffer = []
            return node

    def _flush_buffers(self, ctx: ParserContext) -> List[ASTNode]:
        nodes = []
        if ctx.state == ParserState.IN_CODE_BLOCK:
            nodes.append(self._create_code_block_node(
                ctx.code_language,
                '\n'.join(ctx.code_buffer),
                ctx.line_number - len(ctx.code_buffer)
            ))
        elif ctx.state == ParserState.IN_CALLOUT:
             children = self._parse_fragment('\n'.join(ctx.callout_buffer), ctx.line_number - len(ctx.callout_buffer))
             nodes.append(CalloutNode(
                type='callout',
                callout_type=ctx.callout_type,
                title=ctx.callout_title,
                fold_state=ctx.callout_fold,
                children=children,
                position=SourcePosition(
                    start=LineColumn(ctx.line_number - len(ctx.callout_buffer), 0, 0),
                    end=LineColumn(ctx.line_number, 0, 0)
                ),
                raw=""
            ))
        elif ctx.state == ParserState.IN_TABLE:
            nodes.append(self._create_table_node(ctx.table_buffer, ctx.line_number - len(ctx.table_buffer)))

        return nodes

    def _parse_fragment(self, text: str, start_line: int) -> List[ASTNode]:
        """Recursively parse a fragment of markdown."""
        # Avoid infinite recursion if possible, but for callouts we need it.
        # Create a new parser or reuse logic.
        return self._parse_body(text, start_line)

    def _create_heading_node(self, level: int, text: str, line: int, block_id: Optional[str] = None) -> HeadingNode:
        """Create heading node with anchor generation."""
        # Extract block ID if present in text (if not passed from line processing)
        if not block_id:
            block_match = PATTERNS[PatternType.BLOCK_ID].regex.search(text)
            if block_match:
                block_id = block_match.group('id')
                text = text[:block_match.start()].rstrip()

        # Generate anchor slug
        anchor = self._generate_anchor(text)

        # Parse inline content for wikilinks, tags, etc.
        inline_nodes = self._parse_inline(text, line)

        return HeadingNode(
            type='heading',
            level=level,
            text=text,
            anchor=anchor,
            block_id=block_id,
            position=SourcePosition(
                start=LineColumn(line, 0, 0),
                end=LineColumn(line, len(text), 0)
            ),
            inline_content=inline_nodes,
            children=[],
            raw=f"{'#' * level} {text}"
        )

    def _generate_anchor(self, text: str) -> str:
        """Generate URL-safe anchor from heading text."""
        cleaned = re.sub(r'\*\*|\*|`|~~|==', '', text)
        cleaned = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', cleaned)
        anchor = cleaned.lower().strip()
        anchor = re.sub(r'\s+', '-', anchor)
        anchor = re.sub(r'[^a-z0-9-]', '', anchor)
        anchor = re.sub(r'-+', '-', anchor)
        return anchor.strip('-')

    def _parse_inline(self, text: str, line: int) -> List[InlineNode]:
        """Parse inline content for wikilinks, tags, footnotes, etc."""
        nodes = []

        # This is a simplified inline parser. A real one would need to handle overlapping matches.
        # For now, we just scan for patterns independently, which might result in overlaps.
        # Prioritized list?

        # Extract wikilinks
        for match in PATTERNS[PatternType.WIKILINK].find_all(text):
            nodes.append(WikiLinkInline(
                type='wikilink',
                target=match.group('target'),
                display=match.group('display'),
                heading=match.group('heading'),
                block_id=match.group('block'),
                position=SourcePosition(
                    start=LineColumn(line, match.start(), 0),
                    end=LineColumn(line, match.end(), 0)
                )
            ))

        # Extract tags
        for match in PATTERNS[PatternType.NESTED_TAG].find_all(text):
            nodes.append(TagInlineNode(
                type='tag',
                path=match.group('path').split('/'),
                position=SourcePosition(
                    start=LineColumn(line, match.start(), 0),
                    end=LineColumn(line, match.end(), 0)
                )
            ))

        # Extract footnote references
        for match in PATTERNS[PatternType.FOOTNOTE_REF].find_all(text):
            nodes.append(FootnoteRefNode(
                type='footnote_ref',
                id=match.group('id'),
                position=SourcePosition(
                    start=LineColumn(line, match.start(), 0),
                    end=LineColumn(line, match.end(), 0)
                )
            ))

        # If no special nodes, return TextNode?
        if not nodes:
            nodes.append(TextNode(
                type='text',
                text=text,
                position=SourcePosition(
                    start=LineColumn(line, 0, 0),
                    end=LineColumn(line, len(text), 0)
                )
            ))

        return nodes

    def _create_paragraph_node(self, text: str, line: int, block_id: Optional[str]) -> ParagraphNode:
        return ParagraphNode(
            type='paragraph',
            block_id=block_id,
            position=SourcePosition(
                start=LineColumn(line, 0, 0),
                end=LineColumn(line, len(text), 0)
            ),
            inline_content=self._parse_inline(text, line),
            raw=text
        )

    def _create_code_block_node(
        self,
        language: Optional[str],
        content: str,
        line: int
    ) -> CodeBlockNode:
        """Create code block node with execution metadata."""
        is_executable = language in ('mermaid', 'dataview', 'python', 'bash', 'javascript')
        execution_type = None

        if language == 'mermaid':
            execution_type = 'mermaid'
        elif language == 'dataview':
            execution_type = 'dataview'
        elif language in ('python', 'bash', 'javascript'):
            execution_type = 'script'

        return CodeBlockNode(
            type='codeblock',
            language=language,
            content=content,
            is_executable=is_executable,
            execution_type=execution_type,
            position=SourcePosition(
                start=LineColumn(line, 0, 0),
                end=LineColumn(line + content.count('\n') + 2, 0, 0)
            ),
            raw=f"```{language or ''}\n{content}\n```"
        )

    def _create_table_node(self, buffer: List[str], line: int) -> TableNode:
        # TODO: Parse table structure
        return TableNode(
            type='table',
            position=SourcePosition(
                start=LineColumn(line, 0, 0),
                end=LineColumn(line + len(buffer), 0, 0)
            ),
            raw='\n'.join(buffer)
        )
