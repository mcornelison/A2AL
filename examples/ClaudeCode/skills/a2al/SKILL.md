---
name: a2al
description: Read or write A2AL/0.5.0 agent-to-agent messages — plain-text shorthand with a mandatory routing header. Use when composing or parsing a message whose audience is another AI agent (peer-agent notes, inbox drops, handoffs, status pings, acks, blockers, decisions), or when an inbound message declares `audience=agent` or identifies its sender as an agent. Also triggers on "post status", "log progress", "checkpoint to peer", "ack that", "compress this for <agent>", "decode this A2AL message". NOT for messages a human will read — write Markdown for those.
---

# A2AL/0.5.0 — Agent-to-Agent Language

Plain-text shorthand for agent-to-agent messages. A routing header on line 1, a compact body below. No JSON, no envelope, no schema validation of messages.

Spec: `specs/A2A-Core.md` in the A2AL repo. Vocabulary: the `library/` path named in this project's CLAUDE.md.

---

## Step 0 — Apply the audience rule BEFORE composing

This gate runs first, every time. Getting it wrong is the most common failure.

| Audience | Format |
|---|---|
| **Agent-only** — every sender and recipient is an agent, no human reads or reviews at any point | **A2AL MUST** |
| **Human anywhere in the audience** — PM triage, archival reading, decision-trail review | **Markdown** |
| **Ambiguous or mixed** | **Markdown** (default) |

**Reactive rule (normative):** if the inbound message carries `audience=agent`, or its sender identifies as an AI agent (routing header or other agent-marker), the reply **MUST** be A2AL.

**Channel signals:** a repo may declare agent-only paths by convention (`agent-channel/`, `*/inbox-internal/`, `.a2a/`). Traffic there is A2AL. Absent a signal, assume mixed.

If you cannot tell whether the audience is agent-only, **ask the operator before producing A2AL**.

### When A2AL is the wrong tool (write Markdown, and say so)

A2AL is a flat fact-stream format. It is weak on tree-shaped argumentation. Do not force it on:

- RCA memos, post-mortems, anything with conditional or hedged reasoning
- Architecture decision records, design specs, multi-branch option analyses
- Anything with archival shelf-life that a human will re-read months later
- Long deliberation — "thinking out loud at a peer" rather than reporting a result

Choosing Markdown for these is conformant, not under-use. Say which rule you applied.

### Embedded A2AL block (spec 2.5)

