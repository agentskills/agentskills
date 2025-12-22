---
name: skill-evolver
description: >
  Proposes concrete edits to skill definitions based on validated lessons.
  This meta skill closes the feedback loop by transforming high-confidence
  lessons into actionable changes that require human approval before applying.

  Use when: A skill has accumulated lessons with confidence >= 0.9 and status
  "validated". The evolver analyses the lesson context, the current skill
  definition, and proposes minimal, targeted edits.

  The human-in-the-loop requirement ensures that:
  1. Changes are reviewed before crystallising into permanent definitions
  2. Unintended consequences are caught before they propagate
  3. Institutional knowledge is validated by human judgment
level: 3
operation: TRANSFORM
composes:
  - explain-execution
inputs:
  - name: skill_path
    type: string
    required: true
    description: Path to the skill directory to evolve
  - name: lesson_ids
    type: string[]
    required: false
    description: Specific lesson IDs to process (default: all ready_to_apply)
  - name: dry_run
    type: boolean
    required: false
    description: If true, only show proposed changes without generating edit
outputs:
  - name: proposed_edits
    type: ProposedEdit[]
    description: List of proposed edits with diffs and rationale
    requires_rationale: true
  - name: approval_prompt
    type: string
    description: Human-readable summary for approval decision
  - name: risk_assessment
    type: RiskAssessment
    description: Analysis of potential impact and reversibility
---

# Skill Evolver

**Purpose:** Transform validated lessons into concrete skill improvements, with human approval as a gate.

## The Feedback Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS IMPROVEMENT LOOP                       │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ Execute  │───►│ Observe  │───►│ Validate │───►│ Propose  │      │
│  │  Skill   │    │ Pattern  │    │ Lesson   │    │  Edit    │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│       ▲                                               │              │
│       │          ┌──────────┐    ┌──────────┐        │              │
│       └──────────│  Apply   │◄───│  Human   │◄───────┘              │
│                  │  Change  │    │ Approval │                       │
│                  └──────────┘    └──────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Why Human Approval?

The skill-evolver deliberately requires human approval because:

1. **Safety**: Automated changes to skill definitions could have cascading effects
2. **Context**: Humans can assess whether a lesson generalises or was situational
3. **Quality**: Not all validated patterns should become permanent constraints
4. **Trust**: Users retain control over how their skills evolve

## How It Works

### Phase 1: Lesson Analysis

For each lesson with `ready_to_apply == True`:
- Parse the `context` to understand WHEN the lesson applies
- Parse the `learned` to understand WHAT should change
- Check if `proposed_edit` already exists (from earlier runs)

### Phase 2: Edit Generation

If no `proposed_edit` exists, generate one:
- Analyse the current skill definition
- Identify the minimal change that implements the lesson
- Generate a diff-style proposal
- Assess risk (scope, reversibility, side effects)

### Phase 3: Approval Request

Present to human:
- The lesson context and what was learned
- The proposed edit as a diff
- Risk assessment and potential impact
- Clear approve/reject/modify options

### Phase 4: Application (if approved)

- Apply the edit to the skill file
- Update lesson status to "applied"
- Record `applied_at` timestamp
- Commit with message referencing lesson ID

## Example Flow

**Input Skill with Validated Lesson:**
```yaml
name: research
lessons:
  - id: L-research-001
    context: "WHEN sources conflict on factual claims"
    learned: "Always cite all conflicting sources, don't pick one"
    confidence: 0.95
    status: validated
    validated_at: "2025-12-15"
```

**Generated Proposal:**
```yaml
proposed_edit: |
  ## Diff for research/SKILL.md

  @@ outputs @@
  - name: findings
    type: string
  + requires_rationale: true
  +
  + - name: source_conflicts
  +   type: SourceConflict[]
  +   description: "Any conflicting claims between sources"

risk_assessment:
  scope: "Adds new output field"
  reversibility: "Easy - remove field if not useful"
  side_effects: "Downstream skills may need to handle new field"
  recommendation: "Low risk, improves transparency"
```

**Approval Prompt:**
```
LESSON L-research-001 is ready to apply:

Context: When sources conflict on factual claims
Learned: Always cite all conflicting sources, don't pick one
Confidence: 0.95 (validated 2025-12-15)

Proposed change:
  - Add 'source_conflicts' output field to capture disagreements
  - Add requires_rationale to findings for transparency

Risk: Low (additive change, easy to reverse)

[Approve] [Reject] [Modify]
```

## Benefits of This Approach

### 1. Institutional Memory
Lessons persist in the skill definition itself, not external docs. New team members or AI agents see the accumulated wisdom directly.

### 2. Minimal Edits
The evolver proposes the smallest change that implements the lesson. No unnecessary refactoring or "while we're at it" additions.

### 3. Traceable Evolution
Every skill change links to a lesson ID. Git history + lesson history = full audit trail.

### 4. Confidence-Gated
Only high-confidence, validated lessons are proposed. Weak signals stay as observations until they strengthen.

### 5. Reversible
Applied lessons remain in the skill file (with status: "applied"). If a change proves problematic, the lesson context explains why it was made and how to revert.

## Integration with Other Meta Skills

| Meta Skill | Relationship |
|------------|-------------|
| `explain-execution` | Provides execution traces that generate lessons |
| `intent-refiner` | Lessons can inform intent refinement preferences |
| `skill-synthesizer` | New skills can inherit lessons from composed skills |

## CLI Usage (Future)

```bash
# Show lessons ready to apply for a skill
agentskills evolve research --dry-run

# Propose edits for specific lessons
agentskills evolve research --lessons L-research-001,L-research-002

# Interactive approval mode
agentskills evolve research --interactive

# Auto-approve low-risk changes
agentskills evolve research --auto-approve-low-risk
```
