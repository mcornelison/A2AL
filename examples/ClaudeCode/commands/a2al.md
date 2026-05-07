---
description: Read, write, or compress a peer agent message in A2AL/0.4.0 (plain-text shorthand)
---

Use the `a2al` skill to handle this request.

If the user provided a path or text:
- If it's a path to a file ending in `.txt` → read mode (parse `term=expansion` definitions, summarize in plain English)
- If it's a verbose Markdown / English message → write mode (compress to shorthand following the style guide)
- If it's already shorthand text → read mode (parse and summarize)
- Otherwise → write mode (produce a shorthand message from the user's description)

Before writing, ensure the appropriate vocabulary library files are loaded for the conversation domain (`library/core.yaml` always; add `library/<domain>.yaml` per the skill's loading table).

If unclear, ask the user: "Reading an existing message, writing a new one, or compressing prose?"
