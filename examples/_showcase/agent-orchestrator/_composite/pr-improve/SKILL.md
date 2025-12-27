# pr-improve

Make code changes to address review feedback and improve the pull request.

## Description

This skill implements changes based on PR feedback:
1. **Analyse** - Understand what changes are requested
2. **Plan** - Determine modifications needed
3. **Implement** - Make the code changes
4. **Verify** - Run tests and checks
5. **Commit** - Create commit addressing feedback
6. **Respond** - Update reviewers on changes made

Handles various improvement scenarios:
- Accepting code suggestions
- Fixing bugs identified in review
- Adding missing tests
- Improving documentation
- Refactoring for clarity
- Addressing security concerns

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
  - refactoring
  - implementation
```

## Composes

- `pr-read` - Fetch PR context and feedback
- `pr-diff-read` - Understand current changes
- `pr-comment-create` - Reply with update notifications

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
    feedback_source:
      type: string
      enum: [all, suggestions, comments, review]
      description: What feedback to address
      default: "all"
    specific_comments:
      type: array
      description: Specific comment IDs to address
      items:
        type: integer
    auto_apply_suggestions:
      type: boolean
      description: Automatically apply GitHub suggestions
      default: true
    run_tests:
      type: boolean
      description: Run tests after changes
      default: true
    run_linter:
      type: boolean
      description: Run linter after changes
      default: true
    commit_style:
      type: string
      enum: [single, per_issue, squash_ready]
      description: |
        - single: One commit for all changes
        - per_issue: Separate commit per issue addressed
        - squash_ready: Single well-formatted squash commit
      default: "single"
    notify_reviewers:
      type: boolean
      description: Comment to notify reviewers of changes
      default: true
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - changes_made
  properties:
    success:
      type: boolean
    changes_made:
      type: array
      items:
        type: object
        properties:
          feedback_id:
            type: integer
            description: Original comment ID addressed
          feedback_summary:
            type: string
          action_taken:
            type: string
            enum:
              - suggestion_applied
              - code_fixed
              - test_added
              - docs_added
              - refactored
              - configuration_changed
          files_modified:
            type: array
            items:
              type: string
          commit_sha:
            type: string
    commits_created:
      type: array
      items:
        type: object
        properties:
          sha:
            type: string
          message:
            type: string
    tests_result:
      type: object
      properties:
        passed:
          type: boolean
        summary:
          type: string
    notifications_sent:
      type: array
      items:
        type: object
        properties:
          comment_id:
            type: integer
          reviewer:
            type: string
    issues_not_addressed:
      type: array
      description: Feedback that couldn't be automatically addressed
      items:
        type: object
        properties:
          feedback_id:
            type: integer
          reason:
            type: string
```

## Improvement Strategies

### Apply GitHub Suggestions

```python
def apply_suggestion(suggestion_comment: dict, repo_path: str) -> dict:
    """
    Apply a GitHub suggestion block.

    GitHub suggestions have format:
    ```suggestion
    replacement code
    ```
    """
    path = suggestion_comment['path']
    start_line = suggestion_comment.get('start_line') or suggestion_comment['line']
    end_line = suggestion_comment['line']
    suggestion_code = extract_suggestion_block(suggestion_comment['body'])

    # Read file
    file_path = repo_path / path
    lines = file_path.read_text().splitlines()

    # Replace lines
    new_lines = (
        lines[:start_line - 1] +
        suggestion_code.splitlines() +
        lines[end_line:]
    )

    # Write back
    file_path.write_text('\n'.join(new_lines) + '\n')

    return {
        'path': path,
        'lines_replaced': (start_line, end_line),
        'new_content': suggestion_code
    }
```

### Address Common Feedback Types

