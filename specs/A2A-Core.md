# A2AL — `A2AL/0.4.0` Core Specification

**Status:** Normative. Replaces the deprecated A2AL/0.3.0 JSON envelope spec.
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

### Optimization target

Minimize tokens on Claude's tokenizer specifically. The design uses single-token English words and standard tech jargon, both of which Claude's BPE handles efficiently.

## 2. When to use A2AL

A2AL is for **agent-to-agent communication** — messages dropped between AI agents (or between automated processes). The format is plain text, designed to be produced and consumed by an LLM with the library loaded into its system prompt.

**Use A2AL when:**

- Sending status updates, action requests, blocker notifications, ack messages between agents
- Compressing prose reports for downstream agent consumption
- Storing agent-to-agent message logs (compact archival)

**Do NOT use A2AL when:**

- The audience is human — write Markdown instead. A2AL is not optimized for human readability.
- The content is genuinely unstructured prose with no shorthand savings (e.g., a poem). Plain text is fine.
- You need a structured envelope (timestamps, signatures, routing metadata) — that's transport, out of scope for A2AL.

For the historical record, A2AL/0.3.0 used a JSON envelope; that approach was abandoned because it cost more tokens than plain Markdown on real conversational traffic. See [`archive/0.3.0/`](../archive/0.3.0) for the deprecated spec.

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

## 4. Vocabulary Library

The vocabulary lives in [`library/`](../library) — one YAML file per domain. Always-loaded core: [`library/core.yaml`](../library/core.yaml) (~77 universal terms). Domain extensions:

- [`library/programming.yaml`](../library/programming.yaml) — code-review and dev-process specifics (`MR`, `CR`, `IaC`, `code-complete`, etc.)
- [`library/infrastructure.yaml`](../library/infrastructure.yaml) — cloud/orchestration/data (`DAG`, `ETL`, `k8s`, `AWS`, `Azure`, `GCP`, `VPC`, `VNet`, etc.)
- [`library/project-mgmt.yaml`](../library/project-mgmt.yaml) — specialized roles and SRE/ops vocabulary (`EM`, `TPM`, `SRE`, `SLA`, `SLO`, `SLI`, `MTTR`, `RCA`)
- [`library/security.yaml`](../library/security.yaml) — security threats and controls (`RCE`, `XSS`, `SSRF`, `CVE`, `CVSS`, `OWASP`, `MFA`, `IAM`, `RBAC`)
- [`library/ai-agents.yaml`](../library/ai-agents.yaml) — agents/LLM-specific (`LLM`, `MCP`, `A2A`, `RAG`, `KV`)

See [`library/README.md`](../library/README.md) for entry schema and loading model.

The library is open and contributable. To propose a new term, open a PR adding an entry to the appropriate domain file (or core, if universal). Run `python tools/validate_library.py` locally first.

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

1. **Adopted in the wild** — agents define and use new shortenings in real conversations using `term=expansion` syntax
2. **Captured locally** — user (or a periodic agent task) collects shortenings used 5+ times across multiple threads
3. **Reviewed** — proposer evaluates the candidate against criteria: tokenizes well, unambiguous, broadly applicable
4. **Promoted** — open a PR adding an entry to `library/<domain>.yaml`. CI runs `tools/validate_library.py` to enforce schema and uniqueness.
5. **Documented** — `VersionHistory.md` lists library minor-version bumps when entries are added.

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
