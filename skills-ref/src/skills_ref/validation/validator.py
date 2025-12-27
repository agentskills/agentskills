# skills_ref/validation/validator.py — Comprehensive skill validation

from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Any
from enum import Enum, auto
import re
from pathlib import Path

from ..types.ast import ASTNode, CodeBlockNode, CalloutNode
from ..types.index import SemanticIndex
from ..types.core import SkillProperties, SourcePosition, LineColumn
from .legacy import validate_metadata as legacy_validate_metadata

class Severity(Enum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()


@dataclass
class ValidationIssue:
    """Single validation issue."""
    code: str
    message: str
    severity: Severity
    line: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result."""
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]


class SkillValidator:
    """
    Comprehensive skill validation.

    Validates:
    1. Frontmatter schema compliance
    2. Block ID uniqueness
    3. Wikilink resolution
    4. Callout type validity
    5. Code block syntax
    6. Tag consistency
    7. Footnote completeness
    8. Token budget
    """

    VALID_CALLOUT_TYPES = {
        'note', 'abstract', 'summary', 'tldr', 'info', 'todo',
        'tip', 'hint', 'important', 'success', 'check', 'done',
        'question', 'help', 'faq', 'warning', 'caution', 'attention',
        'failure', 'fail', 'missing', 'danger', 'error', 'bug',
        'example', 'quote', 'cite'
    }

    NAME_PATTERN = re.compile(r'^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$')

    def __init__(self, max_tokens: int = 5000):
        self.max_tokens = max_tokens

    def validate(
        self,
        properties: SkillProperties,
        ast: List[ASTNode],
        index: SemanticIndex,
        raw_body: str
    ) -> ValidationResult:
        """Run all validation checks."""
        issues = []

        # Frontmatter validation
        issues.extend(self._validate_frontmatter(properties))

        # Block ID validation
        issues.extend(self._validate_block_ids(index))

        # Wikilink validation
        issues.extend(self._validate_wikilinks(index))

        # Callout validation
        issues.extend(self._validate_callouts(ast))

        # Code block validation
        issues.extend(self._validate_code_blocks(ast))

        # Tag validation
        issues.extend(self._validate_tags(index))

        # Footnote validation
        issues.extend(self._validate_footnotes(index))

        # Token budget validation
        issues.extend(self._validate_token_budget(raw_body))

        # Compute metrics
        metrics = self._compute_metrics(ast, index, raw_body)

        # Determine validity (no errors)
        valid = not any(i.severity == Severity.ERROR for i in issues)

        return ValidationResult(valid=valid, issues=issues, metrics=metrics)

    def _validate_frontmatter(
        self,
        properties: SkillProperties
    ) -> List[ValidationIssue]:
        """Validate frontmatter fields."""
        issues = []

        # Re-use legacy validation logic but convert to ValidationIssue
        metadata_dict = {
            "name": properties.name,
            "description": properties.description,
            "license": properties.license,
            "compatibility": properties.compatibility,
            "metadata": properties.metadata,
            "allowed-tools": properties.allowed_tools
        }
        # Filter None
        metadata_dict = {k: v for k, v in metadata_dict.items() if v is not None}

        legacy_errors = legacy_validate_metadata(metadata_dict)
        for err in legacy_errors:
             issues.append(ValidationIssue(
                code='E001_LEGACY', # Generic code for legacy errors
                message=err,
                severity=Severity.ERROR,
                line=1
            ))

        return issues

    def _validate_block_ids(self, index: SemanticIndex) -> List[ValidationIssue]:
        """Validate block ID uniqueness and format."""
        issues = []

        # Check for duplicate block IDs (E006)
        for duplicate in index.duplicate_block_ids:
            position = duplicate.get('position')
            line = None
            if position:
                if hasattr(position, 'start'):
                    line = position.start.line
                elif isinstance(position, dict):
                    line = position.get('start', {}).get('line')

            issues.append(ValidationIssue(
                code='E006',
                message=f"Duplicate block ID: '^{duplicate['id']}'",
                severity=Severity.ERROR,
                line=line,
                suggestion="Each block ID must be unique within a skill"
            ))

        # Check format of registered block IDs
        for block_id, entry in index.block_registry.items():
            # Check format
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', block_id):
                issues.append(ValidationIssue(
                    code='W002',
                    message=f"Block ID '^{block_id}' has non-standard format",
                    severity=Severity.WARNING,
                    suggestion="Use alphanumeric characters, starting with a letter",
                    line=entry.node.position.start.line if hasattr(entry.node, 'position') else None
                ))

        return issues

    def _validate_wikilinks(self, index: SemanticIndex) -> List[ValidationIssue]:
        """Validate wikilink targets."""
        issues = []

        for link in index.unresolved_links:
            # We treat unresolved links as Warnings as they might point to other files not loaded
            # Unless we are validating a full knowledge base.
            issues.append(ValidationIssue(
                code='W003',
                message=f"Unresolved link to '{link['target']}'",
                severity=Severity.WARNING,
                line=link.get('position', {}).get('start', 0) if isinstance(link.get('position'), dict) else link.get('position').start.line, # Handle dict vs object
                suggestion="Verify the target exists or will be created"
            ))

        return issues

    def _validate_callouts(self, ast: List[ASTNode]) -> List[ValidationIssue]:
        """Validate callout types."""
        issues = []

        def check_node(node: ASTNode):
            if isinstance(node, CalloutNode):
                callout_type = node.callout_type.lower()
                if callout_type not in self.VALID_CALLOUT_TYPES:
                    issues.append(ValidationIssue(
                        code='E005',
                        message=f"Invalid callout type: '{callout_type}'",
                        severity=Severity.ERROR,
                        line=node.position.start.line,
                        suggestion=f"Use one of: {', '.join(sorted(self.VALID_CALLOUT_TYPES)[:10])}..."
                    ))

            # Recurse into children
            if hasattr(node, 'children'):
                for child in node.children:
                    check_node(child)

        for node in ast:
            check_node(node)

        return issues

    def _validate_code_blocks(self, ast: List[ASTNode]) -> List[ValidationIssue]:
        """Validate code block syntax."""
        issues = []

        def check_node(node: ASTNode):
            if isinstance(node, CodeBlockNode):
                # Check for language specification
                if not node.language:
                    issues.append(ValidationIssue(
                        code='W005',
                        message="Code block missing language specification",
                        severity=Severity.WARNING,
                        line=node.position.start.line,
                        suggestion="Add language identifier after opening ```"
                    ))

                # Validate mermaid syntax
                if node.language == 'mermaid':
                    mermaid_issues = self._validate_mermaid(node.content, node.position.start.line)
                    issues.extend(mermaid_issues)

            # Recurse
            if hasattr(node, 'children'):
                for child in node.children:
                    check_node(child)

        for node in ast:
            check_node(node)

        return issues

    def _validate_mermaid(self, content: str, line_offset: int) -> List[ValidationIssue]:
        """Validate Mermaid diagram syntax."""
        issues = []

        lines = content.strip().split('\n')
        if not lines or not content.strip():
            issues.append(ValidationIssue(
                code='E010',
                message="Empty Mermaid diagram",
                severity=Severity.ERROR,
                line=line_offset
            ))
            return issues

        # Check diagram type declaration
        first_line = lines[0].strip().lower()
        # Remove comments
        if first_line.startswith('%%'):
             # Look for first non-comment line
             for l in lines:
                 if not l.strip().startswith('%%') and l.strip():
                     first_line = l.strip().lower()
                     break

        valid_types = [
            'graph', 'flowchart', 'sequencediagram', 'classdiagram',
            'statediagram', 'erdiagram', 'gantt', 'pie', 'gitgraph',
            'timeline', 'mindmap'
        ]

        has_valid_type = any(first_line.startswith(t) for t in valid_types)
        if not has_valid_type:
            # Maybe it is a direction like TD or LR immediately? usually graph TD
            issues.append(ValidationIssue(
                code='E010',
                message=f"Unknown or missing Mermaid diagram type",
                severity=Severity.ERROR,
                line=line_offset,
                suggestion=f"Start with one of: {', '.join(valid_types)}"
            ))

        return issues

    def _validate_tags(self, index: SemanticIndex) -> List[ValidationIssue]:
        """Validate tag consistency."""
        issues = []

        # Group tags by first segment
        tag_groups: Dict[str, List[str]] = {}
        for entry in index.tag_entries:
            if entry.segments:
                first = entry.segments[0]
                if first not in tag_groups:
                    tag_groups[first] = []
                tag_groups[first].append(entry.full_path)

        # Check for inconsistent nesting
        for group, paths in tag_groups.items():
            depths = set(len(p.split('/')) for p in paths)
            if len(depths) > 2:
                issues.append(ValidationIssue(
                    code='W006',
                    message=f"Inconsistent tag depth for #{group}/*",
                    severity=Severity.WARNING,
                    suggestion="Standardize tag hierarchy depth"
                ))

        return issues

    def _validate_footnotes(self, index: SemanticIndex) -> List[ValidationIssue]:
        """Validate footnote references and definitions."""
        issues = []

        # Check for orphaned references
        for ref_id, refs in index.footnote_refs.items():
            if ref_id not in index.footnote_defs:
                for ref in refs:
                    pos = ref.get('position') # Dict or Object
                    line = pos.start.line if hasattr(pos, 'start') else pos.get('start', {}).get('line')

                    issues.append(ValidationIssue(
                        code='E008',
                        message=f"Footnote reference [^{ref_id}] has no definition",
                        severity=Severity.ERROR,
                        line=line
                    ))

        # Check for unused definitions
        for def_id in index.footnote_defs:
            if def_id not in index.footnote_refs:
                issues.append(ValidationIssue(
                    code='W007',
                    message=f"Footnote [^{def_id}] is defined but never referenced",
                    severity=Severity.WARNING
                ))

        return issues

    def _validate_token_budget(self, raw_body: str) -> List[ValidationIssue]:
        """Validate token count is within budget."""
        issues = []

        try:
            import tiktoken
            encoder = tiktoken.get_encoding('cl100k_base')
            token_count = len(encoder.encode(raw_body))

            if token_count > self.max_tokens:
                issues.append(ValidationIssue(
                    code='W004',
                    message=f"Skill body exceeds token budget: {token_count} > {self.max_tokens}",
                    severity=Severity.WARNING,
                    suggestion="Consider splitting content into references/ files"
                ))
        except ImportError:
            # tiktoken not available, skip check
            pass

        return issues

    def _compute_metrics(
        self,
        ast: List[ASTNode],
        index: SemanticIndex,
        raw_body: str
    ) -> Dict[str, Any]:
        """Compute validation metrics."""
        return {
            'node_count': len(ast),
            'block_id_count': len(index.block_registry),
            'heading_count': self._count_headings(ast),
            'link_count': sum(len(v) for v in index.outbound_links.values()),
            'unresolved_link_count': len(index.unresolved_links),
            'tag_count': len(index.tag_entries),
            'footnote_count': len(index.footnote_defs),
            'code_block_count': self._count_code_blocks(ast),
            'callout_count': self._count_callouts(ast),
            'line_count': raw_body.count('\n') + 1,
            'char_count': len(raw_body)
        }

    def _count_headings(self, ast: List[ASTNode]) -> int:
        count = 0
        for node in ast:
            if getattr(node, 'type', '') == 'heading':
                count += 1
            if hasattr(node, 'children'):
                count += self._count_headings(node.children)
        return count

    def _count_code_blocks(self, ast: List[ASTNode]) -> int:
        count = 0
        for node in ast:
            if getattr(node, 'type', '') == 'codeblock':
                count += 1
            if hasattr(node, 'children'):
                count += self._count_code_blocks(node.children)
        return count

    def _count_callouts(self, ast: List[ASTNode]) -> int:
        count = 0
        for node in ast:
            if getattr(node, 'type', '') == 'callout':
                count += 1
            if hasattr(node, 'children'):
                count += self._count_callouts(node.children)
        return count
