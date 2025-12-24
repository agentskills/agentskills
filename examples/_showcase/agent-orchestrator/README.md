# Agent Orchestrator Showcase

Meta-skills for discovering, composing, and orchestrating other skills. This showcase demonstrates how agents can reason about their own capabilities, resolve ambiguity, and execute parallel work safely.

## Overview

The Agent Orchestrator provides skills for:

1. **Skill Discovery** - Find relevant skills based on user intent
2. **Skill Composition** - Dynamically compose new skills from existing primitives
3. **Disambiguation** - Flag unclear requests and resolve ambiguity
4. **Coherence Checking** - Validate skill consistency and detect conflicts
5. **Agent Spawning** - Decide when to use sub-agents for parallel work
6. **Worktree Isolation** - Use git worktrees to prevent conflicting edits

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                           │
├─────────────────────────────────────────────────────────────────┤
│  L3 Workflows                                                   │
│  ├── skill-compose         Compose new skills dynamically      │
│  ├── worktree-isolate      Parallel execution with isolation   │
│  ├── parallel-execute      Orchestrate multi-agent execution   │
│  ├── mcp-skill-generate    Generate skills from MCP servers    │
│  └── mcp-reliable-execute  Production-grade MCP execution      │
├─────────────────────────────────────────────────────────────────┤
│  L2 Composites                                                  │
│  ├── skill-discover        Find skills by intent               │
│  ├── skill-disambiguate    Resolve unclear selections          │
│  ├── skill-coherence-check Validate skill consistency          │
│  ├── agent-spawn-decide    Decide sub-agent strategy           │
│  ├── conflict-detect       Detect file edit conflicts          │
│  ├── mcp-tool-discover     Find MCP tools across servers       │
│  ├── mcp-skill-map         Map MCP tools to skill definitions  │
│  ├── mcp-tool-retry        Execute MCP tools with retry logic  │
│  ├── mcp-tool-batch        Batch execute multiple MCP tools    │
│  └── mcp-tool-validate     Validate MCP tool arguments         │
├─────────────────────────────────────────────────────────────────┤
│  L1 Atomics                                                     │
│  ├── skill-registry-read   Read skill definitions              │
│  ├── skill-graph-query     Query composition graph             │
│  ├── intent-classify       Classify user intent                │
│  ├── worktree-create       Create git worktree                 │
│  ├── worktree-merge        Merge worktree changes              │
│  ├── agent-session-spawn   Spawn isolated agent session        │
│  ├── completion-marker-set Set idempotency marker              │
│  ├── mcp-server-list       Discover configured MCP servers     │
│  ├── mcp-tools-list        Query tools from MCP server         │
│  ├── mcp-tool-call         Execute single MCP tool             │
│  ├── mcp-resources-list    Query resources from MCP server     │
│  └── mcp-prompts-list      Query prompts from MCP server       │
└─────────────────────────────────────────────────────────────────┘
```

## Key Patterns

### 1. Declarative Task Specification

Tasks are defined declaratively with explicit safety boundaries:

```yaml
name: customer-intel
schedule: "0 7 * * 1-5"  # 7am weekdays
complexity: medium
max_duration_mins: 15
auto_approve_writes: true
allowed_write_paths:
  - "daily/**"
  - "customers/**"
forbidden_operations:
  - "git push"
  - "rm -rf"
```

### 2. Marker-Based Idempotency

Completion markers prevent duplicate executions:

```
.cache/automation-markers/
├── customer-intel-2025-12-23.done
├── daily-synthesis-2025-12-23.done
└── workspace-sync-2025-12-23.done
```

### 3. Worktree Isolation for Parallel Work

When multiple skills might edit the same files:

```
.trees/
├── task-a/              # Isolated worktree for task A
│   └── (full repo copy)
├── task-b/              # Isolated worktree for task B
│   └── (full repo copy)
└── merge-queue/         # Staging area for conflict resolution
```

### 4. Intent-Based Skill Discovery

```
User: "I need to check customer status and send an update"
         │
         ▼
    intent-classify
         │
    ┌────┴────┐
    │         │
    ▼         ▼
READ intent  WRITE intent
    │         │
    ▼         ▼
customer-    email-
intel        compose
```

## Usage

### Discover Skills for Intent

```
Find skills that help with "analysing portfolio risk"
→ skill-discover returns: [risk-metrics-calculate, scenario-analyse, risk-profile-estimate]
```

### Compose Skills Dynamically

```
Create a skill that reads customer data, checks compliance, and generates a report
→ skill-compose creates: customer-compliance-report (L2)
   composes: [customer-data-read, compliance-check, report-generate]
```

### Handle Ambiguous Requests

```
User: "Update the data"
→ skill-disambiguate flags:
   - "data" is ambiguous (customer data? market data? portfolio data?)
   - Multiple skills match: [customer-data-update, market-data-fetch, holdings-ingest]
   - Clarification needed: "Which data would you like to update?"
```

### Spawn Parallel Agents

```
Tasks: [analyse-portfolio-a, analyse-portfolio-b, analyse-portfolio-c]
→ agent-spawn-decide determines:
   - Tasks are independent (no shared file writes)
   - Parallelisation safe
   - Spawn 3 isolated agents in worktrees
