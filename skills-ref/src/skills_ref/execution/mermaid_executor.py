# skills_ref/execution/mermaid_executor.py — Mermaid diagram rendering

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum, auto
import subprocess
import tempfile
import re
from pathlib import Path


class RenderFormat(Enum):
    """Output formats for Mermaid rendering."""
    SVG = auto()
    PNG = auto()
    PDF = auto()
    ASCII = auto()  # Text-based representation


@dataclass
class MermaidExecutionResult:
    """Result of Mermaid diagram execution."""
    success: bool
    format: RenderFormat
    output: Optional[bytes] = None       # Binary output (SVG/PNG/PDF)
    text_output: Optional[str] = None    # ASCII representation
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MermaidExecutor:
    """
    Execute Mermaid diagrams with validation and rendering.
    """

    def __init__(self, mmdc_path: str = 'mmdc'):
        self.mmdc_path = mmdc_path
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if mermaid-cli is available."""
        try:
            subprocess.run(
                [self.mmdc_path, '--version'],
                capture_output=True,
                timeout=2
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def validate(self, mermaid_code: str) -> tuple[bool, Optional[str]]:
        """Validate Mermaid syntax without rendering."""
        if not self._available:
            return True, None # Skip validation if tool not available

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.mmd',
            delete=False
        ) as f:
            f.write(mermaid_code)
            input_path = f.name

        try:
            result = subprocess.run(
                [self.mmdc_path, '-i', input_path, '-o', '/dev/null'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
        finally:
            Path(input_path).unlink(missing_ok=True)

    def execute(
        self,
        mermaid_code: str,
        format: RenderFormat = RenderFormat.SVG,
        theme: str = 'default'
    ) -> MermaidExecutionResult:
        """Execute Mermaid diagram and return rendered output."""

        # Extract metadata before rendering
        metadata = self._extract_metadata(mermaid_code)

        if format == RenderFormat.ASCII or not self._available:
            return self._render_ascii(mermaid_code, metadata)

        # Render to binary format
        return self._render_binary(mermaid_code, format, theme, metadata)

    def _render_binary(
        self,
        mermaid_code: str,
        format: RenderFormat,
        theme: str,
        metadata: Dict[str, Any]
    ) -> MermaidExecutionResult:
        """Render to SVG/PNG/PDF."""
        format_map = {
            RenderFormat.SVG: '.svg',
            RenderFormat.PNG: '.png',
            RenderFormat.PDF: '.pdf'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / 'input.mmd'
            output_path = Path(tmpdir) / f'output{format_map[format]}'

            input_path.write_text(mermaid_code)

            result = subprocess.run(
                [
                    self.mmdc_path,
                    '-i', str(input_path),
                    '-o', str(output_path),
                    '-t', theme,
                    '-b', 'transparent'
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return MermaidExecutionResult(
                    success=False,
                    format=format,
                    error=f"Rendering failed: {result.stderr}"
                )

            output_bytes = output_path.read_bytes()

            return MermaidExecutionResult(
                success=True,
                format=format,
                output=output_bytes,
                metadata=metadata
            )

    def _render_ascii(
        self,
        mermaid_code: str,
        metadata: Dict[str, Any]
    ) -> MermaidExecutionResult:
        """Render ASCII representation for terminal/text contexts."""
        # Parse diagram type and structure
        lines = mermaid_code.strip().split('\n')
        diagram_type = self._detect_diagram_type(lines[0]) if lines else 'unknown'

        # Build ASCII representation based on type
        if diagram_type in ('graph', 'flowchart'):
            ascii_output = self._ascii_flowchart(lines)
        elif diagram_type == 'sequenceDiagram':
            ascii_output = self._ascii_generic(lines, diagram_type)
        else:
            ascii_output = self._ascii_generic(lines, diagram_type)

        return MermaidExecutionResult(
            success=True,
            format=RenderFormat.ASCII,
            text_output=ascii_output,
            metadata=metadata
        )

    def _detect_diagram_type(self, first_line: str) -> str:
        """Detect Mermaid diagram type from first line."""
        first_line = first_line.strip().lower()

        if first_line.startswith(('graph', 'flowchart')):
            return 'flowchart'
        elif first_line.startswith('sequencediagram'):
            return 'sequenceDiagram'
        elif first_line.startswith('classdiagram'):
            return 'classDiagram'
        else:
            return first_line.split()[0] if first_line else 'unknown'

    def _extract_metadata(self, mermaid_code: str) -> Dict[str, Any]:
        """Extract metadata from Mermaid diagram."""
        metadata = {
            'diagram_type': None,
            'nodes': [],
            'edges': [],
            'internal_links': [],
            'subgraphs': []
        }

        lines = mermaid_code.strip().split('\n')
        if lines:
            metadata['diagram_type'] = self._detect_diagram_type(lines[0])

        # Extract nodes and edges for flowcharts (simple regex)
        if metadata['diagram_type'] == 'flowchart':
            # Node pattern: A[Label] or A{Label} or A((Label)) etc.
            node_pattern = re.compile(r'(\w+)[\[\{\(\<]([^\]\}\)\>]+)[\]\}\)\>]')

            # Edge pattern: A --> B or A -- text --> B
            edge_pattern = re.compile(r'(\w+)\s*[-=]+>?\|?([^|]*)\|?\s*(\w+)')

            # Internal link class
            link_class_pattern = re.compile(r'class\s+([\w,]+)\s+internal-link')

            for line in lines[1:]:
                # Find nodes
                for match in node_pattern.finditer(line):
                    metadata['nodes'].append({
                        'id': match.group(1),
                        'label': match.group(2)
                    })

                # Find edges
                for match in edge_pattern.finditer(line):
                    metadata['edges'].append({
                        'from': match.group(1),
                        'label': match.group(2).strip() if match.group(2) else None,
                        'to': match.group(3)
                    })

                # Find internal-link classes
                for match in link_class_pattern.finditer(line):
                    node_ids = match.group(1).split(',')
                    metadata['internal_links'].extend(node_ids)

        return metadata

    def _ascii_flowchart(self, lines: list) -> str:
        """Generate ASCII art for flowchart."""
        output_lines = ["┌─ Flowchart ─┐", "│"]

        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('class') or line.startswith('style') or line.startswith('%%'):
                continue

            # Simple transformation to ASCII
            line = line.replace('-->', ' → ')
            line = line.replace('---', ' ── ')
            line = line.replace('[', '┌')
            line = line.replace(']', '┐')
            line = line.replace('{', '◇')
            line = line.replace('}', '◇')

            output_lines.append(f"│  {line}")

        output_lines.append("│")
        output_lines.append("└─────────────┘")

        return '\n'.join(output_lines)

    def _ascii_generic(self, lines: list, diagram_type: str) -> str:
        """Generic ASCII representation."""
        return f"[{diagram_type}]\n" + '\n'.join(f"  {l}" for l in lines[1:])
