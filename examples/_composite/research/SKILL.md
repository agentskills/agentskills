---
name: research
description: >
  Research a topic using web search, source verification, and synthesis.
  Composes web-search and web-fetch to gather information, then synthesises
  findings with source attribution. Handles conflicting sources by citing all.

  Use when: User asks to research a topic, find information, or answer
  factual questions that require current data beyond training cutoff.

level: 2
operation: READ
composes:
  - web-search
  - web-fetch

# Version tracking for safe evolution
version: 1.3.0
version_history:
  - version: 1.0.0
    released_at: "2025-01-15"
    changes:
      - change_type: feature
        description: Initial release with basic web search and synthesis

  - version: 1.1.0
    released_at: "2025-06-01"
    changes:
      - change_type: feature
        description: Add source attribution to all findings
        lesson_id: L-research-001

  - version: 1.2.0
    released_at: "2025-09-15"
    changes:
      - change_type: feature
        description: Add source_conflicts output for transparency
        lesson_id: L-research-002

  - version: 1.3.0
    released_at: "2025-12-22"
    changes:
      - change_type: feature
        description: Add data_freshness indicator with publication dates
        lesson_id: L-research-003

# Version constraints for dependencies
requires:
  - skill_name: web-search
    constraint: ">=1.0.0"
  - skill_name: web-fetch
    constraint: "^1.0.0"

# Type-checked inputs and outputs
inputs:
  - name: query
    type: string
    required: true
    description: The research question or topic to investigate

  - name: max_sources
    type: integer
    required: false
    description: Maximum number of sources to consult (default 5)

  - name: prefer_primary
    type: boolean
    required: false
    description: Prefer primary sources over aggregators when available

outputs:
  - name: findings
    type: string
    required: true
    description: Synthesised findings with inline citations
    requires_rationale: true

  - name: sources
    type: Source[]
    required: true
    description: List of sources consulted with URLs and titles

  - name: source_conflicts
    type: SourceConflict[]
    required: false
    description: Any conflicting claims between sources (added in v1.2.0)

  - name: data_freshness
    type: DataFreshness
    required: false
    description: Indicator of how recent the data is (added in v1.3.0)

  - name: confidence
    type: number
    required: true
    description: Confidence score 0.0-1.0 based on source quality and agreement

# Lessons learned from execution - the heart of continuous improvement
lessons:
  # APPLIED: This lesson has been crystallised into the skill (v1.1.0)
  - id: L-research-001
    context: "WHEN presenting findings without attribution"
    learned: "Always include inline citations linking claims to specific sources"
    confidence: 0.98
    status: applied
    source: "User feedback: 'Where did you get this information?'"
    proposed_edit: "Add source attribution requirement to findings output"
    validated_at: "2025-05-15"
    applied_at: "2025-06-01"

  # APPLIED: This lesson has been crystallised into the skill (v1.2.0)
  - id: L-research-002
    context: "WHEN sources conflict on factual claims"
    learned: "Always cite ALL conflicting sources, never pick one silently"
    confidence: 0.95
    status: applied
    source: "User correction after conflicting data was presented as fact"
    proposed_edit: |
      Add source_conflicts output field:
      - name: source_conflicts
        type: SourceConflict[]
        description: "Any conflicting claims between sources"
    validated_at: "2025-08-20"
    applied_at: "2025-09-15"

  # APPLIED: This lesson has been crystallised into the skill (v1.3.0)
  - id: L-research-003
    context: "WHEN dealing with time-sensitive information"
    learned: "Always check and report publication dates, flag outdated sources"
    confidence: 0.92
    status: applied
    source: "Served outdated COVID statistics from 2021 article"
    proposed_edit: "Add data_freshness output with publication date analysis"
    validated_at: "2025-11-10"
    applied_at: "2025-12-22"

  # VALIDATED: Ready for human approval in next version
  - id: L-research-004
    context: "WHEN primary sources are unavailable or paywalled"
    learned: "Explicitly note the limitation and suggest alternatives"
    confidence: 0.90
    status: validated
    source: "User asked about academic paper but only abstracts were accessible"
    proposed_edit: |
      Add source_limitations output field:
      - name: source_limitations
        type: string[]
        description: "Any limitations in source access (paywalls, regions, etc.)"
    validated_at: "2025-12-20"

  # PROPOSED: Accumulating evidence, needs more validation
  - id: L-research-005
    context: "WHEN query is ambiguous or could mean multiple things"
    learned: "Ask clarifying question before researching, or research all interpretations"
    confidence: 0.75
    status: proposed
    source: "Researched wrong 'Python' (snake vs language)"

  # OBSERVED: Pattern noticed, needs more instances to strengthen
  - id: L-research-006
    context: "WHEN sources are from known biased outlets"
    learned: "Flag potential bias and seek balancing viewpoints"
    confidence: 0.55
    status: observed
    source: "Political topic research cited only one-sided sources"

  # DEPRECATED: No longer applicable after v1.2.0 changes
  - id: L-research-007
    context: "WHEN only one source is found"
    learned: "Warn user about single-source limitation"
    confidence: 0.80
    status: deprecated
    source: "This is now handled by confidence score calculation"
