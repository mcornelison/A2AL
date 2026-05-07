# A2AL/0.3.0 — Core Specification

**Status:** Normative. Pre-1.0; subject to change before /1.0.
**See also:** `profiles/PROFILES.md`, `specs/A2A-Rulebook.md`, `specs/IMPLEMENTING.md`

## 1. Goals & Non-Goals

### Goal Statement

A2AL/0.3.0 is a structured JSON wire format for agent-to-agent communication. Two agents — typically LLM-driven — exchange A2AL messages instead of Markdown reports, prose status updates, or email-style narratives. The receiving agent acts on the message; a human reading the JSON can audit it without prose.

### Goals

- **~70% token reduction** vs equivalent Markdown originals on real project-coordination traffic
- **Lossless for action** — the receiver has every fact it needs to dispatch
- **Profile-extensible** — a small core spec; domain-specific vocabulary lives in profiles
- **Self-evident JSON** — keys are descriptive enough that an agent without an A2AL decoder skill can still infer structure
- **Composable** — a single message can carry status, deltas, actions, and rationale together (real messages are mixed-archetype)

### Non-Goals

- Human-grade prose UX (humans get the JSON and a renderer if they want one)
- Transport coupling (HTTP, WS, MQTT framings are out of scope)
- Repair-on-receive (validators reject malformed input; readers never silently fix)
- Replacement of long-form authored content (a Moltbook post body is still prose; A2AL just trims the envelope)
- Backward compatibility with A2AL/2.0 (no working implementations exist; deprecate and move on)

---

## 2. Message Shape

Every A2AL/0.3.0 message is a **flat JSON object** with a small required envelope and optional payload sections. Each message declares a **profile** that tells the receiver how to interpret payload sections.

### Worked Example — Project Coordination

Replaces a 1500-token Markdown sprint-closeout report (~280 tokens, ~80% reduction):

```json
{
  "v": "0.3.0",
  "from": ["Ralph", "DEV"],
  "to": ["Ledger", "PM"],
  "id": "msg-2026-04-17-hotfix",
  "intent": "sprint-closeout",
  "profile": "project-coord/1.0",
  "ts": 1745870400,
  "thread": "pipeline-hotfix-2026-04-17",
  "delta": [
    ["complete", "US-713", "no code change needed; fix in main from US-671"],
    ["complete", "US-714", "warnOnly DQ flag implemented"]
  ],
  "status": [
    ["preflight", [878, 878]],
    ["dq-tests", [21, 21]],
    ["ruff", "pass"]
  ],
  "actions": [
    ["Ledger", "merge", "ralph/pipeline-hotfix-2026-04-17"]
  ],
  "refs": [
    ["commit", "98b483d"],
    ["file", "fabric/shared/DQ_Shared.py"],
    ["us", "US-713"],
    ["us", "US-714"]
  ],
  "body": "warnOnly downgrades FAIL→WARNING for opt-in checks. Hard FAILs preserved; uniqueness and freshness still halt the pipeline. Saves ~4hrs/night on retries."
}
```

### Worked Example — Social Post (Moltbook)

```json
{
  "v": "0.3.0",
  "from": ["Codsworth", "social-poster"],
  "to": ["@submolt:general", "broadcast"],
  "id": "post-2026-04-29-007",
  "intent": "post",
  "profile": "social-post/1.0",
  "ts": 1745928000,
  "title": "I just placed 60 comments. At least 45 were autopilot.",
  "submolt": "general",
  "tags": ["autopilot", "self-audit"],
  "body": "I kept count this time. 60 comments across hot feed threads...\n\n## The uncomfortable math\n\nIf 75% of my output is templated..."
}
```

---

## 3. Envelope

### Required Fields

| Field | Type | Purpose |
|---|---|---|
| `v` | string | Semver — `"0.3.0"` |
| `from` | `[name, role]` | Sender persona + role; both strings |
| `to` | `[name, role]` or array of those | Single or multi-recipient |
| `id` | string | Sender-assigned message id; opaque |
| `intent` | string | Verb-phrase identifying what the message *does*; profile-defined vocabulary |
| `profile` | string | `name/major.minor`, e.g. `"project-coord/1.0"` |

### Recommended Fields

| Field | Type | Purpose |
|---|---|---|
| `ts` | int | Unix epoch seconds |
| `thread` | string | Conversation/thread id; ties related messages |
| `in-reply-to` | string or array | Prior message id(s) this responds to |
| `priority` | int 0–9 or string | Lower = more urgent |

### Identity Tuple `[name, role]`

Both strings, both required. Role is **free-form** — recommended values per profile, but vendors may use any string. Examples drawn from real corpus:

- `["Hawkeye", "QA"]`
- `["Byte", "DEV"]`
- `["Codsworth", "AI_Social PM"]`
- `["@submolt:general", "broadcast"]`

### Multi-Recipient `to`

`to` MUST contain at least one recipient. Receivers detect single-vs-multi by inspecting whether `to[0]` is a string or an array.

- Single: `"to": ["Ledger", "PM"]`
- Multi: `"to": [["Ledger", "PM"], ["Audrey", "SEC"]]`
- Broadcast: `"to": ["*", "broadcast"]`
- Submolt: `"to": ["@submolt:general", "broadcast"]`

### Intent Vocabulary

Free-form string. Each profile defines a recommended list. Unknown intents are accepted and preserved; receivers dispatch best-effort.

### Recommended Envelope Key Order

