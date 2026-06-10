# A2A Shorthand 0.1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship A2A Shorthand 0.1.0 — a plain-text shorthand for conversational agent-to-agent messages that complements A2AL/0.3.0 (which only pays for itself on structured payloads). Add the spec, examples, Claude Code skill, integration, and test-harness migration.

**Architecture:** Sibling to A2AL/0.3.0, independently versioned. Lives at `specs/A2A-Shorthand.md` with examples in `examples/shorthand/` and an installable skill at `examples/ClaudeCode/skills/a2a-shorthand/`. Decision rule: A2AL above ~5 structured items per message, Shorthand below. Both skills cross-route to the appropriate other when message shape doesn't match.

**Tech Stack:** Markdown specs and skill files; plain text examples; no code (the validator is the LLM's existing English fluency).

---

## File Structure

**Create:**
- `specs/A2A-Shorthand.md` — canonical normative spec
- `examples/shorthand/README.md`
- `examples/shorthand/welcome.txt`
- `examples/shorthand/sprint-status.txt`
- `examples/shorthand/blocker.txt`
- `examples/shorthand/compound-update.txt`
- `examples/ClaudeCode/skills/a2a-shorthand/SKILL.md`

**Modify:**
- `examples/ClaudeCode/skills/a2al/SKILL.md` — add inverse routing
- `examples/ClaudeCode/README.md` — list both skills
- `VersionHistory.md` — add `a2a-shorthand/0.1.0` entry
- `README.md` — add "When to use which format" section
- `CLAUDE.md` (gitignored, local) — add decision-rule subsection
- `testing/agent1/CLAUDE.md` (gitignored) — add decision rule
- `testing/agent2/CLAUDE.md` (gitignored) — add decision rule
- `testing/agent2/analysis.md` — add three-way comparison
- `~/.claude/projects/C--Users-mcornelison-Projects-A2A-Protocal/memory/feedback_a2a_required.md` — revise rule

**Install (gitignored, no commit):**
- `testing/agent1/.claude/skills/a2a-shorthand/SKILL.md` — copy of canonical skill
- `testing/agent2/.claude/skills/a2a-shorthand/SKILL.md` — copy

---

## Task 1: Write `specs/A2A-Shorthand.md`

**Files:**
- Create: `specs/A2A-Shorthand.md`

This is the canonical normative spec. Source content lives in the design doc at `docs/superpowers/specs/2026-05-05-a2a-shorthand-0.1.0-design.md`, sections 1–6. Transcribe those sections (skipping the "Origin" front-matter and the implementation sections 7–11), with light editing to make it read as a standalone normative spec.

- [ ] **Step 1: Read the design doc**

```bash
cat docs/superpowers/specs/2026-05-05-a2a-shorthand-0.1.0-design.md
```

- [ ] **Step 2: Create `specs/A2A-Shorthand.md` with this exact content**

```markdown
# A2A Shorthand — `a2a-shorthand/0.1.0`

**Status:** Reference style guide. Sibling to A2AL/0.3.0 — not a replacement.
**See also:** `specs/A2A-Core.md` (A2AL/0.3.0), `examples/shorthand/`, `examples/ClaudeCode/skills/a2a-shorthand/`

A2A Shorthand is a *style guide* and *recommended jargon palette* for agent-to-agent messages where structural density is too low to justify A2AL/0.3.0's envelope. It is plain text — not a JSON wire format. It is not a constructed/symbolic language; it is a tight dialect of English chosen to tokenize efficiently on Claude's vocabulary.

## 1. Goals & Non-Goals

### Goals

- ~40–50% token reduction vs verbose English on conversational/status traffic
- Zero per-session dictionary overhead — relies on the LLM's existing English training
- LLM-fluent on both write and read without specialized training
- Coexists with A2AL/0.3.0 — different tool for different message shapes

### Non-Goals

- Not a JSON wire format (plain text, no envelope)
- Not a constructed/symbolic language
- Not a replacement for A2AL/0.3.0
- Not aimed at maximum compression at any cost — accepts the tokenizer reality and stops at the natural English-jargon floor

### Optimization target

Minimize tokens on Claude's tokenizer specifically. The design uses single-token English words and standard tech jargon, both of which Claude's BPE handles efficiently.

## 2. When to use Shorthand vs A2AL/0.3.0

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

| Message shape | Use |
|---|---|
| Handshakes, acks, single-fact updates | A2A Shorthand |
| Conversational coordination ("merge?", "blocked on X") | A2A Shorthand |
| Status updates with ≤3 metrics or ≤3 deltas | A2A Shorthand |
| Sprint closeouts, multi-section reports, ≥5 deltas | A2AL/0.3.0 |
| Risk briefs with multiple findings + citations | A2AL/0.3.0 |
| Anything that compresses well into structured sections | A2AL/0.3.0 |

## 3. Style Rules

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

- Sentence fragments instead of full sentences
- Imperative mood for actions: `merge X`, not `please merge X`
- Past tense / status adjectives for state: `done`, `blocked`, `shipped`, `passed`, `failed`
- Standard tech jargon that tokenizes as 1 token: `PR`, `AC`, `CI`, `CD`, `DQ`, `QA`, `PM`, `RCE`, `CVE`, `CVSS`, `MR`
- IDs as bare tokens: `US-713`, `commit-98b483d`, `T-202`

### 3.3 Format conventions

- One fact per fragment
- `;` between related facts (same topic): `US-713 done; AC met; CI green`
- `.` (or newline) between unrelated facts
- `:` after a subject to expand: `US-713: AC met but CI broke`
- `/` for ratios: `21/21 tests`, `878/878 preflight`
- `?` for questions/asks: `merge?`, `block on US-718?`
- `--` to attach an inline rationale: `defer US-718 -- no source in Silver`

### 3.4 Anti-patterns

- ❌ **Creative abbreviations** (`cmplt`, `prgm`, `mrg`) — often tokenize as 2–3 tokens; the full word is usually 1
- ❌ **Rare Unicode symbols** (✓ ⟳ ✗ →) — usually multi-token in Claude's vocab
- ❌ **Dropping critical context** for terseness (e.g., dropping the story ID makes the message unactionable — false economy)
- ❌ **Stacking facts without separators** — harder for the receiver to parse

## 4. Recommended Glossary

A curated palette of words and abbreviations that almost certainly tokenize as 1 token in Claude's vocabulary. Use these by default; the LLM's full vocabulary is available beyond this list.

> Token counts here are estimates. Validate with the Anthropic tokenizer before depending on a specific term.

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

### 4.4 Severity (5 levels)

`crit`, `high`, `med`, `low`, `info`

(Same scale as A2AL/0.3.0 risk profile.)

### 4.5 Multi-token but worth it

Some phrases are 2–3 tokens but still net-positive when they replace longer English. Use sparingly:

- `code-complete`, `feature-flag`, `dead-letter`, `fast-follow`

### 4.6 Not in the glossary (deliberately)

- ❌ Vowel-dropped forms (`cmplt`, `prgm`)
- ❌ Single-letter codes (`c`, `b`, `r`)
- ❌ Emoji or rare Unicode (✓ ✗ ⟳ 🟢 🔴)
- ❌ Greek letters (`Δ`, `λ`)

The palette is recommended, not enforced. Writers may use any term in standard form (e.g., `Spark`, `Fabric`, `OAuth2`).

## 5. Extending the Vocabulary

### 5.1 Inline definition

A new shortening is introduced on first use with `term=expansion`:

```
DR=design-review. DR sched Tuesday; PR ready post-DR; AC sign-off needed post-DR.
```

After the first use, the receiver may use bare `DR` for the rest of the thread. The definition runs until the next sentence-terminating punctuation (`.`, `;`, `?`, `!`, `--`, newline). The expansion itself should be a single word or hyphenated phrase without internal spaces or `--`.

### 5.2 Scope

| Scope | Behavior |
|---|---|
| **Per-thread** (default) | Terms defined in a thread are valid for all subsequent messages in that thread. New thread = clean slate. |
| Per-pair | (Optional) Agents may keep a local note file of terms they've adopted with each peer. Implementation-specific; not part of the spec. |
| Repo-canonical | Promoted via PR after the user reviews accepted terms. |

### 5.3 Implicit acceptance

Acceptance is signaled by the receiver using the term in their reply. If the receiver doesn't recognize:

- They may ignore the shortening and reply in canonical-glossary form
- They may ask: `?DR` or `DR=?` to request a definition
- They may propose an alternative: `DR=design-review (or DRev?)`

### 5.4 When to introduce a shortening

Net-positive only when the term will be used 3+ times in the thread. Defining once costs the definition tokens (`DR=design-review` ≈ 4 tokens) plus the bare uses.

**Rule of thumb: 3 uses in a thread = define it; fewer = don't.**

### 5.5 Anti-patterns

- ❌ Re-defining a canonical term: don't write `PR=pull-request`. `PR` is already canonical.
- ❌ Cryptic single letters: `D=delta`, `S=status` — comprehension cost outweighs savings; ambiguity with A2AL lane tags.
- ❌ Renegotiating mid-thread: once defined, stick with the form.

### 5.6 Promotion to canonical glossary

1. Adopted in the wild — agents define and use new shortenings in real conversations
2. Captured locally — user (or a periodic agent task) collects shortenings used 5+ times across multiple threads
3. Reviewed — user evaluates each candidate against criteria: tokenizes well, unambiguous, broadly applicable
4. Promoted — added to the glossary in a minor version bump (e.g., `0.1.0` → `0.2.0`)
5. Documented — `VersionHistory.md` lists the new vocabulary additions

Vocabulary additions = minor versions. Structural changes to the style rules = major.

## 6. Patterns

### 6.1 Single-fact state change

**Form:** `<id> <state>`. Example: `US-713 done`

### 6.2 Multi-fact state with details

**Form:** `<id> <state>; <fact>; <fact>; ...`. Example: `US-713 done; AC met; CI green; PR ready`

### 6.3 Status report

**Form:** `<metric> <value>; <metric> <value>; ...`. Example: `tests 21/21; preflight 878/878; ruff pass; build green`

### 6.4 Action directive

**Form:** `<verb> <target>` or `<actor>: <verb> <target>`. Example: `merge ralph/auth-fix`

### 6.5 Blocker notification

**Form:** `<id> blocked: <reason>`. Example: `US-718 blocked: no household source in Silver`

### 6.6 Question / quick ask

**Form:** `<verb>?` or `<id> <verb>?`. Example: `merge?`, `US-713 sign-off?`

### 6.7 Decision communication

**Form:** `<decision>: <id|target> -- <rationale>`. Example: `approved: US-713 PRD -- 1 AC added`

### 6.8 Acknowledgment

**Form:** `ack <id>` or just `ack`. Example: `ack US-713 closeout`
```

- [ ] **Step 3: Verify the file is well-formed**

```bash
wc -l specs/A2A-Shorthand.md
grep -c "^## " specs/A2A-Shorthand.md
```
Expected: ~150 lines; 6 top-level sections.

- [ ] **Step 4: Commit**

```bash
git add specs/A2A-Shorthand.md
git commit -m "Add specs/A2A-Shorthand.md (a2a-shorthand/0.1.0 normative spec)

Plain-text shorthand sibling to A2AL/0.3.0. Style guide with drops/uses/
format conventions, recommended single-token glossary, vocabulary
extension via inline term=expansion, and 8 message patterns. Decision
rule for shorthand vs A2AL is in §2."
```

---

## Task 2: Write shorthand example files

**Files:**
- Create: `examples/shorthand/README.md`
- Create: `examples/shorthand/welcome.txt`
- Create: `examples/shorthand/sprint-status.txt`
- Create: `examples/shorthand/blocker.txt`
- Create: `examples/shorthand/compound-update.txt`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p examples/shorthand
```

- [ ] **Step 2: Write `examples/shorthand/welcome.txt`**

```text
Welcome Agent2. Inbox live: 2026-05-05 22:05 CDT.
```

- [ ] **Step 3: Write `examples/shorthand/sprint-status.txt`**

```text
Sprint-2 done. tests 172/172; preflight 878/878; ruff pass; build green; defects 0.
US-852 done; US-853 done; US-858 done.
merged ralph/sprint-2-tech-debt-and-auth -> main.
```

- [ ] **Step 4: Write `examples/shorthand/blocker.txt`**

```text
US-718 blocked: no household source in Silver. Defer next sprint.
Switched to US-719 -- deps met, source unambiguous.
PM: accept US-718 slip; plan HubSpot Contact-Household extractor next sprint.
```

- [ ] **Step 5: Write `examples/shorthand/compound-update.txt`**

```text
US-713 done; AC met; CI green; PR ready -- merge?
US-714 done; warnOnly DQ flag; 21/21 DQ tests; ruff pass.
US-718 blocked: no household source in Silver. Defer next sprint.
Ledger: merge ralph/pipeline-hotfix-2026-04-17 when ready.
```

- [ ] **Step 6: Write `examples/shorthand/README.md`**

```markdown
# A2A Shorthand Examples

Plain-text agent-to-agent messages following the `a2a-shorthand/0.1.0` style guide. See [`specs/A2A-Shorthand.md`](../../specs/A2A-Shorthand.md).

## Files

| File | Pattern | Notes |
|---|---|---|
| [welcome.txt](./welcome.txt) | Handshake | The test-harness welcome that motivated the design |
| [sprint-status.txt](./sprint-status.txt) | Status report + state changes | Multi-fact compound message |
| [blocker.txt](./blocker.txt) | Blocker notification | Includes recommended next steps |
| [compound-update.txt](./compound-update.txt) | Mixed: state change + blocker + action directive | Realistic multi-topic update |

## When NOT to use shorthand

If your message has 5+ structured items, multiple section types, or formal-record characteristics (sprint closeout, decision log, risk brief with citations), use A2AL/0.3.0 instead. See [`examples/project-coord/`](../project-coord/) for those.

The two formats are complementary. Decision rule lives in [`specs/A2A-Shorthand.md`](../../specs/A2A-Shorthand.md) §2.
```

- [ ] **Step 7: Commit**

```bash
git add examples/shorthand/
git commit -m "Add a2a-shorthand/0.1.0 example messages

Five files: README plus four worked examples covering welcome, sprint
status, blocker, and a compound multi-topic update. The welcome example
re-encodes the test-harness handshake (originally ~30 tokens MD; now
~13 tokens shorthand)."
```

---

## Task 3: Write the `a2a-shorthand` Claude Code skill

**Files:**
- Create: `examples/ClaudeCode/skills/a2a-shorthand/SKILL.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p examples/ClaudeCode/skills/a2a-shorthand
```

- [ ] **Step 2: Write `examples/ClaudeCode/skills/a2a-shorthand/SKILL.md`**

```markdown
---
name: a2a-shorthand
description: Use when the user asks to send a short conversational agent-to-agent message, write a quick status update, ack a peer, or compress a verbose MD report into a tight English shorthand. Plain-text format, no envelope. Triggers on phrases like "send a quick update", "ack that", "shorthand this", "tell agent2 X", short conversational asks. NOT for sprint closeouts, decision logs, risk briefs, or messages with 5+ structured items — those use the a2al skill.
---

# A2A Shorthand Skill

A2A Shorthand is a plain-text style for short agent-to-agent messages. It is sibling to A2AL/0.3.0; the two are complementary.

Reference: https://github.com/mcornelison/A2AL — `specs/A2A-Shorthand.md` and `examples/shorthand/`.

## When to use

- Handshakes, acks, single-fact updates
- Conversational coordination ("merge?", "blocked on X")
- Status updates with ≤3 metrics or ≤3 deltas
- Quick action requests

## When NOT to use (route to a2al instead)

If the message has 5+ structured items, spans 3+ section types, needs structured citations (refs), or is a formal record (sprint closeout, decision log, risk brief), use the `a2al` skill — A2A Shorthand is net-negative on tokens for those shapes.

## Style rules

### Drop
- Articles (`the`, `a`, `an`)
- Helping/linking verbs (`is`, `are`, `was`) when state is unambiguous
- Subjective framing (`I think`, `it seems`)
- Politeness (`please`, `could you`)
- Filler (`in order to` → `to`)
- Repeated subjects across fragments — use `;`

### Use
- Sentence fragments
- Imperative mood for actions
- Past tense / status adjectives for state
- Standard tech jargon: `PR`, `AC`, `CI`, `CD`, `DQ`, `RCE`, `CVE`, `CVSS`, etc.
- IDs as bare tokens: `US-713`, `commit-98b483d`

### Punctuation
- `;` between related facts (same topic)
- `.` between unrelated facts
- `:` after subject to expand
- `/` for ratios
- `?` for questions
- `--` for inline rationale

### Avoid
- Creative abbreviations (`cmplt`, `prgm`) — usually tokenize as 2–3 tokens
- Rare Unicode (✓ ⟳ ✗) — usually multi-token in Claude's vocab
- Single-letter codes (`c`, `b`, `r`) — ambiguous

## Patterns

| Pattern | Form | Example |
|---|---|---|
| State change | `<id> <state>` | `US-713 done` |
| Multi-fact state | `<id> <state>; <fact>; <fact>` | `US-713 done; AC met; CI green` |
| Status report | `<metric> <value>; ...` | `tests 21/21; preflight 878/878; build green` |
| Action | `<verb> <target>` or `<actor>: <verb> <target>` | `merge ralph/auth-fix` |
| Blocker | `<id> blocked: <reason>` | `US-718 blocked: no household source in Silver` |
| Question | `<verb>?` or `<id> <verb>?` | `merge?`, `US-713 sign-off?` |
| Decision | `<decision>: <id> -- <rationale>` | `approved: US-713 PRD -- 1 AC added` |
| Ack | `ack <id>` | `ack US-713 closeout` |

## Mode 1 — Read

When given a shorthand message:
1. Parse `term=expansion` definitions on first occurrence; remember within the thread
2. Expand the message in your head (don't echo the expansion to the user unless asked)
3. Summarize key facts in 1–2 plain-English sentences for the user

## Mode 2 — Write

When the user asks to compose a message:
1. Identify the structural shape (state change / status / action / blocker / question / decision / ack)
2. Pick the matching pattern from the table above
3. Use canonical glossary terms where possible; expand to full English for novel concepts
4. Apply style rules — drop fillers, use fragments, semicolons between related facts
5. **Check the routing:** if you're producing 5+ structured items or multiple section types, **stop** and tell the user to use the `a2al` skill instead

## Mode 3 — Vocabulary extension

If the user wants to introduce a new shortening:
1. Verify the term will be used 3+ times in the thread (else just write it out in full)
2. On first use, write `<term>=<expansion>` (no spaces in the expansion)
3. After first use, use the bare term

Example: `DR=design-review. DR sched Tuesday; PR ready post-DR.`

## Worked example — write

User: "Tell Agent1 the sprint hotfix is done — 713 needed no code change, 714 implemented warnOnly DQ flag, all tests pass, ready to merge."

You produce:

```
US-713 done; no code change -- already in main from US-671.
US-714 done; warnOnly DQ flag; 21/21 DQ tests; preflight 878/878.
merge ralph/pipeline-hotfix-2026-04-17?
```

You write that to the file/inbox the user specified, then summarize: "Wrote sprint hotfix update to Agent1. Three lines, ~30 tokens vs ~95 in verbose English. Asks Agent1 to merge."

## Worked example — read

User: "What does this say?" (provides `US-713 done; AC met; CI green; PR ready -- merge?`)

You reply: "US-713 is complete with acceptance criteria met and CI green. Sender's PR is ready and they're asking permission to merge."

## When to stop and route to a2al

If the user's intent compresses better in A2AL — i.e., it has structured fields like multi-item delta, status, actions, refs, decision, risk, gates, inventory — stop and say: "This message has [N] structured items / spans [M] section types. A2AL/0.3.0 will be more token-efficient here. Switch to the `a2al` skill?"

Specifically:
- 5+ deltas → A2AL
- Multiple sections + body rationale → A2AL
- Citations (`refs` of commits/files/CVEs) → A2AL
- Sprint closeout, decision log, risk brief → A2AL

For everything else, A2A Shorthand wins.
```

- [ ] **Step 3: Commit**

```bash
git add examples/ClaudeCode/skills/a2a-shorthand/
git commit -m "Add a2a-shorthand Claude Code skill

Installable skill that teaches an agent the A2A Shorthand style guide,
recommended glossary, and 8 patterns. Includes write/read modes plus
explicit routing to the a2al skill when message shape exceeds the
shorthand break-even point."
```

---

## Task 4: Update `a2al` skill with inverse routing

**Files:**
- Modify: `examples/ClaudeCode/skills/a2al/SKILL.md` (append a new "When NOT to use this skill" subsection or expand the existing one)

- [ ] **Step 1: Read the current skill**

```bash
cat examples/ClaudeCode/skills/a2al/SKILL.md
```

- [ ] **Step 2: Find the section "When NOT to use this skill" near the bottom (if it exists) and replace it with this expanded version. If the section doesn't exist, append it before the closing of the file.**

```markdown
## When NOT to use this skill

A2AL/0.3.0 has a fixed envelope cost (~150 tokens) that must amortize across structured payload. For messages without that structure, A2AL is net-negative on tokens — it makes the message more expensive, not less. Use the `a2a-shorthand` skill instead when:

- The message is a handshake, ack, or single-fact update
- The message is conversational coordination ("merge?", "blocked on X")
- The message has ≤3 metrics, ≤3 deltas, or ≤3 actions and no other structured content
- The body is mostly prose without extractable structured fields (a Moltbook-style post is still A2AL because the `social-post/1.0` profile expects `title`/`submolt`/`body` — but a free-form chat message is not)

If you're unsure, count structured items. **5+ structured items = A2AL. Below that = shorthand.**

The two skills are complementary. The `a2a-shorthand` skill will route back to `a2al` when its threshold is exceeded.
```

- [ ] **Step 3: Verify the file still parses (frontmatter intact, all sections present)**

```bash
head -5 examples/ClaudeCode/skills/a2al/SKILL.md
grep -c "^## " examples/ClaudeCode/skills/a2al/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git add examples/ClaudeCode/skills/a2al/SKILL.md
git commit -m "Update a2al skill with inverse routing to a2a-shorthand

Adds explicit guidance that A2AL is net-negative on token cost for short
conversational messages (handshakes, acks, ≤3-item updates). Directs the
agent to use a2a-shorthand for those cases. Threshold: 5+ structured
items = A2AL; below = shorthand."
```

---

## Task 5: Update `examples/ClaudeCode/README.md`

**Files:**
- Modify: `examples/ClaudeCode/README.md`

- [ ] **Step 1: Read the current file**

```bash
cat examples/ClaudeCode/README.md
```

- [ ] **Step 2: Replace the "## Files" table with this expanded version that includes both skills**

Find the existing table starting with `## Files` and replace it with:

```markdown
## Files

| Path | Purpose |
|---|---|
| [`skills/a2al/SKILL.md`](./skills/a2al/SKILL.md) | A2AL/0.3.0 skill — invoke for **structured payloads** (sprint closeouts, decision logs, risk briefs, ≥5 structured items) |
| [`skills/a2a-shorthand/SKILL.md`](./skills/a2a-shorthand/SKILL.md) | A2A Shorthand skill — invoke for **short conversational messages** (handshakes, acks, ≤3-item updates) |
| [`commands/a2al.md`](./commands/a2al.md) | Slash command `/a2al` — explicit user invocation of the A2AL skill |

## Choosing between the two skills

The two skills are complementary, not competing:

| Message shape | Skill |
|---|---|
| Handshake / ack / single-fact update | `a2a-shorthand` |
| Status update with ≤3 metrics | `a2a-shorthand` |
| Sprint closeout / decision log / risk brief | `a2al` |
| Multi-section structured payload (≥5 deltas) | `a2al` |
| Anything with structured citations (refs) | `a2al` |

The `a2a-shorthand` skill self-routes back to `a2al` when its threshold is exceeded; `a2al` self-routes to `a2a-shorthand` when the message is conversational. Either skill is a valid entry point.
```

- [ ] **Step 3: If the README has an "Installing" section, ensure it mentions both skills**

The existing copy commands should already be flexible (`cp -r examples/ClaudeCode/skills/a2al .claude/skills/`). Add a note immediately above or below those commands:

```markdown
> Repeat the same `cp` commands with `a2a-shorthand` in place of `a2al` to install the shorthand skill alongside.
```

- [ ] **Step 4: Commit**

```bash
git add examples/ClaudeCode/README.md
git commit -m "List both Claude Code skills (a2al + a2a-shorthand) with selection table"
```

---

## Task 6: Update `VersionHistory.md`

**Files:**
- Modify: `VersionHistory.md`

- [ ] **Step 1: Read the current file**

```bash
cat VersionHistory.md
```

- [ ] **Step 2: Add a new row to the version table for `a2a-shorthand/0.1.0`**

Find the existing version table and add a new row immediately below the header, above the existing 0.3.0 row. The complete updated table should look like:

```markdown
| Version | Date | Brief Name | Description |
|---|---|---|---|
| `a2a-shorthand/0.1.0` | 2026-05-05 | Plain-text agent shorthand | Sibling to A2AL/0.3.0 for short conversational messages. Style guide and recommended jargon palette designed to tokenize efficiently on Claude's tokenizer. Plain text — no envelope, no JSON. Decision rule: 5+ structured items = A2AL; below = shorthand. |
| 0.3.0 | 2026-05-05 | Flexible Object + Profiles | Replaces /2.0 array-only positional spec. Flat-object format with descriptive envelope keys; positional section items; profile-extensible. Two reference profiles ship: `project-coord/1.0` and `social-post/1.0`. Reference Python validator runs in core + profile-aware modes. |
| 0.2.x | (deprecated) | Array-Only Positional (CoPilot draft) | Initial public spec generated by CoPilot. No working implementations; superseded by 0.3.0. Preserved in git history only. |
```

Note: A2AL core spec versions (0.2.x, 0.3.0) and standalone shorthand versions (`a2a-shorthand/0.1.0`) live in the same table because they're sibling artifacts. The `a2a-shorthand/` prefix disambiguates.

- [ ] **Step 3: Below the table, add a "## Companion Specs" subsection if it doesn't exist, explaining the prefix convention**

Add this immediately after the version table:

```markdown
## Companion Specs

Some entries in the version table are versioned independently of the core A2AL spec. They use a prefix:

- Core spec: bare version (`0.3.0`, `0.2.x`)
- Companion: `<name>/<version>` (e.g., `a2a-shorthand/0.1.0`)

Profiles registered under A2AL itself (e.g., `project-coord/1.0`, `social-post/1.0`) are documented in [`profiles/PROFILES.md`](./profiles/PROFILES.md) and are not separately listed here.
```

- [ ] **Step 4: Commit**

```bash
git add VersionHistory.md
git commit -m "Add a2a-shorthand/0.1.0 to VersionHistory.md

Sibling artifact to the A2AL core spec; tracked in the same version
table with a name/version prefix to disambiguate from core versions."
```

---

## Task 7: Update top-level `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the current README**

```bash
cat README.md
```

- [ ] **Step 2: Find the "Repository Layout" section. Immediately AFTER it, add a new "When to use which format" section.**

The new section to add:

```markdown
## When to use which format

A2AL/0.3.0 and A2A Shorthand are complementary, not competing. Pick the right tool for the message:

| Message shape | Use |
|---|---|
| Handshake, ack, single-fact update | A2A Shorthand |
| Conversational coordination ("merge?", "blocked on X") | A2A Shorthand |
| Status updates with ≤3 metrics or ≤3 deltas | A2A Shorthand |
| Sprint closeouts, multi-section reports | A2AL/0.3.0 |
| Risk briefs with multiple findings + citations | A2AL/0.3.0 |
| Decision logs / formal records | A2AL/0.3.0 |
| Anything with 5+ structured items | A2AL/0.3.0 |

A2AL has a fixed envelope cost (~150 tokens) that amortizes across structured payload. Below ~5 structured items, that envelope makes messages *more* expensive, not less — that's where A2A Shorthand pays off.

See [`specs/A2A-Shorthand.md`](./specs/A2A-Shorthand.md) for the shorthand style guide and [`specs/A2A-Core.md`](./specs/A2A-Core.md) for A2AL.
```

- [ ] **Step 3: Find the "Repository Layout" table and ensure `specs/A2A-Shorthand.md`, `examples/shorthand/`, and the new skill are listed**

Find the existing table. Add these rows (or insert them in alphabetical order if existing rows have a sort):

```markdown
| [`specs/A2A-Shorthand.md`](./specs/A2A-Shorthand.md) | A2A Shorthand 0.1.0 — plain-text style guide for short conversational messages |
| [`examples/shorthand/`](./examples/shorthand) | Worked shorthand examples |
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "README: add 'When to use which format' section + shorthand artifacts

Codifies the A2AL/0.3.0 vs A2A Shorthand decision rule with a shape→tool
table. Adds specs/A2A-Shorthand.md and examples/shorthand/ to the
repository layout table."
```

---

## Task 8: Update local `CLAUDE.md` and project memory (no commits)

**Files:**
- Modify: `CLAUDE.md` (gitignored — no commit)
- Modify: `~/.claude/projects/C--Users-mcornelison-Projects-A2A-Protocal/memory/feedback_a2a_required.md` (user-local — no commit)

These files are not tracked. Update them so future Claude Code sessions in this repo have the correct guidance.

- [ ] **Step 1: Update `CLAUDE.md`**

Find the existing "## Repository Layout" section. Immediately AFTER it, insert a new section:

```markdown
## When to use which format (A2AL vs A2A Shorthand)

Two complementary formats coexist:

- **A2AL/0.3.0** (`specs/A2A-Core.md`) — JSON envelope + structured sections. Use for sprint closeouts, decision logs, risk briefs, status reports with ≥5 structured items. Envelope cost (~150 tokens) only amortizes when payload is structured.
- **A2A Shorthand** (`specs/A2A-Shorthand.md`) — plain text. Use for handshakes, acks, single-fact updates, conversational coordination, status updates with ≤3 metrics or ≤3 deltas.

**Decision rule:** 5+ structured items = A2AL; below = shorthand.

Both have Claude Code skills under `examples/ClaudeCode/skills/`. The skills cross-route — invoking either is a valid entry point; they redirect when message shape doesn't match.
```

- [ ] **Step 2: Replace the memory entry**

Open `C:/Users/mcornelison/.claude/projects/C--Users-mcornelison-Projects-A2A-Protocal/memory/feedback_a2a_required.md`. Replace its full content with:

```markdown
---
name: A2AL vs A2A Shorthand routing
description: Use A2AL for structured payloads, A2A Shorthand for conversational/short, plain text for anything that fits neither
type: feedback
---

**Routing rule, post-2026-05-05 test:**

A2AL/0.3.0 was previously thought of as the format for all peer-to-peer agent messages. The 2026-05-05 welcome-handshake test showed A2AL is **1.86× more expensive** than plain MD on pure-prose handshakes — its envelope (~150 tokens) only amortizes when there's structured content to compress.

**Why:** A2AL's value comes from compressing structured fields (delta/status/actions/risk/etc.) into positional arrays vs prose paragraphs. With no structure, the envelope is dead weight.

**How to apply:**

- 5+ structured items in any category, OR multiple section types, OR formal record (sprint closeout, decision log, risk brief, security intel) → use **A2AL/0.3.0** (`a2al` skill)
- Conversational, handshake, ack, single-fact update, ≤3 metrics, ≤3 deltas → use **A2A Shorthand** (`a2a-shorthand` skill)
- Pure prose with no facts to compress (rare for agent comms) → plain text, no protocol

The two skills cross-route. Either is a valid entry point.

**Original rule (now superseded):** "MUST use A2AL for all peer messages, no plain text drops" — this was wrong. It increased token cost on the conversational subset of agent comms.
```

- [ ] **Step 3: Verify**

```bash
grep -c "^## " CLAUDE.md
cat ~/.claude/projects/C--Users-mcornelison-Projects-A2A-Protocal/memory/feedback_a2a_required.md
```
Expected: CLAUDE.md has the new section; memory entry is replaced.

- [ ] **Step 4: No commit**

These files are gitignored / user-local. No `git add` or `git commit` needed.

---

## Task 9: Install `a2a-shorthand` skill in test-harness agents

**Files:**
- Create: `testing/agent1/.claude/skills/a2a-shorthand/SKILL.md` (copy)
- Create: `testing/agent2/.claude/skills/a2a-shorthand/SKILL.md` (copy)

These are gitignored (`.claude/` is in `.gitignore`). Installing the skill = copying the canonical SKILL.md into each agent's local skills dir.

- [ ] **Step 1: Create the directories**

```bash
mkdir -p testing/agent1/.claude/skills/a2a-shorthand
mkdir -p testing/agent2/.claude/skills/a2a-shorthand
```

- [ ] **Step 2: Copy the canonical skill**

```bash
cp examples/ClaudeCode/skills/a2a-shorthand/SKILL.md testing/agent1/.claude/skills/a2a-shorthand/SKILL.md
cp examples/ClaudeCode/skills/a2a-shorthand/SKILL.md testing/agent2/.claude/skills/a2a-shorthand/SKILL.md
```

- [ ] **Step 3: Verify**

```bash
ls testing/agent1/.claude/skills/
ls testing/agent2/.claude/skills/
```
Expected: each agent has both `a2al/` and `a2a-shorthand/` directories.

- [ ] **Step 4: No commit**

`.claude/` is gitignored. Installation is local-only.

---

## Task 10: Update test-agent `CLAUDE.md` files with the decision rule

**Files:**
- Modify: `testing/agent1/CLAUDE.md` (gitignored if `CLAUDE.md` is in root .gitignore, else tracked)
- Modify: `testing/agent2/CLAUDE.md` (same)

- [ ] **Step 1: Check tracked status**

```bash
git check-ignore testing/agent1/CLAUDE.md testing/agent2/CLAUDE.md
```
Expected: both ignored (echo or empty depending on git version). If tracked, the commit at the end of this task will pick them up.

- [ ] **Step 2: Read the current files**

```bash
cat testing/agent1/CLAUDE.md
cat testing/agent2/CLAUDE.md
```

- [ ] **Step 3: Append a "When to use which format" section to each**

For BOTH files, append at the end:

```markdown

## When to use which format (A2AL vs A2A Shorthand)

Two complementary formats:

- **A2AL/0.3.0** (`a2al` skill) — JSON envelope, structured sections. Use for messages with 5+ structured items (sprint closeouts, decision logs, risk briefs).
- **A2A Shorthand** (`a2a-shorthand` skill) — plain text. Use for handshakes, acks, ≤3-item updates, conversational coordination.

**Decision rule:** 5+ structured items = A2AL; below = shorthand.

When writing a peer message, pick the right skill based on shape, not by default. Per the 2026-05-05 test, A2AL on a short handshake is ~1.86× the tokens of plain MD; shorthand is ~0.43×.
```

- [ ] **Step 4: Verify**

```bash
tail -20 testing/agent1/CLAUDE.md
tail -20 testing/agent2/CLAUDE.md
```

- [ ] **Step 5: Commit only if tracked**

```bash
git add testing/agent1/CLAUDE.md testing/agent2/CLAUDE.md 2>&1 || true
git diff --cached --stat
```

If anything is staged:

```bash
git commit -m "testing/agentN/CLAUDE.md: add A2AL vs A2A Shorthand decision rule"
```

If nothing was staged (files are gitignored), no commit is needed.

---

## Task 11: Re-run the welcome handshake test with shorthand

**Files:**
- Create: `testing/agent2/inbox/agent1-welcome-shorthand.txt`
- Create: `testing/agent1/inbox/agent2-welcome-ack-shorthand.txt`
- Modify: `testing/agent2/analysis.md` (extend with three-way comparison)

The original test compared MD vs A2AL on the welcome handshake. This task adds a Shorthand variant and updates the analysis.

- [ ] **Step 1: Write the shorthand welcome (Agent1 → Agent2)**

```bash
cat > testing/agent2/inbox/agent1-welcome-shorthand.txt <<'EOF'
Welcome Agent2. Inbox live: 2026-05-05 22:05 CDT.
Reply when ready. -- Agent1
EOF
```

- [ ] **Step 2: Write the shorthand ack (Agent2 → Agent1)**

```bash
cat > testing/agent1/inbox/agent2-welcome-ack-shorthand.txt <<'EOF'
ack welcome. Agent2 online: 2026-05-05 22:06 CDT.
Limerick noted; reply pending muse. -- Agent2
EOF
```

- [ ] **Step 3: Measure character counts**

```bash
wc -c testing/agent2/inbox/agent1-welcome-shorthand.txt
wc -c testing/agent1/inbox/agent2-welcome-ack-shorthand.txt
```

Record these counts. The token estimate is `chars/4` (cl100k-style heuristic — same method the original analysis used).

- [ ] **Step 4: Read the existing analysis**

```bash
cat testing/agent2/analysis.md
```

- [ ] **Step 5: Append a new section to `testing/agent2/analysis.md`**

Append at the end of the file:

```markdown

---

## Re-run with A2A Shorthand (2026-05-05)

After identifying that A2AL was 1.86× more expensive than MD on the pure-prose handshake, A2A Shorthand 0.1.0 was added as a sibling format for short conversational messages. Re-running the same handshake using shorthand:

### Per-message sizes (shorthand)

| Operation | Format | File | Bytes | Chars | ~Tokens |
|---|---|---|---:|---:|---:|
| Read (Agent1 → Agent2) | Shorthand | `testing/agent2/inbox/agent1-welcome-shorthand.txt` | (measured) | (measured) | (chars/4) |
| Write (Agent2 → Agent1) | Shorthand | `testing/agent1/inbox/agent2-welcome-ack-shorthand.txt` | (measured) | (measured) | (chars/4) |

Replace `(measured)` with actual values from `wc -c` output.

### Three-way comparison (round-trip totals)

| Format | Read | Write | Total | Ratio vs MD |
|---|---:|---:|---:|---:|
| MD | 88 | 80 | **168** | 1.00× |
| A2AL JSON | 154 | 158 | **312** | **1.86×** |
| A2A Shorthand | (insert) | (insert) | **(insert)** | **(insert)×** |

### Interpretation

A2A Shorthand wins for this exchange because:
- No envelope (no `v`, `from`, `to`, `id`, `intent`, `profile`, `ts`, `thread` overhead)
- Tight English fragments instead of full grammar
- Tech jargon (`ack`, `Agent2`, `online`) tokenizes as 1 token

Confirms the design hypothesis: **shorthand pays off below ~5 structured items; A2AL pays off above**. The two formats are complementary.
```

- [ ] **Step 6: Replace the `(measured)` and `(insert)` placeholders with the actual values from Step 3**

Read the wc output. Compute `chars / 4` for each token estimate. Sum read + write for the total. Compute ratio: shorthand_total / md_total (which is 168). Round to 2 decimal places.

Edit the analysis.md file in place to substitute the actual numbers.

- [ ] **Step 7: Verify the analysis is internally consistent**

```bash
grep -c "Shorthand" testing/agent2/analysis.md
```
Expected: ≥3 occurrences.

- [ ] **Step 8: Commit**

```bash
git add testing/agent1/inbox/agent2-welcome-ack-shorthand.txt testing/agent2/inbox/agent1-welcome-shorthand.txt testing/agent2/analysis.md
git commit -m "Re-run welcome handshake with A2A Shorthand; update analysis

Adds shorthand variants of the agent1↔agent2 welcome exchange and
extends testing/agent2/analysis.md with a three-way comparison
(MD / A2AL / Shorthand). Confirms the design rule: A2AL is net-negative
on tokens for pure-prose handshakes; Shorthand wins for that shape."
```

---

## Task 12: Push to GitHub

- [ ] **Step 1: Verify clean working tree**

```bash
git status --short
```
Expected: empty (all in-scope changes already committed; gitignored files locally modified are fine).

- [ ] **Step 2: Show commits to push**

```bash
git log --oneline origin/main..HEAD
```
Expected: ~9 commits from this plan (Tasks 1, 2, 3, 4, 5, 6, 7, 11; Tasks 8–10 may have 0 or 1 depending on tracked status).

- [ ] **Step 3: Push**

```bash
git push
```

- [ ] **Step 4: Verify on GitHub**

Open https://github.com/mcornelison/A2AL and confirm:
- `specs/A2A-Shorthand.md` is visible
- `examples/shorthand/` directory exists with 5 files
- `examples/ClaudeCode/skills/a2a-shorthand/SKILL.md` exists
- `VersionHistory.md` shows the new `a2a-shorthand/0.1.0` row
- `README.md` has the new "When to use which format" section

---

## Self-Review Notes

This plan was self-reviewed against the design doc on 2026-05-05.

**Spec coverage:**
- Design §1 (Scope) → Task 1 (`specs/A2A-Shorthand.md` §1)
- Design §2 (When to use vs A2AL) → Task 1 §2 + Task 7 (README) + Task 4 (a2al skill)
- Design §3 (Style Rules) → Task 1 §3 + Task 3 (skill)
- Design §4 (Glossary) → Task 1 §4 + Task 3
- Design §5 (Extending Vocabulary) → Task 1 §5 + Task 3 (mode 3)
- Design §6 (Patterns) → Task 1 §6 + Task 3 (patterns table) + Task 2 (examples)
- Design §7 (Repository Layout) → Tasks 1, 2, 3, 6, 7
- Design §8 (Skill Behavior) → Tasks 3, 4
- Design §9 (Memory and CLAUDE.md updates) → Task 8
- Design §10 (Test Harness Migration) → Tasks 9, 10, 11
- Design §11 (Out of Scope) → not implemented (correctly deferred)

No spec gaps detected.

**Placeholder check:** No "TBD"/"TODO" left in normative content. The Task 11 analysis update has `(measured)` and `(insert)` placeholders that the implementer must fill with real wc-derived values before committing — this is intentional and explicitly called out in Step 6.

**Type/name consistency:**
- Skill name: `a2a-shorthand` (consistent across all tasks)
- Spec name: `a2a-shorthand/0.1.0` (consistent)
- Decision rule: "5+ structured items" (consistent across tasks 1, 3, 4, 7, 8, 10)
- File paths: `specs/A2A-Shorthand.md`, `examples/shorthand/`, `examples/ClaudeCode/skills/a2a-shorthand/` (consistent)
