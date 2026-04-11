"""Skill quality evaluation framework.

Evaluates Agent Skills for completeness, clarity, and structure.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from .models import SkillProperties
from .parser import read_properties


class Severity(str, Enum):
    """Severity level for evaluation findings."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class EvaluationFinding:
    """A single evaluation finding.

    Attributes:
        severity: Severity level (error, warning, info)
        category: Category of the finding (e.g., "completeness", "clarity")
        message: Human-readable description of the finding
        suggestion: Optional suggestion for improvement
    """

    severity: Severity
    category: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class EvaluationResult:
    """Result of evaluating a skill.

    Attributes:
        skill_path: Path to the skill directory
        skill_name: Name of the skill (if parseable)
        findings: List of evaluation findings
        scores: Numeric scores for different dimensions (0-100)
    """

    skill_path: Path
    skill_name: Optional[str] = None
    findings: list[EvaluationFinding] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level findings."""
        return any(f.severity == Severity.ERROR for f in self.findings)

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warning-level findings."""
        return any(f.severity == Severity.WARNING for f in self.findings)

    @property
    def overall_score(self) -> float:
        """Calculate overall quality score (average of dimension scores)."""
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)


class SkillEvaluator:
    """Evaluates Agent Skills for quality metrics."""

    def __init__(self):
        """Initialize the evaluator."""
        self.min_description_length = 20
        self.max_description_length = 500
        self.min_content_length = 100
        self.recommended_sections = {
            "## Overview",
            "## When to Use",
            "## Usage",
            "## Examples",
        }

    def evaluate(self, skill_path: Path) -> EvaluationResult:
        """Evaluate a skill for quality.

        Args:
            skill_path: Path to the skill directory

        Returns:
            EvaluationResult with findings and scores
        """
        result = EvaluationResult(skill_path=skill_path)
        skill_file = skill_path / "SKILL.md"

        if not skill_file.exists():
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.ERROR,
                    category="completeness",
                    message="SKILL.md file not found",
                    suggestion="Create a SKILL.md file in the skill directory",
                )
            )
            self._calculate_scores(result)
            return result

        # Try to parse skill properties
        try:
            props = read_properties(skill_path)
            result.skill_name = props.name
            self._evaluate_properties(props, result)
        except Exception as e:
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.ERROR,
                    category="parsing",
                    message=f"Failed to parse skill properties: {e}",
                    suggestion="Ensure SKILL.md has valid YAML frontmatter",
                )
            )
            self._calculate_scores(result)
            return result

        # Evaluate content
        content = skill_file.read_text(encoding="utf-8")
        self._evaluate_content(content, result)

        # Calculate scores
        self._calculate_scores(result)

        return result

    def _evaluate_properties(
        self, props: SkillProperties, result: EvaluationResult
    ) -> None:
        """Evaluate skill properties from frontmatter."""
        # Check description length and clarity
        desc_len = len(props.description)
        if desc_len < self.min_description_length:
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.WARNING,
                    category="clarity",
                    message=f"Description is too short ({desc_len} chars)",
                    suggestion=f"Provide a description of at least {self.min_description_length} characters",
                )
            )
        elif desc_len > self.max_description_length:
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.WARNING,
                    category="clarity",
                    message=f"Description is too long ({desc_len} chars)",
                    suggestion=f"Keep description under {self.max_description_length} characters. Move details to the main content.",
                )
            )

        # Check for "when to use" indicators in description
        when_indicators = ["when", "use this", "use it", "for"]
        if not any(indicator in props.description.lower() for indicator in when_indicators):
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.INFO,
                    category="clarity",
                    message="Description doesn't clearly indicate when to use the skill",
                    suggestion="Include guidance on when the agent should invoke this skill",
                )
            )

        # Check for license
        if not props.license:
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.INFO,
                    category="completeness",
                    message="No license specified",
                    suggestion="Add a 'license' field to SKILL.md frontmatter",
                )
            )

    def _evaluate_content(self, content: str, result: EvaluationResult) -> None:
        """Evaluate skill content structure and quality."""
        # Remove frontmatter for content analysis
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]

        content = content.strip()

        # Check minimum content length
        if len(content) < self.min_content_length:
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.WARNING,
                    category="completeness",
                    message=f"Content is too short ({len(content)} chars)",
                    suggestion=f"Provide at least {self.min_content_length} characters of guidance",
                )
            )

        # Check for recommended sections
        missing_sections = []
        for section in self.recommended_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)

        if missing_sections:
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.INFO,
                    category="structure",
                    message=f"Missing recommended sections: {', '.join(missing_sections)}",
                    suggestion="Consider adding these sections for better clarity",
                )
            )

        # Check for examples
        if "```" not in content and "<example>" not in content.lower():
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.WARNING,
                    category="completeness",
                    message="No code examples or examples found",
                    suggestion="Add examples to demonstrate skill usage",
                )
            )

        # Check for actionable language
        action_verbs = ["should", "must", "always", "never", "use", "call", "invoke"]
        if not any(verb in content.lower() for verb in action_verbs):
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.INFO,
                    category="clarity",
                    message="Content may lack actionable guidance",
                    suggestion="Use clear directives (should, must, use) to guide the agent",
                )
            )

        # Check for tool references
        if "<tool>" in content.lower() or "tool" in content.lower():
            result.findings.append(
                EvaluationFinding(
                    severity=Severity.INFO,
                    category="completeness",
                    message="Skill references tools",
                    suggestion="Consider adding 'allowed-tools' to frontmatter if tools are required",
                )
            )

    def _calculate_scores(self, result: EvaluationResult) -> None:
        """Calculate quality scores based on findings."""
        # Start with perfect scores
        scores = {
            "completeness": 100.0,
            "clarity": 100.0,
            "structure": 100.0,
        }

        # Deduct points for findings
        for finding in result.findings:
            if finding.severity == Severity.ERROR:
                penalty = 30
            elif finding.severity == Severity.WARNING:
                penalty = 15
            else:  # INFO
                penalty = 5

            if finding.category in scores:
                scores[finding.category] = max(0, scores[finding.category] - penalty)

        result.scores = scores


def evaluate_skill(skill_path: Path) -> EvaluationResult:
    """Convenience function to evaluate a skill.

    Args:
        skill_path: Path to the skill directory

    Returns:
        EvaluationResult with findings and scores
    """
    evaluator = SkillEvaluator()
    return evaluator.evaluate(skill_path)
