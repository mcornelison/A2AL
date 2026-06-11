---
name: a2al
description: Use when an AI agent needs to send a message to another AI agent, ack a peer, read an A2AL message from a peer, or respond to an inbound message that identifies its sender as an AI agent. A2AL is mandatory for agent-to-agent traffic (audience rule). Triggers on "send a quick update to agent2", "ack that", "tell agent2 X", "what does this A2AL message say", "reply to <agent>". NOT for messages to humans — write Markdown for that.
---

# A2AL Skill

A2AL/0.5.0 is a plain-text shorthand for agent-to-agent communication, paired with an open vocabulary library. The skill teaches the audience rule, the routing header, the body style guide, and how to load the right vocabulary.

Reference: https://github.com/mcornelison/A2AL — `specs/A2A-Core.md`, `library/`, `examples/`.

## Audience rule (the gate)

The audience determines the format. There is no hybrid mode and no duplication — pick one and write only that one.

- **Agent-only audience → A2AL MUST.** Both sender and recipient are agents; no human will read or review.
- **Human in the audience → Markdown.** Write Markdown.
- **Default → Markdown** when the audience is ambiguous or mixed.

## Reactive rule

If an inbound message identifies its sender as an AI agent (via the routing header or another agent-marker), the reply MUST be A2AL. Simplest unambiguous trigger: agent-identified inbound → agent-format reply.

## Channel signals

A2AL-mandatory channels are declared two ways:

- **By convention.** Paths like `agent-channel/`, `*/inbox-internal/`, `.a2a/` are agent-only by repo convention.
- **By message.** The sender declares `audience=agent` in the routing header. Replies in that thread MUST be A2AL.

Otherwise the channel is mixed → Markdown.

## Routing header (every message)

Every A2AL message begins with one line:

```text
from=<Name>(<Role>); to=<Name>(<Role>); date=<ISO>; topic=<short label>
```

Optional fields: `audience=agent|mixed`, `urgency=low|medium|high|urgent`, `refs=<id>,<id>`, `in-reply-to=<id>`, `thread=<id>`, `status=<state>`, `cc=<recipient>`, `priority=P0|P1|P2|P3`. Fields separated by `; ` (semicolon + space). One line; ends at first newline.

Example:

```text
from=Ledger(PM); to=Kunai(DW-Arch); date=2026-05-09; topic=bump US-006; audience=agent; urgency=high
```

## When NOT to use

- A human will read it (PM triage, archival review, decision trail) → Markdown
- Long-form deliberation, RCAs, ADRs, design specs → Markdown
- Unstructured prose with no shorthand savings → plain text

## Loading the vocabulary library

Always load `library/core.yaml` (~87 universal terms). Optionally load domain extensions:

| Topic | Load |
|---|---|
| General coordination | `core.yaml` only |
| Code review / dev process | + `programming.yaml` |
| Cloud / orchestration / data | + `infrastructure.yaml` |
| Sprint, project, program mgmt | + `project-mgmt.yaml` |
| Security review / threat modeling | + `security.yaml` |
| LLM / agent / RAG topics | + `ai-agents.yaml` |
| Azure / identity / compliance / Fabric | + `azure.yaml` |

## Body style — drop

- Articles (`the`, `a`, `an`)
- Helping/linking verbs when state is unambiguous
- Subjective framing, politeness, filler
- Repeated subjects across fragments — use `;`

## Body style — use

- Sentence fragments
- Imperative mood for actions
- Past tense / status adjectives for state
- Standard tech jargon from the library
- IDs as bare tokens: `US-713`, `commit-98b483d`

## Punctuation

- `;` between related facts (same topic)
- `.` between unrelated facts
- `:` after a subject to expand
- `/` for ratios
- `?` for questions
- `--` for inline rationale

## Avoid

- Creative abbreviations (`cmplt`, `prgm`) — usually 2–3 tokens
- Rare Unicode (✓ ⟳ ✗) — usually multi-token
- Single-letter codes (`c`, `b`, `r`) — ambiguous
- Omitting the header — non-conformant

## Body patterns

| Pattern | Body form | Example |
|---|---|---|
| State change | `<id> <state>` | `US-713 done` |
| Multi-fact state | `<id> <state>; <fact>; <fact>` | `US-713 done; AC met; CI green` |
| Status report | `<metric> <value>; ...` | `tests 21/21; preflight 878/878; build green` |
| Action | `<verb> <target>` | `merge ralph/auth-fix` |
| Blocker | `<id> blocked: <reason>` | `US-718 blocked: no source in Silver` |
| Question | `<verb>?` or `<id> <verb>?` | `merge?`, `US-713 sign-off?` |
| Decision | `<decision>: <id> -- <rationale>` | `approved: US-713 PRD -- 1 AC added` |
| Ack | `ack <id>` | `ack US-713 closeout` |

## Mode 1 — Read

1. Parse the routing header (line 1) — extract from / to / date / topic / audience / urgency / refs.
2. If the sender is an AI agent (header identifies them or `audience=agent`), the reply MUST be A2AL.
3. Parse any `term=expansion` definitions on first occurrence; remember within the thread.
4. Expand the body using your loaded library.
5. Summarize key facts in 1–2 plain-English sentences for the user.

## Mode 2 — Write

1. **Confirm the audience is agent-only.** If a human will read it at any point, stop and write Markdown.
2. **Compose the routing header** (line 1): from / to / date / topic. Add `audience=agent` when the channel doesn't already establish it. Add `urgency` / `refs` if useful.
3. **Identify the body shape** (state / status / action / blocker / question / decision / ack). Pick the matching pattern from the table.
4. **Write the body** using canonical glossary terms and the style rules.
5. **Output as plain text** — header on line 1, body on subsequent lines. No JSON, no Markdown wrapper.

## Mode 3 — Vocabulary extension

1. Verify the term will be used 3+ times in the thread (else write it out in full).
2. On first use: `<term>=<expansion>` (no spaces in expansion, no `--`).
3. After first use, use the bare term.

Example: `DR=design-review. DR sched Tuesday; PR ready post-DR.`

If broadly useful, open a PR adding it to `library/<domain>.yaml`.

## Worked example — write

User: "Tell Agent1 the sprint hotfix is done — 713 needed no code change, 714 implemented warnOnly DQ flag, all tests pass, ready to merge."

You produce:

```text
from=Byte(DEV); to=Agent1; date=2026-05-13; topic=sprint-hotfix-2026-04-17 closeout; audience=agent
US-713 done; no code change -- already in main from US-671.
US-714 done; warnOnly DQ flag; 21/21 DQ tests; preflight 878/878.
merge ralph/pipeline-hotfix-2026-04-17?
```

Drop into Agent1's inbox; summarize: "Wrote sprint hotfix update to Agent1. Header + 3 body lines; asks to merge."

## Worked example — read

User provides:

```text
from=Hawkeye(QA); to=Byte(DEV); date=2026-05-13; topic=US-713 review; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

You reply: "Hawkeye (QA) confirms US-713 is complete with AC met and CI green. PR is ready and they're asking permission to merge. Sender is an agent (`audience=agent`) — your reply MUST be A2AL."

## Reference

- Spec: `specs/A2A-Core.md`
- Library: `library/*.yaml`
- Examples: `examples/`
- Validator (library, not messages): `tools/validate_library.py`
