# Why Composable Skills > MCP + Static Prompts

This document explains why the composable skills architecture provides significant advantages over the common pattern of MCP servers + static system prompts.

## The Problem with MCP + Static Prompts

### Current Approach

Most AI agent implementations follow this pattern:

```
┌─────────────────────────────────────────────┐
│              Static System Prompt            │
│  "You have access to these tools:            │
│   - gmail_send: Send emails                  │
│   - calendar_read: Read calendar             │
│   - slack_post: Post to Slack                │
│                                              │
│   When the user asks to schedule a meeting,  │
│   first check their calendar, then send      │
│   an email invitation, then post to Slack"   │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│              MCP Servers                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │  Gmail  │ │ Calendar│ │  Slack  │        │
│  │  Server │ │ Server  │ │  Server │        │
│  └─────────┘ └─────────┘ └─────────┘        │
└─────────────────────────────────────────────┘
```

### Problems with This Approach

#### 1. **Monolithic Prompts Don't Scale**

As capabilities grow, the system prompt becomes unwieldy:

```
❌ "When scheduling a meeting, check calendar, then...
    When following up after a meeting, fetch transcript from
    Fireflies OR Otter OR Zoom depending on what's configured,
    then look up the contact in HubSpot OR Salesforce OR Notion,
    then draft an email in Gmail OR Outlook, then..."
```

This creates:
- **Context bloat**: Prompt grows with every workflow
- **Conflicting instructions**: Edge cases create contradictions
- **Maintenance nightmare**: Changing one workflow requires editing giant prompt
- **No reusability**: Similar logic repeated across workflows

#### 2. **Tools Without Semantics**

MCP servers expose raw tool schemas:

```json
{
  "name": "gmail_send",
  "description": "Send an email via Gmail",
  "parameters": {
    "to": "string",
    "subject": "string",
    "body": "string"
  }
}
```

What's missing:
- **No operation classification**: Is this READ or WRITE? Safe or dangerous?
- **No composition rules**: How does this relate to other tools?
- **No discovery metadata**: When should this be used vs `outlook_send`?
- **No workflow context**: What typically comes before/after?

#### 3. **Fragile Tool Selection**

The LLM must figure out which tools to use from:
- Tool names and descriptions alone
- User's current request
- Whatever's in the system prompt

This leads to:
- Wrong tool selection (gmail vs outlook)
- Missing steps (forgot to check calendar)
- Inconsistent behavior across similar requests

#### 4. **No Graceful Degradation**

When a tool fails or isn't configured:

```
User: "Send a follow-up email after my meeting"
Agent: [Tries Fireflies] → 404 Not Found
       "I cannot access your meeting transcripts"
```

No fallback. No alternatives. Just failure.

---

## The Composable Skills Solution

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Skill Discovery                    │
│  "User wants post-meeting follow-up"                │
│   → Matches: meeting-followup (L3)                  │
│   → Composes: transcript-fetch, contact-lookup,     │
│               email-search, email-draft-create      │
└─────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│              Skill Definitions (SKILL.md)            │
│                                                      │
│  meeting-followup:                                   │
│    level: 3                                          │
│    operation: WRITE                                  │
│    composes: [transcript-fetch, contact-lookup...]   │
│    tool_discovery:                                   │
│      transcript: [fireflies, otter, zoom, teams]     │
│      email: [gmail, outlook]                         │
│      crm: [hubspot, salesforce, notion]              │
└─────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│              Tool Discovery Runtime                  │
│                                                      │
│  transcript_fetch:                                   │
│    → Check: Fireflies configured? ✓                  │
│    → Use: fireflies-transcript-read                  │
│                                                      │
│  email_draft:                                        │
│    → Check: Gmail configured? ✗                      │
│    → Check: Outlook configured? ✓                    │
│    → Use: outlook-draft-create                       │
└─────────────────────────────────────────────────────┘
```

---

## Advantage-by-Advantage Comparison

### 1. Composability vs Monolithic Instructions

| Aspect | MCP + Static Prompts | Composable Skills |
|--------|---------------------|-------------------|
| **Workflow definition** | Embedded in giant prompt | Discrete SKILL.md files |
| **Reusability** | Copy-paste between prompts | Import and compose |
| **Modification** | Edit prompt, test everything | Edit skill, composed skills inherit |
| **Understanding** | Read entire prompt | Read composition graph |

**Example: Adding email threading**

```
# MCP + Static Prompts
Edit the 5000-token prompt, find all email-related
instructions, add threading logic, hope nothing breaks

