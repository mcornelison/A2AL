# Markdown → A2AL Transpilation Example

Worked example showing how a verbose Markdown sprint-closeout MD becomes a single A2AL/0.3.0 `project-coord/1.0` message. The receiving agent's behavior is identical, but with ~80% fewer tokens and zero ambiguity.

> **Status:** Illustrative. Token counts approximate.

---

## Source: Markdown Sprint Closeout (~1500 tokens)

```markdown
---
from: Ralph
to: Ledger (PM)
date: 2026-04-17
priority: sprint closeout — hotfix sprint pipeline-hotfix-2026-04-17
subject: Both hotfix stories addressed; ready for your merge decision
---

# Summary

Both stories in `ralph/pipeline-hotfix-2026-04-17` are addressed. One required no code
change; one was implemented via the architect's recommended approach. Commit pushed to
the feature branch — merge to main is your call.

# US-713 — Employee Master unique_id

**Outcome:** No code change required. The fix was already in main from US-671
(commit `98b483d`, 2026-04-16). Verified line 868 of `Silver_Master_Employee.ipynb`
has the `unifiedDf.withColumn("unique_id", F.monotonically_increasing_id())` call
in the correct position (after `dropDuplicates`, before `runMatching`).

[... ~70 more lines of prose covering verification, files changed, deploy path, follow-up risks ...]
```

## Target: A2AL/0.3.0 `project-coord/1.0` (~280 tokens)

See [`examples/project-coord/sprint-closeout.json`](./project-coord/sprint-closeout.json) for the full file.

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
  "status": [["dq-tests", [21, 21]], ["preflight", [878, 878]], ["ruff", "pass"]],
  "actions": [["Ledger", "merge", "ralph/pipeline-hotfix-2026-04-17"]],
  "refs": [["commit", "98b483d"], ["us", "US-713"], ["us", "US-714"]],
  "body": "warnOnly downgrades FAIL→WARNING for opt-in checks. Hard FAILs preserved."
}
```

## What Was Stripped, What Was Kept

| Markdown content | A2AL field | Why |
|---|---|---|
| YAML front-matter (from, to, date, subject) | `from`, `to`, `ts`, `intent` | Same meaning, structured |
| "Both stories addressed; ready for merge decision" | `actions[0]` | Action directive |
| "US-713 — Employee Master unique_id … no code change required" | `delta[0]` | State change |
| "US-714 — warnOnly implemented" | `delta[1]` | State change |
| "Verified line 868 of Silver_Master_Employee.ipynb has F.monotonically..." | (omitted) | Verification implementation detail; receiver doesn't need it |
| "Preflight tests 878/878; ruff baseline F821 count unchanged" | `status` | Metric snapshot |
| "Per standing project rule, push to main auto-deploys" | (omitted) | Standing rule, not a delta |
| "warnOnly downgrades FAIL→WARNING …" | `body` | Irreducible rationale; receiver MAY surface to humans |
| Files-changed list | `refs` | Citations |

## Why This Matters

A2AL is not "Markdown without formatting." It is a **structured envelope + closed sections + prose tail**. Every kept item maps to a profile-defined section with deterministic meaning. The receiver dispatches on `delta`, `status`, `actions` — no parsing English to act on the message.

For 100 status reports per day across 10 agents, the token savings compound, and so do the inference errors avoided.
