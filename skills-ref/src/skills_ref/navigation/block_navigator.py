# skills_ref/navigation/block_navigator.py — Block-level content addressing

from dataclasses import dataclass
from typing import Optional, List, Union, Dict
from pathlib import Path

from ..types.ast import ASTNode
from ..types.index import SemanticIndex, BlockEntry, HeadingTreeNode
from ..parser.extended_parser import ExtendedParseResult


@dataclass
class NavigationContext:
    """Context around navigated content."""
    skill_name: str
    section_path: List[str]
    parent_heading: Optional[str]
    siblings: List[str]
    depth: int


@dataclass
class NavigationResult:
    """Result of a navigation request."""
    found: bool
    content: Optional[str] = None
    node: Optional[ASTNode] = None
    context: Optional[NavigationContext] = None
    error: Optional[str] = None


class SkillRegistry:
    """Registry of parsed skills with their indexes."""

    def __init__(self):
        self._skills: Dict[str, ExtendedParseResult] = {}

    def register(self, skill_name: str, parse_result: ExtendedParseResult) -> None:
        """Register a parsed skill."""
        self._skills[skill_name] = parse_result

    def get_index(self, skill_name: str) -> Optional[SemanticIndex]:
        """Get semantic index for a skill."""
        result = self._skills.get(skill_name)
        return result.index if result else None

    def list_skills(self) -> List[str]:
        """List all registered skill names."""
        return list(self._skills.keys())


class BlockNavigator:
    """
    Navigate to specific blocks, headings, or sections within skills.

    Addressing schemes:
    - `skill:^block-id`      → Specific block by ID
    - `skill:#heading`       → Heading by anchor
    - `skill:#heading/sub`   → Nested heading path
    - `skill:*`              → Entire skill body
    """

    def __init__(self, skill_registry: SkillRegistry):
        self.registry = skill_registry

    def navigate(self, address: str) -> NavigationResult:
        """
        Navigate to content by address.
        """
        try:
            skill_name, target = self._parse_address(address)
        except ValueError as e:
            return NavigationResult(found=False, error=str(e))

        # Get skill index
        skill_index = self.registry.get_index(skill_name)
        if skill_index is None:
            return NavigationResult(
                found=False,
                error=f"Skill not found: {skill_name}"
            )

        # Navigate based on target type
        if target == '*':
            return self._navigate_full_skill(skill_name)
        elif target.startswith('^'):
            return self._navigate_to_block(skill_index, target[1:], skill_name)
        elif target.startswith('#'):
            return self._navigate_to_heading(skill_index, target[1:], skill_name)
        else:
            return NavigationResult(
                found=False,
                error=f"Invalid target format: {target}"
            )

    def _parse_address(self, address: str) -> tuple[str, str]:
        """Parse address into skill name and target."""
        if ':' not in address:
            raise ValueError(f"Invalid address format (missing ':'): {address}")

        parts = address.split(':', 1)
        skill_name = parts[0].strip()
        target = parts[1].strip()

        if not skill_name:
            raise ValueError("Empty skill name in address")
        if not target:
            raise ValueError("Empty target in address")

        return skill_name, target

    def _navigate_full_skill(self, skill_name: str) -> NavigationResult:
        parse_result = self.registry._skills.get(skill_name)
        return NavigationResult(
            found=True,
            content=parse_result.raw_body,
            context=NavigationContext(
                skill_name=skill_name,
                section_path=[],
                parent_heading=None,
                siblings=[],
                depth=0
            )
        )

    def _navigate_to_block(
        self,
        index: SemanticIndex,
        block_id: str,
        skill_name: str
    ) -> NavigationResult:
        """Navigate to specific block by ID."""
        entry = index.lookup_block(block_id)

        if entry is None:
            return NavigationResult(
                found=False,
                error=f"Block not found: ^{block_id}"
            )

        # entry.node.raw might be available
        content = getattr(entry.node, 'raw', str(entry.node))

        return NavigationResult(
            found=True,
            content=content,
            node=entry.node,
            context=NavigationContext(
                skill_name=skill_name,
                section_path=entry.context.section_path,
                parent_heading=entry.context.parent_heading,
                siblings=self._get_sibling_blocks(index, entry),
                depth=entry.context.depth
            )
        )

    def _navigate_to_heading(
        self,
        index: SemanticIndex,
        heading_path: str,
        skill_name: str
    ) -> NavigationResult:
        """Navigate to heading by anchor path."""
        path_segments = heading_path.split('/')

        # Simplify search: just find the leaf anchor.
        # In a real implementation we would traverse the tree path.
        target_anchor = path_segments[-1]
        node = index.find_heading_by_anchor(target_anchor)

        if not node:
             return NavigationResult(found=False, error=f"Heading not found: {target_anchor}")

        return NavigationResult(
            found=True,
            content=self._extract_section_content(node),
            node=node.heading,
            context=NavigationContext(
                skill_name=skill_name,
                section_path=path_segments,
                parent_heading=path_segments[-1],
                siblings=self._get_sibling_headings(node),
                depth=len(path_segments)
            )
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

    def _get_sibling_blocks(
        self,
        index: SemanticIndex,
        entry: BlockEntry
    ) -> List[str]:
        """Get sibling block IDs at same depth."""
        siblings = []
        for block_id, block_entry in index.block_registry.items():
            if (block_entry.context.section_path == entry.context.section_path and
                block_id != entry.id):
                siblings.append(block_id)
        return siblings

    def _get_sibling_headings(self, node: HeadingTreeNode) -> List[str]:
        """Get sibling heading anchors."""
        if node.parent is None:
            return []
        return [
            child.heading.anchor
            for child in node.parent.children
            if child.heading.anchor != node.heading.anchor
        ]