```yaml
feedback_handlers:
  - type: "missing_error_handling"
    detection:
      - "needs error handling"
      - "what if this fails"
      - "add try/except"
    action: |
      Wrap identified code block in try/except with:
      - Specific exception types
      - Proper logging
      - Graceful fallback or re-raise

  - type: "missing_tests"
    detection:
      - "add tests"
      - "test coverage"
      - "untested"
    action: |
      Generate test file with:
      - Test for happy path
      - Edge case tests
      - Error condition tests

  - type: "missing_docs"
    detection:
      - "add docstring"
      - "needs documentation"
      - "unclear"
    action: |
      Add documentation:
      - Function docstrings
      - Parameter descriptions
      - Return value documentation
      - Usage examples

  - type: "security_fix"
    detection:
      - "security"
      - "vulnerability"
      - "injection"
      - "sanitize"
    action: |
      Apply security fix:
      - Input validation
      - Output encoding
      - Parameterised queries
      - Secrets management

  - type: "performance"
    detection:
      - "performance"
      - "slow"
      - "optimize"
      - "n+1"
    action: |
      Optimize code:
      - Batch operations
      - Caching
      - Algorithm improvement
      - Query optimization
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       pr-improve                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. GATHER FEEDBACK                                             │
│     ├─ pr-read → Get reviews and comments                       │
│     ├─ Filter by feedback_source                                │
│     └─ Prioritise: blockers > suggestions > nitpicks            │
│                                                                  │
│  2. CHECKOUT BRANCH                                             │
│     ├─ git fetch origin {pr_branch}                             │
│     ├─ git checkout {pr_branch}                                 │
│     └─ Ensure clean working directory                           │
│                                                                  │
│  3. FOR EACH FEEDBACK ITEM                                      │
│     ├─ Classify feedback type                                   │
│     ├─ Determine appropriate action                             │
│     ├─ Read affected file(s)                                    │
│     ├─ Make modification                                        │
│     └─ Track changes made                                       │
│                                                                  │
│  4. VERIFY CHANGES                                              │
│     ├─ Run linter (if run_linter)                               │
│     │   └─ Auto-fix if possible                                 │
│     ├─ Run tests (if run_tests)                                 │
│     │   └─ Report any failures                                  │
│     └─ Check for unintended changes                             │
│                                                                  │
│  5. COMMIT CHANGES                                              │
│     ├─ Stage modified files                                     │
│     ├─ Create commit(s) per commit_style                        │
│     │   ├─ single: "Address review feedback"                    │
│     │   ├─ per_issue: "Fix: {issue} (#{comment_id})"            │
│     │   └─ squash_ready: Well-formatted with all changes        │
│     └─ Push to PR branch                                        │
│                                                                  │
│  6. NOTIFY REVIEWERS                                            │
│     ├─ pr-comment-create replies to addressed comments          │
│     │   └─ "Addressed in {commit_sha}"                          │
│     └─ General update comment if multiple changes               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Commit Message Templates

### Single Commit
```
Address review feedback

Changes:
- Applied suggestion for improved error handling (r1234)
- Added missing unit tests (r1235)
- Updated docstrings per style guide (r1236)

Fixes feedback from: @reviewer1, @reviewer2
```

### Per-Issue Commits
```
fix(api): add error handling for network calls

Addresses review comment #1234 by @reviewer

- Wrap requests in try/except
- Add retry logic with backoff
- Log failures with context
```

### Squash-Ready
```
feat(auth): implement OAuth2 flow

- Add OAuth2 provider integration
- Implement token refresh logic
- Add comprehensive test suite
- Update API documentation

Addresses review feedback:
- Security: token storage (r1234)
- Tests: edge cases (r1235)
- Docs: usage examples (r1236)

Co-authored-by: reviewer <reviewer@example.com>
```

## Examples

### Apply Multiple Suggestions
```yaml
input:
  repo: "org/project"
  pr_number: 42
  feedback_source: "suggestions"
  auto_apply_suggestions: true
  run_tests: true
  commit_style: "single"
  notify_reviewers: true

output:
  success: true
  changes_made:
    - feedback_id: 1001
      feedback_summary: "Use list comprehension"
      action_taken: "suggestion_applied"
      files_modified: ["src/utils.py"]
      commit_sha: "abc123"
    - feedback_id: 1002
      feedback_summary: "Add type hints"
      action_taken: "suggestion_applied"
      files_modified: ["src/utils.py"]
      commit_sha: "abc123"
    - feedback_id: 1003
      feedback_summary: "Improve error message"
      action_taken: "suggestion_applied"
      files_modified: ["src/api/client.py"]
      commit_sha: "abc123"
  commits_created:
    - sha: "abc123"
      message: |
        Apply review suggestions

        - Use list comprehension in utils.py (r1001)
        - Add type hints to process() (r1002)
        - Improve error message clarity (r1003)
  tests_result:
    passed: true
    summary: "42 passed, 0 failed, 0 skipped"
  notifications_sent:
    - comment_id: 1001
      reviewer: "senior-dev"
    - comment_id: 1002
      reviewer: "senior-dev"
    - comment_id: 1003
      reviewer: "tech-lead"
```

### Address Complex Feedback
```yaml
input:
  repo: "org/project"
  pr_number: 42
  specific_comments: [2001]  # Security concern
  run_tests: true
  commit_style: "per_issue"

output:
  success: true
  changes_made:
    - feedback_id: 2001
      feedback_summary: "SQL injection vulnerability in user query"
      action_taken: "security_fix"
      files_modified:
        - "src/db/queries.py"
        - "tests/test_queries.py"
      commit_sha: "def456"
  commits_created:
    - sha: "def456"
      message: |
        fix(security): prevent SQL injection in user queries

        Addresses security concern raised in review #2001:
        - Replace string concatenation with parameterised queries
        - Add input validation for user IDs
        - Add tests for injection attempts

        Security: SQL injection prevention
  tests_result:
    passed: true
    summary: "45 passed (3 new), 0 failed"
  notifications_sent:
    - comment_id: 2001
      reviewer: "security-team"
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| Suggestion conflicts | Mark as not addressed, notify |
| Tests fail | Report failures, don't commit |
| Merge conflict | Abort, flag for manual resolution |
| Permission denied | Return error with explanation |
| Ambiguous feedback | Add to issues_not_addressed |
