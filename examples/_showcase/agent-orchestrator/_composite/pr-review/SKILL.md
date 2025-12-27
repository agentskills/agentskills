# pr-review

Perform a comprehensive code review of a pull request with intelligent analysis.

## Description

This skill orchestrates a complete code review:
1. **Read** - Fetch PR metadata, context, and existing discussions
2. **Analyse** - Examine diff for issues, patterns, and improvements
3. **Comment** - Provide inline feedback with suggestions
4. **Submit** - Submit formal review with summary

Uses AI-powered analysis to identify:
- Security vulnerabilities
- Performance issues
- Code style violations
- Logic errors
- Missing tests
- Documentation gaps
- Best practice violations

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
  - ai-analysis
  - quality
```

## Composes

- `pr-read` - Fetch PR metadata and status
- `pr-diff-read` - Get the code changes
- `pr-comment-create` - Add inline comments
- `pr-review-submit` - Submit formal review

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
    review_focus:
      type: array
      description: Areas to focus review on
      items:
        type: string
        enum:
          - security
          - performance
          - correctness
          - style
          - tests
          - docs
          - architecture
      default: [security, correctness, performance]
    severity_threshold:
      type: string
      enum: [critical, high, medium, low, info]
      description: Minimum severity to report
      default: "medium"
    auto_approve:
      type: boolean
      description: Auto-approve if no issues found
      default: false
    include_suggestions:
      type: boolean
      description: Include code suggestions for fixes
      default: true
    language_hints:
      type: array
      description: Languages in the PR (auto-detected if not specified)
      items:
        type: string
    max_comments:
      type: integer
      description: Maximum inline comments to create
      default: 15
    context:
      type: object
      description: Additional context about the codebase
      properties:
        coding_standards:
          type: string
          description: URL or content of coding standards
        architecture_docs:
          type: string
          description: Architecture documentation
        related_issues:
          type: array
          items:
            type: integer
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - review_result
  properties:
    success:
      type: boolean
    review_result:
      type: object
      properties:
        decision:
          type: string
          enum: [APPROVE, REQUEST_CHANGES, COMMENT]
        summary:
          type: string
        issues_found:
          type: array
          items:
            type: object
            properties:
              severity:
                type: string
                enum: [critical, high, medium, low, info]
              category:
                type: string
              file:
                type: string
              line:
                type: integer
              description:
                type: string
              suggestion:
                type: string
        metrics:
          type: object
          properties:
            files_reviewed:
              type: integer
            lines_analysed:
              type: integer
            issues_by_severity:
              type: object
            time_taken_ms:
              type: integer
    comments_created:
      type: array
      items:
        type: object
        properties:
          id:
            type: integer
          path:
            type: string
          line:
            type: integer
    review_submitted:
      type: object
      properties:
        id:
          type: integer
        state:
          type: string
        html_url:
          type: string
```

## Review Analysis Patterns

### Security Review

```yaml
security_checks:
  - name: "SQL Injection"
    pattern: "string concatenation in SQL"
    severity: critical
    languages: [python, javascript, java, php]

  - name: "XSS Vulnerability"
    pattern: "unsanitised user input in HTML"
    severity: critical
    languages: [javascript, typescript, html]

  - name: "Hardcoded Secrets"
    pattern: "API keys, passwords in code"
    severity: critical
    languages: all

  - name: "Path Traversal"
    pattern: "unvalidated file paths"
    severity: high
    languages: all

  - name: "Insecure Deserialization"
    pattern: "pickle.loads, yaml.load without Loader"
    severity: high
    languages: [python]
```

### Performance Review

```yaml
performance_checks:
  - name: "N+1 Query"
    pattern: "database query in loop"
    severity: high

  - name: "Missing Index"
    pattern: "filter without index hint"
    severity: medium

  - name: "Unbounded Query"
    pattern: "SELECT * without LIMIT"
    severity: medium

  - name: "Blocking I/O"
    pattern: "synchronous I/O in async context"
    severity: high
```

### Code Quality Review

