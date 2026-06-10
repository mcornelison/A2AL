# A2A Shorthand 0.1.0 — Design

**Date:** 2026-05-05
**Status:** Approved design, pre-implementation. Sibling to A2AL/0.3.0 — not a replacement.
**Owner:** Michael Cornelison
**Origin:** Test result `testing/agent2/analysis.md` showed A2AL/0.3.0 used 1.86× the tokens of plain MD on a pure-prose welcome handshake. A2AL's envelope (~150 tokens) only amortizes on structured payloads. This design fills the gap below A2AL's break-even threshold with a leaner format.

---

## 1. Scope and Naming

**Working name:** **A2A Shorthand**, versioned `a2a-shorthand/0.1.0`. Independently versioned from A2AL.

**What it is:** A *style guide* and *recommended jargon palette* for agent-to-agent messages. Not a JSON wire format — plain text. Not a constructed/symbolic language — a tight dialect of English designed to tokenize efficiently on Claude's vocabulary.

### 1.1 Goals

- ~40–50% token reduction vs verbose English on conversational/status traffic
- **Zero per-session dictionary overhead** — relies on the LLM's existing English training; no glossary loaded into system prompt
- LLM-fluent on both write and read without specialized training
- Coexists with A2AL/0.3.0 — different tool for different message shapes

### 1.2 Non-Goals

- Not a JSON wire format (plain text, no envelope)
- Not a constructed/symbolic language (intentionally rejected after considering the tradeoffs)
- Not a replacement for A2AL/0.3.0
- Not aimed at maximum compression at any cost — accepts the tokenizer reality and stops at the natural English-jargon floor

### 1.3 Optimization Target

Minimize tokens on **Claude's tokenizer specifically** (not byte count, not tokenizer-agnostic length). The design uses single-token English words and standard tech jargon, both of which Claude's BPE handles efficiently.

---

## 2. When to use Shorthand vs A2AL/0.3.0

The two formats are complementary. Decision rule for the writer:

```
if message has 5+ structured items in ANY category (delta/status/risk/etc)
   OR spans 3+ section types
   OR needs structured citations (refs)
   OR is a formal record (sprint closeout, decision log, risk brief):
       → use A2AL/0.3.0
elif message is conversational, short, declarative, or single-purpose:
       → use A2A Shorthand
else (in between):
       → A2A Shorthand by default; promote to A2AL if it grows
```

In numbers: the breakeven point is roughly **5–7 structured items**. Below that, A2AL's envelope dominates and net token cost rises; above that, the structure compresses and A2AL wins.

| Message shape | Use |
|---|---|
| Handshakes, acks, single-fact updates | A2A Shorthand |
| Conversational coordination ("merge?", "blocked on X") | A2A Shorthand |
| Status updates with ≤3 metrics or ≤3 deltas | A2A Shorthand |
| Sprint closeouts, multi-section reports, ≥5 deltas | A2AL/0.3.0 |
| Risk briefs with multiple findings + citations | A2AL/0.3.0 |
| Anything that compresses well into structured sections | A2AL/0.3.0 |

---

## 3. Style Rules

The rules are **drops** (omit by default), **uses** (preferred forms), and **format conventions** (separators).

### 3.1 Drops

| Drop | Why |
|---|---|
| Articles (`the`, `a`, `an`) | Each is 1 token; usually adds nothing |
| Helping/linking verbs in declarative state (`is`, `are`, `was`) | Often droppable: "US-713 *is* done" → "US-713 done" |
| Subjective framing (`I think`, `it seems`, `we believe`) | Bias signal, not information |
| Politeness (`please`, `could you`, `would you mind`) | Inter-agent — politeness is wasted tokens |
| Filler phrases (`in order to` → `to`; `due to the fact that` → `because`) | Pure padding |
| Repeated subjects in compound sentences | Use `;` instead: "X done; tests pass; PR ready" |

### 3.2 Uses

- **Sentence fragments** instead of full sentences
- **Imperative mood** for actions: `merge X`, not `please merge X`
- **Past tense / status adjectives** for state: `done`, `blocked`, `shipped`, `passed`, `failed`
- **Standard tech jargon** that tokenizes as 1 token: `PR`, `AC`, `CI`, `CD`, `DQ`, `QA`, `PM`, `RCE`, `CVE`, `CVSS`, `MR`
- **IDs as bare tokens**: `US-713`, `commit-98b483d`, `T-202`

### 3.3 Format conventions

