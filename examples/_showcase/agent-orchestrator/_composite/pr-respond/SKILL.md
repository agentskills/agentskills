# pr-respond

Intelligently respond to comments and review feedback on a pull request.

## Description

This skill handles responding to PR feedback:
1. **Understand** - Analyse comment context and intent
2. **Research** - Look up relevant code and documentation
3. **Formulate** - Craft appropriate response
4. **Reply** - Post response in correct thread

Handles different response scenarios:
- Answering questions about code changes
- Acknowledging feedback and explaining next steps
- Defending design decisions with reasoning
- Accepting suggestions with thanks
- Asking clarifying questions

## Metadata

```yaml
domain: github
level: 2
type: composite
version: 1.0.0
operation: WRITE
tags:
  - github
  - pull-request
  - code-review
  - communication
  - comments
```

## Composes

- `pr-read` - Fetch PR context
- `pr-diff-read` - Get relevant code changes
- `pr-comment-create` - Post responses

## Input Schema

```yaml
inputSchema:
  type: object
  required:
    - repo
    - pr_number
  properties:
    repo:
      type: string
      description: Repository in owner/repo format
    pr_number:
      type: integer
      description: Pull request number
    comment_id:
      type: integer
      description: Specific comment to respond to (optional, responds to all pending if not specified)
    response_mode:
      type: string
      enum: [interactive, batch, selective]
      description: |
        - interactive: Respond to one comment at a time with confirmation
        - batch: Respond to all pending comments automatically
        - selective: Only respond to specified comment_id
      default: "batch"
    tone:
      type: string
      enum: [professional, friendly, technical, concise]
      description: Response tone
      default: "professional"
    auto_accept_suggestions:
      type: boolean
      description: Automatically accept valid code suggestions
      default: false
    context:
      type: object
      description: Additional context for responses
      properties:
        design_docs:
          type: string
        constraints:
          type: array
          items:
            type: string
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - responses
  properties:
    success:
      type: boolean
    responses:
      type: array
      items:
        type: object
        properties:
          original_comment_id:
            type: integer
          original_author:
            type: string
          original_body:
            type: string
          response_type:
            type: string
            enum:
              - acknowledgment
              - explanation
              - question
              - acceptance
              - defense
              - followup
          response_body:
            type: string
          response_id:
            type: integer
          suggestions_accepted:
            type: array
            items:
              type: string
    pending_comments:
      type: array
      description: Comments that couldn't be auto-responded to
      items:
        type: object
        properties:
          comment_id:
            type: integer
          reason:
            type: string
```

## Comment Classification

```yaml
comment_types:
  - type: "question"
    patterns:
      - "?"
      - "why did you"
      - "can you explain"
      - "what about"
      - "have you considered"
    response_strategy: "explanation"

  - type: "suggestion"
    patterns:
      - "```suggestion"
      - "consider using"
      - "you could"
      - "what if"
      - "maybe"
    response_strategy: "evaluation"

  - type: "concern"
    patterns:
      - "i'm worried"
      - "this might"
      - "be careful"
      - "potential issue"
    response_strategy: "address_concern"

  - type: "approval"
    patterns:
      - "lgtm"
      - "looks good"
      - "nice work"
      - ":+1:"
      - "👍"
    response_strategy: "thank"

  - type: "request"
    patterns:
      - "please add"
      - "could you"
      - "would you mind"
      - "need to"
    response_strategy: "commit_or_discuss"

  - type: "nitpick"
    patterns:
      - "nit:"
      - "minor:"
      - "optional:"
      - "just a thought"
    response_strategy: "acknowledge_optional"
```

## Response Templates

### Acknowledgment
```markdown
Thanks for the feedback! I'll address this in the next commit.
```

### Explanation
```markdown
Good question! I chose this approach because:

1. {reason_1}
2. {reason_2}

The alternative of {alternative} was considered but {why_not}.
```

### Accepting Suggestion
```markdown
Great suggestion! ✅ Applied in {commit_sha}.
```

### Defending Decision
```markdown
I understand the concern. Here's my reasoning:

