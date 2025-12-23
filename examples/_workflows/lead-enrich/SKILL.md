---
name: lead-enrich
description: |
  Enrich a new lead or contact with company data, news, social profiles,
  and relationship signals. Updates CRM and notifies sales rep with
  talking points and lead score.
level: 3
operation: WRITE
license: Apache-2.0
composes:
  - crm-contact-read
  - crm-contact-update
  - company-lookup
  - news-search
  - linkedin-profile-read
  - web-search
  - slack-message-send
tool_discovery:
  crm:
    prefer: [hubspot-contact-read, salesforce-contact-read, pipedrive-contact-read]
    fallback: notion-database-query
  enrichment:
    prefer: [clearbit-enrich, apollo-enrich, linkedin-profile-read]
    fallback: web-search
  notification:
    prefer: [slack-message-send, email-send]
---

# Lead Enrich

Automatically enrich new leads with comprehensive business intelligence.

## Trigger Phrases

- "Enrich lead [email or name]"
- "What do we know about [company]?"
- "Prepare for call with [prospect]"
- Auto-trigger: New lead in CRM webhook

## Workflow Steps

```
1. IDENTIFY: Parse lead identifier
       │
       ├── Email → Domain extraction
       ├── Name + Company → Lookup
       └── Company only → Find contacts
       │
       ▼
2. FETCH EXISTING: Check CRM for current data
       │
       │ Avoid duplicate enrichment
       │
       ▼
3. ENRICH: Gather data from multiple sources
       │
       ├── Company data (Clearbit, Crunchbase)
       │   • Industry, size, funding, tech stack
       │
       ├── Person data (LinkedIn, Apollo)
       │   • Role, tenure, background
       │
       ├── News (recent mentions)
       │   • Funding, product launches, hiring
       │
       └── Signals (intent indicators)
           • Job postings, tech changes, growth
       │
       ▼
4. SCORE: Calculate lead quality
       │
       ├── Fit score (ICP match)
       ├── Intent signals
       ├── Timing indicators
       └── Relationship proximity
       │
       ▼
5. GENERATE: Create talking points
       │
       ├── Personalisation hooks
       ├── Pain points (inferred)
       ├── Mutual connections
       └── Recent triggers
       │
       ▼
6. UPDATE: Write enriched data to CRM
       │
       ▼
7. NOTIFY: Alert sales rep
       │
       │ Slack with summary + talking points
       │
       ▼
8. RETURN: Enrichment summary
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifier` | string | Yes | Email, name, or company to enrich |
| `crm_id` | string | No | Existing CRM record ID |
| `assigned_rep` | string | No | Sales rep to notify (Slack handle) |
| `notify` | boolean | No | Send Slack notification (default: true) |
| `update_crm` | boolean | No | Update CRM record (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `lead` | object | Enriched lead data |
| `company` | object | Company information |
| `score` | object | Lead scoring breakdown |
| `talking_points` | string[] | Personalised conversation starters |
| `signals` | object[] | Intent and timing signals |
| `crm_updated` | boolean | Whether CRM was updated |
| `notification_sent` | boolean | Whether rep was notified |

## Usage

```
Enrich lead sarah.chen@acme.com and notify @john in sales
```

```
What do we know about Stripe before my call tomorrow?
```

```
Prepare for my meeting with the VP of Engineering at Notion
```

## Example Response

```json
{
  "lead": {
    "name": "Sarah Chen",
    "email": "sarah.chen@acme.com",
    "title": "VP Engineering",
    "linkedin": "https://linkedin.com/in/sarahchen",
    "tenure": "2 years",
    "previous": ["Google", "Dropbox"]
  },
  "company": {
    "name": "Acme Corp",
    "domain": "acme.com",
    "industry": "Developer Tools",
    "size": "200-500",
    "funding": "$50M Series B",
    "tech_stack": ["Python", "AWS", "PostgreSQL"],
    "growth_signals": "Hiring 15 engineers"
  },
  "score": {
    "overall": 85,
    "fit": 90,
    "intent": 75,
    "timing": 85,
    "breakdown": "Strong ICP fit, recent funding, actively hiring"
  },
  "talking_points": [
    "Congrats on the Series B - scaling the eng team?",
    "Saw you're hiring Python devs - how's the developer experience?",
    "Your background at Google - any lessons on scaling?"
  ],
  "signals": [
    {
      "type": "funding",
      "detail": "Series B announced 2 weeks ago",
      "implication": "Budget unlocked, scaling mode"
    },
    {
      "type": "hiring",
      "detail": "15 open engineering roles",
      "implication": "Growing team, potential pain points"
    }
  ],
  "crm_updated": true,
  "notification_sent": true
}
```

## Enrichment Sources

| Data Type | Primary Source | Fallback |
|-----------|---------------|----------|
| Company info | Clearbit, Crunchbase | Web search |
| Person info | LinkedIn, Apollo | Web search |
| Tech stack | BuiltWith, Wappalyzer | Job postings |
| News | News API, Google News | Web search |
| Funding | Crunchbase, PitchBook | News search |

## Why Level 3

This workflow demonstrates:
1. **Multi-source enrichment**: Company + person + news + signals
2. **Lead scoring**: Algorithmic quality assessment
3. **CRM integration**: Reads and writes to sales systems
4. **Notification routing**: Alerts the right person
5. **Personalisation**: Generates contextual talking points
6. **Webhook trigger**: Can run automatically on new leads

## Composition Graph

```
lead-enrich (L3)
    │
    ├─── crm-contact-read (L1) ───► Existing data
    │
    ├─┬─ [Parallel Enrichment]
    │ │
    │ ├── company-lookup (L1) ────► Firmographics
    │ ├── linkedin-profile-read (L1) ► Person data
    │ ├── news-search (L1) ───────► Recent news
    │ └── web-search (L1) ────────► Additional signals
    │
    ├──► [Score & Analyse]
    │     • ICP fit scoring
    │     • Intent signal detection
    │     • Talking point generation
    │
    ├─── crm-contact-update (L1) ─► Update record
    │
    └─── slack-message-send (L1) ─► Notify rep
```

## Notes

- Respects rate limits on enrichment APIs
- Caches enrichment to avoid duplicate API calls
- LinkedIn data requires proper authentication
- Lead scoring weights are configurable
- Can be triggered via CRM webhook for automation
