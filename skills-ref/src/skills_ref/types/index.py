# skills_ref/types/index.py — Semantic index types

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .ast import ASTNode, HeadingNode, SourcePosition

@dataclass
class BlockContext:
    section_path: List[str]  # ["reduce", "five primitive operations"]
    depth: int
    parent_heading: Optional[str] = None

@dataclass
class BlockEntry:
    id: str
    node: ASTNode
    context: BlockContext
    section_path: List[str] # Redundant with context but kept for compatibility with PRD code
    depth: int # Redundant

@dataclass
class HeadingTreeNode:
    heading: HeadingNode
    children: List['HeadingTreeNode'] = field(default_factory=list)
    parent: Optional['HeadingTreeNode'] = None

@dataclass
class TagEntry:
    full_path: str      # "component/parameter"
    segments: List[str]    # ["component", "parameter"]
    position: Dict[str, Any] # Serialized SourcePosition or dict
    context: str       # Surrounding text

@dataclass
class LinkInfo:
    source: str        # Current skill or block
    target: str        # Target skill, heading, or block
    link_type: str     # 'wikilink' | 'external' | 'footnote'
    position: Optional[Dict[str, Any]]
    resolved: bool
    heading: Optional[str] = None
    block_id: Optional[str] = None

@dataclass
class SemanticIndex:
    block_registry: Dict[str, BlockEntry]
    heading_tree: Optional[HeadingTreeNode]
    tag_entries: List[TagEntry]
    tag_tree: Dict[str, Any]
    outbound_links: Dict[str, List[Dict[str, Any]]] # Source -> Links
    inbound_links: Dict[str, List[Dict[str, Any]]]  # Target -> Links
    unresolved_links: List[Dict[str, Any]]
    footnote_refs: Dict[str, List[Dict[str, Any]]]
    footnote_defs: Dict[str, Dict[str, Any]]
    duplicate_block_ids: List[Dict[str, Any]] = field(default_factory=list)  # For E006 validation

    def lookup_block(self, block_id: str) -> Optional[BlockEntry]:
        """O(1) block lookup."""
        return self.block_registry.get(block_id)

    def find_heading_by_anchor(self, anchor: str) -> Optional[HeadingTreeNode]:
        """Find heading node by anchor slug."""
        def search(node: Optional[HeadingTreeNode]) -> Optional[HeadingTreeNode]:
            if node is None:
                return None
            if node.heading.anchor == anchor:
                return node
            for child in node.children:
                result = search(child)
                if result:
                    return result
            return None
        return search(self.heading_tree)
