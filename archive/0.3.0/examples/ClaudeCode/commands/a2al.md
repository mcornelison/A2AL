---
description: Read, write, or validate an A2AL/0.3.0 message
---

Use the `a2al` skill to handle this request.

If the user provided a path or a JSON blob:
- If it's a path to a file ending in `.json` → read mode (summarize the message)
- If it's a JSON object literal → read mode (parse and summarize)
- Otherwise → write mode (produce a canonical A2AL message from the user's description)

If unclear, ask the user: "Reading an existing A2AL message, writing a new one, or validating?"
