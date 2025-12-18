---
name: research
description: Research a topic comprehensively with web search and optional source archival. Use for in-depth investigation requiring multiple sources and verification.
level: 2
operation: READ
composes:
  - web-search
  - pdf-save
license: Apache-2.0
---

# Research

Comprehensive topic research combining web search with source verification and optional archival.

## Why This is a Composite Skill

This skill **composes** two atomic skills:

```
research (Level 2)
├── web-search (Level 1, READ)  → Get synthesised answer with citations
└── pdf-save (Level 1, WRITE)   → Archive sources (optional)
```

By composing atomic skills, we get:
- **Reusability**: Both `web-search` and `pdf-save` can be used independently
- **Testability**: Each component can be tested in isolation
- **Flexibility**: Archival step is optional based on `save_sources` parameter
- **Transparency**: Clear what this skill does by reading its composition

## When to Use

Use this skill when:
- Deep investigation of a topic is needed
- Multiple sources should be cross-referenced
- Sources need to be preserved for future reference
- User asks for "research" rather than a quick search

## Workflow

```
1. SEARCH
   └── Use web-search to get initial answer + citations

2. VERIFY (if depth >= standard)
   └── Fetch full content from top citations
   └── Cross-reference key claims

3. ARCHIVE (if save_sources = true)
   └── Use pdf-save for each citation
   └── Generate source index
```

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | The research question |
| `depth` | string | No | `standard` | `quick`, `standard`, or `thorough` |
| `save_sources` | boolean | No | `false` | Archive citations as PDFs |
| `output_dir` | string | No | `./sources` | Where to save PDFs |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Synthesised research findings |
| `sources` | list | Citations with key points extracted |
| `saved_pdfs` | list | Paths to archived PDFs (if save_sources) |
| `confidence` | string | How well-supported the findings are |

## Depth Levels

| Level | Behaviour |
|-------|-----------|
| `quick` | Single web-search, return synthesised answer |
| `standard` | Fetch top 3 citations, cross-reference claims |
| `thorough` | Fetch all citations, deep verification, comprehensive report |

## Usage Examples

### Quick Research
```
Research "what are the current GDPR requirements for AI training data in the EU"
```

### Thorough Research with Archival (Legal Case Preparation)

This example shows why composition matters - preparing evidence for legal proceedings requires both comprehensive research AND permanent archival of sources:

```
Research "case law on software patent infringement for machine learning algorithms in the Unified Patent Court, focusing on decisions from 2023-2024 regarding training data and model weights as patentable subject matter" with thorough depth and save sources to ./case-evidence/patent-precedents/
```

**What happens under the hood:**

```
research (Level 2)
│
├─→ web-search: Find relevant UPC decisions, legal commentary, and official court records
│   Returns: 12 citations including EPO guidelines, UPC case database, legal journals
│
├─→ [For each citation - thorough mode]
│   Fetch full content, extract key holdings and rationale
│   Cross-reference: Flag conflicting interpretations between jurisdictions
│
└─→ pdf-save: Archive each source with metadata
    Saves: 12 PDFs to ./case-evidence/patent-precedents/
    Each PDF includes: capture timestamp, original URL, evidence reference number
```

**Output:**
```json
{
  "summary": "The UPC has addressed ML patent eligibility in 3 key decisions...",
  "sources": [
    {
      "url": "https://www.unified-patent-court.org/en/decisions/2024-001",
      "key_points": ["Training data not patentable per se", "Model architecture may qualify"],
      "saved_pdf": "./case-evidence/patent-precedents/upc-2024-001.pdf"
    }
  ],
  "confidence": "high",
  "conflicts_flagged": ["German vs French interpretation of 'technical effect'"]
}
```

This demonstrates the power of composition: a single Level 2 skill coordinates web-search and pdf-save to produce court-admissible evidence with full provenance.

## Notes

- Operation is READ because pdf-save writes locally, not to external systems
- For research that creates Linear issues or sends notifications, use a Level 3 workflow
- Cross-referencing automatically flags conflicting information between sources
- Saved PDFs include metadata headers for evidence chain of custody
