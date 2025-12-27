"""
Integration tests for skill composition flow.
"""

import pytest

from skills_ref.composition import (
    SkillChain,
    SkillChainExecutor,
    SkillDefinitionExt,
    SkillTransition,
    SkillInputContract,
    SkillOutputContract,
    FieldSchema,
    DataType,
    ErrorHandlingStrategy,
    CompositionValidator,
    ContractValidator,
    ValidationResult,
)


class TestContractValidation:
    """Test input/output contract validation."""

    @pytest.fixture
    def validator(self):
        return ContractValidator()

    def test_validate_required_fields(self, validator):
        """Test validation of required fields."""
        contract = SkillInputContract(fields=[
            FieldSchema(name="query", type=DataType.STRING, required=True),
            FieldSchema(name="limit", type=DataType.INTEGER, required=False, default=10),
        ])

        # Valid input
        result = validator.validate_input(contract, {"query": "test"})
        assert result.valid

        # Missing required field
        result = validator.validate_input(contract, {})
        assert not result.valid
        assert any("query" in str(e) for e in result.errors)

    def test_validate_types(self, validator):
        """Test type validation."""
        contract = SkillInputContract(fields=[
            FieldSchema(name="count", type=DataType.INTEGER),
            FieldSchema(name="name", type=DataType.STRING),
            FieldSchema(name="active", type=DataType.BOOLEAN),
        ])

        # Valid types
        result = validator.validate_input(contract, {
            "count": 5,
            "name": "test",
            "active": True,
        })
        assert result.valid

        # Invalid type
        result = validator.validate_input(contract, {
            "count": "five",  # Should be int
            "name": "test",
            "active": True,
        })
        assert not result.valid

    def test_validate_string_constraints(self, validator):
        """Test string length constraints."""
        contract = SkillInputContract(fields=[
            FieldSchema(
                name="title",
                type=DataType.STRING,
                min_length=3,
                max_length=50,
            ),
        ])

        # Valid length
        result = validator.validate_input(contract, {"title": "Hello World"})
        assert result.valid

        # Too short
        result = validator.validate_input(contract, {"title": "Hi"})
        assert not result.valid

        # Too long
        result = validator.validate_input(contract, {"title": "x" * 100})
        assert not result.valid

    def test_validate_number_constraints(self, validator):
        """Test number range constraints."""
        contract = SkillInputContract(fields=[
            FieldSchema(
                name="age",
                type=DataType.INTEGER,
                min_value=0,
                max_value=150,
            ),
        ])

        # Valid range
        result = validator.validate_input(contract, {"age": 25})
        assert result.valid

        # Below minimum
        result = validator.validate_input(contract, {"age": -5})
        assert not result.valid

        # Above maximum
        result = validator.validate_input(contract, {"age": 200})
        assert not result.valid

    def test_validate_enum_values(self, validator):
        """Test enum value validation."""
        contract = SkillInputContract(fields=[
            FieldSchema(
                name="status",
                type=DataType.STRING,
                enum_values=["pending", "active", "completed"],
            ),
        ])

        # Valid enum value
        result = validator.validate_input(contract, {"status": "active"})
        assert result.valid

        # Invalid enum value
        result = validator.validate_input(contract, {"status": "unknown"})
        assert not result.valid

    def test_validate_contract_compatibility(self, validator):
        """Test output-to-input contract compatibility."""
        output_contract = SkillOutputContract(fields=[
            FieldSchema(name="result", type=DataType.STRING),
            FieldSchema(name="count", type=DataType.INTEGER),
        ])

        input_contract = SkillInputContract(fields=[
            FieldSchema(name="data", type=DataType.STRING, required=True),
        ])

        # With mapping
        result = validator.validate_compatibility(
            output_contract,
            input_contract,
            field_mapping={"data": "result"},
        )
        assert result.valid

        # Without mapping (no match)
        result = validator.validate_compatibility(
            output_contract,
            input_contract,
        )
        assert not result.valid  # No field "data" in output


