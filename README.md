# A2AL — Agent-to-Agent Language

A2AL is a deterministic, token-minimal communication standard for multi-agent systems. It replaces verbose human-readable artifacts (Markdown reports, narrative status updates, prose decision logs) with an array-only wire format built around seven fixed message archetypes.

**Status:** A2AL/2.0 — Project Coordination Profile (Array-Only). Specification frozen.

**License:** Apache-2.0 — see [LICENSE](./LICENSE).

## Why

In real multi-agent execution, 60–90% of inter-agent tokens are mechanical waste — narrative prose, framing, justification — none of which changes the receiving agent's behavior. A2AL strips that out and exchanges only **state and intent**, in a format a machine can parse deterministically and a human can audit.

## Goals

- **Token-minimal** — positional fields, numeric codes, no narrative
- **Deterministic** — same semantic message ⇒ same canonical bytes
- **Lossless** — unknown codes are preserved verbatim across relays
- **Role-agnostic** — works for PM, QA, Architect, Security, DevOps agents
- **Transport-agnostic** — wire format is a strict JSON subset (arrays + ints + strings)

## The Seven Archetypes

Every A2AL message is exactly one of:

1. **Scope Delta** — what entities were added/removed/modified
2. **Decision Record** — what was decided
3. **Execution Status** — current metrics
4. **Risk / Threat Intelligence** — severity, vector, action
5. **Signals & Gates** — invariants that must hold
6. **Inventory / Topology** — services, environments, dependencies
7. **Next Actions** — actor, verb, target

## Quick Look

A minimal A2AL message is a two-element array `[H, B]` — header and body:

```text
[[2,"dw-etl",0,2,1,"Qm9Jp8v4qZp8fN2d"],["Δ",[2,0,"US-852"],[2,0,"US-853"],[1,0,"US-858"],[3,0,"US-856"]]]
```

Header `[v=2, ctx="dw-etl", src=PM, dst=QA, typ=Scope Delta, msg_id]` carries routing; body lane `"Δ"` carries four scope-delta items (remove US-852, remove US-853, add US-858, modify US-856). No prose, no objects, no nulls — just structure.

## Repository Layout

| Path | Contents |
|---|---|
| [`specs/`](./specs) | Normative specification documents (grammar, rulebook) |
| [`examples/`](./examples) | Worked examples per archetype, transpilation samples *(planned)* |
| [`validator/`](./validator) | Reference validator and conformance test corpus *(planned)* |
| [`Session.md`](./Session.md) | Design session summary |
| [`OpenSource.md`](./OpenSource.md) | Open-standard promotion and governance plan |

Start with [`specs/A2A-Grammar.md`](./specs/A2A-Grammar.md) for the normative grammar and [`specs/A2A-Rulebook.md`](./specs/A2A-Rulebook.md) for reader/writer agent obligations.

## Versioning

A2AL follows semantic versioning. The seven archetypes and core grammar are frozen at A2AL/2.0; structural changes are a major-version event. Extensions go to reserved code spaces (`1000+`) per `specs/A2A-Grammar.md` §8.

## Contributing

Contributions, issues, and adoption reports are welcome. The protocol is designed to be vendor- and framework-neutral — see [OpenSource.md](./OpenSource.md) for governance principles.
