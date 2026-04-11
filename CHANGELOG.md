# Changelog

## [Unreleased]

### Added

- **Skill Quality Evaluation Framework**
  - New `evaluate` CLI command to assess skill quality
  - Three quality dimensions: Completeness, Clarity, Structure
  - Numeric scoring system (0-100 per dimension)
  - Three severity levels: ERROR, WARNING, INFO
  - Actionable findings with suggestions for improvement
  - Support for custom evaluator configuration
  - JSON output format for automation
  - Minimum score threshold option (--min-score)
  - Comprehensive test suite (15 test cases)
  - Full documentation in EVALUATION.md

- **New Python API exports**
  - `evaluate_skill(skill_path)` - Convenience function
  - `SkillEvaluator` - Main evaluator class
  - `EvaluationResult` - Results dataclass
  - `EvaluationFinding` - Finding dataclass
  - `Severity` - Severity enum

- **CLI enhancements**
  - `skills-ref evaluate <path>` - Evaluate skill quality
  - `skills-ref evaluate <path> --json` - JSON output
  - `skills-ref evaluate <path> --min-score N` - Quality threshold

### Changed

- Updated README.md with evaluation framework documentation
- Updated __init__.py to export evaluation classes
- Enhanced CLI with evaluate command

### Documentation

- Added EVALUATION.md - Comprehensive evaluation guide
- Added EVALUATION_QUICKREF.md - Quick reference
- Added IMPLEMENTATION_SUMMARY.md - Implementation details
- Updated README.md with evaluation examples

### Testing

- Added tests/test_evaluator.py with comprehensive test coverage
- Tests for all quality dimensions
- Tests for severity levels and scoring
- Tests for edge cases and error handling

## Quality Checks Implemented

### Completeness
- SKILL.md existence
- Description field presence
- License field presence
- Minimum content length (100 chars)
- Code example detection
- Tool reference detection

### Clarity
- Description length validation (20-500 chars)
- "When to use" guidance detection
- Actionable language verification
- Clear directive checking

### Structure  
- Recommended section detection (Overview, When to Use, Usage, Examples)
- Content organization assessment
- Markdown formatting validation

## Integration Examples

The framework supports:
- CI/CD pipeline integration
- Pre-commit hook validation
- Batch skill processing
- Custom quality thresholds
- Automated quality reports
