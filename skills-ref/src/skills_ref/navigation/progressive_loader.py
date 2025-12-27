# skills_ref/navigation/progressive_loader.py — Token-aware progressive loading

from dataclasses import dataclass, field
from typing import List, Optional, Iterator, Callable
from enum import Enum, auto
import tiktoken

from ..parser.extended_parser import ExtendedParseResult
from ..types.index import HeadingTreeNode
from ..types.ast import ASTNode
from .block_navigator import SkillRegistry


class LoadingStrategy(Enum):
    """Strategies for progressive content loading."""
    FULL = auto()           # Load entire skill
    HEADING_ONLY = auto()   # Load headings + descriptions
    SECTION = auto()        # Load specific section
    BLOCK = auto()          # Load specific block
    SUMMARY = auto()        # Load summary/overview only


@dataclass
class LoadRequest:
    """Request for content loading."""
    skill_name: str
    strategy: LoadingStrategy
    target: Optional[str] = None        # Heading anchor or block ID
    max_tokens: Optional[int] = None    # Token budget
    include_context: bool = True        # Include surrounding context
    depth: int = 1                       # For HEADING_ONLY: how deep to show


@dataclass
class LoadedContent:
    """Result of progressive loading."""
    content: str
    token_count: int
    truncated: bool
    sections_loaded: List[str]
    sections_available: List[str]
    continuation_hint: Optional[str] = None


