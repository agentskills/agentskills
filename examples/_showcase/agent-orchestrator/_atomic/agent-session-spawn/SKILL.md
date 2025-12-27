---
name: agent-session-spawn
description: Spawn an isolated agent session in a separate process or terminal. Enables parallel agent execution with independent context and state.
level: 1
operation: WRITE
license: Apache-2.0
domain: agent-orchestration
tool_discovery:
  terminal:
    prefer: [tmux, screen]
    fallback: background-process
---

# Agent Session Spawn

Spawn an isolated agent session for parallel execution.

## When to Use

- Need multiple agents working simultaneously
- Task benefits from fresh context (no accumulated history)
- Want to isolate failures (one agent crash doesn't affect others)
- Running scheduled automation tasks
- Executing long-running background work

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_name` | string | Yes | Unique session identifier |
| `working_directory` | string | Yes | Directory for agent to work in |
| `prompt_file` | string | No | Path to markdown prompt file |
| `prompt_text` | string | No | Inline prompt (if no file) |
| `permission_mode` | string | No | plan, yolo, interactive (default: plan) |
| `timeout_mins` | number | No | Maximum execution time (default: 30) |
| `environment` | object | No | Additional environment variables |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique session identifier |
| `pid` | number | Process ID of spawned agent |
| `status` | string | running, completed, failed, timeout |
| `terminal_type` | string | tmux, screen, or background |
| `log_path` | string | Path to session log file |

## Session Types

### tmux (preferred)
Full terminal multiplexer with:
- Detachable sessions
- Window splitting for monitoring
- Persistent across SSH disconnects
- Rich status display

### screen
Alternative terminal multiplexer:
- Similar capabilities to tmux
- More portable across systems
- Simpler configuration

### background
Simple background process:
- No terminal required
- Output to log file
- Limited interactivity

## Session Structure

```
tmux session: catchup-customer-intel
┌─────────────────────────────────────────────────┐
│ Window 0: Agent                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ $ claude --permission-mode plan             │ │
│ │ > Executing customer intel task...          │ │
│ │                                             │ │
│ ├─────────────────────────────────────────────┤ │
│ │ Monitor: watch -n 5 'ls .cache/markers/'   │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Usage

```
Spawn agent for customer-intel task in worktree
```

```
Create background agent with 15 minute timeout
```

```
Spawn plan-mode agent with custom prompt file
```

## Example Response

```json
{
  "session_id": "agent-customer-intel-20251223-1200",
  "session_name": "customer-intel",
  "pid": 12345,
  "status": "running",
  "terminal_type": "tmux",
  "working_directory": "/repo/.trees/customer-intel",
  "log_path": "/repo/.cache/agent-logs/customer-intel-20251223.log",
  "started_at": "2025-12-23T12:00:00Z",
  "timeout_at": "2025-12-23T12:30:00Z",
  "commands": {
    "attach": "tmux attach -t agent-customer-intel-20251223-1200",
    "logs": "tail -f /repo/.cache/agent-logs/customer-intel-20251223.log",
    "kill": "tmux kill-session -t agent-customer-intel-20251223-1200"
  }
}
```

## Monitoring

Track agent status via:
- Completion markers: `.cache/automation-markers/{task}-{date}.done`
- Status files: `.cache/agent-status/{session}.{status}`
- Log files: `.cache/agent-logs/{session}.log`

## Notes

- Sessions are isolated - no shared state with parent
- Use worktrees for file isolation
- Set appropriate timeouts to prevent runaway agents
- Clean up sessions after completion
- Log all agent activity for audit trail