→ worktree-isolate creates:
   - .trees/portfolio-a/
   - .trees/portfolio-b/
   - .trees/portfolio-c/
→ parallel-execute orchestrates completion and merge
```

## Skills

### Atomic (L1)

| Skill | Operation | Description |
|-------|-----------|-------------|
| skill-registry-read | READ | Read skill definitions from registry |
| skill-graph-query | READ | Query skill composition graph |
| intent-classify | TRANSFORM | Classify user intent into operation types |
| worktree-create | WRITE | Create isolated git worktree |
| worktree-merge | WRITE | Merge worktree back to main |
| agent-session-spawn | WRITE | Spawn isolated agent session |
| completion-marker-set | WRITE | Set completion marker for idempotency |

### Composite (L2)

| Skill | Operation | Description |
|-------|-----------|-------------|
| skill-discover | READ | Find skills matching user intent |
| skill-disambiguate | READ | Flag unclear skill selections |
| skill-coherence-check | READ | Validate skill consistency |
| agent-spawn-decide | READ | Decide sub-agent strategy |
| conflict-detect | READ | Detect potential file conflicts |

### Workflow (L3)

| Skill | Operation | Description |
|-------|-----------|-------------|
| skill-compose | WRITE | Compose new skills dynamically |
| worktree-isolate | WRITE | Full worktree isolation workflow |
| parallel-execute | WRITE | Orchestrate parallel agent execution |

## MCP Integration Skills

The agent orchestrator includes comprehensive skills for integrating with Model Context Protocol (MCP) servers. These skills enable automatic tool discovery, skill generation, and reliable execution with decorators for retries, validation, and batching.

### MCP Atomic (L1)

| Skill | Operation | Description |
|-------|-----------|-------------|
| mcp-server-list | READ | Discover configured MCP servers |
| mcp-tools-list | READ | Query available tools from a server |
| mcp-tool-call | WRITE | Execute a single MCP tool |
| mcp-resources-list | READ | Query resources from a server |
| mcp-prompts-list | READ | Query prompts from a server |

### MCP Composite (L2)

| Skill | Operation | Description |
|-------|-----------|-------------|
| mcp-tool-discover | READ | Find tools across all servers by intent |
| mcp-skill-map | TRANSFORM | Map MCP tools to skill definitions |
| mcp-tool-retry | WRITE | Execute with retry, backoff, circuit breaker |
| mcp-tool-batch | WRITE | Execute multiple tools in sequence/parallel |
| mcp-tool-validate | READ | Validate arguments against schema |

### MCP Workflow (L3)

| Skill | Operation | Description |
|-------|-----------|-------------|
| mcp-skill-generate | WRITE | Generate complete skill library from MCP servers |
| mcp-reliable-execute | WRITE | Production-grade execution with full reliability |

### MCP Benefits

1. **Automatic Skill Generation** - Discover MCP servers and automatically generate L1 skills for each tool
2. **Reliability Decorators** - Built-in retry, timeout, circuit breaker, and validation patterns
3. **Schema-Driven Validation** - Pre-validate arguments against tool inputSchema before execution
4. **Batch Operations** - Execute multiple tools with dependency tracking and parallel execution
5. **Intent-Based Discovery** - Find relevant MCP tools using natural language queries

### MCP Usage Example

```
# Discover all filesystem tools
mcp-tool-discover --query "read and write files"
→ Returns: [filesystem/read_file, filesystem/write_file, filesystem/list_directory]

# Execute with reliability
mcp-reliable-execute \
  --server filesystem \
  --tool read_file \
  --arguments '{"path": "/home/user/config.json"}' \
  --retry.max_attempts 3 \
  --retry.backoff exponential \
  --validate true
→ Returns: file contents with retry report

# Generate skills from all MCP servers
mcp-skill-generate \
  --output_dir ./generated-skills \
  --include_decorators true \
  --include_composites true
→ Creates: L1 skill for each MCP tool, L2 composites for common patterns
```

## Safety Model

### Permission Boundaries

```yaml
auto_approve_writes: true
allowed_write_paths:
  - ".trees/**"           # Worktree operations
  - ".cache/**"           # Completion markers
  - "skills/_generated/**" # Generated skills
forbidden_operations:
  - "git push"            # No auto-push
  - "rm -rf"              # No destructive deletes
  - "skill delete"        # No skill deletion
```

### Conflict Resolution

When parallel agents produce conflicting edits:

1. **Detection** - conflict-detect identifies overlapping file writes
2. **Isolation** - Each agent works in separate worktree
3. **Verification** - Outputs verified before merge
4. **Sequential Merge** - Conflicts resolved in merge-queue
5. **Rollback** - Failed merges can be rolled back cleanly

## Integration with Scheduled Automation

The agent orchestrator integrates with cron-based scheduling:

```json
{
  "name": "parallel-customer-intel",
  "schedule": "0 7 * * 1-5",
  "use_worktrees": true,
  "parallel_subtasks": [
    {"name": "customer-a-intel", "customer_id": "A"},
    {"name": "customer-b-intel", "customer_id": "B"},
    {"name": "customer-c-intel", "customer_id": "C"}
  ],
  "merge_strategy": "sequential",
  "conflict_resolution": "manual"
}
```
