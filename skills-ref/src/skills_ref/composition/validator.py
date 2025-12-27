"""
Validators for skill composition.
"""

import re
from typing import Any, Dict, List, Optional, Set

from .types import (
    CompositionError,
    CompositionErrorType,
    DataType,
    FieldSchema,
    OperationType,
    ResourceConstraints,
    SkillChain,
    SkillDefinitionExt,
    SkillInputContract,
    SkillOutputContract,
    SkillTransition,
    ValidationResult,
)


class ContractValidator:
    """
    Validates skill input/output contracts.

    Features:
    - Type validation
    - Required field checking
    - Epistemic requirement validation
    - Pattern matching
    """

    def validate_input(
        self,
        contract: SkillInputContract,
        data: Dict[str, Any],
    ) -> ValidationResult:
        """Validate input data against contract."""
        errors = []

        # Check required fields
        for field in contract.get_required_fields():
            if field.name not in data:
                if field.default is None:
                    errors.append(CompositionError(
                        error_type=CompositionErrorType.MISSING_REQUIRED_INPUT,
                        message=f"Missing required field: {field.name}",
                        field_name=field.name,
                    ))

        # Validate each field
        for field in contract.fields:
            if field.name in data:
                field_errors = self._validate_field(field, data[field.name])
                errors.extend(field_errors)

        if errors:
            return ValidationResult.failure(errors)
        return ValidationResult.success()

    def validate_output(
        self,
        contract: SkillOutputContract,
        data: Dict[str, Any],
    ) -> ValidationResult:
        """Validate output data against contract."""
        errors = []
        warnings = []

        for field in contract.fields:
            if field.name in data:
                value = data[field.name]

                # Type validation
                field_errors = self._validate_field(field, value)
                errors.extend(field_errors)

                # Epistemic requirements
                if field.requires_source and not self._has_source(value):
                    errors.append(CompositionError(
                        error_type=CompositionErrorType.TYPE_MISMATCH,
                        message=f"Field {field.name} requires source citation",
                        field_name=field.name,
                    ))

                if field.requires_rationale and not self._has_rationale(value):
                    errors.append(CompositionError(
                        error_type=CompositionErrorType.TYPE_MISMATCH,
                        message=f"Field {field.name} requires rationale",
                        field_name=field.name,
                    ))

                if field.min_items is not None:
                    if isinstance(value, list) and len(value) < field.min_items:
                        errors.append(CompositionError(
                            error_type=CompositionErrorType.TYPE_MISMATCH,
                            message=f"Field {field.name} requires at least {field.min_items} items",
                            field_name=field.name,
                            expected=str(field.min_items),
                            actual=str(len(value)),
                        ))
            else:
                if field.required:
                    warnings.append(f"Expected output field {field.name} not present")

        if errors:
            return ValidationResult.failure(errors)
        return ValidationResult.success(warnings)

    def validate_compatibility(
        self,
        output_contract: SkillOutputContract,
        input_contract: SkillInputContract,
        field_mapping: Optional[Dict[str, str]] = None,
    ) -> ValidationResult:
        """
        Check if output contract is compatible with input contract.

        Validates that outputs can satisfy inputs.
        """
        errors = []
        mapping = field_mapping or {}

        for input_field in input_contract.get_required_fields():
            # Find corresponding output field
            output_field_name = mapping.get(input_field.name, input_field.name)
            output_field = output_contract.get_field(output_field_name)

            if output_field is None:
                errors.append(CompositionError(
                    error_type=CompositionErrorType.MISSING_REQUIRED_INPUT,
                    message=f"No output field '{output_field_name}' to satisfy input '{input_field.name}'",
                    field_name=input_field.name,
                ))
                continue

            # Check type compatibility
            if not self._types_compatible(output_field.type, input_field.type):
                errors.append(CompositionError(
                    error_type=CompositionErrorType.TYPE_MISMATCH,
                    message=f"Type mismatch: output '{output_field_name}' is {output_field.type.value}, "
                           f"but input '{input_field.name}' expects {input_field.type.value}",
                    field_name=input_field.name,
                    expected=input_field.type.value,
                    actual=output_field.type.value,
                ))

        if errors:
            return ValidationResult.failure(errors)
        return ValidationResult.success()

    def _validate_field(self, field: FieldSchema, value: Any) -> List[CompositionError]:
        """Validate a single field value."""
        errors = []

        # Type check
        if not self._check_type(field.type, value):
            errors.append(CompositionError(
                error_type=CompositionErrorType.TYPE_MISMATCH,
                message=f"Field '{field.name}' has wrong type",
                field_name=field.name,
                expected=field.type.value,
                actual=type(value).__name__,
            ))
            return errors  # Skip other checks if type is wrong

        # String constraints
        if field.type == DataType.STRING and isinstance(value, str):
            if field.min_length and len(value) < field.min_length:
                errors.append(CompositionError(
                    error_type=CompositionErrorType.TYPE_MISMATCH,
                    message=f"Field '{field.name}' is too short (min {field.min_length})",
                    field_name=field.name,
                ))
            if field.max_length and len(value) > field.max_length:
                errors.append(CompositionError(
                    error_type=CompositionErrorType.TYPE_MISMATCH,
                    message=f"Field '{field.name}' is too long (max {field.max_length})",
                    field_name=field.name,
                ))
            if field.pattern and not re.match(field.pattern, value):
                errors.append(CompositionError(
                    error_type=CompositionErrorType.TYPE_MISMATCH,
                    message=f"Field '{field.name}' doesn't match pattern {field.pattern}",
                    field_name=field.name,
                ))

        # Number constraints
        if field.type in [DataType.NUMBER, DataType.INTEGER]:
            if field.min_value is not None and value < field.min_value:
                errors.append(CompositionError(
                    error_type=CompositionErrorType.TYPE_MISMATCH,
                    message=f"Field '{field.name}' is below minimum ({field.min_value})",
                    field_name=field.name,
                ))
            if field.max_value is not None and value > field.max_value:
                errors.append(CompositionError(
                    error_type=CompositionErrorType.TYPE_MISMATCH,
                    message=f"Field '{field.name}' is above maximum ({field.max_value})",
                    field_name=field.name,
                ))

        # Enum check
        if field.enum_values and value not in field.enum_values:
            errors.append(CompositionError(
                error_type=CompositionErrorType.TYPE_MISMATCH,
                message=f"Field '{field.name}' value not in allowed values",
                field_name=field.name,
                expected=str(field.enum_values),
                actual=str(value),
            ))

        return errors

    def _check_type(self, expected: DataType, value: Any) -> bool:
        """Check if value matches expected type."""
        if expected == DataType.ANY:
            return True
        if expected == DataType.STRING:
            return isinstance(value, str)
        if expected == DataType.NUMBER:
            return isinstance(value, (int, float))
        if expected == DataType.INTEGER:
            return isinstance(value, int)
        if expected == DataType.BOOLEAN:
            return isinstance(value, bool)
        if expected == DataType.ARRAY:
            return isinstance(value, list)
        if expected == DataType.OBJECT:
            return isinstance(value, dict)
        return True

    def _types_compatible(self, output_type: DataType, input_type: DataType) -> bool:
        """Check if output type can satisfy input type."""
        if input_type == DataType.ANY:
            return True
        if output_type == input_type:
            return True
        # Allow widening: integer -> number
        if output_type == DataType.INTEGER and input_type == DataType.NUMBER:
            return True
        # Allow datetime -> date
        if output_type == DataType.DATETIME and input_type == DataType.DATE:
            return True
        return False

    def _has_source(self, value: Any) -> bool:
        """Check if value has source citation."""
        if isinstance(value, dict):
            return "source" in value or "sources" in value or "citation" in value
        if isinstance(value, str):
            # Simple heuristic: look for URL patterns or citation markers
            return "http" in value or "[" in value
        return False

    def _has_rationale(self, value: Any) -> bool:
        """Check if value has rationale/reasoning."""
        if isinstance(value, dict):
            return "rationale" in value or "reasoning" in value or "explanation" in value
        if isinstance(value, str):
            # Simple heuristic: check for length
            return len(value) > 50
        return False