# Composable Skills
1. Update email-reply skill
2. All workflows composing email-reply automatically benefit
```

### 2. Tool Discovery vs Static Tool Lists

| Aspect | MCP + Static Prompts | Composable Skills |
|--------|---------------------|-------------------|
| **Tool selection** | LLM guesses from descriptions | Declared in skill metadata |
| **Alternatives** | Hardcoded or none | Preference ordering with fallbacks |
| **User config** | Manual prompt editing | Runtime discovery |
| **New integrations** | Update every prompt | Add to discovery list |

**Example: User switches from Gmail to Outlook**

```
# MCP + Static Prompts
1. User edits system prompt
2. Changes every "gmail" reference to "outlook"
3. Hopes they didn't miss any
4. Tests all workflows manually

# Composable Skills
1. User configures Outlook MCP server
2. Runtime discovers Outlook is available
3. tool_discovery automatically prefers Outlook
4. All email skills work immediately
```

### 3. Graceful Degradation vs Hard Failures

| Aspect | MCP + Static Prompts | Composable Skills |
|--------|---------------------|-------------------|
| **Missing tool** | Error, stop | Try fallback, continue |
| **Partial success** | Often unclear | Explicit fallback chain |
| **User experience** | "I can't do that" | "Using alternative: X" |

**Example: Fireflies not configured**

```
# MCP + Static Prompts
Agent: "Error: fireflies_read is not available.
        I cannot fetch meeting transcripts."

# Composable Skills
tool_discovery:
  transcript:
    prefer: [fireflies, otter, zoom, teams]
    fallback: manual-notes-read

Agent: "Fireflies not configured. Checking Otter...
        not configured. Checking Zoom... found!
        Fetching transcript from Zoom."
```

### 4. Semantic Operations vs Raw Tools

| Aspect | MCP + Static Prompts | Composable Skills |
|--------|---------------------|-------------------|
| **Safety classification** | None | READ/WRITE explicit |
| **Composition rules** | Implicit in prompt | Explicit in `composes` |
| **Validation** | Runtime errors | Build-time validation |
| **Documentation** | Tool descriptions only | Full workflow docs |

**Example: Preventing dangerous operations**

```yaml
# MCP + Static Prompts
# Nothing prevents LLM from calling gmail_delete
# or sending emails without confirmation

# Composable Skills
name: email-draft-create
operation: WRITE  # Requires confirmation
# vs
name: email-send
operation: WRITE  # Also requires confirmation,
                  # but skill docs say "draft first"
```

### 5. Hierarchical Composition vs Flat Tools

| Aspect | MCP + Static Prompts | Composable Skills |
|--------|---------------------|-------------------|
| **Abstraction levels** | All tools equal | L1 → L2 → L3 hierarchy |
| **Complexity hiding** | All details visible | Encapsulated in skills |
| **Testing** | Test whole system | Test each level |
| **Debugging** | Full trace needed | Follow composition graph |

**Example: Debugging meeting-followup**

```
# MCP + Static Prompts
- Check entire conversation
- Trace all 8 tool calls
- Figure out which failed
- No clear structure

# Composable Skills
meeting-followup (L3)
  ├── transcript-fetch (L1) ✓
  ├── contact-lookup (L1) ✓
  ├── email-search (L1) ✗ ← Problem here
  └── email-draft-create (L1) [not reached]
