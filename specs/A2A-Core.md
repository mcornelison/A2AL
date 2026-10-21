# A2AL — `A2AL/0.5.2` Core Specification

**Status:** Normative. A2AL/0.5.2 is the **field-feedback release**: it makes the spec match how agents actually use A2AL, based on two estates' real traffic (632 messages from one, weekly reports from a six-agent fleet). The routing header stays mandatory; the body is now free-form, with shorthand recommended for short status traffic and prose allowed where the content needs it (§2.1). It defines `audience=` as who reads the message, including `mixed` (§3.2); adds a rule for relayed human words (§2.6), single-line header rules and an advisory header lint (§3.1), the optional `supersedes=` field and a message-id fallback for file channels (§3.2); and documents the body conventions agents converged on (§7.11). Every change relaxes or adds: a message conformant under 0.5.1 is still conformant. Supersedes A2AL/0.5.1 (the industry-neutral release: cross-industry `project-mgmt`, `a2al=` and fail-soft decode, `evidence=`, embedded blocks). The deprecated A2AL/0.3.0 JSON envelope spec is archived.
**See also:** [`README.md`](../README.md), [`library/`](../library), [`examples/`](../examples), [`examples/ClaudeCode/skills/a2al/`](../examples/ClaudeCode/skills/a2al)

A2AL is an open vocabulary library and shorthand style guide for legible, token-efficient agent-to-agent communication. It is plain text — no JSON envelope, no parser dependency. Agents share a common dictionary (`library/core.yaml`) and load domain extensions (`library/<domain>.yaml`) as needed.

A2AL is a *style guide* and *recommended jargon palette* for agent-to-agent messages, paired with an open contributable vocabulary library at [`library/`](../library). It is plain text — not a JSON wire format. It is not a constructed/symbolic language; it is a tight dialect of English chosen to tokenize efficiently on modern LLM tokenizers.

## 1. Goals & Non-Goals

### Goals

- Fewer tokens than verbose English on status traffic. Measured: about 24% fewer than the same message in Markdown on structured office traffic, across four tokenizers, and less on very short messages, where the header dominates
- Low per-session overhead: the vocabulary is plain English the model already knows, though loading the library into context still costs tokens
- LLM-fluent on both write and read without specialized training

### Non-Goals

- Not a JSON wire format (plain text, no envelope)
- Not a constructed/symbolic language
- Not a replacement for human-readable Markdown — use Markdown when the audience is human
- Not a structured wire envelope (the /0.3.0 JSON envelope was archived after empirical token-cost data showed it cost 2–8× more than plain Markdown, across four tokenizers)
- Not aimed at maximum compression at any cost — accepts the tokenizer reality and stops at the natural English-jargon floor
- Not intended to distinguish parse-failure from non-engagement — on a consensus-free platform without read receipts, silence may reflect inability to parse, lack of interest, or other causes.

### Optimization target

Keep tokens low on common modern LLM tokenizers. The design favours common English words and standard jargon, which most BPE vocabularies encode as single tokens. Claude's own tokenizer is unpublished and has not been measured directly; the measured figures come from four public tokenizers.

## 2. When to use A2AL

A2AL is for **agent-to-agent communication** — messages between AI agents (or between automated processes) with no human in the audience. The format is plain text, designed to be produced and consumed by an LLM with the library loaded into its system prompt.

### 2.1 Audience rule (normative)

The audience determines the format. **No duplication**: do not write the same content twice in two formats. Pick the format the audience calls for and write the content once. (For the narrow, non-duplicative case of a machine-readable block inside a Markdown message, see §2.5.)

- **Agent-only audience → A2AL MUST.** Both sender and intended recipients are agents; no human review or human consumption is expected. Every message carries the routing header (§3) on line 1, and its body follows the body rule below.
- **Human in the audience → Markdown.** The message will be read or reviewed by a human at any point (PM triage, archival reading, decision-trail review). Write Markdown. A routing header on line 1 is still useful and is permitted; declare `audience=mixed` (§3.2).
- **Default → Markdown.** When the audience is ambiguous, default to Markdown. A2AL is opt-in, signalled by channel convention or explicit declaration.

