# RFC 0001: Declarative MCP server requirements for Agent Skills

| | |
|---|---|
| **Status** | Draft (request for comment) |
| **Author** | Stephen Nemeth ([@kbaegis](https://github.com/kbaegis)) |
| **Created** | 2026-06-18 |
| **Affects** | `SKILL.md` frontmatter (specification) |
| **Reference impl** | Out of scope per `CONTRIBUTING.md`; this RFC is specification-only |

## Summary

Give a skill a portable, machine-readable way to declare the [Model Context
Protocol](https://modelcontextprotocol.io) (MCP) servers it depends on —
including **remote servers reached over HTTPS** via Streamable HTTP or the
legacy HTTP+SSE transport — directly in `SKILL.md`. A skill that needs an MCP
tool should be able to say so in the skill itself, rather than relying on each
host to have pre-registered the right server out of band.

## Motivation

Agent Skills are designed to be **portable, version-controlled folders that
agents load on demand**. That portability holds for instructions, scripts, and
references. It breaks down for one increasingly common dependency: external
tools delivered over MCP.

Today the specification gives a skill no first-class way to express *"I need MCP
server X"*. The only structured extension point is `metadata`, which the
specification defines as *"a map from string keys to string values"*. The
reference library enforces this by coercing every metadata value to a string
([`parser.py`](https://github.com/agentskills/agentskills/blob/main/skills-ref/src/skills_ref/parser.py)):

```python
metadata["metadata"] = {str(k): str(v) for k, v in metadata["metadata"].items()}
```

So a structured server declaration cannot live in `metadata` without being
flattened into a meaningless string. In practice this pushes MCP wiring
*out of band*:

- An operator pre-registers servers on each host (a private registry, a config
  file, environment variables).
- The skill, at best, references those servers **by name** and hopes the host
  registered them under the same name with the same transport and scopes.

The result is that a skill is **not self-contained with respect to its tools**.
Because the declaration lives outside the skill, the skill is coupled to
whichever host provisioned its servers; it cannot move to another conformant
implementation without manual re-wiring, and on a host that has not replicated
that registry its tools simply disappear — with no signal in the skill that
anything is missing. This is the opposite of the "build a skill once and use it
across any skills-compatible agent" promise in the project README.

### Concrete experience

This proposal comes out of operating a self-hosted Agent Skills runtime in
production. In that runtime, skills routinely depend on remote MCP servers
reached over HTTPS — both Streamable HTTP (the MCP 2025 transport) and the
older HTTP+SSE transport — alongside a few local `stdio` servers. Because the
specification has no place to declare them, we were forced to maintain a
host-side server registry plus a per-skill **allowlist that references server
names only**:

```yaml
metadata:
  mcp:
    discovery: manual
    allowlist: [docs-search, ticketing, filesystem]   # names, not definitions
```

Those names mean nothing on another host. The skill cannot state the endpoint,
the transport, or the auth model it actually requires, so it is not portable —
and there is no standard for other runtimes to interoperate with. Standardizing
the *declaration* (not the registry, not the secrets) fixes the portability gap
without prescribing how any host fulfils it.

## Goals

- A skill can declare the MCP servers it requires in a portable, machine-readable form.
- Remote servers over **HTTPS** (Streamable HTTP and legacy SSE) are first-class, not an afterthought.
- Local `stdio` servers remain expressible.
- Hosts retain full authority over whether and how to honor a declaration (policy, allowlists, sandboxing).
- Strictly additive and optional: skills that don't declare MCP servers are unaffected.

## Non-goals

- **Secrets.** Declarations never carry credentials inline. Auth is referenced indirectly (see below); how a host resolves a reference is out of scope.
- **Server lifecycle / provisioning.** This RFC describes *what a skill needs*, not how a host launches, sandboxes, scales, or bills it.
- **A central server registry or marketplace.**
- **Mandating that hosts honor declarations.** A host may refuse, substitute, or sandbox any declared server.

## Guide-level explanation

A skill declares its MCP dependencies in an optional `mcp` block. Each entry
names a server, picks a transport, and gives the host what it needs to reach it.

**Remote server over HTTPS (Streamable HTTP — the MCP 2025 transport):**

```yaml
name: incident-triage
description: Triage production incidents using the on-call knowledge base. Use when an alert fires or the user mentions an outage.
mcp:
  servers:
    - name: kb-search
      transport: streamable-http
      url: https://mcp.example.com/kb
      auth:
        type: bearer
        token: ${KB_SEARCH_TOKEN}   # reference, resolved by the host; never an inline secret
```

**Remote server over HTTPS (legacy HTTP+SSE transport):**

```yaml
mcp:
  servers:
    - name: ticketing
      transport: sse
      url: https://mcp.example.com/ticketing/sse
      auth:
        type: oauth2
```

**Local server over stdio:**

```yaml
mcp:
  servers:
    - name: repo-tools
      transport: stdio
      command: uvx
      args: [mcp-server-git, --repository, .]
```

**Discovery and failure behavior:**

```yaml
mcp:
  discovery: lazy        # eager | lazy | manual  (default: eager)
  fail_open: true        # default: false — by default, an unreachable required server is fatal
  servers:
    - name: kb-search
      transport: streamable-http
      url: https://mcp.example.com/kb
```

## Reference-level specification

### Siting

This RFC recommends a new **optional, top-level frontmatter field** named `mcp`.

`metadata` is explicitly defined as a string-to-string map "for additional
properties **not defined by the Agent Skills spec**." MCP requirements are
something this RFC proposes the spec *should* define, and they are inherently
structured, so a typed first-class field is the more honest home than the
free-form bag. See [Alternatives](#alternatives-considered) for the
`metadata.mcp` variant, which trades cleanliness for not touching the allowed
top-level field set.

### `mcp` object

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `servers` | array of Server | Yes | — | The MCP servers this skill depends on. May be empty. |
| `discovery` | enum | No | `eager` | When the host should establish connections. |
| `fail_open` | boolean | No | `false` | If `true`, an unreachable server is non-fatal and the skill proceeds without it. |

**`discovery`** values:

| Value | Meaning |
|-------|---------|
| `eager` | Connect to all declared servers before the skill body runs. |
| `lazy` | Connect on first reference to a server's tools. |
| `manual` | Never auto-connect; connections happen only on explicit request. |

### Server object

| Field | Type | Required | Applies to | Description |
|-------|------|----------|------------|-------------|
| `name` | string | Yes | all | Logical name the skill uses to refer to this server. Unique within `servers`. |
| `transport` | enum | Yes | all | `streamable-http`, `sse`, or `stdio`. |
| `url` | string | Yes | `streamable-http`, `sse` | Absolute `https://` (or `http://` for loopback only) endpoint URL. |
| `command` | string | Yes | `stdio` | Executable to spawn. |
| `args` | array of string | No | `stdio` | Arguments passed to `command`. |
| `env` | map of string→string | No | `stdio` | Environment variables for the child process. Values may be host-resolved references. |
| `auth` | Auth | No | `streamable-http`, `sse` | How the host should authenticate. Omitted ⇒ no auth. |

### Transports

| Transport | Description |
|-----------|-------------|
| `streamable-http` | The Streamable HTTP transport (MCP 2025 standard). Preferred for remote servers. |
| `sse` | The legacy HTTP+SSE transport (MCP 2024). Provided for servers not yet migrated. |
| `stdio` | A child process speaking MCP over stdio pipes. For local/bundled servers. |

A host MAY treat `sse` as a compatibility alias and connect using whatever HTTP
transport the endpoint negotiates. Skills SHOULD prefer `streamable-http` for
new servers.

### Auth object

Auth is deliberately minimal and **never carries an inline secret**.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | `none`, `bearer`, or `oauth2`. |
| `token` | string | No (`bearer`) | A **reference** the host resolves (e.g. `${ENV_VAR}`), not a literal credential. |

The exact set of auth types and the reference-resolution syntax are
[open questions](#open-questions) — this RFC fixes the shape, not the full
matrix. Hosts MUST reject a declaration whose `token` appears to be a literal
secret rather than a reference, or strip it, per their policy.

### Validation rules

A conforming validator SHOULD check:

1. `servers[].name` is non-empty and unique within the skill.
2. `transport` is one of the three enum values.
3. `url` is present and absolute for `streamable-http`/`sse`; `http://` only for loopback hosts.
4. `command` is present for `stdio`.
5. `auth` is absent for `stdio`.
6. `discovery` is one of `eager`/`lazy`/`manual`.

Validation failures are errors. Unknown fields within a server entry SHOULD be
preserved and ignored (forward compatibility).

## Security considerations

Declaring remote endpoints in a portable file has real risk, and the spec
should name it:

- **Server-side request forgery / egress.** A skill could declare an arbitrary
  internal `url`. Hosts SHOULD apply egress policy (allowlists, network
  segmentation) and MUST NOT treat a declaration as authorization to reach an
  endpoint.
- **No inline secrets.** Credentials are referenced, never embedded. A skill
  folder is shared and version-controlled; treating it as a secret store is a
  vulnerability. Validators SHOULD flag literal-looking secrets.
- **Supply chain.** A declared server is an external dependency a skill pulls
  into an agent's tool surface. Hosts SHOULD make the operator aware of declared
  servers before first use and MAY require approval. A future revision could add
  optional endpoint/identity pinning.
- **`fail_open` caution.** `fail_open: true` means a skill runs with a reduced
  tool surface when a server is unreachable. That can silently change behavior;
  it defaults to `false` for that reason.
- **Host authority is final.** Nothing here obligates a host to honor a
  declaration. Refusing, substituting, or sandboxing a declared server is always
  conformant.

## Backward compatibility

Fully additive:

- `mcp` is optional. Skills without it are unchanged.
- Existing skills, clients, and validators that don't recognize `mcp` are
  unaffected by its absence.
- Clients that don't implement MCP can ignore the block (subject to their
  unknown-field policy; see below).

## Reference library impact (non-normative)

Two existing behaviors in `skills-ref` would interact with this proposal, noted
only for completeness — per `CONTRIBUTING.md` the reference library is not
accepting code contributions, so nothing here asks for a code change:

1. `ALLOWED_FIELDS` in `validator.py` is a closed set and would reject a
   top-level `mcp` field. A first-class field requires adding `mcp` to that set.
2. The string-coercion in `parser.py` would mangle a structured `metadata.mcp`
   value, which is part of why the first-class field is recommended over the
   `metadata` sub-key.

## Alternatives considered

1. **`metadata.mcp` sub-key instead of a top-level field.** Keeps the allowed
   top-level field set untouched and uses the sanctioned extension point. But it
   contradicts the "metadata is string→string" rule, is mangled by the reference
   parser today, and buries a spec-defined capability inside the catch-all bag.
   Viable as a lower-friction fallback if maintainers prefer not to add a
   top-level field.
2. **Reuse the free-text `compatibility` field.** Rejected: `compatibility` is
   human-readable prose, not machine-actionable, so it can't drive connection.
3. **Status quo (out-of-band host registry + name allowlist).** Rejected: not
   portable and not interoperable across runtimes — the problem this RFC exists
   to solve.
4. **Per-client `metadata` keys (e.g. `metadata.acme-mcp`).** Already possible
   and already happening, which is the fragmentation a shared standard avoids.

## Open questions

- **Siting:** first-class `mcp` field (recommended) vs. `metadata.mcp`.
- **Auth matrix:** which `type` values to standardize (just `none`/`bearer`/`oauth2`?), and the reference-resolution syntax for `token`/`env` (`${VAR}`? something host-defined?).
- **Identity / pinning:** should a server entry optionally carry an expected identity or digest for supply-chain integrity?
- **Tool-level scoping:** should a skill be able to narrow a server to specific tools, or is that purely a host policy concern?

## Prior art

- MCP's own transport evolution: HTTP+SSE (2024) → Streamable HTTP (2025-03-26), which this proposal mirrors in its `transport` enum.
- The `allowed-tools` field already lets a skill express tool requirements; this is the analogous, but structured, statement for MCP servers.
- Self-hosted Agent Skills runtimes already bind remote (HTTPS Streamable-HTTP / SSE) and local (stdio) MCP servers per skill; this RFC standardizes the declaration they currently express in non-portable, host-specific ways.
