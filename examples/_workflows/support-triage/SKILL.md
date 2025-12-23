---
name: support-triage
description: |
  Automatically triage incoming support tickets: classify urgency and category,
  search knowledge base for solutions, check customer history, and either
  draft a response or escalate to the right team.
level: 3
operation: WRITE
license: Apache-2.0
composes:
  - ticket-read
  - ticket-update
  - customer-lookup
  - kb-search
  - slack-message-send
  - email-draft-create
tool_discovery:
  ticketing:
    prefer: [zendesk-ticket-read, intercom-ticket-read, freshdesk-ticket-read]
    fallback: email-read
  knowledge_base:
    prefer: [zendesk-kb-search, notion-search, confluence-search]
    fallback: web-search
  crm:
    prefer: [hubspot-contact-read, salesforce-contact-read]
  escalation:
    prefer: [slack-message-send, pagerduty-alert]
---

# Support Triage

Intelligent ticket classification, routing, and response drafting.

## Trigger Phrases

- "Triage this support ticket"
- "Handle incoming ticket [ID]"
- "What's the best response for this customer issue?"
- Auto-trigger: New ticket webhook

## Workflow Steps

```
1. INGEST: Fetch ticket details
       │
       ├── Subject, body, attachments
       ├── Customer identifier
       └── Channel (email, chat, form)
       │
       ▼
2. CLASSIFY: Determine ticket attributes
       │
       ├── Category (bug, feature, billing, how-to)
       ├── Urgency (critical, high, medium, low)
       ├── Sentiment (frustrated, neutral, positive)
       ├── Complexity (simple, moderate, complex)
       └── Product area (if applicable)
       │
       ▼
3. ENRICH: Gather customer context
       │
       ├── Account tier (free, pro, enterprise)
       ├── Past tickets (patterns, history)
       ├── Account health (NPS, usage)
       └── Relationship (new, loyal, at-risk)
       │
       ▼
4. SEARCH: Find relevant solutions
       │
       ├── Knowledge base articles
       ├── Similar past tickets + resolutions
       ├── Known issues / bugs
       └── Internal documentation
       │
       ▼
5. DECIDE: Route based on classification
       │
       ├── [Simple + KB match] → Draft response
       ├── [Known issue] → Link to status + ETA
       ├── [Complex] → Escalate to specialist
       ├── [VIP + Critical] → Page on-call
       └── [Billing] → Route to billing team
       │
       ▼
6. ACT: Execute decision
       │
       ├── Draft response (for review)
       ├── Update ticket (tags, priority)
       ├── Escalate (Slack, PagerDuty)
       └── Assign to specialist
       │
       ▼
7. RETURN: Triage summary + actions taken
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | string | Yes | Ticket identifier |
| `auto_respond` | boolean | No | Auto-send low-risk responses (default: false) |
| `escalation_channel` | string | No | Slack channel for escalations |
| `vip_threshold` | string | No | Account tier requiring VIP handling |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `ticket` | object | Original ticket details |
| `classification` | object | Category, urgency, sentiment |
| `customer` | object | Customer context and history |
| `suggested_response` | string | Draft response (if applicable) |
| `kb_articles` | object[] | Relevant knowledge base articles |
| `actions_taken` | object[] | What the workflow did |
| `routing` | object | Where ticket was routed |

## Usage

```
Triage ticket #12345 from Zendesk
```

```
Handle the latest incoming ticket, escalate critical issues to #support-urgent
```

```
What's the best response for this billing question?
```

## Example Response

```json
{
  "ticket": {
    "id": "12345",
    "subject": "API returning 500 errors intermittently",
    "customer_email": "dev@acme.com",
    "created": "2024-12-23T10:30:00Z"
  },
  "classification": {
    "category": "bug",
    "urgency": "high",
    "sentiment": "frustrated",
    "complexity": "moderate",
    "product_area": "api",
    "confidence": 0.92
  },
  "customer": {
    "name": "Acme Corp",
    "tier": "enterprise",
    "account_health": "good",
    "past_tickets": 3,
    "relationship": "loyal",
    "mrr": "$5,000"
  },
  "suggested_response": "Hi,\n\nThank you for reporting this. I can see you're experiencing intermittent 500 errors on the API.\n\nWe've identified an issue affecting a subset of API requests and our engineering team is actively working on a fix. Current ETA is within the next 2 hours.\n\nI'll update this ticket as soon as the fix is deployed. In the meantime, implementing retry logic with exponential backoff should help mitigate the impact.\n\nStatus page: https://status.example.com/incident/123\n\nApologies for the disruption.",
  "kb_articles": [
    {
      "title": "API Error Handling Best Practices",
      "url": "https://docs.example.com/api-errors",
      "relevance": 0.85
    }
  ],
  "actions_taken": [
    {"action": "classified", "result": "bug/high/api"},
    {"action": "enriched", "result": "enterprise customer, good health"},
    {"action": "searched_kb", "result": "2 relevant articles"},
    {"action": "linked_incident", "result": "incident #123"},
    {"action": "drafted_response", "result": "ready for review"},
    {"action": "notified", "result": "#api-team via Slack"}
  ],
  "routing": {
    "team": "api-team",
    "escalated": true,
    "reason": "Enterprise customer + high urgency bug"
  }
}
```

## Classification Logic

| Signal | Weight | Example |
|--------|--------|---------|
| **Account tier** | High | Enterprise → higher urgency |
| **Keywords** | Medium | "down", "broken", "ASAP" → critical |
| **Sentiment** | Medium | Frustrated → prioritise |
| **Past history** | Low | Repeat issue → escalate |
| **Time of day** | Low | After hours → defer if low urgency |

## Routing Rules

| Condition | Action |
|-----------|--------|
| Simple + KB match | Draft response, assign to queue |
| Known incident | Link status, set expectations |
| Enterprise + Critical | Page on-call, notify account manager |
| Billing | Route to billing team |
| Feature request | Tag, add to backlog, acknowledge |
| Complex technical | Assign to specialist |

## Why Level 3

This workflow demonstrates:
1. **Multi-factor classification**: NLP + rules + context
2. **Customer enrichment**: Account tier affects routing
3. **Knowledge integration**: Searches multiple sources
4. **Decision tree**: Different paths based on classification
5. **Multi-action output**: Classify + draft + route + notify
6. **Human-in-the-loop**: Drafts for review, not auto-send

## Composition Graph

```
support-triage (L3)
    │
    ├─── ticket-read (L1) ────────► Fetch ticket
    │
    ├──► [Classify]
    │     • Category, urgency
    │     • Sentiment analysis
    │     • Complexity assessment
    │
    ├─── customer-lookup (L1) ───► Account context
    │    [Tool Discovery: HubSpot|Salesforce]
    │
    ├─── kb-search (L1) ─────────► Find solutions
    │    [Tool Discovery: Zendesk|Notion|Confluence]
    │
    ├──► [Decision Engine]
    │     • Route based on rules
    │     • Select response strategy
    │
    ├─┬─ [Actions - Based on Decision]
    │ │
    │ ├── email-draft-create (L1) ► Draft response
    │ ├── ticket-update (L1) ─────► Tags, priority
    │ ├── slack-message-send (L1) ► Escalate
    │ └── pagerduty-alert (L1) ──► Page on-call
    │
    └──► [Return summary]
```

## Notes

- Never auto-sends to customers by default (safety)
- Enterprise accounts always get human review
- Learns from corrections to improve classification
- Integrates with incident management for known issues
- Can batch process ticket queue
