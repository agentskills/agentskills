# skills_ref/integration/composition.py — Skill composition patterns

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable, Any
from enum import Enum, auto

from ..navigation.block_navigator import SkillRegistry, BlockNavigator, NavigationResult


class CompositionType(Enum):
    """Types of skill composition."""
    PIPELINE = auto()      # Sequential execution
    PARALLEL = auto()      # Concurrent execution
    CONDITIONAL = auto()   # Based on conditions
    FALLBACK = auto()      # Try alternatives


@dataclass
class CompositionStep:
    """Single step in a composition."""
    skill_name: str
    section: Optional[str] = None      # Specific section to load
    block_id: Optional[str] = None     # Specific block to load
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None  # When to execute
    fallback: Optional['CompositionStep'] = None


@dataclass
class SkillComposition:
    """Composed skill from multiple skills."""
    name: str
    description: str
    steps: List[CompositionStep]
    composition_type: CompositionType
    shared_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComposedResult:
    """Result of skill composition execution."""
    success: bool
    steps: List[Dict[str, Any]]
    final_context: Dict[str, Any]


class SkillComposer:
    """
    Compose multiple skills into workflows.
    """

    def __init__(self, registry: SkillRegistry, navigator: BlockNavigator):
        self.registry = registry
        self.navigator = navigator

    def compose(self, composition: SkillComposition) -> ComposedResult:
        """Execute skill composition."""

        if composition.composition_type == CompositionType.PIPELINE:
            return self._execute_pipeline(composition)
        elif composition.composition_type == CompositionType.PARALLEL:
            # Not implemented yet
            return ComposedResult(success=False, steps=[], final_context={})
        else:
            raise ValueError(f"Unknown or unimplemented composition type: {composition.composition_type}")

    def _execute_pipeline(self, composition: SkillComposition) -> ComposedResult:
        """Execute steps sequentially, passing context."""
        context = dict(composition.shared_context)
        results = []

        for step in composition.steps:
            # Check condition
            if step.condition and not step.condition(context):
                continue

            # Navigate to content
            if step.block_id:
                address = f"{step.skill_name}:^{step.block_id}"
            elif step.section:
                address = f"{step.skill_name}:#{step.section}"
            else:
                address = f"{step.skill_name}:*"

            result = self.navigator.navigate(address)

            if not result.found and step.fallback:
                # Try fallback
                fallback_address = f"{step.fallback.skill_name}:#{step.fallback.section or '*'}"
                result = self.navigator.navigate(fallback_address)

            results.append({
                'step': step.skill_name,
                'result': result,
                'context': dict(context)
            })

            # Update context with result
            if result.found and result.context:
                # context['last_section'] = result.context.section_path
                # Store content in context?
                context['last_content'] = result.content

        return ComposedResult(
            success=all(r['result'].found for r in results),
            steps=results,
            final_context=context
        )