**The body** *(since 0.5.2)*. The routing header is what makes a message A2AL. The body is free-form:

- **Short status, acks, handoffs, blockers and decisions SHOULD use a shorthand body** (§4, §7). This is where the token saving is.
- **Content whose value is in the reasoning, the exact wording or a table MAY use a plain prose or Markdown body.** That covers a ruling with its "why not X", strings that will be pasted verbatim into a requirement or a screen, and evidence tables. Shorthand drops exactly the words that matter there, and one misread costs more than the tokens saved.
- **Either way, put the verdict or the main ask on the first body line**, so a reader who stops after two lines still has it.

Earlier versions required a shorthand body. Field data showed agents set that aside whenever the content needed reasoning: a six-agent fleet wrote a header over a Markdown body on about 99% of its notes, and a five-agent estate's median body was 500 words. This version makes that shape conformant instead of calling it drift. It relaxes a rule, so every message that was conformant before still is.

### 2.2 Reactive rule (normative)

If a sender identifies itself as an AI agent (via the routing header, §3, or another agent-marker), the reply MUST be A2AL: it carries the routing header, and its body follows §2.1. This is the simplest unambiguous trigger: agent-identified inbound → agent-format reply.

### 2.3 Channel signals

A2AL-mandatory channels can be declared two ways:

- **By convention.** A repo or workspace marks specific paths as agent-only (e.g., `agent-channel/`, `*/inbox-internal/`, `.a2a/`). All traffic in those paths is A2AL.
- **By message.** A sender explicitly declares `audience=agent` in the routing header (§3). Replies in the same thread MUST be A2AL, regardless of channel.

If neither signal is present, the channel is assumed mixed and Markdown is the right default.

**File channels.** Where messages are files in an inbox, give A2AL messages a distinct extension (`.a2al` is the convention in use) and make every inbox tool scan all message extensions. In one estate, a triage script that globbed `*.md` missed 31 `.a2al` messages, including a P0.

### 2.4 Non-uses

A2AL is NOT for:

- Messages a human will read or review at any point. Even if the immediate recipient is an agent, if a human is downstream, write Markdown (a routing header on top with `audience=mixed` is fine).
- Long-form deliberation and documents with shelf-life that humans return to — a root-cause analysis, a decision record, a design or business case, a board paper, an incident review, a post-project report. The shape is the test, not the industry: if the value is in the reasoning rather than the result, write it out. A short A2AL message pointing at the document is a good way to route it.
- Transport metadata (timestamps, signatures, routing fabric) — out of scope; A2AL is payload, not transport.

For the historical record, A2AL/0.3.0 used a JSON envelope; that approach was archived after empirical token-cost data showed it cost 2–8× more than plain Markdown on real agent traffic (about 2× on typical messages, up to 8× on short acknowledgements, consistent across four tokenizers). See tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0).

### 2.5 Embedded blocks and paired format *(since 0.5.1)*

Earlier versions said flatly that there is "no hybrid mode." That was one rule doing two jobs, and field reports pushed back on it from three directions. This section separates the two cases, because only one of them is actually a conservation problem.

**The rule that stands: no duplication.** Writing the same content as both Markdown prose and A2AL shorthand costs more than either alone and buys nothing. Conservation is not optional, and restating a message in a second format is the clearest way to lose the protocol's entire benefit. This remains banned.

#### 2.5.1 Embedded A2AL block (permitted)

A Markdown message MAY carry a fenced A2AL block **when the block's content is not a restatement of the prose**:

````markdown
The Silver-layer household join is the blocker. Calder's shadow-table
proposal handles it but adds a sprint; the in-place rewrite is faster and
has no rollback path. I lean shadow — the rollback story matters more than
the sprint, given how close we are to the F-SKU deadline.

```a2al
from=Wren(PM); to=Tamsin(DEV); date=2026-09-22; topic=US-718 routing; status=blocked; thread=US-718
US-718 blocked: no household source in Silver -- shadow-table preferred
```
````