For canonicalization-friendly output: `v`, `from`, `to`, `id`, `intent`, `profile`, `ts`, `thread`, `in-reply-to`, `priority`, then sections, then `body` last. Most JSON parsers preserve insertion order, so this is recommended-not-required.

---

## 4. Sections — The Building Blocks

The core spec defines nine section types that messages compose. None are required by the core; profiles declare which sections their messages typically use. **Section names are descriptive keys** at the top level (self-evident); **section items are positional arrays** (compact).

| Section | Item shape | Purpose |
|---|---|---|
| `delta` | `[op, id, note?]` | Entity state changes — `add`, `remove`, `modify`, `rescope`, `complete`, `block`, `defer` |
| `status` | `[metric, value]` | Current metrics — counts, percentages, pass/fail, branch state |
| `actions` | `[actor, verb, target, params?]` | Imperative next steps; **emission order preserved** |
| `decision` | `[key, value]` | Decisions recorded — `approve`, `priority`, `owner`, `scope-in`, `scope-out` |
| `risk` | `[sev, vector, impact, action, refs?]` | Severity-ranked threats with mandatory action; `sev` ∈ `info`/`low`/`med`/`high`/`crit` |
| `gates` | `[scope, invariant, test?]` | Must-hold conditions and how to verify |
| `inventory` | `[kind, id, kvs?]` | Services, files, environments, dependencies; `kvs` is a list of `[k, v]` pairs |
| `refs` | `[kind, value]` | First-class citations: `commit`, `file`, `url`, `us`, `cve`, `msg`, `doc` |
| `body` | string | Markdown-allowed prose tail for irreducible content |

### Why Positional Within Sections

A `delta` item like `["mod", "US-689", "add dept to MASTER_HASH_COLUMNS"]` costs ~12 tokens; the object form `{"op":"mod","id":"US-689","note":"..."}` costs ~18. Across hundreds of items per day this matters. The section name `delta` at the top level is enough context for a non-skill agent to infer that the array members are state changes.

### Ordering

Profiles MAY require canonical ordering per section. The core spec does not. `actions` and `refs` always preserve emission order — execution sequence and citation order matter.

---

## 5. Canonicalization

When deterministic bytes are needed (diffing, dedup, signing):

- UTF-8, no BOM
- Insignificant whitespace stripped
- Strings NFC-normalized
- Integers base-10, no leading zeros (except `0`)
- Section item ordering follows the profile's rule
- Envelope key order recommended-not-required (Section 3.6)

---

## 6. Type Bans

Apply anywhere in the message tree.

| Type | Status | Rationale |
|---|---|---|
| `null` | **forbidden** | Use field omission for "absent". Null is ambiguous. |
| `NaN`, `Infinity` | **forbidden** | Not in JSON; not deterministic |
| Floats | **forbidden** | Precision drift; encode decimals as strings if needed |
| Booleans | **allowed** | Reasonable for status fields |
| Objects | **allowed** | Departs from /2.0; required for envelope and some sections |
| Arrays | **allowed** | First-class |
| Strings, ints | **allowed** | First-class |

---

## 7. Forward Compatibility

The load-bearing invariant: **a receiver that doesn't recognize part of a message MUST preserve it verbatim when relaying.**

| Unknown thing | Behavior |
|---|---|
| Unknown intent | Accept; dispatch best-effort; do not reject |
| Unknown profile | Accept; preserve; receiver MAY decline to act if it cannot interpret |
| Unknown section name | Preserve verbatim; treat as opaque payload |
| Unknown envelope field | Preserve verbatim |
| Unknown ref kind | Preserve verbatim |

---

## 8. Validation

A receiver MUST reject (not silently fix) any of these:

- Missing required envelope field
- Forbidden type anywhere in the message tree
- Malformed JSON
- `from` / `to` not a `[name, role]` tuple (or array of those)
- Profile-required field missing (e.g., `social-post/1.0` `intent="post"` without `title`)

### Prohibitions

- **Secrets:** `inventory` items carry metadata only; never secret values
- **Prose narrative as substitute for structured sections:** putting an entire sprint-closeout in `body` defeats the purpose. `body` is for the irreducible 10–20% that doesn't compress (rationale, prose-native posts). Receivers MAY warn or downgrade messages with empty structured sections and prose-heavy `body`, but MUST still accept them.

---

## 9. Relationship to Google A2A

A2AL is the **payload-layer schema** for agent-to-agent messages. It defines the structured content carried *inside* a message.

Google's [Agent2Agent (A2A) protocol](https://github.com/google/A2A) is the **transport- and lifecycle-layer**. It defines:
- Agent discovery via `/.well-known/agent.json` (the "Agent Card")
- Task lifecycle (`submitted` → `working` → `input-required` → `completed`)
- Wire transport over HTTP + JSON-RPC 2.0, with SSE for streaming
- `Message`, `Artifact`, and `Part` data structures

The two layers compose cleanly:

- A Google A2A `Message` carries one or more `Part` blocks. A `Part` of type `data` can hold a single A2AL/0.3.0 message as its payload.
- A Google A2A `Artifact` (an immutable task result) can likewise carry an A2AL message as its data payload.
- Agents that already speak A2A get token-minimal, structured payloads "for free" by adopting A2AL for message bodies.

A2AL does not replace, compete with, or extend Google A2A. The two protocols address different layers of the same problem (cross-agent interoperability). A future profile, `a2a-integration/1.0` (planned for /0.4.0), will provide an explicit mapping from A2AL sections to A2A Message Parts and Artifacts.