- One fact per fragment
- `;` between related facts (same topic): `US-713 done; AC met; CI green`
- `.` (or newline) between unrelated facts
- `:` after a subject to expand: `US-713: AC met but CI broke`
- `/` for ratios: `21/21 tests`, `878/878 preflight`
- `?` for questions/asks: `merge?`, `block on US-718?`
- `--` to attach an inline rationale: `defer US-718 -- no source in Silver`

### 3.4 Anti-patterns (don't)

- ❌ **Creative abbreviations** (`cmplt`, `prgm`, `mrg`) — often tokenize as 2–3 tokens; the full word is usually 1
- ❌ **Rare Unicode symbols** (✓ ⟳ ✗ →) — usually multi-token in Claude's vocab
- ❌ **Dropping critical context** for terseness (e.g., dropping the story ID makes the message unactionable — false economy)
- ❌ **Stacking facts without separators** — harder for the receiver to parse and may save zero tokens

---

## 4. Recommended Glossary

A curated palette of words and abbreviations that almost certainly tokenize as **1 token** in Claude's vocabulary. Use these by default; the LLM's full vocabulary is available beyond this list, but these are the safe, validated picks.

> Caveat: token counts here are estimates based on common-English BPE behavior. Before locking the glossary into a published spec, validate with the actual Anthropic tokenizer (`anthropic.tokenizers.count_tokens` or the SDK's tokenization endpoint).

### 4.1 States

`done`, `complete`, `finished`, `shipped`, `deployed`, `merged`, `released`, `passed`, `passing`, `ok`, `green`, `healthy`, `working`, `ready`, `pending`, `waiting`, `queued`, `started`, `active`, `paused`, `stalled`, `deferred`, `blocked`, `failed`, `failing`, `broken`, `red`, `yellow`

### 4.2 Actions (verbs — imperative)

`merge`, `ship`, `deploy`, `release`, `push`, `pull`, `revert`, `rollback`, `review`, `approve`, `reject`, `sign-off`, `block`, `unblock`, `defer`, `escalate`, `assign`, `claim`, `release`, `test`, `verify`, `validate`, `implement`, `fix`, `patch`, `refactor`, `document`, `add`, `remove`, `modify`

### 4.3 Domain abbreviations

| Cluster | Terms |
|---|---|
| Code/process | `PR`, `MR`, `CR`, `AC`, `CI`, `CD`, `DQ`, `IaC` |
| Roles | `PM`, `QA`, `DEV`, `EM`, `TPM`, `SRE`, `DEVOPS`, `SEC`, `ARCH`, `PMO` |
| Quality/SLA | `SLA`, `SLO`, `SLI`, `MTTR`, `RCA` |
| Security | `RCE`, `XSS`, `SSRF`, `SQLi`, `CVE`, `CVSS`, `OWASP`, `MFA`, `IAM`, `RBAC` |
| API/infra | `API`, `SDK`, `CLI`, `DAG`, `ETL`, `ELT`, `DB`, `k8s`, `AWS`, `Azure`, `GCP`, `VPC`, `VNet` |
| Agents/AI | `LLM`, `MCP`, `A2A`, `RAG`, `KV` |

### 4.4 Severity (5 levels, single-token)

`crit`, `high`, `med`, `low`, `info`

(Same scale as A2AL/0.3.0 risk profile — kept consistent so messages move between formats cleanly.)

### 4.5 Multi-token but worth it

Some phrases are 2–3 tokens but still net-positive when they replace longer English. Use sparingly:

- `code-complete` (vs "the code is finished") — ~2 tokens vs ~5
- `feature-flag` (vs "feature flag controlled by config") — ~2 tokens vs ~7
- `dead-letter` (vs "messages that failed processing and were moved aside") — ~3 tokens vs ~12

### 4.6 What NOT to put in the glossary

- ❌ Vowel-dropped forms (`cmplt`, `prgm`, `mrg`) — usually 2–3 tokens
- ❌ Single-letter codes (`c`, `b`, `r`) — ambiguous; comprehension cost exceeds the token saving
- ❌ Emoji or rare Unicode (✓ ✗ ⟳ 🟢 🔴) — tokenization is unpredictable, often expensive
- ❌ Greek letters used as variables (`Δ`, `λ`) — sometimes 1 token but inconsistent across tokenizer versions

### 4.7 Scope

The "palette" is a recommended starting set, not an enforced vocabulary. Writers may use any term in standard form (e.g., `Spark`, `Fabric`, `OAuth2`) — the receiver reads English without a dictionary.

---

## 5. Extending the Vocabulary

Agents introduce new shortenings inline. Useful ones get promoted to the canonical glossary in future spec versions.

### 5.1 Inline definition syntax

A new shortening is introduced on **first use** with `term=expansion`:

```
DR=design-review. DR sched Tuesday; PR ready post-DR; AC sign-off needed post-DR.
```

After first use, the receiver may use bare `DR` for the rest of the **thread**. The definition runs until the next sentence-terminating punctuation (`.`, `;`, `?`, `!`, `--`, newline). The expansion itself should be a single word or hyphenated phrase without internal spaces or `--`.

### 5.2 Scope: per-thread persistence

| Scope | Behavior |
|---|---|
| **Per-thread** (default) | Terms defined in a thread are valid for all subsequent messages in that thread. New thread = clean slate. |
| Per-pair | (Optional) Agents may keep a local note file of terms they've adopted with each peer. Implementation-specific; not part of the spec. |
| Repo-canonical | Promoted via PR after the user reviews accepted terms. |

### 5.3 Implicit acceptance

There is no explicit "accept" message. Acceptance is signaled by **the receiver using the term in their reply**. If the receiver doesn't recognize or doesn't want to adopt:

- They may ignore the shortening and reply in canonical-glossary form
- They may ask: `?DR` or `DR=?` to request a definition (or re-definition)
- They may propose an alternative: `DR=design-review (or DRev?)`

Disagreements resolve by the writer choosing — first-mover usually wins for the thread, or both agents revert to canonical English until they sync up.

### 5.4 When to introduce a shortening

Net-positive only when the term will be **used 3+ times** in the thread. Defining once costs the definition tokens (`DR=design-review` ≈ 4 tokens) plus the bare uses. If used once or twice, write the full form.

**Rule of thumb: 3 uses in a thread = define it; fewer = don't.**

### 5.5 Anti-patterns

- ❌ **Re-defining a canonical term**: Don't write `PR=pull-request`. `PR` is already canonical.
- ❌ **Cryptic single letters**: `D=delta`, `S=status` — comprehension cost outweighs savings; ambiguity with A2AL/0.3.0 lane tags.
- ❌ **Renegotiating mid-thread**: Once defined, stick with the form for the thread.

### 5.6 Promotion to canonical glossary

Workflow for moving accepted shortenings into the spec:

1. **Adopted in the wild** — agents define and use new shortenings in real conversations
2. **Captured locally** — user (or a periodic agent task) collects shortenings used 5+ times across multiple threads
3. **Reviewed** — user evaluates each candidate against the criteria: tokenizes well, unambiguous, broadly applicable
4. **Promoted** — added to `specs/A2A-Shorthand.md` glossary in a minor version bump (e.g., `0.1.0` → `0.2.0`)
5. **Documented** — `VersionHistory.md` lists the new vocabulary additions

Vocabulary additions = minor versions. Structural changes to the style rules = major.

A future helper script could parse agent inboxes for `term=expansion` patterns and surface candidates for promotion. For `0.1.0`, manual curation is sufficient.

---

## 6. Patterns

Common message shapes in shorthand form, with verbose equivalents.

### 6.1 Single-fact state change

**Form:** `<id> <state>`

| Verbose (~5) | Shorthand (~3) |
|---|---|
| "US-713 is now complete." | "US-713 done" |

### 6.2 Multi-fact state with details

**Form:** `<id> <state>; <fact>; <fact>; <fact>`

| Verbose (~22) | Shorthand (~10) |
|---|---|
| "US-713 is complete. All acceptance criteria are met. CI is green. PR is ready." | "US-713 done; AC met; CI green; PR ready" |

### 6.3 Status report

**Form:** `<metric> <value>; <metric> <value>; ...`

| Verbose (~22) | Shorthand (~12) |
|---|---|
| "All 21 tests passed. Preflight passed 878 of 878. Ruff passed. The build is green." | "tests 21/21; preflight 878/878; ruff pass; build green" |

### 6.4 Action directive

**Form:** `<verb> <target>` or `<actor>: <verb> <target>`

| Verbose (~11) | Shorthand (~5) |
|---|---|
| "Could you please merge the auth-fix branch?" | "merge ralph/auth-fix" |

### 6.5 Blocker notification

**Form:** `<id> blocked: <reason>`

| Verbose (~17) | Shorthand (~9) |
|---|---|
| "US-718 is blocked because there is no household source available in the Silver layer." | "US-718 blocked: no household source in Silver" |

### 6.6 Question / quick ask

**Form:** `<verb>?` or `<id> <verb>?`

| Verbose (~6) | Shorthand (~2) |
|---|---|
| "Are you ready to merge?" | "merge?" |

### 6.7 Decision communication

**Form:** `<decision>: <id|target>` (optional rationale appended after `--`)

| Verbose (~12) | Shorthand (~6) |
|---|---|
| "We have approved the PRD for US-713 with one AC addition." | "approved: US-713 PRD -- 1 AC added" |

### 6.8 Acknowledgment

**Form:** `ack <id>` or just `ack` for the most recent

| Verbose (~11) | Shorthand (~5) |
|---|---|
| "Got it, I've received the US-713 closeout." | "ack US-713 closeout" |

### 6.9 Compound message

**Verbose (~70 tokens):**
> Hi Agent2, I wanted to give you a quick update. US-713 is now complete — all acceptance criteria are met and CI is green. The PR is ready to merge. Could you take a look at it? Also, I had to block US-718 because there's no deterministic household source available in the Silver layer. We'll need to defer that one to next sprint.

**Shorthand (~23 tokens):**
```
US-713 done; AC met; CI green; PR ready -- merge?
US-718 blocked: no household source in Silver. Defer next sprint.
```

**Savings: ~67%.**

### 6.10 Re-running the welcome handshake

The test that motivated this design.

**Original MD (~30 tokens):**
> Welcome to the harness, Agent2. As of Tuesday, May 5, 2026 at 10:05 PM CDT, the line is open and your inbox is live.

**Shorthand (~13 tokens):**
```
Welcome Agent2. Inbox live: 2026-05-05 22:05 CDT.
```

**Savings: ~57%.** No envelope, no profile, no JSON wrapper.

### 6.11 Three-way comparison (welcome handshake)

| Format | Tokens (approx) | Vs MD |
|---|---:|---:|
| Verbose English narrative | 30 | 1.00× |
| Plain MD | 30 | 1.00× |
| **A2A Shorthand** | **13** | **0.43×** |
| A2AL/0.3.0 JSON | ~60 | 2.00× |

---

## 7. Repository Layout

```
A2AL/
├── specs/
│   ├── A2A-Core.md           # existing — A2AL/0.3.0
│   ├── A2A-Rulebook.md       # existing
│   ├── A2A-Shorthand.md      # NEW — canonical 0.1.0 spec
│   └── IMPLEMENTING.md       # existing
├── examples/
│   ├── project-coord/        # existing
│   ├── social-post/          # existing
│   ├── shorthand/            # NEW
│   │   ├── README.md
│   │   ├── welcome.txt
│   │   ├── sprint-status.txt
│   │   ├── blocker.txt
│   │   └── compound-update.txt
│   └── ClaudeCode/
│       └── skills/
│           ├── a2al/             # existing
│           └── a2a-shorthand/    # NEW
│               └── SKILL.md
├── VersionHistory.md         # add a2a-shorthand/0.1.0 entry
└── README.md                 # add "When to use which" section
```

---

## 8. Skill Behavior

The new `a2a-shorthand` skill mirrors the existing `a2al` skill's structure but does the inverse job:

- **Read mode**: parse a `.txt` shorthand message; expand `term=expansion` definitions; summarize in plain English for the LLM/user.
- **Write mode**: take user intent, render as shorthand following the style rules and glossary; output as plain text (no JSON wrapper).
- **Routing**: if the writer's intent has 5+ structured items, the skill should *suggest* using A2AL instead and link to the `a2al` skill.

The existing `a2al` skill will be updated with the inverse routing: if the user asks to write something that's clearly conversational, suggest A2A Shorthand.

---

## 9. Memory and CLAUDE.md updates

Two specific entries need revision:

- `~/.claude/projects/.../memory/feedback_a2a_required.md` — currently says "MUST use A2AL for peer messages." Revise to: "Use A2AL for structured payloads; A2A Shorthand for conversational/short. Plain text is acceptable when neither applies."
- `CLAUDE.md` (local) — add a "When to use which format" subsection mirroring the decision rule above.

---

## 10. Test Harness Migration

After publishing:

1. Install `a2a-shorthand` skill in both `testing/agent1/.claude/skills/` and `testing/agent2/.claude/skills/`
2. Update each agent's `CLAUDE.md` with the decision rule
3. Re-run the welcome handshake using shorthand
4. Confirm the analysis: shorthand should beat both verbose MD and A2AL/0.3.0 for that message type
5. Update `testing/agent2/analysis.md` with the three-way comparison

---

## 11. Out of Scope (deferred)

- **Automatic verbose↔shorthand transpilation tooling** (the LLM does this on demand)
- **Token-count validation tooling** (would need Anthropic tokenizer access)
- **Inline embedding of A2AL within shorthand** (defer until real use surfaces it)
- **Promotion-to-canonical automation** (manual curation for v0.1.0)
- **Shorthand validation library** (it's plain text; little to validate beyond "did the writer follow the style rules?")
