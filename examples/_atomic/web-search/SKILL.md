---
name: web-search
description: Search the web using AI-powered search. Returns synthesised answers with citations. Use when you need current information, research, or fact-checking.
level: 1
operation: READ
license: Apache-2.0
---

# Web Search

Search the web and get an AI-synthesised answer with source citations.

## When to Use

Use this skill when:
- User needs current information beyond your knowledge cutoff
- Researching a topic that requires multiple sources
- Fact-checking claims or verifying information
- Finding specific data (prices, dates, statistics)

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query |
| `focus` | string | No | Focus area: `web`, `academic`, `news` |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Synthesised response |
| `citations` | list | URLs of sources used |
| `images` | list | Relevant image URLs (if any) |

## Usage

```
Search the web for "Does Singapore Changi airport provide wheelchair assistance for connecting flights, does Singapore Airlines allow small dogs under 8kg in the cabin on long-haul flights, and what pet import documents and quarantine requirements apply when entering New Zealand with a dog"
```

This query demonstrates the power of web-search: synthesising answers from multiple domains (airport services, airline policies, immigration regulations) into a single coherent response with citations to official sources.

## Example Response

```json
{
  "answer": "Singapore Changi Airport provides complimentary wheelchair assistance for passengers with reduced mobility, including between terminals for connecting flights - request this when booking or at check-in. Singapore Airlines permits small dogs up to 6kg (including carrier) in the cabin on selected routes, but pets are not allowed on flights to/from Australia, New Zealand, or the UK due to destination country restrictions. New Zealand has strict biosecurity requirements: dogs must be imported from an approved country, have an import permit from MPI, complete rabies vaccination and titre testing at least 6 months prior, and spend a minimum 10 days in quarantine at the Auckland quarantine facility. Full documentation requirements are listed on the MPI website.",
  "citations": [
    "https://www.changiairport.com/en/airport-guide/facilities-and-services/wheelchair-services.html",
    "https://www.singaporeair.com/en_UK/us/travel-info/special-assistance/travelling-with-pets/",
    "https://www.mpi.govt.nz/bring-send-to-nz/pets-travelling-to-nz/bringing-cats-and-dogs-to-nz/"
  ]
}
```

## Why This Matters for Composition

As a Level 1 atomic skill, `web-search` provides the READ foundation that higher-level skills build upon:
- **research** (Level 2) uses web-search + pdf-save to archive the official sources
- **travel-planner** (Level 3) orchestrates multiple web-searches for flights, accommodation, and requirements

## Notes

- Results are synthesised from multiple sources
- Citations should be verified for accuracy
- For archival purposes, consider using `pdf-save` to preserve sources