class TestChainValidation:
    """Test skill chain validation."""

    @pytest.fixture
    def validator(self):
        return CompositionValidator()

    @pytest.fixture
    def skill_a(self):
        return SkillDefinitionExt(
            name="skill-a",
            version="1.0.0",
            level=1,
            output_contract=SkillOutputContract(fields=[
                FieldSchema(name="output_a", type=DataType.STRING),
            ]),
        )

    @pytest.fixture
    def skill_b(self):
        return SkillDefinitionExt(
            name="skill-b",
            version="1.0.0",
            level=2,
            input_contract=SkillInputContract(fields=[
                FieldSchema(name="input_b", type=DataType.STRING, required=True),
            ]),
            output_contract=SkillOutputContract(fields=[
                FieldSchema(name="output_b", type=DataType.STRING),
            ]),
            composes=["skill-a"],
        )

    def test_valid_chain(self, validator, skill_a, skill_b):
        """Test validation of a valid chain."""
        chain = SkillChain(
            id="test-chain",
            skills=[skill_a, skill_b],
            transitions=[
                SkillTransition(
                    from_skill="skill-a",
                    to_skill="skill-b",
                    field_mapping={"output_a": "input_b"},
                ),
            ],
        )

        result = validator.validate_chain(chain)
        assert result.valid

    def test_missing_skill_reference(self, validator, skill_a):
        """Test validation catches missing skill references."""
        skill_with_missing_ref = SkillDefinitionExt(
            name="skill-with-ref",
            version="1.0.0",
            level=2,
            composes=["nonexistent-skill"],
        )

        chain = SkillChain(
            id="test-chain",
            skills=[skill_a, skill_with_missing_ref],
        )

        result = validator.validate_chain(chain)
        assert not result.valid
        assert any("nonexistent-skill" in str(e) for e in result.errors)

    def test_circular_dependency_detection(self, validator):
        """Test detection of circular dependencies."""
        skill_x = SkillDefinitionExt(
            name="skill-x",
            level=2,
            composes=["skill-y"],
        )
        skill_y = SkillDefinitionExt(
            name="skill-y",
            level=2,
            composes=["skill-z"],
        )
        skill_z = SkillDefinitionExt(
            name="skill-z",
            level=2,
            composes=["skill-x"],  # Creates cycle
        )

        chain = SkillChain(
            id="circular-chain",
            skills=[skill_x, skill_y, skill_z],
        )

        result = validator.validate_chain(chain)
        assert not result.valid
        assert any("circular" in str(e).lower() for e in result.errors)

    def test_self_recursion_allowed(self, validator):
        """Test that self-recursion is allowed."""
        recursive_skill = SkillDefinitionExt(
            name="recursive-skill",
            level=3,
            composes=["recursive-skill"],  # Self-reference
        )

        chain = SkillChain(
            id="recursive-chain",
            skills=[recursive_skill],
        )

        result = validator.validate_chain(chain)
        # Self-recursion should not cause circular dependency error
        circular_errors = [
            e for e in result.errors
            if "circular" in str(e).lower()
        ]
        assert len(circular_errors) == 0