---

# Research Skill

A composite skill that performs comprehensive research by combining web search, source fetching, and intelligent synthesis.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RESEARCH WORKFLOW                            │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │  Query   │───►│  Search  │───►│  Fetch   │───►│Synthesise│      │
│  │  Input   │    │   Web    │    │ Sources  │    │ Findings │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│                       │               │               │              │
│                       ▼               ▼               ▼              │
│                  [web-search]    [web-fetch]    [attribution]       │
│                                                 [conflicts]         │
│                                                 [freshness]         │
└─────────────────────────────────────────────────────────────────────┘
```

## Evolution Through Lessons

This skill demonstrates the full lessons lifecycle:

| Version | Lesson Applied | What Changed |
|---------|----------------|--------------|
| 1.0.0 | - | Initial release |
| 1.1.0 | L-research-001 | Added source attribution |
| 1.2.0 | L-research-002 | Added conflict detection |
| 1.3.0 | L-research-003 | Added data freshness |
| 1.4.0? | L-research-004 | (pending) Source limitations |

## Lesson Status Summary

```
Applied (3):    L-research-001, L-research-002, L-research-003
Validated (1):  L-research-004 (ready for next version)
Proposed (1):   L-research-005 (needs more validation)
Observed (1):   L-research-006 (early pattern)
Deprecated (1): L-research-007 (superseded)
```

## Usage Example

**Input:**
```yaml
query: "What are the current interest rates in the UK?"
max_sources: 5
prefer_primary: true
```

**Output:**
```yaml
findings: |
  As of December 2025, the Bank of England base rate is 4.75% [1].
  This represents a decrease from the peak of 5.25% in August 2023 [2].
  Some analysts predict further cuts in early 2025 [3].

sources:
  - url: "https://bankofengland.co.uk/monetary-policy"
    title: "Bank of England - Monetary Policy"
    accessed_at: "2025-12-22"
  - url: "https://ft.com/interest-rates"
    title: "Financial Times - UK Interest Rate History"
    accessed_at: "2025-12-22"
  # ... more sources

source_conflicts:
  - claim: "Predicted rate for Q1 2025"
    positions:
      - source: "[3]"
        position: "4.5%"
      - source: "[4]"
        position: "4.25%"
    note: "Analyst predictions vary"

data_freshness:
  oldest_source: "2025-12-15"
  newest_source: "2025-12-22"
  freshness_score: 0.95
  warning: null

confidence: 0.92
```

## Version Compatibility

Consumers of this skill should declare version requirements:

```yaml
# In your skill that uses research:
composes:
  - research
requires:
  - skill_name: research
    constraint: "^1.2.0"  # Needs conflict detection
```

This ensures you get at least v1.2.0 features but accept compatible updates.

## Pending Improvements

**L-research-004** (validated, ready for v1.4.0):
- Add `source_limitations` output for paywalls, region locks, etc.
- Awaiting human approval via `skill-evolver`

**L-research-005** (proposed, confidence 0.75):
- Handle ambiguous queries better
- Needs more validation instances to reach 0.8 threshold
