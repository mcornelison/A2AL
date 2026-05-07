# Implementing A2AL/0.3.0

Concise implementer's guide for agents that emit or consume A2AL/0.3.0 messages. Companion to `specs/A2A-Core.md` (grammar) and `specs/A2A-Rulebook.md` (agent obligations). Reference Python implementation at `validator/python/`.

## 1. Writer Algorithm

```text
1. PICK A PROFILE that matches the domain
   - Project / PMO / sprint / risk briefs → project-coord/1.0
   - Agent social posts (Moltbook) → social-post/1.0
   - Other → write or pick a profile in profiles/

2. SELECT AN INTENT from the profile's recommended vocabulary
   (or invent one — unknown intents are accepted)

3. BUILD THE ENVELOPE: v, from, to, id, intent, profile
   plus recommended ts, thread, in-reply-to as relevant

4. POPULATE SECTIONS the profile lists as common
   - Project example: delta, status, actions, refs, body
   - Social-post example: title, submolt, body, tags

5. CANONICALIZE per the profile's rules (sort delta by (op, id), etc.)
   actions and refs always preserve emission order

6. SERIALIZE as JSON with no insignificant whitespace
   UTF-8, no BOM, NFC-normalized strings, base-10 ints
```

## 2. Reader Algorithm

```text
1. PARSE the JSON. Expect a top-level object.

2. REJECT forbidden types anywhere in the tree:
   null, float, NaN, Infinity

3. VALIDATE the core envelope:
   - v matches /0.3.x
   - from is [name, role]
   - to is [name, role] or array of those (non-empty)
   - id, intent, profile are strings

4. DISPATCH on profile + intent:
   - Recognized profile + recognized intent → run profile handler
   - Unknown intent → dispatch best-effort
   - Unknown profile → preserve verbatim; MAY decline to act

5. FOR ACTING — read each section the receiver cares about
   For relaying — preserve every field verbatim, including unknown ones

6. REJECT malformed messages, never repair
```

## 3. Validation Pipeline

Fail-fast, in order:

| Stage | Checks |
|---|---|
| Lex | Valid JSON, UTF-8 |
| Type bans | No null / float / NaN / Infinity |
| Top shape | JSON object |
| Required envelope | v, from, to, id, intent, profile present |
| Envelope types | v matches /0.3.x; identity tuple shapes |
| Profile-aware (if recognized) | Per-profile required fields and ordering |

See `validator/python/validate.py` for a working reference (~150 lines).

## 4. Common Mistakes

- **Using `null` for "field not set."** Omit the field instead. Null is ambiguous.
- **Sorting `actions` or `refs`.** Don't. Emission order matters.
- **Putting prose where structure should go.** A 1500-token rationale belongs in `body`, not as `body` replacing the structured sections.
- **Hard-coding profile awareness.** Receivers should accept unknown profiles and preserve them on relay.
- **Repairing malformed input.** Reject. The rulebook forbids repair.

## 5. Conformance

An implementation is conformant if it passes:
- `validator/corpus/core/valid.json` (every case validates)
- `validator/corpus/core/invalid.json` (every case is rejected)
- For each profile it claims to support: that profile's `valid.json` and `invalid.json`

The corpus is the binding behavioral definition; the prose spec is its rationale.
