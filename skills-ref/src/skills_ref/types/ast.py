# skills_ref/types/ast.py — Abstract Syntax Tree for skill body content

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any, Literal
from .core import SourcePosition

@dataclass(kw_only=True)
class BaseASTNode:
    type: str
    position: SourcePosition
    raw: str              # Original source text
    block_id: Optional[str] = None # ^id if present

# Forward declarations for children
ASTNode = Union[
    'HeadingNode',
    'ParagraphNode',
    'ListNode',
    'TableNode',
    'CodeBlockNode',
    'CalloutNode',
    'BlockquoteNode',
    'WikiLinkNode',
    'FootnoteNode',
    'TagNode',
    'HorizontalRuleNode',
    'FrontmatterNode'
]

InlineNode = Union[
    'TextNode',
    'EmphasisNode',
    'StrongNode',
    'CodeInlineNode',
    'WikiLinkInline',
    'ExternalLinkNode',
    'FootnoteRefNode',
    'TagInlineNode',
    'HighlightNode'
]

@dataclass(kw_only=True)
class HeadingNode(BaseASTNode):
    type: Literal['heading'] = 'heading'
    level: int = 1
    text: str = ""
    anchor: str = ""
    children: List[ASTNode] = field(default_factory=list)
    inline_content: List[InlineNode] = field(default_factory=list)

@dataclass(kw_only=True)
class ParagraphNode(BaseASTNode):
    type: Literal['paragraph'] = 'paragraph'
    inline_content: List[InlineNode] = field(default_factory=list)

@dataclass(kw_only=True)
class ListNode(BaseASTNode):
    type: Literal['list'] = 'list'
    items: List['ListItemNode'] = field(default_factory=list)
    ordered: bool = False

@dataclass(kw_only=True)
class ListItemNode(BaseASTNode):
    type: Literal['list_item'] = 'list_item'
    children: List[ASTNode] = field(default_factory=list)

@dataclass(kw_only=True)
class TableNode(BaseASTNode):
    type: Literal['table'] = 'table'
    headers: List['TableCell'] = field(default_factory=list)
    rows: List['TableRow'] = field(default_factory=list)
    alignments: List[str] = field(default_factory=list)

@dataclass(kw_only=True)
class TableRow:
    cells: List['TableCell']

@dataclass(kw_only=True)
class TableCell:
    content: List[InlineNode]
    raw: str

@dataclass(kw_only=True)
class CodeBlockNode(BaseASTNode):
    type: Literal['codeblock'] = 'codeblock'
    language: Optional[str] = None
    content: str = ""
    is_executable: bool = False
    execution_type: Optional[str] = None
    meta: Optional[Dict[str, str]] = None

@dataclass(kw_only=True)
class CalloutNode(BaseASTNode):
    type: Literal['callout'] = 'callout'
    callout_type: str = "note"
    title: Optional[str] = None
    fold_state: Optional[str] = None # expanded, collapsed, default
    children: List[ASTNode] = field(default_factory=list)

@dataclass(kw_only=True)
class BlockquoteNode(BaseASTNode):
    type: Literal['blockquote'] = 'blockquote'
    children: List[ASTNode] = field(default_factory=list)

@dataclass(kw_only=True)
class WikiLinkNode(BaseASTNode):
    # This might be used if a wikilink stands alone as a block, or is part of structure
    # Usually wikilinks are inline.
    type: Literal['wikilink_block'] = 'wikilink_block'
    target: str = ""

@dataclass(kw_only=True)
class FootnoteNode(BaseASTNode):
    type: Literal['footnote_def'] = 'footnote_def'
    id: str = ""
    content: List[ASTNode] = field(default_factory=list)

@dataclass(kw_only=True)
class TagNode(BaseASTNode):
    type: Literal['tag_block'] = 'tag_block'
    path: List[str] = field(default_factory=list)

@dataclass(kw_only=True)
class HorizontalRuleNode(BaseASTNode):
    type: Literal['thematic_break'] = 'thematic_break'

@dataclass(kw_only=True)
class FrontmatterNode(BaseASTNode):
    type: Literal['frontmatter'] = 'frontmatter'
    content: str = ""

# Inline Nodes

@dataclass(kw_only=True)
class TextNode:
    type: Literal['text'] = 'text'
    text: str
    position: SourcePosition

@dataclass(kw_only=True)
class EmphasisNode:
    type: Literal['emphasis'] = 'emphasis'
    children: List[InlineNode]
    position: SourcePosition

@dataclass(kw_only=True)
class StrongNode:
    type: Literal['strong'] = 'strong'
    children: List[InlineNode]
    position: SourcePosition

@dataclass(kw_only=True)
class CodeInlineNode:
    type: Literal['inline_code'] = 'inline_code'
    value: str
    position: SourcePosition

@dataclass(kw_only=True)
class WikiLinkInline:
    type: Literal['wikilink'] = 'wikilink'
    target: str
    position: SourcePosition
    display: Optional[str] = None
    heading: Optional[str] = None
    block_id: Optional[str] = None

@dataclass(kw_only=True)
class ExternalLinkNode:
    type: Literal['link'] = 'link'
    url: str
    children: List[InlineNode]
    position: SourcePosition

@dataclass(kw_only=True)
class FootnoteRefNode:
    type: Literal['footnote_ref'] = 'footnote_ref'
    id: str
    position: SourcePosition

@dataclass(kw_only=True)
class TagInlineNode:
    type: Literal['tag'] = 'tag'
    path: List[str]
    position: SourcePosition

@dataclass(kw_only=True)
class HighlightNode:
    type: Literal['highlight'] = 'highlight'
    children: List[InlineNode]
    position: SourcePosition

@dataclass
class ASTMetadata:
    node_count: int
    estimated_tokens: int
    max_depth: int
    has_executable_code: bool

@dataclass
class SkillAST:
    nodes: List[ASTNode]
    metadata: ASTMetadata
