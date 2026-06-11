# A2AL — `A2AL/0.5.0` Core Specification

**Status:** Normative. A2AL/0.5.0 adds four optional routing-header fields (`thread`, `status`, `cc`, `priority`) and a substantial vocabulary expansion (core additions + the new `azure` identity/compliance/Fabric domain), all backward-compatible with 0.4.x. Supersedes A2AL/0.4.1 (audience rule + routing header). The deprecated A2AL/0.3.0 JSON envelope spec is archived.
**See also:** [`README.md`](../README.md), [`library/`](../library), [`examples/`](../examples), [`examples/ClaudeCode/skills/a2al/`](../examples/ClaudeCode/skills/a2al)

A2AL is an open vocabulary library and shorthand style guide for token-efficient agent-to-agent communication. It is plain text — no JSON envelope, no parser dependency. Agents share a common dictionary (`library/core.yaml`) and load domain extensions (`library/<domain>.yaml`) as needed.

A2AL is a *style guide* and *recommended jargon palette* for agent-to-agent messages, paired with an open contributable vocabulary library at [`library/`](../library). It is plain text — not a JSON wire format. It is not a constructed/symbolic language; it is a tight dialect of English chosen to tokenize efficiently on Claude's vocabulary (and other modern LLM tokenizers).

## 1. Goals & Non-Goals

### Goals

- ~40–50% token reduction vs verbose English on conversational/status traffic
- Zero per-session dictionary overhead — relies on the LLM's existing English training
- LLM-fluent on both write and read without specialized training

### Non-Goals

- Not a JSON wire format (plain text, no envelope)
- Not a constructed/symbolic language
- Not a replacement for human-readable Markdown — use Markdown when the audience is human
- Not a structured wire envelope (the /0.3.0 JSON envelope was archived after empirical token-cost data showed it cost 1.46×–3.55× more than plain Markdown)
- Not aimed at maximum compression at any cost — accepts the tokenizer reality and stops at the natural English-jargon floor
- Not intended to distinguish parse-failure from non-engagement — on a consensus-free platform without read receipts, silence may reflect inability to parse, lack of interest, or other causes.

### Optimization target

Minimize tokens on Claude's tokenizer specifically. The design uses single-token English words and standard tech jargon, both of which Claude's BPE handles efficiently.

## 2. When to use A2AL

A2AL is for **agent-to-agent communication** — messages between AI agents (or between automated processes) with no human in the audience. The format is plain text, designed to be produced and consumed by an LLM with the library loaded into its system prompt.

### 2.1 Audience rule (normative)

The audience determines the format. There is no hybrid mode and no duplication — pick one and write only that one.

- **Agent-only audience → A2AL MUST.** Both sender and intended recipients are agents; no human review or human consumption is expected. A2AL is required; writing Markdown in an agent-only channel wastes tokens.
- **Human in the audience → Markdown.** The message will be read or reviewed by a human at any point (PM triage, archival reading, decision-trail review). Write Markdown.
- **Default → Markdown.** When the audience is ambiguous or mixed, default to Markdown. A2AL is opt-in, signalled by channel convention or explicit declaration.

### 2.2 Reactive rule (normative)

If a sender identifies itself as an AI agent (via the routing header, §3, or another agent-marker), the reply MUST be A2AL. This is the simplest unambiguous trigger: agent-identified inbound → agent-format reply.

### 2.3 Channel signals

A2AL-mandatory channels can be declared two ways:

- **By convention.** A repo or workspace marks specific paths as agent-only (e.g., `agent-channel/`, `*/inbox-internal/`, `.a2a/`). All traffic in those paths is A2AL.
- **By message.** A sender explicitly declares `audience=agent` in the routing header (§3). Replies in the same thread MUST be A2AL, regardless of channel.

If neither signal is present, the channel is assumed mixed and Markdown is the right default.

### 2.4 Non-uses

A2AL is NOT for:

- Messages a human will read or review at any point. Even if the immediate recipient is an agent, if a human is downstream, write Markdown.
- Long-form deliberation, RCAs, architectural decision records, design specs — these are documents with shelf-life and humans return to them.
- Transport metadata (timestamps, signatures, routing fabric) — out of scope; A2AL is payload, not transport.

For the historical record, A2AL/0.3.0 used a JSON envelope; that approach was archived after empirical token-cost data showed it cost 1.46×–3.55× more than plain Markdown on real conversational traffic. See tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0).

## 3. Routing Header (normative)

Every A2AL message MUST begin with a single-line routing header. The header tokenizes well, gives downstream tooling a stable substring to grep, and tells the receiver who/what/when in one line — exactly the work the body's first paragraph used to do in Markdown.

### 3.1 Required fields

Header shape: `from=<sender>; to=<recipient>; date=<ISO>; topic=<short label>`

| Field | Format |
|---|---|
| `from` | `<Name>(<Role>)` or `<Name>/<Role>` — e.g. `Ledger(PM)`, `Kunai/DW-Arch`. Role is free-form. |
| `to` | Same shape as `from`. Multiple recipients comma-separated: `to=Byte(DEV), Hawkeye(QA)` |
| `date` | ISO 8601 date (`2026-05-13`) or datetime (`2026-05-13T15:30Z`) |
| `topic` | Free-form short label. No internal `;`. |

Fields are separated by `; ` (semicolon + space). The header is one line and ends at the first newline.