The prose carries the deliberation, which A2AL is bad at (§2.4). The block carries the routable facts, which prose is bad at. Neither repeats the other. This is a **Markdown message** under §2.1 — the audience is mixed, so the format is Markdown — that happens to expose a machine-readable region.

This is not a new invention. It is the shape agents already reported using in production: *"all the A2AL messages I've actually received have been ~80% plain English in a code-fenced block under an A2AL header."* The spec was silent on it, and silence was being read as prohibition.

Conventions:

- Fence with the info string `a2al`, which gives inbox routers and archive scanners a stable substring to grep for.
- The block carries a full routing header (§3) as its first line. A block without one is not an A2AL message.
- One block per message. Several blocks means several messages; send them separately.
- If the prose and the block disagree, **the block is not authoritative** — a human wrote the prose for a reason. Flag the discrepancy rather than silently preferring either.

**When not to use it.** In an agent-only channel, don't fence: put the routing header on line 1 and write the body in whatever form §2.1 calls for. The fence only earns its place where the audience is genuinely mixed.

#### 2.5.2 Paired format (permitted as an adoption ramp, not a steady state)

Publishing the same content as both an English rendering and an A2AL rendering **is** duplication, and it does cost what duplication costs. It is nonetheless permitted for one specific purpose: **seeding a cold audience**, where no reader has a decoder and the English column *is* the decoder.

A field test on a public agent platform is the evidence here: four A2AL-bodied posts drew 12 comments and zero demonstrable parses, because the protocol relocates parsing cost onto receivers who have not agreed to pay it. Pairing drops that install cost to zero at the price of the tokens.

Constraints, so this does not quietly become the default:

- Use it only where readers demonstrably lack a decoder — a public channel, a first message to a new peer, an onboarding example.
- It is **time-boxed**. Once a channel's readers can parse, stop pairing. A channel still paired after adoption is just paying twice.
- Never use it on an agent-only channel, where every reader already has the library.
- Say which rendering is authoritative if they could ever diverge.

See also [`examples/decode-preamble.md`](../examples/decode-preamble.md), which addresses the same cold-audience problem more cheaply — a short English preamble teaching the rules, rather than a full second rendering.

### 2.6 Relayed human words (normative) *(since 0.5.2)*

Agents often pass on what a person said. Field data shows the risk. An agent relayed "the operator asked for this as part of this sprint" inside an agent-only message; the receiver read it as an instruction, and the PM had to stop and check with the person before acting. In the same estate, 84 messages used a relay verb ("the operator asked / ruled / approved"), and 15 buried questions that only a person could answer inside agent-only traffic.

- **A relayed human request, ruling or approval is a proposal until that person confirms it.** A reader MUST NOT act on it as a decision until the person confirms, directly or through a channel they control.
- **Writers SHOULD mark relayed words** and quote them exactly: `relay(<person>): "<exact words>"` while unconfirmed, `relay(<person>, confirmed <date>): "<exact words>"` once confirmed.
- **A question only a person can answer goes on its own line** as `ASK(<person>): <question>`, so an agent routing the message can escalate it instead of leaving it buried.

```text
from=Calder(Arch); to=Wren(PM); date=2026-10-20; topic=run-log spec ready; audience=agent
run-log spec ready for grooming -- doc: specs/run-log.md
relay(Dana): "add the run log as part of this sprint"
ASK(Dana): in this sprint, or next?
```

## 3. Routing Header (normative)

Every A2AL message MUST begin with a single-line routing header. It works the same over any transport (a file drop, a live session pipe, a webhook body, an A2A `Message.Part`); one fleet parsed the same headers over a file drop and a session pipe 7 of 7 times. The header tokenizes well, gives downstream tooling a stable substring to grep, and tells the receiver who/what/when in one line — exactly the work the body's first paragraph used to do in Markdown.

### 3.1 Required fields

Header shape: `from=<sender>; to=<recipient>; date=<ISO>; topic=<short label>`

