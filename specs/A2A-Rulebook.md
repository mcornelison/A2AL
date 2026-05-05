# A2AL Agent-to-Agent Reader–Writer Rulebook

## Purpose
This document defines the mandatory rules for agents that **emit** or **consume** A2AL messages.

A2AL is designed to eliminate ambiguity, redundancy, and narrative overhead in multi-agent systems.

---

## Roles

### Writer Agent
- Translates verbose or human-oriented inputs into A2AL messages

### Reader Agent
- Consumes A2AL messages and updates internal state or executes actions

---

## Global Rules (Non-Negotiable)

1. If information does **not change agent behavior**, it must not be transmitted
2. Narrative, prose, apology, justification, or framing is forbidden
3. Every message MUST conform to **exactly one** of the seven archetypes
4. Order is deterministic; omissions imply defaults
5. Messages are immutable once emitted

---

## Writer Rules

- Emit only **current truth and deltas**
- Strip history, background, and rhetorical structure
- Normalize data into the minimal archetype representation
- Do not encode intent implicitly — all intent must be explicit

---

## Reader Rules

- Consume messages literally; never infer beyond provided semantics
- Unknown future archetypes must be ignored gracefully
- No attempts at “understanding context” beyond the message
- Do not reintroduce narrative internally

---

## Validation Rules

- Unknown keys or malformed archetypes are errors
- Free-text outside defined structures invalidates the message
- Messages failing validation must be rejected, not repaired

---

## Design Principle

**Agents exchange state, not explanations.**