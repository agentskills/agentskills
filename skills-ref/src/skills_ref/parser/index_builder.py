# skills_ref/parser/index_builder.py — Semantic index construction

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

from ..types.ast import ASTNode, HeadingNode, WikiLinkInline
from ..types.index import (
    SemanticIndex, BlockEntry, HeadingTreeNode, TagEntry, LinkInfo
)

# Placeholder for ValidationError which we might need to import or define
class ValidationError(Exception):
    def __init__(self, code, message, position):
        self.code = code
        self.message = message
        self.position = position
        super().__init__(message)


class SemanticIndexBuilder:
    """
    Builds semantic index during AST traversal.

    Indexes:
    - Block IDs → nodes (O(1) lookup)
    - Heading tree (hierarchical navigation)
    - Tag taxonomy (prefix search)
    - Link graph (outbound/inbound)
    - Footnotes (ref → def mapping)
    """

    def __init__(self):
        self.block_registry: Dict[str, BlockEntry] = {}
        self.duplicate_block_ids: List[Dict[str, Any]] = []  # Track duplicates for validation
        self.heading_tree: Optional[HeadingTreeNode] = None
        self.heading_stack: List[HeadingTreeNode] = []
        self.tag_entries: List[TagEntry] = []
        self.tag_tree: Dict[str, Any] = {}
        self.outbound_links: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.inbound_links: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.unresolved_links: List[Dict[str, Any]] = []
        self.footnote_refs: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.footnote_defs: Dict[str, Dict[str, Any]] = {}
        self.current_section_path: List[str] = []

    def index_node(self, node: ASTNode) -> None:
        """Index a single AST node."""

        # Index by node type
        # Using getattr/isinstance checks or type string checks
        node_type = getattr(node, 'type', None)

        if node_type == 'heading':
            self._index_heading(node)

        # Index block ID if present (after handling heading structure update)
        if getattr(node, 'block_id', None):
            self._index_block(node)
        elif node_type == 'wikilink':
            self._index_wikilink_node(node)
        elif node_type == 'tag':
            self._index_tag_node(node)
        elif node_type == 'footnote_ref':
            self._index_footnote_ref(node)
        elif node_type == 'footnote_def':
            self._index_footnote_def(node)

        # Recursively index inline content
        if hasattr(node, 'inline_content'):
            for inline in node.inline_content:
                # Inline nodes are not ASTNode but might have indexing needs (wikilinks, tags)
                self._index_inline(inline)

        # Recursively index children
        if hasattr(node, 'children'):
            for child in node.children:
                self.index_node(child)

    def _index_inline(self, inline_node: Any) -> None:
        inline_type = getattr(inline_node, 'type', None)
        if inline_type == 'wikilink':
             self._index_wikilink_inline(inline_node)
        elif inline_type == 'tag':
            self._index_tag_inline(inline_node)
        elif inline_type == 'footnote_ref':
            self._index_footnote_ref(inline_node)

    def _index_block(self, node: ASTNode) -> None:
        """Register a block ID."""
        block_id = node.block_id

        if block_id in self.block_registry:
            # Track duplicate for validation (E006 error)
            self.duplicate_block_ids.append({
                'id': block_id,
                'position': getattr(node, 'position', None),
                'first_occurrence': self.block_registry[block_id].node
            })
            # Keep the first occurrence, don't overwrite
        else:
            # We need to serialize context
            from ..types.index import BlockContext
            context = BlockContext(
                section_path=list(self.current_section_path),
                depth=len(self.current_section_path),
                parent_heading=self.current_section_path[-1] if self.current_section_path else None
            )

            self.block_registry[block_id] = BlockEntry(
                id=block_id,
                node=node,
                context=context,
                section_path=context.section_path,
                depth=context.depth
            )

    def _index_heading(self, node: HeadingNode) -> None:
        """Add heading to hierarchical tree."""
        tree_node = HeadingTreeNode(heading=node)

        # Pop stack until we find parent level
        while (self.heading_stack and
               self.heading_stack[-1].heading.level >= node.level):
            self.heading_stack.pop()
            if self.current_section_path:
                self.current_section_path.pop()

        # Set parent relationship
        if self.heading_stack:
            parent = self.heading_stack[-1]
            tree_node.parent = parent
            parent.children.append(tree_node)
        else:
            # Root level heading
            if self.heading_tree is None:
                self.heading_tree = tree_node

        self.heading_stack.append(tree_node)
        self.current_section_path.append(node.anchor)

    def _index_tag_node(self, node: Any) -> None:
        # TagBlock
        self._index_tag_generic(node.path, node.position)

    def _index_tag_inline(self, node: Any) -> None:
        self._index_tag_generic(node.path, node.position)

    def _index_tag_generic(self, path: List[str], position: Any) -> None:
        """Index hierarchical tag."""
        full_path = '/'.join(path)

        entry = TagEntry(
            full_path=full_path,
            segments=path,
            position=position if isinstance(position, dict) else {'start': position.start, 'end': position.end},
            context=""  # TODO: Extract surrounding text
        )
        self.tag_entries.append(entry)

        # Build tag tree
        current = self.tag_tree
        for segment in path:
            if segment not in current:
                current[segment] = {'_entries': [], '_children': {}}
            current[segment]['_entries'].append(entry)
            current = current[segment]['_children']

    def _index_wikilink_node(self, node: Any) -> None:
        # This is for block-level wikilinks (rare in Obsidian but possible)
        self._index_wikilink_generic(node.target, getattr(node, 'heading', None), getattr(node, 'block_id', None), node.position)

    def _index_wikilink_inline(self, node: Any) -> None:
        self._index_wikilink_generic(node.target, node.heading, node.block_id, node.position)

    def _index_wikilink_generic(self, target: str, heading: Optional[str], block_id: Optional[str], position: Any) -> None:
        """Index wikilink for graph construction."""
        source = '/'.join(self.current_section_path) if self.current_section_path else 'root'

        link_info = {
            'source': source,
            'target': target,
            'heading': heading,
            'block_id': block_id,
            'position': position if isinstance(position, dict) else {'start': position.start, 'end': position.end},
            'resolved': False,
            'link_type': 'wikilink'
        }

        self.outbound_links[source].append(link_info)
        self.inbound_links[target].append(link_info)

    def _index_footnote_ref(self, node: Any) -> None:
        self.footnote_refs[node.id].append({
            'position': node.position,
            'id': node.id
        })

    def _index_footnote_def(self, node: Any) -> None:
        self.footnote_defs[node.id] = {
            'position': node.position,
            'content': node.content
        }

    def build(self, ast: List[ASTNode]) -> SemanticIndex:
        """Build complete index from AST."""
        # Index all nodes
        for node in ast:
            self.index_node(node)

        # Resolve links
        self._resolve_links()

        # Build final index object
        return SemanticIndex(
            block_registry=self.block_registry,
            heading_tree=self.heading_tree,
            tag_entries=self.tag_entries,
            tag_tree=self.tag_tree,
            outbound_links=dict(self.outbound_links),
            inbound_links=dict(self.inbound_links),
            unresolved_links=self.unresolved_links,
            footnote_refs=dict(self.footnote_refs),
            footnote_defs=self.footnote_defs,
            duplicate_block_ids=self.duplicate_block_ids
        )

    def _resolve_links(self) -> None:
        """Resolve wikilinks to targets."""
        for source, links in self.outbound_links.items():
            for link in links:
                target = link['target']

                # Check if target is a block ID reference (internal to this skill for now, external handled by Resolver later)
                # If target is empty or current skill name, it's internal.
                # But we don't know current skill name here easily unless passed.
                # Assuming internal links don't have target set (or target is empty string?),
                # actually in Obsidian [[#heading]] means target is empty string.
                # In our pattern, target captures the file name.

                # If target is NOT empty, it's likely another file/skill.
                # If target IS empty, it's internal.

                if not target:
                    # Internal link
                    if link.get('block_id'):
                        if link['block_id'] in self.block_registry:
                            link['resolved'] = True
                        else:
                            self.unresolved_links.append(link)
                    elif link.get('heading'):
                         # TODO: Implement heading resolution (search heading tree)
                         # Simple check against all headings?
                         # We can traverse the heading tree.
                         found = False
                         if self.heading_tree:
                             # BFS or DFS to find anchor
                             queue = [self.heading_tree]
                             while queue:
                                 curr = queue.pop(0)
                                 if curr.heading.anchor == link['heading']:
                                     found = True
                                     break
                                 queue.extend(curr.children)

                         if found:
                             link['resolved'] = True
                         else:
                             self.unresolved_links.append(link)
                else:
                    # External link (to another skill)
                    # We can't resolve it here fully without the full registry.
                    # Mark as unresolved for now.
                    self.unresolved_links.append(link)
