"""
Skill chain executor with error handling.
"""

import asyncio
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .types import (
    ErrorHandlingStrategy,
    SkillChain,
    SkillDefinitionExt,
    SkillTransition,
    ValidationResult,
)
from .validator import CompositionValidator


@dataclass
class SkillExecutionResult:
    """Result of a single skill execution."""
    skill_name: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    retries: int = 0


@dataclass
class ChainExecutionResult:
    """Result of a skill chain execution."""
    chain_id: str
    success: bool
    results: List[SkillExecutionResult] = field(default_factory=list)
    final_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    total_duration_ms: float = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    cost: float = 0  # Accumulated cost


class SkillChainExecutor:
    """
    Executes skill chains with error handling.

    Features:
    - Sequential and parallel execution
    - Error handling strategies
    - Context passing between skills
    - Cost tracking
    """

    def __init__(
        self,
        skill_executor: Callable[[SkillDefinitionExt, Dict[str, Any]], Any],
        validator: Optional[CompositionValidator] = None,
        on_skill_start: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_skill_end: Optional[Callable[[SkillExecutionResult], None]] = None,
    ):
        """
        Initialize executor.

        Args:
            skill_executor: Function to execute a single skill
            validator: Composition validator (for pre-execution validation)
            on_skill_start: Callback when skill starts
            on_skill_end: Callback when skill ends
        """
        self.skill_executor = skill_executor
        self.validator = validator or CompositionValidator()
        self._on_skill_start = on_skill_start
        self._on_skill_end = on_skill_end

    async def execute(
        self,
        chain: SkillChain,
        initial_inputs: Dict[str, Any],
        validate_first: bool = True,
    ) -> ChainExecutionResult:
        """
        Execute a skill chain.

        Args:
            chain: The skill chain to execute
            initial_inputs: Initial inputs for the first skill
            validate_first: Whether to validate chain before execution

        Returns:
            ChainExecutionResult with all skill results
        """
        started_at = datetime.utcnow()
        start_time = time.time()

        # Validate chain first
        if validate_first:
            validation = self.validator.validate_chain(chain)
            if not validation.valid:
                return ChainExecutionResult(
                    chain_id=chain.id,
                    success=False,
                    error=f"Validation failed: {validation.errors[0]}",
                    started_at=started_at,
                    ended_at=datetime.utcnow(),
                )

        results: List[SkillExecutionResult] = []
        current_context = dict(initial_inputs)
        total_cost = 0

        try:
            # Execute skills in order
            for i, skill in enumerate(chain.skills):
                # Emit start callback
                if self._on_skill_start:
                    self._on_skill_start(skill.name, current_context)

                # Execute skill with retries
                result = await self._execute_skill_with_retry(
                    skill,
                    current_context,
                    chain.max_retries,
                )
                results.append(result)

                # Emit end callback
                if self._on_skill_end:
                    self._on_skill_end(result)

                if not result.success:
                    # Handle error based on strategy
                    if chain.error_handling == ErrorHandlingStrategy.STOP:
                        return ChainExecutionResult(
                            chain_id=chain.id,
                            success=False,
                            results=results,
                            error=result.error,
                            total_duration_ms=(time.time() - start_time) * 1000,
                            started_at=started_at,
                            ended_at=datetime.utcnow(),
                            cost=total_cost,
                        )
                    elif chain.error_handling == ErrorHandlingStrategy.COMPENSATE:
                        # Run compensation
                        await self._run_compensation(
                            chain, results, current_context
                        )
                        return ChainExecutionResult(
                            chain_id=chain.id,
                            success=False,
                            results=results,
                            error=f"Compensated after: {result.error}",
                            total_duration_ms=(time.time() - start_time) * 1000,
                            started_at=started_at,
                            ended_at=datetime.utcnow(),
                            cost=total_cost,
                        )
                    # CONTINUE: just proceed to next skill

                else:
                    # Success - merge output into context
                    if result.output:
                        # Apply transition mapping if available
                        if i < len(chain.skills) - 1:
                            next_skill = chain.skills[i + 1]
                            transition = chain.get_transition(skill.name, next_skill.name)
                            if transition and transition.field_mapping:
                                for src, dst in transition.field_mapping.items():
                                    if src in result.output:
                                        current_context[dst] = result.output[src]
                            else:
                                current_context.update(result.output)
                        else:
                            current_context.update(result.output)

            return ChainExecutionResult(
                chain_id=chain.id,
                success=True,
                results=results,
                final_output=current_context,
                total_duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                ended_at=datetime.utcnow(),
                cost=total_cost,
            )

        except Exception as e:
            return ChainExecutionResult(
                chain_id=chain.id,
                success=False,
                results=results,
                error=str(e),
                total_duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                ended_at=datetime.utcnow(),
                cost=total_cost,
            )

    async def execute_parallel(
        self,
        skills: List[SkillDefinitionExt],
        inputs: Dict[str, Any],
    ) -> List[SkillExecutionResult]:
        """Execute multiple skills in parallel."""
        tasks = [
            self._execute_skill(skill, inputs)
            for skill in skills
        ]
        return await asyncio.gather(*tasks)

    async def _execute_skill(
        self,
        skill: SkillDefinitionExt,
        inputs: Dict[str, Any],
    ) -> SkillExecutionResult:
        """Execute a single skill."""
        started_at = datetime.utcnow()
        start_time = time.time()

        try:
            # Handle timeout
            timeout = skill.timeout_ms / 1000
            output = await asyncio.wait_for(
                self._run_skill(skill, inputs),
                timeout=timeout,
            )

            return SkillExecutionResult(
                skill_name=skill.name,
                success=True,
                output=output if isinstance(output, dict) else {"result": output},
                duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                ended_at=datetime.utcnow(),
            )

        except asyncio.TimeoutError:
            return SkillExecutionResult(
                skill_name=skill.name,
                success=False,
                error=f"Timeout after {skill.timeout_ms}ms",
                duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                ended_at=datetime.utcnow(),
            )

        except Exception as e:
            return SkillExecutionResult(
                skill_name=skill.name,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                ended_at=datetime.utcnow(),
            )

    async def _execute_skill_with_retry(
        self,
        skill: SkillDefinitionExt,
        inputs: Dict[str, Any],
        max_retries: int,
    ) -> SkillExecutionResult:
        """Execute skill with retries."""
        last_result = None
        retries = 0

        for attempt in range(max_retries + 1):
            result = await self._execute_skill(skill, inputs)
            result.retries = retries

            if result.success:
                return result

            last_result = result
            retries += 1

            # Exponential backoff
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)

        return last_result or SkillExecutionResult(
            skill_name=skill.name,
            success=False,
            error="Max retries exceeded",
        )

    async def _run_skill(
        self,
        skill: SkillDefinitionExt,
        inputs: Dict[str, Any],
    ) -> Any:
        """Actually run the skill executor."""
        if asyncio.iscoroutinefunction(self.skill_executor):
            return await self.skill_executor(skill, inputs)
        else:
            return self.skill_executor(skill, inputs)

    async def _run_compensation(
        self,
        chain: SkillChain,
        results: List[SkillExecutionResult],
        context: Dict[str, Any],
    ) -> None:
        """Run compensation skills for rollback."""
        for comp_name in reversed(chain.compensation_skills):
            comp_skill = chain.get_skill(comp_name)
            if comp_skill:
                # Add info about what failed
                comp_context = {
                    **context,
                    "_compensation": True,
                    "_failed_skills": [r.skill_name for r in results if not r.success],
                }
                await self._execute_skill(comp_skill, comp_context)


class SkillExecutorFactory:
    """
    Factory for creating skill executors.

    Useful for testing and dependency injection.
    """

    @staticmethod
    def create_mock_executor() -> Callable[[SkillDefinitionExt, Dict[str, Any]], Any]:
        """Create a mock executor for testing."""
        async def mock_execute(skill: SkillDefinitionExt, inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"mock_result": f"Executed {skill.name}"}
        return mock_execute

    @staticmethod
    def create_logging_executor(
        base_executor: Callable[[SkillDefinitionExt, Dict[str, Any]], Any],
        logger: Any,
    ) -> Callable[[SkillDefinitionExt, Dict[str, Any]], Any]:
        """Wrap executor with logging."""
        async def logging_execute(skill: SkillDefinitionExt, inputs: Dict[str, Any]) -> Any:
            logger.info(f"Executing skill: {skill.name}")
            result = await base_executor(skill, inputs)
            logger.info(f"Completed skill: {skill.name}")
            return result
        return logging_execute