class CompositionValidator:
    """
    Validates skill composition and chains.

    Features:
    - Circular dependency detection
    - Level hierarchy validation
    - Contract compatibility checking
    - Version compatibility
    """

    def __init__(self, contract_validator: Optional[ContractValidator] = None):
        self.contract_validator = contract_validator or ContractValidator()

    def validate_chain(
        self,
        chain: SkillChain,
        available_skills: Optional[Dict[str, SkillDefinitionExt]] = None,
    ) -> ValidationResult:
        """
        Validate a skill chain.

        Checks:
        - All skills exist
        - No circular dependencies
        - Contract compatibility
        - Valid transitions
        """
        errors = []
        warnings = []
        available = available_skills or {s.name: s for s in chain.skills}

        # Check all skills exist
        for skill in chain.skills:
            for composed in skill.composes:
                if composed not in available and composed != skill.name:
                    errors.append(CompositionError(
                        error_type=CompositionErrorType.MISSING_SKILL,
                        message=f"Skill '{skill.name}' composes unknown skill '{composed}'",
                        skill_name=skill.name,
                    ))

        # Check for circular dependencies (excluding self-recursion)
        circular = self._find_circular_dependencies(chain, available)
        for cycle in circular:
            errors.append(CompositionError(
                error_type=CompositionErrorType.CIRCULAR_DEPENDENCY,
                message=f"Circular dependency detected: {' -> '.join(cycle)}",
            ))

        # Validate transitions
        for transition in chain.transitions:
            from_skill = chain.get_skill(transition.from_skill)
            to_skill = chain.get_skill(transition.to_skill)

            if from_skill is None and transition.from_skill != "input":
                errors.append(CompositionError(
                    error_type=CompositionErrorType.INVALID_TRANSITION,
                    message=f"Transition from unknown skill: {transition.from_skill}",
                ))
                continue

            if to_skill is None and transition.to_skill != "output":
                errors.append(CompositionError(
                    error_type=CompositionErrorType.INVALID_TRANSITION,
                    message=f"Transition to unknown skill: {transition.to_skill}",
                ))
                continue

            # Check contract compatibility
            if from_skill and to_skill:
                result = self.contract_validator.validate_compatibility(
                    from_skill.output_contract,
                    to_skill.input_contract,
                    transition.field_mapping,
                )
                errors.extend(result.errors)

        # Check level hierarchy (warning only)
        for skill in chain.skills:
            for composed in skill.composes:
                if composed == skill.name:
                    continue  # Self-recursion is allowed
                composed_skill = available.get(composed)
                if composed_skill and composed_skill.level >= skill.level:
                    warnings.append(
                        f"Skill '{skill.name}' (L{skill.level}) composes "
                        f"'{composed}' (L{composed_skill.level}) - "
                        f"consider promoting to workflow"
                    )

        if errors:
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        return ValidationResult.success(warnings)

    def validate_composition(
        self,
        skill: SkillDefinitionExt,
        available_skills: Dict[str, SkillDefinitionExt],
    ) -> ValidationResult:
        """
        Validate a single skill's composition.

        Checks that all composed skills exist and are compatible.
        """
        errors = []
        warnings = []

        for composed_name in skill.composes:
            # Self-recursion is explicitly allowed
            if composed_name == skill.name:
                if skill.level < 3:
                    warnings.append(
                        f"Self-recursive skill '{skill.name}' should be Level 3"
                    )
                continue

            composed = available_skills.get(composed_name)
            if composed is None:
                errors.append(CompositionError(
                    error_type=CompositionErrorType.MISSING_SKILL,
                    message=f"Composed skill '{composed_name}' not found",
                    skill_name=skill.name,
                ))
                continue

            # Check level hierarchy
            if composed.level >= skill.level and skill.level < 3:
                warnings.append(
                    f"'{skill.name}' (L{skill.level}) composes "
                    f"'{composed_name}' (L{composed.level})"
                )

        if errors:
            return ValidationResult.failure(errors)
        return ValidationResult.success(warnings)

    def _find_circular_dependencies(
        self,
        chain: SkillChain,
        available: Dict[str, SkillDefinitionExt],
    ) -> List[List[str]]:
        """Find circular dependencies (excluding self-recursion)."""
        cycles = []

        def dfs(skill_name: str, path: List[str], visited: Set[str]):
            if skill_name in path:
                # Found cycle
                cycle_start = path.index(skill_name)
                cycles.append(path[cycle_start:] + [skill_name])
                return

            if skill_name in visited:
                return

            visited.add(skill_name)
            path.append(skill_name)

            skill = available.get(skill_name)
            if skill:
                for composed in skill.composes:
                    # Skip self-recursion
                    if composed != skill_name:
                        dfs(composed, path.copy(), visited)

        visited: Set[str] = set()
        for skill in chain.skills:
            if skill.name not in visited:
                dfs(skill.name, [], visited)

        return cycles

    def check_version_compatibility(
        self,
        skill: SkillDefinitionExt,
        required_version: str,
    ) -> ValidationResult:
        """Check if skill version is compatible with requirement."""
        try:
            from packaging import version
            skill_ver = version.parse(skill.version)
            req_ver = version.parse(required_version.lstrip("^~>=<"))

            # Handle different constraint types
            if required_version.startswith("^"):
                # Compatible within major version
                if skill_ver.major != req_ver.major:
                    return ValidationResult.failure([CompositionError(
                        error_type=CompositionErrorType.INCOMPATIBLE_VERSION,
                        message=f"Major version mismatch: {skill.version} vs {required_version}",
                        skill_name=skill.name,
                        expected=required_version,
                        actual=skill.version,
                    )])
            elif required_version.startswith("~"):
                # Compatible within minor version
                if skill_ver.major != req_ver.major or skill_ver.minor != req_ver.minor:
                    return ValidationResult.failure([CompositionError(
                        error_type=CompositionErrorType.INCOMPATIBLE_VERSION,
                        message=f"Minor version mismatch: {skill.version} vs {required_version}",
                        skill_name=skill.name,
                        expected=required_version,
                        actual=skill.version,
                    )])
            elif required_version.startswith(">="):
                if skill_ver < req_ver:
                    return ValidationResult.failure([CompositionError(
                        error_type=CompositionErrorType.INCOMPATIBLE_VERSION,
                        message=f"Version too old: {skill.version} < {required_version}",
                        skill_name=skill.name,
                        expected=required_version,
                        actual=skill.version,
                    )])

            return ValidationResult.success()

        except ImportError:
            # packaging not available, skip version check
            return ValidationResult.success(["Version checking skipped (packaging not installed)"])

    def validate_effect_safety(
        self,
        skill: SkillDefinitionExt,
        available_skills: Dict[str, SkillDefinitionExt],
    ) -> ValidationResult:
        """
        Validate that declared effect matches transitive reality.

        CRITICAL SECURITY CHECK: A skill cannot claim a lower effect
        than what its composed skills actually perform.

        Example violation:
            skill: "safe-read"
            operation: READ
            composes:
              - delete-data  # WRITE! Violates declared READ
        """
        errors = []

        # Compute transitive effect
        actual_effect = self._compute_transitive_effect(
            skill, available_skills, visited=set()
        )

        # Check if declared effect is accurate
        if actual_effect > skill.operation:
            errors.append(CompositionError(
                error_type=CompositionErrorType.EFFECT_VIOLATION,
                message=(
                    f"Skill '{skill.name}' declares {skill.operation.value} "
                    f"but transitively performs {actual_effect.value}. "
                    f"This is a security violation - skills cannot hide WRITE operations."
                ),
                skill_name=skill.name,
                expected=skill.operation.value,
                actual=actual_effect.value,
            ))

        if errors:
            return ValidationResult.failure(errors)
        return ValidationResult.success()

    def _compute_transitive_effect(
        self,
        skill: SkillDefinitionExt,
        available_skills: Dict[str, SkillDefinitionExt],
        visited: Set[str],
    ) -> OperationType:
        """
        Compute the actual effect by traversing composition tree.

        Effect composition is monotonic: max of all component effects.
        """
        if skill.name in visited:
            # Avoid infinite recursion for self-referential skills
            return skill.operation

        visited.add(skill.name)
        max_effect = skill.operation

        for composed_name in skill.composes:
            # Skip self-recursion
            if composed_name == skill.name:
                continue

            composed = available_skills.get(composed_name)
            if composed:
                composed_effect = self._compute_transitive_effect(
                    composed, available_skills, visited
                )
                if composed_effect > max_effect:
                    max_effect = composed_effect

        return max_effect

    def validate_depth(
        self,
        skill: SkillDefinitionExt,
        available_skills: Dict[str, SkillDefinitionExt],
        max_depth: int = 10,
    ) -> ValidationResult:
        """
        Validate that composition depth doesn't exceed limit.

        Prevents unbounded recursion and ensures reasonable complexity.
        """
        actual_depth = self._compute_depth(
            skill, available_skills, current_depth=0, visited=set()
        )

        if actual_depth > max_depth:
            return ValidationResult.failure([CompositionError(
                error_type=CompositionErrorType.DEPTH_EXCEEDED,
                message=(
                    f"Skill '{skill.name}' has composition depth {actual_depth}, "
                    f"which exceeds the maximum allowed depth of {max_depth}"
                ),
                skill_name=skill.name,
                expected=str(max_depth),
                actual=str(actual_depth),
            )])

        return ValidationResult.success()

    def _compute_depth(
        self,
        skill: SkillDefinitionExt,
        available_skills: Dict[str, SkillDefinitionExt],
        current_depth: int,
        visited: Set[str],
    ) -> int:
        """Compute the maximum depth of the composition tree."""
        if skill.name in visited:
            return current_depth  # Avoid infinite recursion

        visited.add(skill.name)
        max_child_depth = current_depth

        for composed_name in skill.composes:
            if composed_name == skill.name:
                continue  # Skip self-recursion

            composed = available_skills.get(composed_name)
            if composed:
                child_depth = self._compute_depth(
                    composed, available_skills, current_depth + 1, visited.copy()
                )
                max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def validate_full(
        self,
        chain: SkillChain,
        available_skills: Optional[Dict[str, SkillDefinitionExt]] = None,
        max_depth: int = 10,
    ) -> ValidationResult:
        """
        Perform full validation including security checks.

        Combines:
        - Chain structure validation
        - Effect safety validation
        - Depth validation
        """
        available = available_skills or {s.name: s for s in chain.skills}
        all_errors = []
        all_warnings = []

        # Chain validation
        chain_result = self.validate_chain(chain, available)
        all_errors.extend(chain_result.errors)
        all_warnings.extend(chain_result.warnings)

        # Effect safety for each skill
        for skill in chain.skills:
            effect_result = self.validate_effect_safety(skill, available)
            all_errors.extend(effect_result.errors)
            all_warnings.extend(effect_result.warnings)

            # Depth validation
            depth_result = self.validate_depth(skill, available, max_depth)
            all_errors.extend(depth_result.errors)
            all_warnings.extend(depth_result.warnings)

        if all_errors:
            return ValidationResult(valid=False, errors=all_errors, warnings=all_warnings)
        return ValidationResult.success(all_warnings)
