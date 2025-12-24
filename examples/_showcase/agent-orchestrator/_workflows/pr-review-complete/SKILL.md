# pr-review-complete

End-to-end pull request review workflow with iterative feedback loop.

## Description

This workflow skill orchestrates the complete PR review lifecycle:

1. **Initial Review** - Analyse PR and provide comprehensive feedback
2. **Discussion** - Respond to author questions and clarifications
3. **Iteration** - Re-review after changes are made
4. **Resolution** - Track until all issues addressed
5. **Approval** - Give final approval when ready

Supports both reviewer and author perspectives:
- **As Reviewer**: Review, comment, track, approve
- **As Author**: Respond, improve, iterate, resolve

## Metadata

```yaml
domain: github
level: 3
type: workflow
version: 1.0.0
operation: WRITE
tags:
  - github
  - pull-request
  - code-review
  - workflow
  - collaboration
```

## Composes

- `pr-read` - Fetch PR metadata and status
- `pr-diff-read` - Get code changes
- `pr-review` - Perform comprehensive review
- `pr-respond` - Handle comment responses
- `pr-improve` - Make changes to address feedback
- `pr-comment-create` - Create comments
- `pr-review-submit` - Submit formal reviews

## Input Schema

```yaml
inputSchema:
  type: object
  required:
    - repo
    - pr_number
    - role
  properties:
    repo:
      type: string
      description: Repository in owner/repo format
    pr_number:
      type: integer
      description: Pull request number
    role:
      type: string
      enum: [reviewer, author]
      description: Your role in this PR
    review_config:
      type: object
      description: Configuration for review (when role=reviewer)
      properties:
        focus_areas:
          type: array
          items:
            type: string
          default: [security, correctness, performance]
        severity_threshold:
          type: string
          default: "medium"
        auto_approve_threshold:
          type: string
          enum: [none, low_only, medium_and_below]
          default: "none"
    author_config:
      type: object
      description: Configuration for author mode
      properties:
        auto_apply_suggestions:
          type: boolean
          default: true
        run_tests:
          type: boolean
          default: true
        notify_on_complete:
          type: boolean
          default: true
    iteration_limit:
      type: integer
      description: Maximum review iterations before escalating
      default: 3
    timeout_hours:
      type: integer
      description: Hours to wait for response before prompting
      default: 24
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - workflow_state
  properties:
    success:
      type: boolean
    workflow_state:
      type: string
      enum:
        - INITIAL_REVIEW
        - AWAITING_CHANGES
        - CHANGES_SUBMITTED
        - RE_REVIEWING
        - DISCUSSION
        - APPROVED
        - MERGED
        - CLOSED
        - STALLED
    iterations:
      type: array
      items:
        type: object
        properties:
          iteration_number:
            type: integer
          action:
            type: string
          timestamp:
            type: string
          issues_raised:
            type: integer
          issues_resolved:
            type: integer
          comments_exchanged:
            type: integer
    current_status:
      type: object
      properties:
        open_issues:
          type: integer
        resolved_issues:
          type: integer
        pending_responses:
          type: integer
        blocking_issues:
          type: array
          items:
            type: string
    final_review:
      type: object
      properties:
        decision:
          type: string
        summary:
          type: string
        html_url:
          type: string
```

## State Machine