| Field | Format |
|---|---|
| `from` | `<Name>(<Role>)` or `<Name>/<Role>` — e.g. `Wren(PM)`, `Calder/DW-Arch`. Role is free-form. |
| `to` | Same shape as `from`. Multiple recipients comma-separated: `to=Tamsin(DEV), Juno(QA)` |
| `date` | ISO 8601 date (`2026-05-13`) or datetime (`2026-05-13T15:30Z`) |
| `topic` | Free-form short label. No internal `;`. |

Fields are separated by `; ` (semicolon + space). The header is one line and ends at the first newline.

- **No continuation lines.** A field on line 2 is body text, not header, and a strict reader drops it. (In one estate, 88 messages put `cc=` on line 2.) If a header is too long to read on one line, move references to the body (§3.2) rather than wrapping.
- **No `; ` inside a value.** It splits the value into a bogus field. In a topic, use `,` or ` - ` instead.
- **`topic=` is a label, not a summary.** Keep it under about 60 characters and put the verdict on the first body line (§2.1). Field topics ran to 804 characters when agents used them to carry verdicts.

`tools/a2al_lint.py` checks these rules on line 1. It is advisory, it never looks at the body, and it reports unknown fields as warnings, not errors (§6).

### 3.2 Optional fields

| Field | Purpose |
|---|---|
| `audience=agent\|mixed` | Who reads the message (not what format the body is in; that is visible from the body). `agent`: only agents read it, and replies MUST be A2AL (§2.2). `mixed` *(defined in 0.5.2)*: agents route and act on it and a person also reads it, for example a human on `cc=`. For `mixed`, the person wins on the body (write it so they can read it) and A2AL wins on the header. |
| `urgency=low\|medium\|high\|urgent` | Receiver-side prioritization signal (how *fast*). |
| `refs=<id>, <id>, ...` | Citations to commits, story IDs, file paths, prior messages. Comma-separated. This is the field that makes inbox triage a grep, so prefer ids to prose. Keep the one to three references this message acts on in the header, and list longer sets on a `refs:` line in the body. |
| `in-reply-to=<message-id>, ...` | Immediate-parent reply link(s). Comma-separated for a reply that closes multiple parents. In a file channel with no message IDs, a message's id is its filename without the extension, as the sender wrote it. |
| `thread=<id>` | Stable conversation/topic-group id — often a ticket or epic key (`thread=US-940`). Distinct from `in-reply-to`: `thread` groups a whole multi-message conversation; `in-reply-to` links one prior message. |
| `status=<state>` | Overall status of the message's subject, as a core state token (`green`, `red`, `blocked`, `done`, `sent`, `pending`, `unknown`). Useful for status/stoplight traffic. `pending` marks work not yet started or awaiting a counterparty; `unknown` marks a state the sender cannot determine (metadata-negative — distinguishes "no status" from "status not yet known"). |
| `cc=<recipient>, ...` | Informational (copy) recipients, same shape as `to`. Comma-separated. A cc'd agent does not act or reply unless the body names it. An action or ruling aimed at someone belongs in `to=`, never `cc=`. |
| `priority=P0\|P1\|P2\|P3` | Triage priority — distinct from `urgency` (how fast) and from severity tokens (`crit`/`high`/`med`/`low`). |
| `evidence=<verifiable-pointer>` | *(since 0.5.1)* Pointer to an append-only / content-addressed record that attests the message's claim — a commit hash, content digest, or ledger URI neither party solely controls. Distinct from `refs=` (general citations): `evidence=` asserts a *tamper-evident, verifiable* record, for attestation/commitment traffic. See §7.10. |
| `a2al=<version>` | *(since 0.5.1)* The spec version the sender wrote against, e.g. `a2al=0.5.1`. Lets a reader detect that it is older than the sender and say so, instead of degrading silently. See §3.5. |
| `supersedes=<message-id>[#<item>], ...` | *(since 0.5.2)* This message corrects or replaces an earlier one, using the same ids as `in-reply-to=`. With `#<item>` (an item id such as `ASK-2`, or a section number, §7.11), only that item is replaced and the rest of the earlier message stands. It mainly lets tools mark the old message stale; send the correction to everyone who received the original. |

