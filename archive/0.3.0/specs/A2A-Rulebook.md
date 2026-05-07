# A2AL/0.3.0 Reader–Writer Rulebook

This document defines the mandatory rules for agents that **emit** or **consume** A2AL/0.3.0 messages. It is companion to `specs/A2A-Core.md` (normative grammar) and the per-profile rules in `profiles/*.md`.

## Roles

### Writer agent
Translates verbose or human-oriented inputs into A2AL messages. Writers own canonicalization.

### Reader agent
Consumes A2AL messages and updates internal state or executes actions. Readers own validation.

## Global Rules (Non-Negotiable)

1. If information does **not change agent behavior**, it must not be transmitted
2. Narrative prose is forbidden as a substitute for structured sections; `body` is for the irreducible 10–20% only
3. Every message MUST satisfy the core envelope (specs/A2A-Core.md §3)
4. Every message MUST declare a `profile`
5. Messages are immutable once emitted; corrections are new messages

## Writer Rules

- Emit only **current truth and deltas**; strip history, background, and rhetorical structure
- Pick the smallest profile that fits — don't shoehorn a Moltbook post into project-coord
- Apply the profile's canonical ordering before emit (when defined)
- Use field omission for "absent"; never null
- Include `refs` for any factual claim that points to an external artifact (commit, file, story, URL, prior message)

## Reader Rules

- Consume messages literally; never infer beyond provided semantics
- Unknown intents — accept and dispatch best-effort; do not reject
- Unknown profiles — accept and preserve; MAY decline to act if uninterpretable
- Unknown sections — preserve verbatim when relaying; treat as opaque payload
- No attempts at "understanding context" beyond the message
- Do not reintroduce narrative internally

## Validation Rules

- Missing required envelope fields → reject
- Forbidden types (null, float, NaN, Infinity) anywhere → reject
- Identity tuple shape violation → reject
- Profile-required field missing → reject
- Free-text outside defined structures → reject
- **Reject, don't repair.** Malformed messages MUST be discarded, not patched

## Relay Rules (forwarding without acting)

- Preserve unknown codes, sections, and envelope fields verbatim
- Do not re-canonicalize unless the relay is explicitly authorized to canonicalize
- Do not strip fields the relay doesn't recognize

## Design Principle

**Agents exchange state, not explanations.** Profiles define vocabulary; the core defines the contract.
