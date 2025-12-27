# skills_ref/integration/resolver.py — Cross-skill reference resolution

from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import re

from ..navigation.block_navigator import SkillRegistry


@dataclass
class CrossSkillReference:
    """Reference from one skill to another."""
    source_skill: str
    target_skill: str
    target_section: Optional[str]
    target_block: Optional[str]
    display_text: Optional[str]
    position: dict


class CrossSkillResolver:
    """
    Resolve references between skills.

    Reference formats:
    - [[other-skill]]                → Full skill
    - [[other-skill#section]]        → Specific section
    - [[other-skill^block-id]]       → Specific block
    - [[other-skill#section|Text]]   → With display text
    """

    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self._reference_cache: Dict[str, CrossSkillReference] = {}

    def resolve(self, reference: str, source_skill: str) -> Optional[CrossSkillReference]:
        """Resolve a cross-skill reference."""

        cache_key = f"{source_skill}:{reference}"
        if cache_key in self._reference_cache:
            return self._reference_cache[cache_key]

        # Parse reference
        parsed = self._parse_reference(reference)
        if not parsed:
            return None

        target_skill, target_section, target_block, display = parsed

        # Check if target skill exists
        if target_skill not in self.registry.list_skills():
            return None

        # Check if target section/block exists
        target_index = self.registry.get_index(target_skill)
        if target_index:
            if target_section:
                heading = target_index.find_heading_by_anchor(target_section)
                if not heading:
                    # Try fuzzy matching or exact matching failure
                    # Just return None for now if strict
                    return None

            if target_block:
                block = target_index.lookup_block(target_block)
                if not block:
                    return None

        ref = CrossSkillReference(
            source_skill=source_skill,
            target_skill=target_skill,
            target_section=target_section,
            target_block=target_block,
            display_text=display,
            position={}
        )

        self._reference_cache[cache_key] = ref
        return ref

    def _parse_reference(
        self,
        reference: str
    ) -> Optional[Tuple[str, Optional[str], Optional[str], Optional[str]]]:
        """Parse wikilink reference into components."""

        # Pattern: [[target#section^block|display]]
        # Remove [[ and ]] first? Or assume they are passed inside?
        # The parser extracts content inside [[...]].
        # If passed string is "other-skill#section", we parse that.

        # Strip [[ ]] if present
        if reference.startswith('[[') and reference.endswith(']]'):
            reference = reference[2:-2]

        pattern = re.compile(
            r'(?P<target>[^#^|]+)'
            r'(?:#(?P<section>[^\^|]+))?'
            r'(?:\^(?P<block>[^|]+))?'
            r'(?:\|(?P<display>.+))?'
        )

        match = pattern.match(reference)
        if not match:
            return None

        return (
            match.group('target').strip(),
            match.group('section'),
            match.group('block'),
            match.group('display')
        )

    def build_reference_graph(self) -> Dict[str, List[str]]:
        """Build graph of all cross-skill references."""
        graph: Dict[str, List[str]] = {}

        for skill_name in self.registry.list_skills():
            index = self.registry.get_index(skill_name)
            if not index:
                continue

            graph[skill_name] = []

            for links in index.outbound_links.values():
                for link in links:
                    target = link.get('target', '')
                    # Check if it's a cross-skill reference
                    # Internal links have empty target usually in my parser?
                    # No, index_builder: `target` is the note name.
                    # If empty, it's internal link `[[#heading]]` -> target=""
                    # If not empty, it could be internal file or external skill.

                    if target and target in self.registry.list_skills():
                        if target not in graph[skill_name]:
                            graph[skill_name].append(target)

        return graph