{explanation}

The tradeoffs are:
- Pro: {benefits}
- Con: {drawbacks}

Happy to discuss further if you'd like to explore alternatives.
```

### Clarifying Question
```markdown
Could you clarify what you mean by {unclear_part}?

Are you suggesting we should:
1. {option_a}
2. {option_b}
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       pr-respond                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. FETCH CONTEXT                                               │
│     ├─ pr-read → Get PR metadata                                │
│     ├─ Get all comments and reviews                             │
│     └─ Build conversation threads                               │
│                                                                  │
│  2. IDENTIFY PENDING                                            │
│     ├─ Find comments from others (not PR author)                │
│     ├─ Filter to unanswered comments                            │
│     └─ Sort by priority (requests > questions > nitpicks)       │
│                                                                  │
│  3. FOR EACH COMMENT                                            │
│     ├─ Classify comment type                                    │
│     ├─ Get surrounding code context                             │
│     ├─ Determine response strategy                              │
│     └─ Generate appropriate response                            │
│                                                                  │
│  4. HANDLE SUGGESTIONS                                          │
│     ├─ If auto_accept_suggestions enabled                       │
│     │   ├─ Validate suggestion is applicable                    │
│     │   ├─ Apply via commit                                     │
│     │   └─ Reference commit in response                         │
│     └─ Else, acknowledge and note will review                   │
│                                                                  │
│  5. POST RESPONSES                                              │
│     ├─ pr-comment-create (type: reply)                          │
│     └─ Track response IDs                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Respond to Review Feedback
```yaml
input:
  repo: "org/project"
  pr_number: 42
  response_mode: "batch"
  tone: "professional"
  auto_accept_suggestions: true

output:
  success: true
  responses:
    - original_comment_id: 1001
      original_author: "senior-dev"
      original_body: "Why did you use a list here instead of a set?"
      response_type: "explanation"
      response_body: |
        Good question! I used a list because:

        1. We need to preserve insertion order for the output
        2. The collection is typically small (<100 items) so O(n) lookup isn't a concern
        3. We allow duplicates in certain edge cases

        If order preservation isn't required and we want to enforce uniqueness,
        I'm happy to switch to a set. Let me know your preference!
      response_id: 2001

    - original_comment_id: 1002
      original_author: "senior-dev"
      original_body: |
        ```suggestion
        return sorted(items, key=lambda x: x.priority)
        ```
      response_type: "acceptance"
      response_body: |
        Great suggestion! ✅ Applied in abc123.

        This is cleaner than the manual sort I had before.
      response_id: 2002
      suggestions_accepted:
        - "abc123"

    - original_comment_id: 1003
      original_author: "qa-engineer"
      original_body: "nit: Could add a docstring here"
      response_type: "acknowledgment"
      response_body: |
        Good point, I'll add documentation for this in the next commit.
      response_id: 2003
```

### Interactive Response to Concern
```yaml
input:
  repo: "org/project"
  pr_number: 42
  comment_id: 1004
  response_mode: "selective"
  tone: "technical"

output:
  success: true
  responses:
    - original_comment_id: 1004
      original_author: "security-team"
      original_body: "I'm worried about the security implications of storing this in plaintext"
      response_type: "defense"
      response_body: |
        Valid concern, let me clarify the security model:

        1. **What's stored**: Only the session token, not credentials
        2. **Where**: In-memory only, never persisted to disk
        3. **Lifetime**: Cleared on logout or after 15min timeout
        4. **Access**: Protected by process isolation

        The token itself is:
        - Short-lived (15 min server-side expiry)
        - Scoped to read-only operations
        - Revocable via the admin panel

        That said, if you'd prefer we encrypt the in-memory storage,
        I can add AES-256 encryption with a session-derived key.
        Would that address the concern?
      response_id: 2004
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| Comment deleted | Skip, note in pending_comments |
| Thread locked | Return error, cannot respond |
| Rate limited | Batch remaining responses |
| Complex question | Flag for manual response |
| Outdated context | Re-fetch before responding |
