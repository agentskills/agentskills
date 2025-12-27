---
name: email-reply
description: Reply to an email thread with context awareness. Reads the thread history, understands the conversation, and composes an appropriate reply. Use when responding to emails that require context.
level: 2
operation: WRITE
license: Apache-2.0
composes:
  - email-read
  - email-send
---

# Email Reply

Reply to an email thread with full conversation context.

## When to Use

Use this skill when:
- Responding to an ongoing email thread
- User wants to reply with awareness of previous messages
- Drafting responses that reference earlier conversation
- Following up on action items mentioned in thread

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thread_id` | string | Yes | Email thread/conversation ID |
| `reply_content` | string | Yes | The reply message content |
| `reply_all` | boolean | No | Reply to all recipients (default: false) |
| `include_attachments` | string[] | No | File paths to attach |
| `quote_original` | boolean | No | Include quoted original (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `message_id` | string | Sent message ID |
| `thread_id` | string | Thread ID |
| `recipients` | string[] | Who received the reply |
| `thread_summary` | string | Brief summary of thread context |

## Usage

```
Reply to email thread "abc123" saying "Thanks for the update. I'll review the proposal and get back to you by Friday."
```

```
Reply all to thread "xyz789" with "The fix has been deployed. Please verify on your end."
```

## Example Response

```json
{
  "message_id": "msg_456def",
  "thread_id": "abc123",
  "recipients": ["bob@example.com"],
  "thread_summary": "Discussion about Q4 proposal review timeline (3 messages, started 2 days ago)"
}
```

## Why Level 2

This skill composes multiple operations:
1. `email-read` - Fetches thread history for context
2. Analysis - Understands conversation flow and participants
3. `email-send` - Sends the reply with proper threading headers

A simple `email-send` (Level 1) doesn't understand thread context. This skill adds the intelligence of reading before writing.

## Composition Pattern

```
email-reply
    │
    ├── email-read (thread history)
    │       │
    │       ▼
    │   [Understand context]
    │       │
    │       ▼
    └── email-send (threaded reply)
```

## Notes

- Thread ID format varies by email provider
- Reply-all respects original CC recipients
- Consider using for any reply that needs historical context
- Inspired by n8n's Gmail Reply operation (which reads thread + sends)
