---
name: meeting-followup
description: |
  Prepare post-meeting follow-up by fetching transcript, analysing context,
  and drafting a personalised email. Automatically discovers user's configured
  tools for transcripts (Fireflies/Otter/Zoom) and email (Gmail/Outlook).
level: 3
operation: WRITE
license: Apache-2.0
composes:
  - transcript-fetch
  - contact-lookup
  - email-search
  - email-draft-create
tool_discovery:
  transcript_source:
    prefer: [fireflies-transcript-read, otter-transcript-read, zoom-transcript-read, teams-transcript-read]
    fallback: manual-notes-read
  email_provider:
    prefer: [gmail-draft-create, outlook-draft-create]
  contact_source:
    prefer: [hubspot-contact-read, salesforce-contact-read, notion-database-query]
    fallback: email-search
---

# Meeting Follow-up

Automatically prepare post-meeting follow-up emails with context awareness.

## Trigger Phrases

- "Prepare follow-up for my meeting with [person]"
- "Draft post-meeting email for [meeting name]"
- "Create follow-up from today's [client] call"

## Workflow Steps

```
1. IDENTIFY: Parse meeting/person from request
       │
       ▼
2. FETCH TRANSCRIPT: Use configured transcript source
       │ Fireflies → Otter → Zoom → Teams → Manual
       │
       ▼
3. EXTRACT: Pull key information from transcript
       │ • Action items and owners
       │ • Commitments made (by whom, by when)
       │ • Questions raised
       │ • Decisions made
       │
       ▼
4. ENRICH CONTEXT: Gather relationship history
       │ • CRM record (if available)
       │ • Past email threads
       │ • Previous meeting notes
       │
       ▼
5. SYNTHESISE: Combine transcript + context
       │ • Personalise based on relationship
       │ • Reference shared history
       │ • Prioritise action items
       │
       ▼
6. DRAFT: Create email in user's drafts
       │ Gmail or Outlook based on config
       │
       ▼
7. RETURN: Provide draft link + summary
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `meeting_identifier` | string | Yes | Meeting name, date, or attendee name |
| `recipient_email` | string | No | Override recipient (default: infer from meeting) |
| `tone` | string | No | Email tone: formal, friendly, brief (default: match history) |
| `include_action_items` | boolean | No | List action items explicitly (default: true) |
| `include_next_steps` | boolean | No | Propose next meeting/steps (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `draft_url` | string | Link to email draft |
| `draft_id` | string | Draft message ID |
| `recipient` | object | Recipient details |
| `action_items` | object[] | Extracted action items with owners |
| `commitments` | object[] | Commitments made with deadlines |
| `meeting_summary` | string | Brief meeting summary |
| `relationship_context` | string | Relevant history used |

## Usage

```
Prepare follow-up for my meeting with Sarah Chen from Acme Corp
```

```
Draft post-meeting email for the Q4 planning call, keep it brief
```

```
Create follow-up from today's investor call, formal tone
```

## Example Response

```json
{
  "draft_url": "https://mail.google.com/mail/u/0/#drafts/abc123",
  "draft_id": "abc123",
  "recipient": {
    "name": "Sarah Chen",
    "email": "sarah.chen@acme.com",
    "company": "Acme Corp",
    "role": "VP Engineering"
  },
  "action_items": [
    {
      "item": "Send API documentation",
      "owner": "me",
      "deadline": "2024-12-24"
    },
    {
      "item": "Review pricing proposal",
      "owner": "Sarah",
      "deadline": "2024-12-27"
    }
  ],
  "commitments": [
    {
      "by": "Sarah",
      "commitment": "Internal review by Friday",
      "deadline": "2024-12-27"
    }
  ],
  "meeting_summary": "Discussed integration timeline and pricing. Sarah will review proposal internally.",
  "relationship_context": "Third meeting this quarter. Previously discussed POC in October."
}
```

## Tool Discovery

This workflow automatically discovers which tools to use:

| Function | Discovery Order | Fallback |
|----------|-----------------|----------|
| Transcript | Fireflies → Otter → Zoom → Teams | Manual notes input |
| Email | Gmail → Outlook | Error: no email configured |
| CRM | HubSpot → Salesforce → Notion | Email history search |

The runtime checks user's connected integrations and selects the first available.

## Why Level 3

This workflow demonstrates:
1. **Multi-source aggregation**: Transcript + CRM + email history
2. **Tool discovery**: Adapts to user's configured integrations
3. **Intelligent extraction**: NLP for action items and commitments
4. **Personalisation**: Adapts tone based on relationship history
5. **Draft (not send)**: Human-in-the-loop for sensitive communications

## Composition Graph

```
meeting-followup (L3)
    │
    ├─┬─ transcript-fetch (L1)
    │ │   [Tool Discovery: Fireflies|Otter|Zoom|Teams]
    │ │
    │ └─► [Extract: action items, commitments, decisions]
    │
    ├─┬─ contact-lookup (L1)
    │ │   [Tool Discovery: HubSpot|Salesforce|Notion]
    │ │
    │ ├─ email-search (L1)
    │ │   [Past conversations with recipient]
    │ │
    │ └─► [Build relationship context]
    │
    ├──► [Synthesise: personalised follow-up]
    │
    └─── email-draft-create (L1)
          [Tool Discovery: Gmail|Outlook]
```

## Notes

- Creates draft only; never sends automatically
- Respects user's tone preferences from past emails
- Action items include inferred deadlines when mentioned
- Works best with structured meeting transcripts
- Falls back gracefully when tools unavailable
