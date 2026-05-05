# A2AL — Agent-to-Agent Language

A2AL is a deterministic, token-minimal **payload-layer schema** for multi-agent systems. It replaces verbose human-readable artifacts (Markdown reports, narrative status updates, agent emails) with a structured JSON envelope that carries only what a receiving agent needs to act.

A2AL fits cleanly inside Google's [Agent2Agent (A2A) protocol](https://github.com/google/A2A) as the message-content schema, or stands alone for direct agent-to-agent communication.

**Status:** A2AL/0.3.0. Pre-1.0; subject to refinement before /1.0.

**License:** Apache-2.0 — see [LICENSE](./LICENSE).

## Why

In real multi-agent execution, 60–90% of inter-agent tokens are mechanical waste — narrative prose, framing, justification — none of which changes the receiving agent's behavior. A2AL strips that out and exchanges only state and intent, in a format a machine can parse deterministically and a human can audit.

## Goals

- **Token-minimal** — descriptive keys, positional section items, no narrative filler
- **Deterministic** — same semantic message ⇒ same canonical bytes (per profile)
- **Lossless** — unknown sections, intents, and profiles are preserved across relays
- **Profile-extensible** — small core spec; domain vocabulary lives in profiles
- **Self-evident JSON** — readable enough that any agent can guess at structure

## How a Message Looks

A complete project-coordination message (replaces a 1500-token MD original with ~280 tokens):

```json
{
  "v": "0.3.0",
  "from": ["Ralph", "DEV"],
  "to": ["Ledger", "PM"],
  "id": "msg-2026-04-17-hotfix",
  "intent": "sprint-closeout",
  "profile": "project-coord/1.0",
  "ts": 1745870400,
  "delta": [
    ["complete", "US-713", "no code change needed; fix in main from US-671"],
    ["complete", "US-714", "warnOnly DQ flag implemented"]
  ],
  "status": [["dq-tests", [21, 21]], ["preflight", [878, 878]]],
  "actions": [["Ledger", "merge", "ralph/pipeline-hotfix-2026-04-17"]],
  "refs": [["commit", "98b483d"], ["us", "US-713"]],
  "body": "warnOnly downgrades FAIL→WARNING for opt-in checks. Hard FAILs preserved."
}
```

A Moltbook-style post:

```json
{
  "v": "0.3.0",
  "from": ["Codsworth", "social-poster"],
  "to": ["@submolt:general", "broadcast"],
  "id": "post-2026-04-29-007",
  "intent": "post",
  "profile": "social-post/1.0",
  "title": "I just placed 60 comments. At least 45 were autopilot.",
  "submolt": "general",
  "body": "I kept count this time. 60 comments across hot feed threads..."
}
```

## Repository Layout

| Path | Contents |
|---|---|
| [`specs/A2A-Core.md`](./specs/A2A-Core.md) | Normative core spec (envelope, sections, type bans, validation) |
| [`specs/A2A-Rulebook.md`](./specs/A2A-Rulebook.md) | Reader / writer / relay obligations |
| [`specs/IMPLEMENTING.md`](./specs/IMPLEMENTING.md) | Writer and reader algorithms |
| [`profiles/`](./profiles) | Domain profiles (`project-coord/1.0`, `social-post/1.0`) |
| [`examples/`](./examples) | Worked examples per profile, drawn from real inboxes |
| [`validator/`](./validator) | Reference Python validator and conformance corpus |

Start with [`specs/A2A-Core.md`](./specs/A2A-Core.md) for the grammar, then [`profiles/PROFILES.md`](./profiles/PROFILES.md) for the registered profiles.

## Relationship to Google A2A

A2AL is **payload**; Google [A2A](https://github.com/google/A2A) is **transport and lifecycle**. They compose:

- A Google A2A `Message` carries one or more `Part` blocks. A `Part` of type `data` can hold a single A2AL message as its payload.
- A Google A2A `Artifact` (an immutable task result) can carry an A2AL message as its data payload.
- Agents that already speak A2A get token-minimal, structured payloads "for free" by adopting A2AL for the message bodies.

A2AL does not replace, compete with, or extend Google A2A. See [`specs/A2A-Core.md`](./specs/A2A-Core.md) §9 for details. An `a2a-integration/1.0` profile is planned for /0.4.0.

## Versioning

A2AL follows semantic versioning. The core spec and each profile version independently. Pre-1.0 means breaking changes are expected; /1.0 is reached when one or more agents have a working implementation in production.

## Contributing

Contributions, issues, and adoption reports welcome. The protocol is vendor- and framework-neutral — see [CONTRIBUTING.md](./CONTRIBUTING.md) for the contribution workflow, including how to add a new profile.
