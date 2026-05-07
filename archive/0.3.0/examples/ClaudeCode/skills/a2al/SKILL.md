---
name: a2al
description: Use when the user asks to send an agent-to-agent message, convert a Markdown report into A2AL, read or summarize an A2AL JSON file, or validate one. Replaces verbose MD reports with a structured token-minimal envelope. Triggers on phrases like "send the PM details", "convert this to A2AL", "what does this A2AL message say", "validate this A2AL".
---

# A2AL Skill

A2AL/0.3.0 is a structured JSON wire format for agent-to-agent communication. This skill helps you read, write, and validate A2AL messages.

Reference: https://github.com/mcornelison/A2AL

## When to use

- User asks to send another agent a status update, decision, action directive, blocker, risk brief, or similar — produce an A2AL message instead of an MD report
- User asks to read or summarize an existing A2AL JSON file
- User asks to validate that a message conforms to the spec

## Mode 1: Reading an A2AL message

1. Open the file or take input as JSON. Parse it as a JSON object.
2. Validate the core envelope:
   - `v` matches `0.3.x`
   - `from` is `[name, role]` (two strings)
   - `to` is `[name, role]` or an array of those, non-empty
   - `id`, `intent`, `profile` are strings
3. Identify the profile (`project-coord/1.0`, `social-post/1.0`, or other)
4. For each section present (delta, status, actions, decision, risk, gates, inventory, refs, body, plus profile-specific like title/submolt/tags), summarize the items in 1–2 sentences
5. Reply to the user with a short structured summary: who → who, what intent, what changes/actions, key references

## Mode 2: Writing an A2AL message

1. Pick the profile that fits the user's domain:
   - Project / sprint / PMO / risk briefs → `project-coord/1.0`
   - Agent social posts (Moltbook-style) → `social-post/1.0`
   - Other → ask the user or default to `project-coord/1.0`
2. Pick the intent. For project-coord: `review-observations`, `blocker`, `sprint-closeout`, `status-report`, `risk-brief`, `decision`, `next-actions`, `inventory-update`, `gates-update`, `closeout`. For social-post: `post`, `comment`, `reply`, `edit`, `delete`.
3. Build the envelope:
   - `v: "0.3.0"`
   - `from`: `[name, role]` — use the user's persona/role if they have one
   - `to`: `[name, role]` for one recipient, or `[[name1, role1], [name2, role2]]` for many
   - `id`: a unique opaque string (timestamp-prefixed is fine)
   - `intent`: from the profile's vocabulary
   - `profile`: e.g. `"project-coord/1.0"`
   - `ts`: unix epoch seconds (recommended)
   - `thread`: a conversation id if applicable (recommended)
4. Populate sections appropriate to the intent:
   - `delta` — entity state changes: `[op, id, note?]` where op is `add` / `remove` / `modify` / `rescope` / `complete` / `block` / `defer` / `start`
   - `status` — current metrics: `[metric, value]`
   - `actions` — directives: `[actor, verb, target, params?]` — emission order matters, do NOT sort
   - `decision` — decisions: `[key, value]`
   - `risk` — threats: `[sev, vector, impact, action, refs?]`; sev ∈ `crit` / `high` / `med` / `low` / `info`
   - `gates` — invariants: `[scope, invariant, test?]`
   - `inventory` — topology: `[kind, id, kvs?]`
   - `refs` — citations: `[kind, value]`; kinds: `commit`, `file`, `url`, `us`, `cve`, `msg`, `doc`
   - `body` — prose tail for irreducible rationale (use sparingly)
5. Apply canonical ordering for `project-coord/1.0`:
   - `delta` sorted by `(op, id)` ascending
   - `status` sorted by `metric` ascending
   - `decision` sorted by `key` ascending
   - `risk` sorted by `sev` descending then `vector` ascending; sev rank: crit(4) > high(3) > med(2) > low(1) > info(0)
   - `gates` sorted by `(scope, invariant)` ascending
   - `inventory` sorted by `(kind, id)`; KVs within each item sorted by `k`
   - `actions` and `refs` — emission order, do NOT sort
6. Type bans — apply anywhere in the tree:
   - No `null`. Use field omission for "absent."
   - No floats. Use strings or scaled ints if you need decimals.
   - No NaN/Infinity.
7. Serialize as JSON. Receivers will accept whitespace, but canonical bytes have none.

## Mode 3: Validating

If a Python validator exists at `validator/python/validate.py` (or similar) in the user's project, run it:

```bash
python validator/python/validate.py path/to/msg.json
```

Otherwise, manually check:
- All required envelope fields present
- No null / float / NaN anywhere
- `from`/`to` are correctly shaped
- For `project-coord/1.0`: all sections in canonical order
- For `social-post/1.0`: `intent="post"` has `title`, `submolt`, `body`; comment/reply/edit/delete have `in-reply-to`

## Worked example — write

User: "Send Ledger the closeout for the hotfix sprint. US-713 needed no code change (already in main from US-671). US-714 is the warnOnly DQ flag. All preflight tests and DQ tests pass. He needs to merge."

You produce:

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
  "status": [["dq-tests", [21, 21]], ["preflight", [878, 878]]],
  "actions": [["Ledger", "merge", "ralph/pipeline-hotfix-2026-04-17"]],
  "refs": [["us", "US-713"], ["us", "US-714"]]
}
```

## Worked example — read

User: "What does this A2AL message say?" (provides the JSON above)

You reply:

> Sprint closeout from Ralph (DEV) to Ledger (PM), thread `pipeline-hotfix-2026-04-17`.
>
> **Status changes:** US-713 and US-714 both complete. US-713 needed no code change (fix already in main from US-671). US-714 is the warnOnly DQ flag implementation.
>
> **Metrics:** 21/21 DQ tests pass, 878/878 preflight pass.
>
> **Action needed:** Ledger to merge `ralph/pipeline-hotfix-2026-04-17`.

## When NOT to use this skill

A2AL/0.3.0 has a fixed envelope cost (~150 tokens) that must amortize across structured payload. For messages without that structure, A2AL is net-negative on tokens — it makes the message more expensive, not less. Use the `a2a-shorthand` skill instead when:

- The message is a handshake, ack, or single-fact update
- The message is conversational coordination ("merge?", "blocked on X")
- The message has ≤3 metrics, ≤3 deltas, or ≤3 actions and no other structured content
- The body is mostly prose without extractable structured fields (a Moltbook-style post is still A2AL because the `social-post/1.0` profile expects `title`/`submolt`/`body` — but a free-form chat message is not)

If you're unsure, count structured items. **5+ structured items = A2AL. Below that = shorthand.**

The two skills are complementary. The `a2a-shorthand` skill will route back to `a2al` when its threshold is exceeded.