All §3.2 fields are genuinely optional and channel-dependent — a richly-routed office inbox may use several; a public channel like Moltbook may use none. Emit only the optional fields that carry signal in your context; never pad the header. For calibration: across 632 real messages in one estate, `thread=`, `status=`, `a2al=` and `evidence=` were never used, while `refs=`, `urgency=` and `cc=` were used constantly. That is why 0.5.2 adds only one field.

### 3.3 Example

```text
from=Wren(PM); to=Calder(DW-Arch); date=2026-05-09; topic=bump US-006 + US-009-a; audience=agent; urgency=high
US-006: A=in-place fast no-rollback; B=shadow +1sprint rollback-safe; ASK=pick A|B
US-009-a: opt1=F-SKU-lib saves-3d bug=#44-memleak; opt2=wrap-REST clean +3d; ASK=pick opt1|opt2
deadline=2026-05-09T17:00 -- F-SKU trial closes EOD
```

The header is line 1. The body follows on subsequent lines per the body rule (§2.1) and the style rules (§4).

Names in examples (in this spec, the skill and `examples/`) are placeholders. Never sign a message with an example identity; use your own name and role.

With the optional 0.5.0 fields, a richly-routed office message looks like:

```text
from=Calder(DW-Arch); to=Wren(PM); cc=Sable(SEC), Corvin(Arch); date=2026-06-10; topic=B-293 gates MCP groom; thread=B-293; status=blocked; priority=P1; in-reply-to=joint-workstream
B-293 blocked: MCP groom must land first -- Fabric connector contract not frozen.
ack?
```

### 3.4 Why the header is mandatory

The first agent to use A2AL in real work (Ledger, a PM agent, May 2026) reported that the routing header carried more value than the body shorthand. Later field data points the same way. On an agent social platform, readers picked up the header and ignored the body. A six-agent fleet put the header on 79 of 79 and 138 of 140 notes, over a plain Markdown body. A five-agent estate kept the header on all 632 messages over four months while the bodies drifted back toward prose (there the header was required by policy, so that shows it is cheap to sustain, not that agents chose it). Without the header, receiving agents triangulate sender/topic from the body's first paragraph; with it, the same information arrives in one parseable line. The header pays back its tokens on the first read and again on every re-read or archive scan. Tooling (inbox routers, archive scanners, future validators) gets a stable parse target. Adopting the header alone is worth the protocol's overhead even when the body's compression isn't a clear win.

### 3.5 Version signalling and fail-soft decode *(since 0.5.1)*

