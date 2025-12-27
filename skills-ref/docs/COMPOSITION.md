# Skill Composition

The AgentSkills composition module enables building complex workflows by chaining skills together with validation and error handling.

## Overview

The composition system provides:
- **Skill chains**: Sequential and parallel skill execution
- **Input/Output contracts**: Type-safe data flow between skills
- **Validation**: Contract compatibility and circular dependency detection
- **Error handling**: Stop, continue, or compensate strategies

## Quick Start

```python
from skills_ref.composition import (
    SkillChain,
    SkillDefinitionExt,
    SkillChainExecutor,
    CompositionValidator,
)

# Define skills
research_skill = SkillDefinitionExt(
    name="research",
    level=1,
    output_contract=SkillOutputContract(fields=[
        FieldSchema(name="findings", type=DataType.STRING),
    ]),
)

summarise_skill = SkillDefinitionExt(
    name="summarise",
    level=2,
    input_contract=SkillInputContract(fields=[
        FieldSchema(name="content", type=DataType.STRING, required=True),
    ]),
)

# Create chain
chain = SkillChain(
    id="research-and-summarise",
    skills=[research_skill, summarise_skill],
    transitions=[
        SkillTransition(
            from_skill="research",
            to_skill="summarise",
            field_mapping={"findings": "content"},
        ),
    ],
)

# Validate chain
validator = CompositionValidator()
result = validator.validate_chain(chain)
if result.valid:
    print("Chain is valid")
```

## Skill Contracts

### Input Contract

Define what inputs a skill requires:

```python
from skills_ref.composition import (
    SkillInputContract,
    FieldSchema,
    DataType,
)

input_contract = SkillInputContract(
    fields=[
        FieldSchema(
            name="query",
            type=DataType.STRING,
            required=True,
            min_length=1,
            max_length=1000,
            description="Search query",
        ),
        FieldSchema(
            name="max_results",
            type=DataType.INTEGER,
            required=False,
            default=10,
            min_value=1,
            max_value=100,
        ),
        FieldSchema(
            name="filters",
            type=DataType.OBJECT,
            required=False,
        ),
    ],
)

# Get required fields
required = input_contract.get_required_fields()
```

### Output Contract

Define what outputs a skill produces:

```python
from skills_ref.composition import (
    SkillOutputContract,
    FieldSchema,
    DataType,
)

output_contract = SkillOutputContract(
    fields=[
        FieldSchema(
            name="results",
            type=DataType.ARRAY,
            required=True,
            min_items=0,
            description="Search results",
        ),
        FieldSchema(
            name="summary",
            type=DataType.STRING,
            requires_rationale=True,  # Must include explanation
        ),
        FieldSchema(
            name="sources",
            type=DataType.ARRAY,
            requires_source=True,  # Must cite sources
        ),
    ],
)
```

### Data Types

| Type | Python | Description |
|------|--------|-------------|
| `STRING` | `str` | Text data |
| `NUMBER` | `float` | Numeric (float) |
| `INTEGER` | `int` | Whole numbers |
| `BOOLEAN` | `bool` | True/False |
| `ARRAY` | `list` | List of items |
| `OBJECT` | `dict` | Key-value pairs |
| `DATE` | `date` | Date only |
| `DATETIME` | `datetime` | Date and time |
| `ANY` | `Any` | Any type |

## Skill Chains

### Creating Chains

```python
from skills_ref.composition import (
    SkillChain,
    SkillTransition,
    ErrorHandlingStrategy,
)

chain = SkillChain(
    id="data-pipeline",
    name="Data Processing Pipeline",
    skills=[fetch_skill, transform_skill, store_skill],
    transitions=[
        SkillTransition(
            from_skill="fetch",
            to_skill="transform",
            field_mapping={"raw_data": "input_data"},
        ),
        SkillTransition(
            from_skill="transform",
            to_skill="store",
            field_mapping={"processed_data": "data"},
        ),
    ],
    error_handling=ErrorHandlingStrategy.COMPENSATE,
    compensation_skills=["cleanup", "notify"],
    max_retries=3,
)
```

### Error Handling Strategies

| Strategy | Behaviour |
|----------|-----------|
| `STOP` | Stop chain on first error |
| `CONTINUE` | Skip failed skill, continue chain |
| `COMPENSATE` | Run compensation skills to rollback |

```python
# Stop on error (default)
chain = SkillChain(
    ...,
    error_handling=ErrorHandlingStrategy.STOP,
)

# Continue despite errors
chain = SkillChain(
    ...,
    error_handling=ErrorHandlingStrategy.CONTINUE,
)

# Compensate on failure
chain = SkillChain(
    ...,
    error_handling=ErrorHandlingStrategy.COMPENSATE,
    compensation_skills=["rollback", "cleanup"],
)
```

### Field Mapping

Map output fields to input fields:

```python
transition = SkillTransition(
    from_skill="search",
    to_skill="analyse",
    field_mapping={
        "search_results": "documents",   # search.results -> analyse.documents
        "query": "original_query",        # pass through query
    },
    condition="len(search_results) > 0",  # Only proceed if results exist
)
```

## Validation

### Contract Validation

```python
from skills_ref.composition import ContractValidator

validator = ContractValidator()

# Validate input data
result = validator.validate_input(
    contract=skill.input_contract,
    data={"query": "test", "max_results": 50},
)

if not result.valid:
    for error in result.errors:
        print(f"{error.field_name}: {error.message}")
```

### Composition Validation