```yaml
quality_checks:
  - name: "Missing Error Handling"
    pattern: "bare except, empty catch"
    severity: medium

  - name: "Code Duplication"
    pattern: "similar blocks > 10 lines"
    severity: low

  - name: "Complex Function"
    pattern: "cyclomatic complexity > 10"
    severity: medium

  - name: "Missing Type Hints"
    pattern: "function without type annotations"
    severity: low
    languages: [python, typescript]
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        pr-review                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. GATHER CONTEXT                                              │
│     ├─ pr-read → Get PR metadata, author, labels               │
│     ├─ pr-diff-read → Get all changed files and patches        │
│     └─ Fetch existing comments (avoid duplicates)               │
│                                                                  │
│  2. ANALYSE CHANGES                                             │
│     ├─ Parse each file by language                              │
│     ├─ Run security pattern matching                            │
│     ├─ Check for common anti-patterns                           │
│     ├─ Identify missing tests                                   │
│     └─ Score issue severity                                     │
│                                                                  │
│  3. PRIORITISE ISSUES                                           │
│     ├─ Sort by severity (critical → info)                       │
│     ├─ Group by file for readability                            │
│     ├─ Limit to max_comments                                    │
│     └─ Generate suggestions where possible                      │
│                                                                  │
│  4. CREATE COMMENTS                                             │
│     ├─ pr-comment-create for each issue                         │
│     ├─ Include code suggestions                                 │
│     └─ Track created comment IDs                                │
│                                                                  │
│  5. DETERMINE DECISION                                          │
│     ├─ CRITICAL issues → REQUEST_CHANGES                        │
│     ├─ HIGH issues → REQUEST_CHANGES                            │
│     ├─ MEDIUM only → COMMENT (or APPROVE if auto_approve)       │
│     └─ LOW/INFO only → APPROVE (if auto_approve)                │
│                                                                  │
│  6. SUBMIT REVIEW                                               │
│     ├─ pr-review-submit with decision                           │
│     ├─ Include summary of all issues                            │
│     └─ Return complete review result                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision Matrix

```
┌─────────────────┬────────────────────────────────────────────────┐
│ Issues Found    │ Decision                                       │
├─────────────────┼────────────────────────────────────────────────┤
│ Any CRITICAL    │ REQUEST_CHANGES (always)                       │
│ Any HIGH        │ REQUEST_CHANGES (unless all have suggestions)  │
│ MEDIUM only     │ COMMENT (REQUEST_CHANGES if > 5 issues)        │
│ LOW/INFO only   │ APPROVE if auto_approve, else COMMENT          │
│ No issues       │ APPROVE if auto_approve, else COMMENT          │
└─────────────────┴────────────────────────────────────────────────┘
```

## Examples

### Security-Focused Review
```yaml
input:
  repo: "company/webapp"
  pr_number: 123
  review_focus: [security]
  severity_threshold: "high"
  include_suggestions: true

output:
  success: true
  review_result:
    decision: "REQUEST_CHANGES"
    summary: |
      ## Security Review

      Found 2 critical security issues that must be addressed:

      ### Critical Issues
      1. **SQL Injection** in `api/users.py:45` - User input directly concatenated into SQL query
      2. **Hardcoded API Key** in `config/settings.py:12` - AWS credentials exposed

      ### Recommendations
      - Use parameterised queries for all database operations
      - Move secrets to environment variables or secrets manager

      Please address these security concerns before merging.
    issues_found:
      - severity: "critical"
        category: "security"
        file: "api/users.py"
        line: 45
        description: "SQL injection vulnerability - user input in query"
        suggestion: |
          cursor.execute(
              "SELECT * FROM users WHERE id = %s",
              (user_id,)
          )
      - severity: "critical"
        category: "security"
        file: "config/settings.py"
        line: 12
        description: "Hardcoded AWS credentials"
        suggestion: |
          AWS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
    metrics:
      files_reviewed: 15
      lines_analysed: 450
      issues_by_severity:
        critical: 2
        high: 0
        medium: 1
      time_taken_ms: 3500
  comments_created:
    - id: 111
      path: "api/users.py"
      line: 45
    - id: 112
      path: "config/settings.py"
      line: 12
  review_submitted:
    id: 5678
    state: "CHANGES_REQUESTED"
    html_url: "https://github.com/company/webapp/pull/123#pullrequestreview-5678"
```

### Auto-Approve Clean PR
```yaml
input:
  repo: "company/webapp"
  pr_number: 124
  review_focus: [security, correctness, performance]
  auto_approve: true
  severity_threshold: "medium"

output:
  success: true
  review_result:
    decision: "APPROVE"
    summary: |
      ## Review Complete ✅

      No significant issues found. Code looks good!

      ### Highlights
      - Clean error handling throughout
      - Good test coverage for new functionality
      - Performance considerations addressed

      LGTM! 🎉
    issues_found: []
    metrics:
      files_reviewed: 8
      lines_analysed: 200
      issues_by_severity: {}
      time_taken_ms: 2100
  review_submitted:
    id: 5679
    state: "APPROVED"
```

## Error Handling

```yaml
errors:
  - code: "PR_NOT_FOUND"
    handling: "Return error, cannot proceed"

  - code: "DIFF_TOO_LARGE"
    handling: "Review changed files only, note limitation in summary"

  - code: "RATE_LIMITED"
    handling: "Batch comments, reduce API calls"

  - code: "COMMENT_FAILED"
    handling: "Continue with remaining comments, note failures"
```