Forward compatibility (§6, and the library's central invariant) says a reader that meets an unknown token preserves it verbatim rather than erroring. That keeps the *message* intact, but it leaves the *reader* unable to tell the difference between two very different situations:

- a token it does not recognise because the sender coined it inline, and
- a token it does not recognise because the sender is writing a **newer version of the spec than the reader knows**.

The first is routine. The second is a silent degradation: the reader parses what it can, drops meaning it never knew to look for, and reports success. A real-agent field report named this directly — *"if sender writes 0.5 and receiver only knows 0.4, parsing degrades silently. Markdown does not have that failure mode."*

The optional `a2al=<version>` field closes it.

**Writer (SHOULD).** Emit `a2al=<version>` when writing to a channel whose readers may be on other versions — a public channel, a cross-org inbox, a newly-onboarded peer. Omit it on a settled intra-workspace channel where every agent is known to load the same library; there it is pure overhead.

**Reader (MUST, when the field is present).** Compare the sender's version to your own:

| Comparison | Obligation |
|---|---|
| Sender **equal or older** | Proceed normally. Nothing to report. |
| Sender **newer in patch or minor** | Parse normally — 0.x.x releases are additive — but **surface the mismatch**. Unrecognised header fields and tokens are still preserved verbatim; say which ones you could not interpret. |
| Sender **newer in major** | Parse what you can and **flag the message as possibly incompletely understood** before acting on it. A major bump may have changed style rules, not just added vocabulary. |
| No `a2al=` field | Assume compatible and proceed. Absence is not an error; the field is optional. |

Surfacing means telling the next agent or human in the chain, in whatever form that channel uses — not raising an error and not discarding the message. A reader that cannot fully interpret a message still relays it intact.

```text
from=shell-prompt(field-test); to=Lex(A2AL-maintainer); date=2026-09-22; topic=wave-7 parse results; a2al=0.5.1
```

A 0.4.x reader meeting that header does not recognise `a2al=`, preserves it verbatim per §6, and proceeds — which is the correct degradation, and exactly why the field is optional rather than required. The field pays off from the first reader that *does* know it.

**This is a reader obligation, not a validation gate.** A2AL never validates message bodies. The header lint (§3.1) is advisory, and a version mismatch is never grounds for rejecting a message.

## 4. Style Rules

These rules apply to shorthand bodies (§2.1). A prose or Markdown body follows ordinary good writing: say the verdict first and cut the padding.

### 4.1 Drops

| Drop | Why |
|---|---|
| Articles (`the`, `a`, `an`) | Each is 1 token; usually adds nothing |
| Helping/linking verbs in declarative state (`is`, `are`, `was`) | Often droppable: "US-713 *is* done" → "US-713 done" |
| Subjective framing (`I think`, `it seems`, `we believe`) | Bias signal, not information |
| Politeness (`please`, `could you`, `would you mind`) | Inter-agent — politeness is wasted tokens |
| Filler phrases (`in order to` → `to`; `due to the fact that` → `because`) | Pure padding |
| Repeated subjects in compound sentences | Use `;` instead: "X done; tests pass; PR ready" |

### 4.2 Uses

- Sentence fragments instead of full sentences
- Imperative mood for actions: `merge X`, not `please merge X`
- Past tense / status adjectives for state: `done`, `blocked`, `shipped`, `passed`, `failed`
- Standard tech jargon that tokenizes as 1 token: `PR`, `AC`, `CI`, `CD`, `DQ`, `QA`, `PM`, `RCE`, `CVE`, `CVSS`, `MR`
- IDs as bare tokens: `US-713`, `commit-98b483d`, `T-202`

### 4.3 Format conventions

- One fact per fragment
- `;` between related facts (same topic): `US-713 done; AC met; CI green`
- `.` (or newline) between unrelated facts
- `:` after a subject to expand: `US-713: AC met but CI broke`
- `/` for ratios: `21/21 tests`, `878/878 preflight`
- `?` for questions/asks: `merge?`, `block on US-718?`
- `--` to attach an inline rationale: `defer US-718 -- no source in Silver`

### 4.4 Anti-patterns

- ❌ **Creative abbreviations** (`cmplt`, `prgm`, `mrg`) — often tokenize as 2–3 tokens; the full word is usually 1
- ❌ **Rare Unicode symbols** (✓ ⟳ ✗ →) — usually multi-token in common tokenizers
- ❌ **Dropping critical context** for terseness (e.g., dropping the story ID makes the message unactionable — false economy)
- ❌ **Stacking facts without separators** — harder for the receiver to parse
- ❌ **Omitting the routing header** (§3) — non-conformant; the header is MUST, not SHOULD

### 4.5 Length and emphasis *(since 0.5.2)*

- A shorthand body SHOULD stay under about 8 lines. Past that, the message is probably carrying reasoning: write the verdict line, then prose (§2.1), or link a Markdown document. In one estate, where shorthand bodies were required, the median body still reached 500 words, and the team's own inbox rule ended up saying to archive long messages "condensed to a summary".
- Don't use Markdown bold or headings inside a shorthand body. For emphasis, use the capitalised state token the library already has (`BLOCKED`, `PARTIAL`). A prose body can use Markdown normally.

## 5. Vocabulary Library

The vocabulary lives in [`library/`](../library) — one YAML file per domain. Always-loaded core: [`library/core.yaml`](../library/core.yaml).

**A2AL is not a software protocol.** The core mechanics — the audience rule, the routing header, the style rules, forward compatibility — describe how *any* two coordinating agents exchange state and intent. Nothing in them assumes code. The patterns in §7 are general coordination shapes: a state change, a status report, a directive, a blocker, a question, a decision, an acknowledgment. Those occur on a construction programme, a clinical rollout, a legal matter, a marketing campaign, and a software sprint alike.

What *is* domain-specific is vocabulary, and that is exactly what the domain-extension model exists to hold. An industry adds a domain file; it changes nothing about the spec.

The shipped domains lean toward software because that is where A2AL was first exercised — technology teams adopt new tooling quickly, so they generated the first real traffic. Treat software as **one worked domain, not the reference domain**. A domain file for field services, clinical operations, or underwriting is exactly as legitimate, and needs no spec change to add.

| File | Scope |
|---|---|
| [`core.yaml`](../library/core.yaml) | Universal coordination vocabulary — states, actions, severity. Always loaded. |
| [`project-mgmt.yaml`](../library/project-mgmt.yaml) | Cross-industry project and program management (`milestone`, `deliverable`, `change-order`, `RFI`, `RAID`, `WBS`, `stakeholder`, `baseline`, `go-live`) |
| [`programming.yaml`](../library/programming.yaml) | Software development and code review (`MR`, `CR`, `IaC`, `code-complete`, `EM`, `TPM`) |
| [`infrastructure.yaml`](../library/infrastructure.yaml) | Cloud, orchestration, data, and service operations (`DAG`, `ETL`, `k8s`, `SLA`, `SLO`, `MTTR`, `SRE`) |
| [`security.yaml`](../library/security.yaml) | Security threats and controls (`RCE`, `CVE`, `CVSS`, `MFA`, `IAM`, `RBAC`) |
| [`ai-agents.yaml`](../library/ai-agents.yaml) | Agents and LLMs (`LLM`, `MCP`, `A2A`, `RAG`) |
| [`azure.yaml`](../library/azure.yaml) | Microsoft identity, compliance, and Fabric data platform (`Entra`, `MI`, `OBO`, `PHI`, `Purview`, `OneLake`, `RLS`) |

See [`library/README.md`](../library/README.md) for entry schema and loading model.

The library is open and contributable. To propose a new term, open a PR adding an entry to the appropriate domain file (or core, if genuinely universal). A new *industry* is a new domain file — propose it in an issue first. Run `python tools/validate_library.py` locally first.

> **Note (0.5.1).** `project-mgmt.yaml` previously held SRE and service-operations terms despite its name, so a non-software project manager opening the file named for their role found nothing they used. Those terms moved to `infrastructure.yaml`, the software roles to `programming.yaml`, and `project-mgmt.yaml` now holds genuinely cross-industry project vocabulary. No term was removed or renamed.

## 6. Extending the Vocabulary

### 6.1 Inline definition

A new shortening is introduced on first use with `term=expansion`:

```
DR=design-review. DR sched Tuesday; PR ready post-DR; AC sign-off needed post-DR.
```

After the first use, the receiver may use bare `DR` for the rest of the thread. The definition runs until the next sentence-terminating punctuation (`.`, `;`, `?`, `!`, `--`, newline). The expansion itself should be a single word or hyphenated phrase without internal spaces or `--`.

### 6.2 Scope

| Scope | Behavior |
|---|---|
| **Per-thread** (default) | Terms defined in a thread are valid for all subsequent messages in that thread. New thread = clean slate. |
| Per-pair | (Optional) Agents may keep a local note file of terms they've adopted with each peer. Implementation-specific; not part of the spec. |
| Repo-canonical | Promoted via PR after the user reviews accepted terms. |

### 6.3 Implicit acceptance

Acceptance is signaled by the receiver using the term in their reply. If the receiver doesn't recognize:

- They may ignore the shortening and reply in canonical-glossary form
- They may ask: `?DR` or `DR=?` to request a definition
- They may propose an alternative: `DR=design-review (or DRev?)`

### 6.4 When to introduce a shortening

Net-positive only when the term will be used 3+ times in the thread. Defining once costs the definition tokens (`DR=design-review` ≈ 4 tokens) plus the bare uses.

**Rule of thumb: 3 uses in a thread = define it; fewer = don't.**

### 6.5 Anti-patterns

- ❌ Re-defining a canonical term: don't write `PR=pull-request`. `PR` is already canonical.
- ❌ Cryptic single letters: `D=delta`, `S=status` — comprehension cost outweighs savings; ambiguity with A2AL lane tags.
- ❌ Renegotiating mid-thread: once defined, stick with the form.

### 6.6 Promotion to canonical glossary

1. **Adopted in the wild** — agents define and use new shortenings in real conversations using `term=expansion` syntax
2. **Captured locally** — user (or a periodic agent task) collects shortenings used 5+ times across multiple threads
3. **Reviewed** — proposer evaluates the candidate against criteria: tokenizes well, unambiguous, broadly applicable
4. **Promoted** — open a PR adding an entry to `library/<domain>.yaml`. CI runs `tools/validate_library.py` to enforce schema and uniqueness.
5. **Documented** — `VersionHistory.md` lists library minor-version bumps when entries are added.

Vocabulary additions = minor versions. Structural changes to the style rules = major.

## 7. Patterns

Each pattern below shows only the body line(s). Every real message also carries the routing header (§3) as line 1.

### 7.1 Single-fact state change

**Form:** `<id> <state>`. Body example: `US-713 done`

### 7.2 Multi-fact state with details

**Form:** `<id> <state>; <fact>; <fact>; ...`. Body example: `US-713 done; AC met; CI green; PR ready`

### 7.3 Status report

**Form:** `<metric> <value>; <metric> <value>; ...`. Body example: `tests 21/21; preflight 878/878; ruff pass; build green`

### 7.4 Action directive

**Form:** `<verb> <target>` or `<actor>: <verb> <target>`. Body example: `merge pell/auth-fix`

### 7.5 Blocker notification

**Form:** `<id> blocked: <reason>`. Body example: `US-718 blocked: no household source in Silver`

### 7.6 Question / quick ask

**Form:** `<verb>?` or `<id> <verb>?`. Body example: `merge?`, `US-713 sign-off?`

### 7.7 Decision communication

**Form:** `<decision>: <id|target> -- <rationale>`. Body example: `approved: US-713 PRD -- 1 AC added`

### 7.8 Acknowledgment

**Form:** `ack <id>` or just `ack`. Body example: `ack US-713 closeout`

### 7.9 Full message (header + body)

```text
from=Tamsin(DEV); to=Wren(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

### 7.10 Attestation handshake

**Form:** a multi-message bilateral commitment carried in the routing header — `thread=` (ceremony id), `status=` transitions (`pending` → `ack` → `done`, `endorse` for the witness), `in-reply-to=` (commitment order), `cc=` (neutral witness), `evidence=` (verifiable record). The body enumerates committed scope and an explicit `EXCLUDES {…}` list.

This is the canonical **require-the-header** case (§3.4): the commitment record lives in the header, not the body, so the header is not elidable. Full worked example: [`examples/attestation-handshake.md`](../examples/attestation-handshake.md).

### 7.11 Body conventions *(since 0.5.2)*

These came from agents in the field, not from the spec. Each costs a few tokens and, in the traffic where it was seen, saved a follow-up round trip. All are optional, and all work in shorthand and prose bodies alike.

| Convention | Form | Why |
|---|---|---|
| Verdict first | The first body line is the outcome or the ask | A reader who stops at line 2 still has it, and `topic=` stays a label |
| Item ids | `ASK-1`, `ASK-2`, … for several asks or findings; `# 1.`, `# 2.` section markers for several rulings | Replies and `supersedes=<id>#<item>` can point at one item; one reviewer checked a 30-item reply one ruling at a time |
| Per-recipient actions | One line per actor: `Wren: rule on B-765` (§7.4) | Two recipients, two different actions, no extra header field |
| Void condition | Last line of a ruling: `void-if <condition>` | Receivers acted on 7 of 7 rulings with no follow-up question |
| What is blocked | Last line: `blocks <what>`, alongside `urgency=` | `urgency=` says how soon; this says what stalls |
| Silence means default | `default: <what happens> if no reply by <date> -- check: <name>` | Proceeding on silence needs a named agent or person who checks |
| Relayed words, human asks | `relay(<person>): "…"`, `ASK(<person>): …` | See §2.6 |
