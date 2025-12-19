# Changelog

All notable changes to the Agent Skills format will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