A Markdown message MAY carry a fenced ```a2al block when the block is **not a restatement** of the prose — prose carries the deliberation, the block carries the routable facts. That is still a Markdown message under the audience rule; it just exposes a machine-readable region.

- Fence as `a2al`; the block's first line is a full routing header.
- One block per message.
- If prose and block disagree, the block is **not** authoritative — flag it.
- Never do this on an agent-only channel: the prose is pure overhead there.

**Never duplicate.** Writing the same content as both prose and shorthand costs more than either alone. The one exception is a deliberate, time-boxed adoption ramp for an audience with no decoder (spec 2.5.2).

---

## Step 1 — Load the vocabulary

Read the library path recorded in this project's CLAUDE.md ("Library location"). **This skill has no hardcoded path.**

Always load `core.yaml`. Add domain files by conversation topic:

| Topic | Load |
|---|---|
| Code review / dev process | + `programming.yaml` |
| Cloud / orchestration / data | + `infrastructure.yaml` |
| Sprint, project, program management | + `project-mgmt.yaml` |
| Security review / threat modeling | + `security.yaml` |
| LLM / agent / RAG topics | + `ai-agents.yaml` |
| Azure / identity / compliance / Fabric | + `azure.yaml` |

Check the library before inventing a shortening — the canonical term probably exists.

---

## Mode 1 — Read (decode an inbound message)

1. **Parse line 1 as the routing header.** Split on `; `, then on the first `=` per field. Extract `from`, `to`, `date`, `topic`, and any optional fields.
2. **Flag the reply obligation.** If `from` is an agent, or `audience=agent` is present, state plainly: *the reply must be A2AL* (reactive rule).
3. **Collect inline definitions.** Any `term=expansion` in the body defines that term for the rest of the thread. Record them.
4. **Expand the body** against the loaded library, then summarize in plain English for the operator: who sent it, what changed, what is being asked, by when.
5. **Check `a2al=` if present.** If the sender's version is newer than the one you load, still parse — 0.x.x is additive — but **say so**, naming what you could not interpret. A newer *major* version means style rules may have changed: flag the message as possibly incompletely understood before acting on it. Absence of the field is not an error. Never reject a message over a version mismatch.
6. **Preserve unknown tokens verbatim.** An unrecognized token is **not an error**. Carry it through unchanged when relaying and flag it as unresolved rather than guessing or dropping it. This is the load-bearing forward-compat invariant.

---

## Mode 2 — Write (compose an outbound message)

Compose in this order. Do not skip step A.

**A. Decide the shape first.** Pick one pattern from §Patterns below. Naming the shape before writing is the single highest-value discipline in the protocol — it improves clarity even when the output ends up as Markdown.

**B. Write the routing header** as line 1.

**C. Compose the body** under the style rules.

### Routing header (MUST — line 1, one line, ends at the first newline)

```text
from=<Name>(<Role>); to=<Name>(<Role>); date=<ISO>; topic=<short label>
```

Required fields:

| Field | Format |
|---|---|
| `from` | `<Name>(<Role>)` or `<Name>/<Role>`. Role is free-form. |
| `to` | Same shape. Multiple recipients comma-separated. |
| `date` | ISO 8601 date or datetime (`2026-05-13`, `2026-05-13T15:30Z`) |
| `topic` | Free-form short label. No internal `;`. |

Optional fields — emit only those that carry signal, **never pad the header**:

| Field | Purpose |
|---|---|
| `audience=agent\|mixed` | Declares agent-only intent; replies MUST then be A2AL |
| `urgency=low\|medium\|high\|urgent` | How *fast* |
| `refs=<id>, <id>` | Citations — commits, story IDs, paths, prior messages |
| `in-reply-to=<id>, ...` | Immediate-parent link(s); comma-separated to close several |
| `thread=<id>` | Stable conversation/topic-group key (often a ticket or epic, `thread=US-940`) |
| `status=<state>` | Overall subject status — `green`, `red`, `blocked`, `done`, `sent`, `pending`, `unknown` |
| `cc=<recipient>, ...` | Informational recipients |
| `priority=P0\|P1\|P2\|P3` | Triage priority — distinct from `urgency` |
| `evidence=<pointer>` | Verifiable, tamper-evident record (commit hash, digest, ledger URI) for attestation traffic |
| `a2al=<version>` | Spec version written against. Emit on cross-version channels so an older reader can say it is behind rather than degrade silently |

The header is mandatory. Adopting the header alone is worth the protocol's overhead even when the body's compression is not a clear win — three independent agents' live-usage feedback converged on this.

### Style rules

**Drop:** articles (`the`/`a`/`an`); linking verbs in declarative state (`US-713 is done` → `US-713 done`); subjective framing (`I think`, `it seems`); politeness (`please`, `could you`); filler (`in order to` → `to`); repeated subjects in compounds — use `;`.

**Use:** sentence fragments; imperative mood for actions (`merge X`); past-tense/status adjectives for state (`done`, `blocked`, `shipped`, `failed`); 1-token tech jargon (`PR`, `AC`, `CI`, `QA`, `PM`, `CVE`); bare IDs (`US-713`, `commit-98b483d`).

**Punctuation:**

| Mark | Use |
|---|---|
| `;` | between related facts — `US-713 done; AC met; CI green` |
| `.` / newline | between unrelated facts |
| `:` | subject expansion — `US-713: AC met but CI broke` |
| `/` | ratios — `21/21 tests` |
| `?` | questions/asks — `merge?` |
| `--` | inline rationale — `defer US-718 -- no source in Silver` |

**Anti-patterns:** ❌ creative abbreviations (`cmplt`, `mrg`) — they tokenize worse than the full word. ❌ rare Unicode (✓ ⟳ →) — multi-token. ❌ dropping the story ID or other critical context — false economy. ❌ stacking facts with no separator. ❌ omitting the routing header — non-conformant.

---

## Patterns

Bodies only; every real message also carries the header as line 1.

| # | Shape | Form | Example body |
|---|---|---|---|
| 1 | State change | `<id> <state>` | `US-713 done` |
| 2 | Multi-fact state | `<id> <state>; <fact>; ...` | `US-713 done; AC met; CI green; PR ready` |
| 3 | Status report | `<metric> <value>; ...` | `tests 21/21; preflight 878/878; ruff pass; build green` |
| 4 | Action directive | `<verb> <target>` | `merge ralph/auth-fix` |
| 5 | Blocker | `<id> blocked: <reason>` | `US-718 blocked: no household source in Silver` |
| 6 | Question / ask | `<verb>?` | `merge?`, `US-713 sign-off?` |
| 7 | Decision | `<decision>: <target> -- <rationale>` | `approved: US-713 PRD -- 1 AC added` |
| 8 | Acknowledgment | `ack <id>` | `ack US-713 closeout` |

### Worked example — full message

```text
from=Byte(DEV); to=Ledger(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

### Worked example — richly-routed office message

```text
from=Kunai(DW-Arch); to=Ledger(PM); cc=Audrey(SEC); date=2026-06-10; topic=B-293 gates MCP groom; thread=B-293; status=blocked; priority=P1
B-293 blocked: MCP groom must land first -- Fabric connector contract not frozen.
ack?
```

### Worked example — multi-ask decision request

```text
from=Ledger(PM); to=Kunai(DW-Arch); date=2026-05-09; topic=bump US-006 + US-009-a; audience=agent; urgency=high
US-006: A=in-place fast no-rollback; B=shadow +1sprint rollback-safe; ASK=pick A|B
US-009-a: opt1=F-SKU-lib saves-3d bug=#44-memleak; opt2=wrap-REST clean +3d; ASK=pick opt1|opt2
deadline=2026-05-09T17:00 -- F-SKU trial closes EOD
```

---

## Extending the vocabulary

Introduce a new shortening on first use with `term=expansion`:

```
DR=design-review. DR sched Tuesday; PR ready post-DR; AC sign-off needed post-DR.
```

The definition runs until the next `.`, `;`, `?`, `!`, `--`, or newline. The expansion is a single word or hyphenated phrase — no internal spaces.

- **Threshold:** define it only if the term will be used **3+ times in the thread**. Fewer, spell it out.
- **Scope:** per-thread by default. A new thread is a clean slate.
- **Acceptance:** the receiver signals acceptance by using the term. They may instead ask `?DR`, or counter-propose `DR=design-review (or DRev?)`.
- **Don't** redefine a canonical term (`PR=pull-request` — `PR` is already in the library), use cryptic single letters, or renegotiate a form mid-thread.
- **Promotion:** a shortening used 5+ times across multiple threads is a library PR candidate. Add it to the right `library/<domain>.yaml` with `term`/`expansion`/`example`/`notes`, then run `python tools/validate_library.py`.

The validator checks the **library**, not messages. A2AL never validates message shape, by design — there is no header linter.
