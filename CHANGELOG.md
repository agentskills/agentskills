# Changelog

All notable changes to the Agent Skills format will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Portfolio Manager Showcase**: Comprehensive L1/L2/L3 skill library for portfolio management
  - 6 L1 atomic skills (holdings-ingest, market-data-fetch, risk-metrics-calculate, etc.)
  - 12 L2 composite skills (portfolio-summarise, trade-list-generate, drift-monitor, etc.)
  - 4 L3 workflow skills (portfolio-onboard, rebalance-execute, goal-based-review, annual-portfolio-review)
  - Detailed execution traces and human checkpoint examples

- **Financial Advisor Showcase**: Compliance-aware advisory skill library
  - Client lifecycle management (onboard, review, advice delivery)
  - Regulatory compliance integration (SOA, FSG, KYC)

- **Test Infrastructure**:
  - Schema validation tests (13 tests)
  - Cross-showcase consistency tests (18 tests)
  - Property-based tests with Hypothesis (23 tests)
  - Portfolio manager unit tests (119 tests)

- **Developer Tools**:
  - `scripts/skills-lint.py`: Comprehensive SKILL.md linter with error codes
  - `scripts/validate-skills.py`: Quick validation for CI/CD

- **Documentation**:
  - `SKILL-REUSE-GUIDE.md`: Patterns for composing and extending skills
  - Execution trace format for L3 workflows
  - Human checkpoint dialog examples

- **Composable Skills Architecture**: Hierarchical skill composition (L1 Atomic → L2 Composite → L3 Workflow)
  - `level` field: Composition tier (1, 2, or 3)
  - `operation` field: Safety classification (READ, WRITE, TRANSFORM)
  - `composes` field: Explicit skill dependencies

- **Static Type System**: Input/output schemas with type checking
  - `inputs` field: Typed input parameters with validation
  - `outputs` field: Typed output values with constraints
  - Primitive types: `string`, `number`, `integer`, `boolean`, `date`, `datetime`, `any`
  - List types via `[]` suffix: `string[]`, `Flight[]`

- **Epistemic Requirements**: Prevent hallucination through output constraints
  - `requires_source`: Output must cite supporting sources
  - `requires_rationale`: Output must include reasoning
  - `min_length`: Minimum string length for rationale
  - `min_items`: Minimum list items for sources
  - `range`: Valid range for numeric outputs

- **CLI Commands**:
  - `skills-ref typecheck`: Validate type compatibility across composed skills
  - `skills-ref graph`: Visualise composition graph (Mermaid, DOT, JSON)

- **Trip Optimizer Showcase**: Complete example with 12 skills demonstrating all features
  - Self-recursion patterns
  - L3 → L3 composition
  - Typed inputs/outputs with constraints

- **Documentation**:
  - Architecture documentation with type system reference
  - Theoretical foundation (FP-to-hardware parallel)
  - Acknowledgements for FCCM 2014 paper contributors

### Changed

- Updated README with type system overview and showcase link

### Notes

- All new fields are optional: backwards-compatible with Agent Skills v1.0
- Existing skills work unchanged without any modifications

## [1.0.0] - 2024-XX-XX

Initial release of the Agent Skills format.

### Added

- Basic skill structure with `name`, `description`
- YAML frontmatter in SKILL.md files
- `skills-ref` CLI for validation and prompt generation