class TestChainExecution:
    """Test skill chain execution."""

    @pytest.fixture
    def mock_executor(self):
        """Create mock skill executor."""
        async def execute(skill, inputs):
            # Simple mock that transforms input
            return {
                f"{skill.name}_output": f"processed_{inputs.get('input', 'none')}",
            }
        return execute

    @pytest.fixture
    def chain_executor(self, mock_executor):
        return SkillChainExecutor(
            skill_executor=mock_executor,
            validator=CompositionValidator(),
        )

    @pytest.mark.asyncio
    async def test_simple_chain_execution(self, chain_executor):
        """Test executing a simple chain."""
        skill_1 = SkillDefinitionExt(
            name="skill-1",
            level=1,
            timeout_ms=5000,
            output_contract=SkillOutputContract(fields=[
                FieldSchema(name="skill-1_output", type=DataType.STRING),
            ]),
        )
        skill_2 = SkillDefinitionExt(
            name="skill-2",
            level=1,
            timeout_ms=5000,
            input_contract=SkillInputContract(fields=[
                FieldSchema(name="skill-1_output", type=DataType.STRING),
            ]),
        )

        chain = SkillChain(
            id="simple-chain",
            skills=[skill_1, skill_2],
            transitions=[
                SkillTransition(
                    from_skill="skill-1",
                    to_skill="skill-2",
                ),
            ],
        )

        result = await chain_executor.execute(
            chain=chain,
            initial_inputs={"input": "test"},
            validate_first=False,
        )

        assert result.success
        assert len(result.results) == 2
        assert result.total_duration_ms > 0

    @pytest.mark.asyncio
    async def test_chain_with_error_stop(self, chain_executor):
        """Test chain stops on error with STOP strategy."""
        # Create executor that fails on second skill
        async def failing_executor(skill, inputs):
            if skill.name == "failing-skill":
                raise ValueError("Intentional failure")
            return {"output": "success"}

        executor = SkillChainExecutor(
            skill_executor=failing_executor,
        )

        skill_1 = SkillDefinitionExt(name="skill-1", level=1, timeout_ms=5000)
        skill_2 = SkillDefinitionExt(name="failing-skill", level=1, timeout_ms=5000)
        skill_3 = SkillDefinitionExt(name="skill-3", level=1, timeout_ms=5000)

        chain = SkillChain(
            id="failing-chain",
            skills=[skill_1, skill_2, skill_3],
            error_handling=ErrorHandlingStrategy.STOP,
        )

        result = await executor.execute(chain, {}, validate_first=False)

        assert not result.success
        assert len(result.results) == 2  # Stopped after failing skill
        assert "Intentional failure" in result.error

    @pytest.mark.asyncio
    async def test_chain_with_error_continue(self):
        """Test chain continues on error with CONTINUE strategy."""
        execution_order = []

        async def tracking_executor(skill, inputs):
            execution_order.append(skill.name)
            if skill.name == "failing-skill":
                raise ValueError("Intentional failure")
            return {"output": "success"}

        executor = SkillChainExecutor(
            skill_executor=tracking_executor,
        )

        skill_1 = SkillDefinitionExt(name="skill-1", level=1, timeout_ms=5000)
        skill_2 = SkillDefinitionExt(name="failing-skill", level=1, timeout_ms=5000)
        skill_3 = SkillDefinitionExt(name="skill-3", level=1, timeout_ms=5000)

        chain = SkillChain(
            id="continue-chain",
            skills=[skill_1, skill_2, skill_3],
            error_handling=ErrorHandlingStrategy.CONTINUE,
        )

        result = await executor.execute(chain, {}, validate_first=False)

        # All skills should have been attempted
        assert len(execution_order) == 3
        assert "skill-3" in execution_order

    @pytest.mark.asyncio
    async def test_parallel_execution(self, mock_executor):
        """Test parallel skill execution."""
        executor = SkillChainExecutor(skill_executor=mock_executor)

        skills = [
            SkillDefinitionExt(name=f"parallel-{i}", level=1, timeout_ms=5000)
            for i in range(3)
        ]

        results = await executor.execute_parallel(
            skills=skills,
            inputs={"shared": "input"},
        )

        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_field_mapping_in_chain(self, mock_executor):
        """Test field mapping between skills."""
        async def mapping_executor(skill, inputs):
            if skill.name == "producer":
                return {"raw_data": "produced_value"}
            elif skill.name == "consumer":
                return {"consumed": inputs.get("mapped_data", "missing")}
            return {}

        executor = SkillChainExecutor(skill_executor=mapping_executor)

        producer = SkillDefinitionExt(
            name="producer",
            level=1,
            timeout_ms=5000,
            output_contract=SkillOutputContract(fields=[
                FieldSchema(name="raw_data", type=DataType.STRING),
            ]),
        )
        consumer = SkillDefinitionExt(
            name="consumer",
            level=1,
            timeout_ms=5000,
            input_contract=SkillInputContract(fields=[
                FieldSchema(name="mapped_data", type=DataType.STRING),
            ]),
        )

        chain = SkillChain(
            id="mapping-chain",
            skills=[producer, consumer],
            transitions=[
                SkillTransition(
                    from_skill="producer",
                    to_skill="consumer",
                    field_mapping={"raw_data": "mapped_data"},
                ),
            ],
        )

        result = await executor.execute(chain, {}, validate_first=False)

        assert result.success
        # The consumer should have received mapped data


class TestExecutionCallbacks:
    """Test execution callbacks."""

    @pytest.mark.asyncio
    async def test_skill_start_callback(self):
        """Test on_skill_start callback."""
        started_skills = []

        def on_start(skill_name, context):
            started_skills.append(skill_name)

        async def executor_fn(skill, inputs):
            return {"done": True}

        executor = SkillChainExecutor(
            skill_executor=executor_fn,
            on_skill_start=on_start,
        )

        chain = SkillChain(
            id="callback-chain",
            skills=[
                SkillDefinitionExt(name="skill-1", level=1, timeout_ms=5000),
                SkillDefinitionExt(name="skill-2", level=1, timeout_ms=5000),
            ],
        )

        await executor.execute(chain, {}, validate_first=False)

        assert "skill-1" in started_skills
        assert "skill-2" in started_skills

    @pytest.mark.asyncio
    async def test_skill_end_callback(self):
        """Test on_skill_end callback."""
        ended_skills = []

        def on_end(result):
            ended_skills.append({
                "name": result.skill_name,
                "success": result.success,
            })

        async def executor_fn(skill, inputs):
            return {"done": True}

        executor = SkillChainExecutor(
            skill_executor=executor_fn,
            on_skill_end=on_end,
        )

        chain = SkillChain(
            id="callback-chain",
            skills=[
                SkillDefinitionExt(name="skill-1", level=1, timeout_ms=5000),
                SkillDefinitionExt(name="skill-2", level=1, timeout_ms=5000),
            ],
        )

        await executor.execute(chain, {}, validate_first=False)

        assert len(ended_skills) == 2
        assert all(s["success"] for s in ended_skills)