```
                    ┌─────────────────────────────────────────┐
                    │           pr-review-complete            │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │           INITIAL_REVIEW                │
                    │  ┌─────────────────────────────────┐    │
                    │  │ pr-read → pr-diff-read →        │    │
                    │  │ pr-review                       │    │
                    │  └─────────────────────────────────┘    │
                    └─────────────────────────────────────────┘
                                      │
                     ┌────────────────┴────────────────┐
                     │                                 │
                     ▼                                 ▼
        ┌─────────────────────┐          ┌─────────────────────┐
        │ No issues found     │          │ Issues found        │
        │ → APPROVED          │          │ → AWAITING_CHANGES  │
        └─────────────────────┘          └─────────────────────┘
                     │                              │
                     │                              │
                     ▼                              ▼
        ┌─────────────────────┐          ┌─────────────────────┐
        │ pr-review-submit    │          │ Wait for author     │
        │ (APPROVE)           │          │ response/changes    │
        └─────────────────────┘          └─────────────────────┘
                     │                              │
                     │               ┌──────────────┴──────────────┐
                     │               │                             │
                     │               ▼                             ▼
                     │    ┌─────────────────────┐      ┌─────────────────────┐
                     │    │ Author responds     │      │ Author pushes       │
                     │    │ → DISCUSSION        │      │ → CHANGES_SUBMITTED │
                     │    └─────────────────────┘      └─────────────────────┘
                     │               │                             │
                     │               ▼                             │
                     │    ┌─────────────────────┐                  │
                     │    │ pr-respond          │                  │
                     │    │ (clarify/defend)    │                  │
                     │    └─────────────────────┘                  │
                     │               │                             │
                     │               └──────────────┬──────────────┘
                     │                              │
                     │                              ▼
                     │               ┌─────────────────────────────┐
                     │               │        RE_REVIEWING         │
                     │               │  ┌─────────────────────┐    │
                     │               │  │ pr-diff-read (new)  │    │
                     │               │  │ pr-review (delta)   │    │
                     │               │  └─────────────────────┘    │
                     │               └─────────────────────────────┘
                     │                              │
                     │               ┌──────────────┴──────────────┐
                     │               │                             │
                     │               ▼                             ▼
                     │    ┌─────────────────────┐      ┌─────────────────────┐
                     │    │ Issues remain       │      │ All resolved        │
                     │    │ → AWAITING_CHANGES  │      │ → APPROVED          │
                     │    │ (increment iter)    │      │                     │
                     │    └─────────────────────┘      └─────────────────────┘
                     │               │                             │
                     │               │ (iter > limit)              │
                     │               ▼                             │
                     │    ┌─────────────────────┐                  │
                     │    │ STALLED             │                  │
                     │    │ (escalate/close)    │                  │
                     │    └─────────────────────┘                  │
                     │                                             │
                     └─────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │              MERGED                      │
                    │  (PR merged after approval)              │
                    └─────────────────────────────────────────┘
```

## Author Mode Flow

When `role: author`, the workflow helps address feedback:

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHOR MODE FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. FETCH FEEDBACK                                              │
│     ├─ pr-read → Get all reviews and comments                   │
│     ├─ Filter to unresolved feedback                            │
│     └─ Prioritise by severity                                   │
│                                                                  │
│  2. FOR EACH FEEDBACK ITEM                                      │
│     ├─ If question → pr-respond (answer)                        │
│     ├─ If suggestion → pr-improve (apply)                       │
│     ├─ If concern → pr-respond (clarify) or pr-improve (fix)    │
│     └─ If nitpick → pr-improve (apply) or pr-respond (defer)    │
│                                                                  │
│  3. VERIFY CHANGES                                              │
│     ├─ Run tests                                                │
│     ├─ Run linter                                               │
│     └─ Check all feedback addressed                             │
│                                                                  │
│  4. COMMIT AND NOTIFY                                           │
│     ├─ Commit all changes                                       │
│     ├─ pr-comment-create → Notify reviewers                     │
│     └─ Request re-review                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Reviewer: Initial Review with Issues
```yaml
input:
  repo: "org/project"
  pr_number: 42
  role: "reviewer"
  review_config:
    focus_areas: [security, correctness]
    severity_threshold: "medium"

output:
  success: true
  workflow_state: "AWAITING_CHANGES"
  iterations:
    - iteration_number: 1
      action: "initial_review"
      timestamp: "2025-12-24T10:00:00Z"
      issues_raised: 3
      issues_resolved: 0
      comments_exchanged: 3
  current_status:
    open_issues: 3
    resolved_issues: 0
    pending_responses: 0
    blocking_issues:
      - "SQL injection in user_query (critical)"
      - "Missing input validation (high)"
  final_review:
    decision: "REQUEST_CHANGES"
    summary: |
      Found 3 issues requiring attention:
      - 1 critical (security)
      - 1 high
      - 1 medium

      Please address the security concerns before this can be merged.
    html_url: "https://github.com/org/project/pull/42#pullrequestreview-123"
```

