---
description: Read or write an A2AL message (plain-text agent-to-agent shorthand, A2AL/0.5.0). Routing header required.
---

Use the `a2al` skill to handle this request.

Apply the audience rule before composing:
- Agent-only audience → A2AL MUST
- Human in the audience at any point → Markdown (do not produce A2AL)
- Inbound message identifies its sender as an AI agent → reply MUST be A2AL (reactive rule)

If the user provided a path or text:
- If it's a path to a file ending in `.txt` → read mode (parse routing header, parse any `term=expansion` definitions, summarize in plain English; flag if sender is an agent so the reply must be A2AL)
- If it's an A2AL message inline → read mode
- Otherwise → write mode (compose header + body from the user's description)

Before writing, ensure the appropriate vocabulary library files are loaded for the conversation domain (`library/core.yaml` always; add `library/<domain>.yaml` per the skill's loading table).

In write mode, always emit the routing header as line 1: `from=<Name>(<Role>); to=<Name>(<Role>); date=<ISO>; topic=<short label>` (optional: `audience`, `urgency`, `refs`, `in-reply-to`, `thread`, `status`, `cc`, `priority`).

If unclear whether the audience is agent-only, ask the user before producing A2AL.