```

### 6. Testability

| Aspect | MCP + Static Prompts | Composable Skills |
|--------|---------------------|-------------------|
| **Unit testing** | Not possible | Each skill independently |
| **Integration testing** | Full system only | Composition chains |
| **Validation** | Manual review | Automated (skills-ref validate) |
| **CI/CD** | Prompt linting at best | Full test suites |

**Example: Testing email-reply**

```python
# MCP + Static Prompts
# No way to test "email reply" logic in isolation
# Must test entire agent with all tools

# Composable Skills
def test_email_reply_composes_correctly():
    skill = load_skill("email-reply")
    assert skill.level == 2
    assert "email-read" in skill.composes
    assert "email-send" in skill.composes
    assert skill.operation == "WRITE"
```

### 7. Evolution and Versioning

| Aspect | MCP + Static Prompts | Composable Skills |
|--------|---------------------|-------------------|
| **Versioning** | Prompt version control | Semantic versioning per skill |
| **Deprecation** | Edit prompt everywhere | Deprecate skill, provide migration |
| **Compatibility** | Unknown | Declared in `compatible_with` |
| **Rollback** | Restore old prompt | Restore old skill version |

**Example: Upgrading transcript-fetch**

```yaml
# Composable Skills
name: transcript-fetch
version: 2.0.0
compatible_with: [">=1.5.0"]
deprecated_in: 1.4.0
migration: "Use tool_discovery instead of hardcoded sources"
```

---

## Real-World Impact

### Before: Static Prompt Chaos

```markdown
# System Prompt (excerpt, 3000+ tokens)

You have access to these MCP tools:
- fireflies_get_transcript: Get meeting transcript from Fireflies
- otter_get_transcript: Get meeting transcript from Otter.ai
- zoom_get_recording: Get Zoom cloud recording
- hubspot_get_contact: Look up contact in HubSpot
- salesforce_get_contact: Look up contact in Salesforce
- gmail_send: Send email via Gmail
- gmail_create_draft: Create draft in Gmail
- outlook_send: Send email via Outlook
- outlook_create_draft: Create draft in Outlook
...

When the user asks to prepare a follow-up after a meeting:
1. First, try to get the transcript from Fireflies using fireflies_get_transcript
2. If Fireflies fails, try Otter using otter_get_transcript
3. If Otter fails, try Zoom using zoom_get_recording
4. Extract action items from the transcript
5. Look up the meeting attendees in HubSpot using hubspot_get_contact
6. If HubSpot fails, try Salesforce using salesforce_get_contact
7. Get past email history using gmail_search or outlook_search
8. Draft a follow-up email using gmail_create_draft or outlook_create_draft
   depending on which email service is available
9. Include action items and reference past conversations
...

When the user asks for a weekly summary:
[Another 500 tokens of similar instructions]

When the user asks to process an invoice:
[Another 800 tokens]
```

### After: Composable Skills

```yaml
# meeting-followup/SKILL.md
name: meeting-followup
level: 3
operation: WRITE
composes:
  - transcript-fetch
  - contact-lookup
  - email-search
  - email-draft-create
tool_discovery:
  transcript: [fireflies, otter, zoom, teams]
  email: [gmail, outlook]
  crm: [hubspot, salesforce, notion]
```

**System prompt becomes:**

```markdown
You have access to composable skills. When the user makes a request,
identify the most appropriate skill and execute it.

Available skills are discovered at runtime and documented in SKILL.md files.
```

---

## Summary: Key Advantages

| Dimension | MCP + Static Prompts | Composable Skills |
|-----------|---------------------|-------------------|
| **Scalability** | Prompt grows unboundedly | Skills compose cleanly |
| **Maintainability** | Single point of failure | Modular updates |
| **Reusability** | Copy-paste | True composition |
| **Testability** | System-level only | Unit + integration |
| **Flexibility** | Hardcoded tools | Runtime discovery |
| **Robustness** | Hard failures | Graceful degradation |
| **Semantics** | Implicit in prose | Explicit in schema |
| **Evolution** | Risky updates | Versioned skills |

The composable skills architecture transforms agent development from "prompt engineering" into proper software engineering, with all the benefits that implies: modularity, testing, versioning, and clean abstractions.
