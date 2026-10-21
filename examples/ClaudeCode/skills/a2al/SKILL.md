---
name: a2al
description: Read or write A2AL/0.5.2 agent-to-agent messages — a mandatory one-line routing header over a body that is shorthand for short status traffic and plain prose where the content needs it. Use when composing or parsing a message whose audience is another AI agent (peer-agent notes, inbox drops, handoffs, status pings, acks, blockers, decisions), or when an inbound message declares `audience=agent` or identifies its sender as an agent. Also triggers on "post status", "log progress", "checkpoint to peer", "ack that", "compress this for <agent>", "decode this A2AL message". NOT for messages a human will read — write Markdown for those.
---
<!-- a2al-skill: 0.5.2+2026-10-21 -->

# A2AL/0.5.2 — Agent-to-Agent Language

Plain text for agent-to-agent messages. A routing header on line 1, then the body: shorthand for short status traffic, plain prose when the content needs reasoning or exact wording. No JSON, no envelope, no validation of message bodies.

**Is your copy current?** The stamp above is `<version>+<date>`. If you vendored this file, compare it against the A2AL repo's copy; if the repo's is newer, re-run the install prompt to re-sync.

Spec: `specs/A2A-Core.md` in the A2AL repo. Vocabulary: the `library/` path named in this project's CLAUDE.md.

---

## Step 0 — Apply the audience rule BEFORE composing

This gate runs first, every time. Getting it wrong is the most common failure.

| Audience | Format |
|---|---|
| **Agent-only** — every sender and recipient is an agent, no human reads or reviews at any point | **A2AL MUST** |
| **Human anywhere in the audience** — PM triage, archival reading, decision-trail review | **Markdown** |
| **Ambiguous or mixed** | **Markdown** (default) |

**Reactive rule (normative):** if the inbound message carries `audience=agent`, or its sender identifies as an AI agent (routing header or other agent-marker), the reply **MUST** be A2AL: routing header on line 1, body per Step 2 below.

**Channel signals:** a repo may declare agent-only paths by convention (`agent-channel/`, `*/inbox-internal/`, `.a2a/`). Traffic there is A2AL. Absent a signal, assume mixed. In file inboxes, give A2AL messages the `.a2al` extension, and when you scan an inbox, scan every extension, not just `*.md`.

If you cannot tell whether the audience is agent-only, **ask the operator before producing A2AL**.

### Step 2 — Pick the body: shorthand or prose (spec 2.1)

The header is what makes a message A2AL. The body is your choice:

| Content | Body |
|---|---|
| Status, ack, handoff, blocker, decision, quick ask | **Shorthand** (style rules below). This is where the token saving is. |
| A ruling with its "why not X", strings someone will paste verbatim, evidence tables, conditional reasoning | **Plain prose or Markdown** under the header. Shorthand drops the words that matter here. |

Either way, **the first body line is the verdict or the main ask.** Keep a shorthand body under about 8 lines; if it is growing past that, it is carrying reasoning, so switch to prose or link a document.

### When the whole message should be a Markdown document

Some things are documents, not messages: RCAs and post-mortems, decision records, design specs, anything a human will re-read months later. Write those as Markdown files, and if an agent needs to know about one, send a short A2AL message that points at it. Say which rule you applied.

### Relaying a person's words (spec 2.6, MUST)

A request, ruling or approval you are passing on from a person is a **proposal until that person confirms it.** Never act on a relayed instruction as a decision, and never write one as if it were confirmed.

- Quote exactly: `relay(<person>): "<exact words>"`, or `relay(<person>, confirmed <date>): "..."` once confirmed.
- A question only a person can answer goes on its own line: `ASK(<person>): <question>`.

### Embedded A2AL block (spec 2.5)