### Author: Address Feedback
```yaml
input:
  repo: "org/project"
  pr_number: 42
  role: "author"
  author_config:
    auto_apply_suggestions: true
    run_tests: true
    notify_on_complete: true

output:
  success: true
  workflow_state: "CHANGES_SUBMITTED"
  iterations:
    - iteration_number: 1
      action: "address_feedback"
      timestamp: "2025-12-24T14:00:00Z"
      issues_raised: 0
      issues_resolved: 3
      comments_exchanged: 4
  current_status:
    open_issues: 0
    resolved_issues: 3
    pending_responses: 0
    blocking_issues: []
```

### Reviewer: Approve After Changes
```yaml
input:
  repo: "org/project"
  pr_number: 42
  role: "reviewer"
  review_config:
    focus_areas: [security, correctness]

output:
  success: true
  workflow_state: "APPROVED"
  iterations:
    - iteration_number: 1
      action: "initial_review"
      timestamp: "2025-12-24T10:00:00Z"
      issues_raised: 3
      issues_resolved: 0
    - iteration_number: 2
      action: "re_review"
      timestamp: "2025-12-24T15:00:00Z"
      issues_raised: 0
      issues_resolved: 3
  current_status:
    open_issues: 0
    resolved_issues: 3
    pending_responses: 0
    blocking_issues: []
  final_review:
    decision: "APPROVE"
    summary: |
      All previously raised issues have been addressed:

      ✅ SQL injection fixed with parameterised queries
      ✅ Input validation added
      ✅ Error handling improved

      Code looks good now. LGTM! 🎉
    html_url: "https://github.com/org/project/pull/42#pullrequestreview-456"
```

### Stalled PR After Multiple Iterations
```yaml
input:
  repo: "org/project"
  pr_number: 99
  role: "reviewer"
  iteration_limit: 3

output:
  success: true
  workflow_state: "STALLED"
  iterations:
    - iteration_number: 1
      action: "initial_review"
      issues_raised: 5
      issues_resolved: 0
    - iteration_number: 2
      action: "re_review"
      issues_raised: 2
      issues_resolved: 3
    - iteration_number: 3
      action: "re_review"
      issues_raised: 1
      issues_resolved: 1
    - iteration_number: 4
      action: "stalled"
      issues_raised: 0
      issues_resolved: 0
  current_status:
    open_issues: 2
    resolved_issues: 4
    pending_responses: 1
    blocking_issues:
      - "Architecture concern not addressed"
      - "Performance regression not resolved"
```

## Integration Points

### With CI/CD
```yaml
on_state_change:
  APPROVED:
    - trigger: "ci/deploy-preview"
    - notify: "slack#deployments"
  MERGED:
    - trigger: "ci/production-deploy"
    - update: "jira/mark-done"
```

### With Issue Tracking
```yaml
issue_integration:
  link_related_issues: true
  auto_close_on_merge: true
  update_labels: true
  notify_watchers: true
```

## Best Practices

1. **Be responsive**: Don't let PRs stall - respond within 24 hours
2. **Be clear**: Explain why changes are needed, not just what
3. **Be constructive**: Offer solutions, not just criticisms
4. **Be thorough**: Review completely before requesting changes
5. **Be efficient**: Batch feedback to avoid back-and-forth
6. **Be respectful**: Remember there's a person on the other end
7. **Be practical**: Distinguish blockers from nice-to-haves