```python
from skills_ref.composition import CompositionValidator

validator = CompositionValidator()

# Validate entire chain
result = validator.validate_chain(chain)

if not result.valid:
    for error in result.errors:
        print(f"Error: {error.message}")

for warning in result.warnings:
    print(f"Warning: {warning}")
```

### Validation Checks

The validator performs:
1. **Skill existence**: All referenced skills exist
2. **Circular dependencies**: No cycles (except self-recursion)
3. **Contract compatibility**: Outputs match inputs
4. **Level hierarchy**: Warns if higher-level skill composes lower-level
5. **Version compatibility**: Checks semantic version constraints

```python
# Check version compatibility
result = validator.check_version_compatibility(
    skill=my_skill,
    required_version="^1.2.0",
)

# Check single skill composition
result = validator.validate_composition(
    skill=composite_skill,
    available_skills={"atomic-1": skill1, "atomic-2": skill2},
)
```

## Chain Execution

### Basic Execution

```python
from skills_ref.composition import SkillChainExecutor

# Create executor with skill runner
async def run_skill(skill, inputs):
    return await skill.execute(inputs)

executor = SkillChainExecutor(
    skill_executor=run_skill,
    validator=CompositionValidator(),
)

# Execute chain
result = await executor.execute(
    chain=my_chain,
    initial_inputs={"query": "AI trends"},
    validate_first=True,
)

if result.success:
    print(f"Final output: {result.final_output}")
    print(f"Total duration: {result.total_duration_ms}ms")
else:
    print(f"Error: {result.error}")
```

### Execution Results

```python
# ChainExecutionResult
result.chain_id       # Chain identifier
result.success        # Overall success
result.results        # List of SkillExecutionResult
result.final_output   # Final context/output
result.error          # Error message if failed
result.total_duration_ms
result.started_at
result.ended_at
result.cost           # Accumulated cost

# Individual skill results
for skill_result in result.results:
    print(f"{skill_result.skill_name}: {skill_result.success}")
    print(f"  Duration: {skill_result.duration_ms}ms")
    print(f"  Retries: {skill_result.retries}")
```

### Parallel Execution

```python
# Execute skills in parallel
results = await executor.execute_parallel(
    skills=[skill1, skill2, skill3],
    inputs={"shared": "input"},
)

for result in results:
    print(f"{result.skill_name}: {result.output}")
```

### Execution Callbacks

```python
def on_skill_start(skill_name: str, context: dict):
    print(f"Starting {skill_name}")

def on_skill_end(result: SkillExecutionResult):
    print(f"Finished {result.skill_name}: {result.success}")

executor = SkillChainExecutor(
    skill_executor=run_skill,
    on_skill_start=on_skill_start,
    on_skill_end=on_skill_end,
)
```

## Extended Skill Definition

```python
from skills_ref.composition import SkillDefinitionExt

skill = SkillDefinitionExt(
    name="research-skill",
    version="1.2.0",
    level=2,
    description="Research a topic and return findings",

    # Contracts
    input_contract=SkillInputContract(...),
    output_contract=SkillOutputContract(...),

    # Composition
    composes=["web-search", "summarise"],  # Skills this uses

    # Execution
    timeout_ms=30000,
    max_retries=3,

    # Metadata
    tags=["research", "analysis"],
    author="team@example.com",
)
```

## Error Types

| Error Type | Description |
|------------|-------------|
| `MISSING_SKILL` | Referenced skill not found |
| `CIRCULAR_DEPENDENCY` | Circular reference detected |
| `TYPE_MISMATCH` | Data type doesn't match contract |
| `MISSING_REQUIRED_INPUT` | Required field not provided |
| `INVALID_TRANSITION` | Transition references unknown skill |
| `INCOMPATIBLE_VERSION` | Version constraint not satisfied |

```python
from skills_ref.composition import CompositionErrorType

for error in result.errors:
    if error.error_type == CompositionErrorType.TYPE_MISMATCH:
        print(f"Type mismatch: expected {error.expected}, got {error.actual}")
    elif error.error_type == CompositionErrorType.MISSING_REQUIRED_INPUT:
        print(f"Missing required field: {error.field_name}")
```

## Integration Example

```python
from skills_ref.composition import (
    SkillChain,
    SkillChainExecutor,
    CompositionValidator,
)
from skills_ref.observability import DistributedTracer

tracer = DistributedTracer(service_name="skill-chains")

async def traced_executor(skill, inputs):
    with tracer.start_span(f"skill:{skill.name}") as span:
        span.set_attribute("skill.level", skill.level)
        try:
            result = await skill.execute(inputs)
            span.set_status("ok")
            return result
        except Exception as e:
            span.set_status("error", str(e))
            raise

executor = SkillChainExecutor(
    skill_executor=traced_executor,
)

# Execute with tracing
with tracer.start_span("chain:data-pipeline") as span:
    result = await executor.execute(chain, initial_inputs)
    span.set_attribute("chain.success", result.success)
    span.set_attribute("chain.duration_ms", result.total_duration_ms)
```

## Best Practices

1. **Define contracts explicitly**: Always specify input/output contracts
2. **Use field mapping**: Explicitly map fields between skills
3. **Validate early**: Validate chains before execution
4. **Handle errors appropriately**: Choose error strategy based on use case
5. **Test compositions**: Unit test individual skills and integration test chains
6. **Version skills**: Use semantic versioning for skill definitions
7. **Document contracts**: Include descriptions for all fields