### 3.2 Optional fields

| Field | Purpose |
|---|---|
| `audience=agent\|mixed` | Declares agent-only intent (§2.2). When `agent`, replies MUST be A2AL. |
| `urgency=low\|medium\|high\|urgent` | Receiver-side prioritization signal (how *fast*). |
| `refs=<id>, <id>, ...` | Citations to commits, story IDs, file paths, prior messages. Comma-separated. |
| `in-reply-to=<message-id>, ...` | Immediate-parent reply link(s) when the channel has message IDs. Comma-separated for a reply that closes multiple parents. |
| `thread=<id>` | Stable conversation/topic-group id — often a ticket or epic key (`thread=US-940`). Distinct from `in-reply-to`: `thread` groups a whole multi-message conversation; `in-reply-to` links one prior message. |
| `status=<state>` | Overall status of the message's subject, as a core state token (`green`, `red`, `blocked`, `done`, `sent`). Useful for status/stoplight traffic. |
| `cc=<recipient>, ...` | Informational (copy) recipients, same shape as `to`. Comma-separated. |
| `priority=P0\|P1\|P2\|P3` | Triage priority — distinct from `urgency` (how fast) and from severity tokens (`crit`/`high`/`med`/`low`). |

All §3.2 fields are genuinely optional and channel-dependent — a richly-routed office inbox may use several; a public channel like Moltbook may use none. Emit only the optional fields that carry signal in your context; never pad the header.

### 3.3 Example

```text
from=Ledger(PM); to=Kunai(DW-Arch); date=2026-05-09; topic=bump US-006 + US-009-a; audience=agent; urgency=high
US-006: A=in-place fast no-rollback; B=shadow +1sprint rollback-safe; ASK=pick A|B
US-009-a: opt1=F-SKU-lib saves-3d bug=#44-memleak; opt2=wrap-REST clean +3d; ASK=pick opt1|opt2
deadline=2026-05-09T17:00 -- F-SKU trial closes EOD
```

The header is line 1. The body follows on subsequent lines per the style rules (§4).

With the optional 0.5.0 fields, a richly-routed office message looks like:

```text
from=Kunai(DW-Arch); to=Ledger(PM); cc=Audrey(SEC), Archer(Arch); date=2026-06-10; topic=B-293 gates MCP groom; thread=B-293; status=blocked; priority=P1; in-reply-to=atlas-joint-workstream
B-293 blocked: MCP groom must land first -- Fabric connector contract not frozen.
ack?
```

### 3.4 Why the header is mandatory

Live-usage feedback from three independent agents converged on the same finding: the routing header carries more value than the body shorthand. Without it, receiving agents triangulate sender/topic from the body's first paragraph; with it, the same information arrives in one parseable line. The header pays back its tokens on the first read and again on every re-read or archive scan. Tooling (inbox routers, archive scanners, future validators) gets a stable parse target. Adopting the header alone is worth the protocol's overhead even when the body's compression isn't a clear win.

## 4. Style Rules

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
- ❌ **Rare Unicode symbols** (✓ ⟳ ✗ →) — usually multi-token in Claude's vocab
- ❌ **Dropping critical context** for terseness (e.g., dropping the story ID makes the message unactionable — false economy)
- ❌ **Stacking facts without separators** — harder for the receiver to parse
- ❌ **Omitting the routing header** (§3) — non-conformant; the header is MUST, not SHOULD

## 5. Vocabulary Library

The vocabulary lives in [`library/`](../library) — one YAML file per domain. Always-loaded core: [`library/core.yaml`](../library/core.yaml) (~87 universal terms). Domain extensions:

- [`library/programming.yaml`](../library/programming.yaml) — code-review and dev-process specifics (`MR`, `CR`, `IaC`, `code-complete`, etc.)
- [`library/infrastructure.yaml`](../library/infrastructure.yaml) — cloud/orchestration/data (`DAG`, `ETL`, `k8s`, `AWS`, `Azure`, `GCP`, `VPC`, `VNet`, etc.)
- [`library/project-mgmt.yaml`](../library/project-mgmt.yaml) — specialized roles and SRE/ops vocabulary (`EM`, `TPM`, `SRE`, `SLA`, `SLO`, `SLI`, `MTTR`, `RCA`)
- [`library/security.yaml`](../library/security.yaml) — security threats and controls (`RCE`, `XSS`, `SSRF`, `CVE`, `CVSS`, `OWASP`, `MFA`, `IAM`, `RBAC`)
- [`library/ai-agents.yaml`](../library/ai-agents.yaml) — agents/LLM-specific (`LLM`, `MCP`, `A2A`, `RAG`, `KV`)
- [`library/azure.yaml`](../library/azure.yaml) — Microsoft/Azure identity, compliance, and Fabric data-platform (`OBO`, `MI`, `Entra`, `MSAL`, `JWT`, `PHI`, `PII`, `BAA`, `DLP`, `Purview`, `Fabric`, `OneLake`, `RLS`, etc.)

See [`library/README.md`](../library/README.md) for entry schema and loading model.

The library is open and contributable. To propose a new term, open a PR adding an entry to the appropriate domain file (or core, if universal). Run `python tools/validate_library.py` locally first.

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

**Form:** `<verb> <target>` or `<actor>: <verb> <target>`. Body example: `merge ralph/auth-fix`

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
from=Byte(DEV); to=Ledger(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```
