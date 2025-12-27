---
name: research-brief
description: |
  Conduct comprehensive research on a topic, company, or person. Aggregates
  from web, news, academic sources, and social media. Produces a structured
  brief with citations and archived sources.
level: 3
operation: READ
license: Apache-2.0
composes:
  - web-search
  - news-search
  - academic-search
  - social-search
  - pdf-save
  - document-create
  - deep-research
---

# Research Brief

Comprehensive multi-source research with structured deliverable.

## Trigger Phrases

- "Research [topic] and prepare a brief"
- "What do I need to know about [company]?"
- "Deep dive on [person] before our meeting"
- "Competitive analysis of [competitor]"

## Workflow Steps

```
1. PARSE REQUEST: Identify research subject and type
       │
       ├── Topic research (concepts, trends)
       ├── Company research (business intel)
       ├── Person research (background, work)
       └── Competitive analysis (comparison)
       │
       ▼
2. SEARCH: Query multiple sources in parallel
       │
       ├── Web search (general, 3-5 queries)
       ├── News search (recent developments)
       ├── Academic (if technical topic)
       ├── Social media (Twitter, LinkedIn)
       └── Company sources (Crunchbase, LinkedIn)
       │
       ▼
3. DEEP DIVE: Follow promising leads (recursive)
       │
       │ Uses deep-research for citation chains
       │ Depth limited to prevent runaway
       │
       ▼
4. SYNTHESISE: Structure findings
       │
       ├── Executive summary
       ├── Key facts (verified)
       ├── Recent developments
       ├── Risks / concerns
       ├── Opportunities
       └── Open questions
       │
       ▼
5. ARCHIVE: Save important sources
       │
       │ PDF snapshots of key pages
       │
       ▼
6. DELIVER: Create structured document
       │
       │ Google Docs, Notion, or Markdown
       │
       ▼
7. RETURN: Brief + source citations
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | string | Yes | Research subject (topic, company, person) |
| `type` | string | No | Research type: topic, company, person, competitive |
| `depth` | string | No | Research depth: quick, standard, thorough (default: standard) |
| `focus_areas` | string[] | No | Specific aspects to focus on |
| `time_range` | string | No | News recency: week, month, year, all (default: month) |
| `output_format` | string | No | Output: notion, gdoc, markdown (default: markdown) |
| `archive_sources` | boolean | No | Save PDFs of sources (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Executive summary (3-5 sentences) |
| `key_facts` | object[] | Verified facts with citations |
| `recent_news` | object[] | Recent developments |
| `analysis` | object | Risks, opportunities, insights |
| `sources` | object[] | All sources with URLs and archive links |
| `document_url` | string | Link to full research document |
| `confidence` | object | Confidence levels by section |

## Usage

```
Research Anthropic and prepare a brief before my interview
```

```
Deep dive on quantum computing trends, focus on enterprise applications
```

```
Competitive analysis of Notion vs Obsidian vs Roam
```

```
What do I need to know about Sarah Chen before our meeting tomorrow?
```

## Example Response

```json
{
  "summary": "Anthropic is an AI safety company founded in 2021 by former OpenAI researchers. They've raised $7.3B and are known for Claude, their flagship AI assistant. Strong focus on constitutional AI and interpretability research. Recently partnered with Amazon and Google.",
  "key_facts": [
    {
      "fact": "Founded in 2021 by Dario and Daniela Amodei",
      "source": "https://www.anthropic.com/company",
      "confidence": "high"
    },
    {
      "fact": "Total funding: $7.3 billion",
      "source": "https://www.crunchbase.com/organization/anthropic",
      "confidence": "high"
    }
  ],
  "recent_news": [
    {
      "headline": "Anthropic launches Claude 3.5 Sonnet",
      "date": "2024-10-22",
      "source": "TechCrunch",
      "url": "https://techcrunch.com/..."
    }
  ],
  "analysis": {
    "strengths": ["AI safety leadership", "Strong funding", "Enterprise focus"],
    "risks": ["Competitive market", "Regulatory uncertainty"],
    "opportunities": ["Enterprise AI adoption", "Safety-first positioning"]
  },
  "sources": [
    {
      "title": "Anthropic Company Page",
      "url": "https://www.anthropic.com/company",
      "archived": "/archives/anthropic-about-2024-12-23.pdf"
    }
  ],
  "document_url": "https://docs.google.com/document/d/abc123",
  "confidence": {
    "facts": "high",
    "analysis": "medium",
    "predictions": "low"
  }
}
```

## Research Depth Levels

| Level | Sources | Time | Use Case |
|-------|---------|------|----------|
| **quick** | Web + news | 2-3 min | Pre-meeting context |
| **standard** | + social + academic | 5-10 min | Decision support |
| **thorough** | + deep-research recursion | 15-30 min | Strategic analysis |

## Why Level 3

This workflow demonstrates:
1. **Multi-source parallel search**: 5+ source types simultaneously
2. **Recursive depth**: Uses `deep-research` for citation chains
3. **Source verification**: Cross-references facts across sources
4. **Confidence scoring**: Acknowledges uncertainty
5. **Archival**: Preserves sources for future reference
6. **Structured output**: Consistent deliverable format

## Composition Graph

```
research-brief (L3)
    │
    ├─┬─ [Parallel Search]
    │ │
    │ ├── web-search (L1) ─────► General findings
    │ ├── news-search (L1) ────► Recent developments
    │ ├── academic-search (L1) ► Papers, research
    │ └── social-search (L1) ──► Twitter, LinkedIn
    │
    ├─── deep-research (L2) ───► Follow citations
    │         │
    │         └── [Recursive: web-search → pdf-save]
    │
    ├──► [Synthesise & Verify]
    │     • Cross-reference facts
    │     • Assign confidence
    │     • Structure findings
    │
    ├─── pdf-save (L1) ────────► Archive sources
    │
    └─── document-create (L1) ─► Create deliverable
```

## Notes

- Person research respects privacy (public info only)
- Academic search uses Semantic Scholar, arXiv, Google Scholar
- Company research includes Crunchbase, LinkedIn, news
- Sources older than time_range are noted but included if highly relevant
- Confidence scoring helps user assess reliability