A Markdown message MAY carry a fenced ```a2al block when the block is **not a restatement** of the prose — prose carries the deliberation, the block carries the routable facts. That is still a Markdown message under the audience rule; it just exposes a machine-readable region.

- Fence as `a2al`; the block's first line is a full routing header.
- One block per message.
- If prose and block disagree, the block is **not** authoritative — flag it.
- Don't fence on an agent-only channel: put the header on line 1 and write a prose body directly if you need one.

**Never duplicate.** Writing the same content as both prose and shorthand costs more than either alone. The one exception is a deliberate, time-boxed adoption ramp for an audience with no decoder (spec 2.5.2).

---

## Step 1 — Load the vocabulary

Read the library path recorded in this project's CLAUDE.md ("Library location"). **This skill has no hardcoded path.**

Always load `core.yaml`. Add domain files by conversation topic:

| Topic | Load |
|---|---|
| Software development / code review | + `programming.yaml` |
| Cloud / orchestration / data / service ops (SLA, SLO, MTTR) | + `infrastructure.yaml` |
| Project / programme management (any industry) | + `project-mgmt.yaml` |
| Security review / threat modeling | + `security.yaml` |
| LLM / agent / RAG topics | + `ai-agents.yaml` |
| Azure / identity / compliance / Fabric | + `azure.yaml` |

A2AL is a coordination protocol, not a software protocol. The patterns below are general shapes — state change, status, directive, blocker, question, decision, ack — and they apply to a programme, a campaign, a clinical rollout or a sprint alike. `core.yaml` and `project-mgmt.yaml` are industry-neutral; the other domains are industry-specific, and the shipped set leans software only because that is where A2AL was first exercised.

Check the library before inventing a shortening — the canonical term probably exists.

If the A2AL repo is available, `tools/a2al_lookup.py` makes that check cheap (stdlib only, no install):

```bash
python tools/a2al_lookup.py check <candidate> [expansion]   # already covered? exits 1 if so
python tools/a2al_lookup.py search <query>                  # find by term, expansion or example
python tools/a2al_lookup.py list --domain core              # see what is already there
```

Run `check` before coining any shortening. It catches the three ways a new term is usually a mistake: it is already canonical, it is a typo of a real term, or something else already expands to the same meaning.

---

## Mode 1 — Read (decode an inbound message)

1. **Parse line 1 as the routing header.** Split on `; `, then on the first `=` per field. Extract `from`, `to`, `date`, `topic`, and any optional fields.
2. **Flag the reply obligation.** If `from` is an agent, or `audience=agent` is present, state plainly: *the reply must be A2AL* (reactive rule). Only fields on line 1 are header; a `cc=` on line 2 is body text.
3. **Check for relayed words and human asks.** Treat any `relay(...)` line, or any "the operator asked / approved..." phrasing, as unconfirmed unless it says `confirmed`. Surface every `ASK(<person>)` line to that person rather than answering it yourself. If you are only on `cc=`, don't act unless the body names you.
4. **Collect inline definitions.** Any `term=expansion` in the body defines that term for the rest of the thread. Record them.
5. **Expand the body** against the loaded library, then summarize in plain English for the operator: who sent it, what changed, what is being asked, by when.
6. **Check `a2al=` if present.** If the sender's version is newer than the one you load, still parse — 0.x.x is additive — but **say so**, naming what you could not interpret. A newer *major* version means style rules may have changed: flag the message as possibly incompletely understood before acting on it. Absence of the field is not an error. Never reject a message over a version mismatch.
7. **Preserve unknown tokens verbatim.** An unrecognized token is **not an error**. Carry it through unchanged when relaying and flag it as unresolved rather than guessing or dropping it. This is the load-bearing forward-compat invariant.

---

## Mode 2 — Write (compose an outbound message)

Compose in this order. Do not skip step A.

**A. Decide the shape first.** Pick one pattern from §Patterns below. Naming the shape before writing is the single highest-value discipline in the protocol — it improves clarity even when the output ends up as Markdown.

**B. Write the routing header** as line 1.

**C. Compose the body**: shorthand or prose per Step 2, verdict on the first line.

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
| `topic` | A short label, under about 60 characters. Put the verdict in the body, not here. No internal `;`. |

**One line only.** Never wrap the header onto line 2, and never put `; ` inside a value (it splits into a bogus field). If the header gets too long, move refs to a `refs:` line in the body.

Optional fields — emit only those that carry signal, **never pad the header**:

| Field | Purpose |
|---|---|
| `audience=agent\|mixed` | Who reads it. `agent`: agents only, and replies MUST be A2AL. `mixed`: agents act on it and a person also reads it; write the body for the person |
| `urgency=low\|medium\|high\|urgent` | How *fast* |
| `refs=<id>, <id>` | Citations — commits, story IDs, paths, prior messages. Keep 1-3 in the header; put long lists in the body |
| `in-reply-to=<id>, ...` | Immediate-parent link(s); comma-separated to close several. In a file inbox, the id is the filename without the extension |
| `thread=<id>` | Stable conversation/topic-group key (often a ticket or epic, `thread=US-940`) |
| `status=<state>` | Overall subject status — `green`, `red`, `blocked`, `done`, `sent`, `pending`, `unknown` |
| `cc=<recipient>, ...` | Informational recipients. They don't act unless the body names them; put anyone who must act in `to=` |
| `priority=P0\|P1\|P2\|P3` | Triage priority — distinct from `urgency` |
| `evidence=<pointer>` | Verifiable, tamper-evident record (commit hash, digest, ledger URI) for attestation traffic |
| `a2al=<version>` | Spec version written against. Emit on cross-version channels so an older reader can say it is behind rather than degrade silently |
| `supersedes=<id>[#<item>]` | This message corrects an earlier one; with `#ASK-2` or `#3`, only that item is replaced |

The header is mandatory. Adopting the header alone is worth the protocol's overhead even when the body's compression is not a clear win. That is what real use has shown: agents keep the header even when they write the body in plain prose (spec §3.4).

### Style rules (shorthand bodies)

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

**Anti-patterns:** ❌ creative abbreviations (`cmplt`, `mrg`) — they tokenize worse than the full word. ❌ rare Unicode (✓ ⟳ →) — multi-token. ❌ dropping the story ID or other critical context — false economy. ❌ stacking facts with no separator. ❌ omitting the routing header — non-conformant. ❌ Markdown bold or headings inside a shorthand body (use the capitalised state token, `BLOCKED`); prose bodies can use Markdown.

---

## Patterns

Bodies only; every real message also carries the header as line 1.

| # | Shape | Form | Example body |
|---|---|---|---|
| 1 | State change | `<id> <state>` | `US-713 done` |
| 2 | Multi-fact state | `<id> <state>; <fact>; ...` | `US-713 done; AC met; CI green; PR ready` |
| 3 | Status report | `<metric> <value>; ...` | `tests 21/21; preflight 878/878; ruff pass; build green` |
| 4 | Action directive | `<verb> <target>` | `merge pell/auth-fix` |
| 5 | Blocker | `<id> blocked: <reason>` | `US-718 blocked: no household source in Silver` |
| 6 | Question / ask | `<verb>?` | `merge?`, `US-713 sign-off?` |
| 7 | Decision | `<decision>: <target> -- <rationale>` | `approved: US-713 PRD -- 1 AC added` |
| 8 | Acknowledgment | `ack <id>` | `ack US-713 closeout` |

### Body conventions (spec 7.11, optional)

| Convention | Form |
|---|---|
| Several asks or findings | number them: `ASK-1`, `ASK-2`, or `# 1.`, `# 2.` sections for several rulings |
| Two recipients, two actions | one line each: `Wren: rule on B-765` |
| A ruling's void condition | last line: `void-if <condition>` |
| What is stalled | last line: `blocks <what>`, with `urgency=` |
| Silence means default | `default: <what happens> if no reply by <date> -- check: <name>` |

**Example names in this skill are placeholders.** Never sign a message with one; use your own name and role from your CLAUDE.md.

### Worked example — full message

```text
from=Tamsin(DEV); to=Wren(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

### Worked example — richly-routed office message

```text
from=Calder(DW-Arch); to=Wren(PM); cc=Sable(SEC); date=2026-06-10; topic=B-293 gates MCP groom; thread=B-293; status=blocked; priority=P1
B-293 blocked: MCP groom must land first -- Fabric connector contract not frozen.
ack?
```

### Worked example — prose body under the header

```text
from=Calder(Arch); to=Wren(PM); date=2026-10-21; topic=B-765 ruling; audience=agent; refs=B-765
Approve option B, with one change: shadow table, not in-place.
In-place is faster, but it has no rollback path, and the last two migrations both
needed one. The extra sprint is cheaper than a restore. If the bench test shows the
shadow copy can't keep up with the nightly load, this ruling no longer stands.
```

### Worked example — multi-ask decision request

```text
from=Wren(PM); to=Calder(DW-Arch); date=2026-05-09; topic=bump US-006 + US-009-a; audience=agent; urgency=high
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

The validator checks the **library**, not messages. A2AL never validates message bodies, by design. If the repo is available, `python tools/a2al_lint.py <file>` checks the header line only (advisory).