class ProgressiveLoader:
    """
    Load skill content progressively based on token budget.
    """

    def __init__(self, registry: SkillRegistry, tokenizer: str = 'cl100k_base'):
        self.registry = registry
        self.encoder = tiktoken.get_encoding(tokenizer)

    def load(self, request: LoadRequest) -> LoadedContent:
        """Load content based on request."""

        # Access internal dict directly as per AGENTS.md example, or add public getter
        parse_result = self.registry._skills.get(request.skill_name)
        if parse_result is None:
            return LoadedContent(
                content=f"Skill not found: {request.skill_name}",
                token_count=0,
                truncated=False,
                sections_loaded=[],
                sections_available=[]
            )

        if request.strategy == LoadingStrategy.FULL:
            return self._load_full(parse_result, request.max_tokens)
        elif request.strategy == LoadingStrategy.HEADING_ONLY:
            return self._load_headings(parse_result, request.depth, request.max_tokens)
        elif request.strategy == LoadingStrategy.SECTION:
            return self._load_section(parse_result, request.target, request.max_tokens)
        elif request.strategy == LoadingStrategy.BLOCK:
            return self._load_block(parse_result, request.target, request.include_context)
        elif request.strategy == LoadingStrategy.SUMMARY:
            return self._load_summary(parse_result, request.max_tokens)
        else:
            raise ValueError(f"Unknown loading strategy: {request.strategy}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))

    def _load_full(self, parse_result: ExtendedParseResult, max_tokens: Optional[int]) -> LoadedContent:
        content = parse_result.raw_body
        token_count = self._count_tokens(content)
        truncated = max_tokens is not None and token_count > max_tokens

        if truncated:
            content = self._truncate_to_tokens(content, max_tokens)
            token_count = max_tokens

        return LoadedContent(
            content=content,
            token_count=token_count,
            truncated=truncated,
            sections_loaded=['*'],
            sections_available=self._get_all_sections(parse_result)
        )

    def _load_summary(self, parse_result: ExtendedParseResult, max_tokens: Optional[int]) -> LoadedContent:
        # Summary could be description + first section?
        content = f"Skill: {parse_result.properties.name}\nDescription: {parse_result.properties.description}"
        token_count = self._count_tokens(content)
        truncated = max_tokens is not None and token_count > max_tokens
        return LoadedContent(
            content=content,
            token_count=token_count,
            truncated=truncated,
            sections_loaded=['summary'],
            sections_available=self._get_all_sections(parse_result)
        )

    def _load_headings(
        self,
        parse_result: ExtendedParseResult,
        depth: int,
        max_tokens: Optional[int]
    ) -> LoadedContent:
        """Load heading structure with brief descriptions."""
        lines = []
        sections_loaded = []

        def traverse(node: HeadingTreeNode, current_depth: int):
            if node is None:
                return

            # Stop if we reached max depth
            if current_depth >= depth:
                return

            # Add heading with appropriate markdown level
            prefix = '#' * node.heading.level
            lines.append(f"{prefix} {node.heading.text}")
            sections_loaded.append(node.heading.anchor)

            # Add first paragraph
            # Extract first paragraph from flat AST following this heading?
            # Or use inline content logic if possible.
            # Assuming heading node in AST doesn't have children populated (as discovered),
            # we can't easily get the paragraph without flat AST traversal.
            # But for summary, maybe we skip paragraph if expensive?
            # OR we implement a quick lookahead in flat AST.
            # For now, skipping paragraph text in HEADING_ONLY if children empty.
            pass

            # Recurse into children
            for child_node in node.children:
                traverse(child_node, current_depth + 1)

        if parse_result.index.heading_tree:
            traverse(parse_result.index.heading_tree, 0)

        content = '\n\n'.join(lines)
        token_count = self._count_tokens(content)
        truncated = max_tokens is not None and token_count > max_tokens

        if truncated:
            # Truncate content to fit budget
            content = self._truncate_to_tokens(content, max_tokens)
            token_count = max_tokens

        return LoadedContent(
            content=content,
            token_count=token_count,
            truncated=truncated,
            sections_loaded=sections_loaded,
            sections_available=self._get_all_sections(parse_result)
        )

    def _load_section(
        self,
        parse_result: ExtendedParseResult,
        target: Optional[str],
        max_tokens: Optional[int]
    ) -> LoadedContent:
        """Load a specific section fully."""
        if not target:
            return self._load_full(parse_result, max_tokens)

        # Find heading by anchor
        heading_node = parse_result.index.find_heading_by_anchor(target)
        if heading_node is None:
            return LoadedContent(
                content=f"Section not found: #{target}",
                token_count=0,
                truncated=False,
                sections_loaded=[],
                sections_available=self._get_all_sections(parse_result)
            )

        # Extract section content
        # We need _extract_section_content from BlockNavigator or similar.
        # Since I can't import BlockNavigator's private method easily, I'll duplicate/refactor.
        # Ideally this logic belongs in `index.py` or a helper.
        content = self._extract_section_content(heading_node)
        token_count = self._count_tokens(content)
        truncated = max_tokens is not None and token_count > max_tokens

        if truncated:
            content = self._truncate_to_tokens(content, max_tokens)
            token_count = max_tokens

        return LoadedContent(
            content=content,
            token_count=token_count,
            truncated=truncated,
            sections_loaded=[target],
            sections_available=self._get_all_sections(parse_result),
            continuation_hint=self._get_continuation_hint(heading_node)
        )

    def _extract_section_content(self, heading_node: HeadingTreeNode) -> str:
        """Extract all content under a heading."""

        def dump_ast(node: ASTNode) -> List[str]:
            out = []
            if hasattr(node, 'raw'):
                out.append(node.raw)
            if hasattr(node, 'children'):
                for child in node.children:
                    out.extend(dump_ast(child))
            return out

        texts = dump_ast(heading_node.heading)
        return '\n\n'.join(texts)

    def _load_block(
        self,
        parse_result: ExtendedParseResult,
        target: Optional[str],
        include_context: bool
    ) -> LoadedContent:
        """Load specific block by ID."""
        if not target:
            return LoadedContent(
                content="No block ID specified",
                token_count=0,
                truncated=False,
                sections_loaded=[],
                sections_available=[]
            )

        # Remove ^ prefix if present
        block_id = target.lstrip('^')
        entry = parse_result.index.lookup_block(block_id)

        if entry is None:
            return LoadedContent(
                content=f"Block not found: ^{block_id}",
                token_count=0,
                truncated=False,
                sections_loaded=[],
                sections_available=list(parse_result.index.block_registry.keys())
            )

        # Build content with optional context
        parts = []

        if include_context and entry.context.section_path:
            # Add section path as breadcrumb
            parts.append(f"> Section: {' > '.join(entry.context.section_path)}")

        parts.append(getattr(entry.node, 'raw', str(entry.node)))

        content = '\n\n'.join(parts)
        token_count = self._count_tokens(content)

        return LoadedContent(
            content=content,
            token_count=token_count,
            truncated=False,
            sections_loaded=[f"^{block_id}"],
            sections_available=list(parse_result.index.block_registry.keys())
        )

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token budget."""
        tokens = self.encoder.encode(text)
        if len(tokens) <= max_tokens:
            return text

        truncated_tokens = tokens[:max_tokens - 10]  # Leave room for truncation marker
        truncated_text = self.encoder.decode(truncated_tokens)
        return truncated_text + "\n\n[...truncated...]"

    def _get_all_sections(self, parse_result: ExtendedParseResult) -> List[str]:
        """Get list of all section anchors."""
        sections = []

        def collect(node: Optional[HeadingTreeNode]):
            if node is None:
                return
            sections.append(node.heading.anchor)
            for child in node.children:
                collect(child)

        collect(parse_result.index.heading_tree)
        return sections

    def _get_continuation_hint(self, heading_node: HeadingTreeNode) -> Optional[str]:
        """Get hint for what to load next."""
        siblings = []
        if heading_node.parent:
            for sibling in heading_node.parent.children:
                if sibling.heading.anchor != heading_node.heading.anchor:
                    siblings.append(sibling.heading.anchor)

        if siblings:
            return f"Related sections: {', '.join(siblings[:3])}"
        return None
