# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Nature

This is a **specification-only repository** today. Source code (a reference validator and example corpus) is planned under `validator/` and `examples/`, but does not yet exist — there is no build system, package manager, or test suite to run. All current artifacts are Markdown documents defining the **A2AL/2.0 – Project Coordination Profile (Array-Only)** protocol.

## Repository Layout

- `specs/` — normative grammar (`A2A-Grammar.md`) and rulebook (`A2A-Rulebook.md`)
- `examples/` — worked examples per archetype, transpilation samples (planned)
- `validator/` — reference validator and conformance test corpus (planned)
- `Session.md` — design session summary (historical / rationale)
- `OpenSource.md` — open-standard promotion and governance plan
- `README.md`, `LICENSE` (Apache-2.0), `CLAUDE.md` — top-level

## Authoritative Files

The spec is split across two normative documents in `specs/`. When answering protocol questions, always cross-check both — the README is overview only.

- `specs/A2A-Grammar.md` — **the normative grammar**. Defines primitive types, header/body shape, all seven archetypes, canonicalization rules, and forward-compat rules. This is the source of truth for any structural question.
- `specs/A2A-Rulebook.md` — reader/writer agent obligations (what must be emitted, what must be ignored, validation behavior).
- `Session.md` — design rationale and what was proven during the design session. Use as context, not as spec.
- `OpenSource.md` — governance/adoption plan, not protocol content.

## Architecture: What A2AL Is

A2AL replaces narrative agent communication (Markdown reports, prose status updates) with a deterministic, array-only wire format. The mental model has three layers; understanding all three is required before suggesting any change to the grammar.

1. **Wire format (Array-Only JSON subset):** every message is `[H, B]` — a two-element array of header and body. **No objects, no `null`, no floats, no NaN.** Maps are encoded as KV-lists `[[k,v],...]`. This constraint is load-bearing: it is what makes messages deterministic and token-minimal.
2. **Seven archetypes (typ=1..7):** every body conforms to exactly one archetype. The set is closed; do not propose an eighth archetype without explicit user direction. Each archetype has a one-character lane tag at body position 0 (`Δ D S R G I O`) and a fixed item shape:
   - A1 Scope Delta `"Δ"` — `[op, etype, id, meta?]`
   - A2 Decision Record `"D"` — `[dkey, dval]` pairs
   - A3 Execution Status `"S"` — `[mkey, mval]` pairs
   - A4 Risk `"R"` — `[sev, vec, impact, action, refs?]`
   - A5 Signals & Gates `"G"` — `[scope, invariant, test?]`
   - A6 Inventory `"I"` — `[kind, id, KV*]`
   - A7 Next Actions `"O"` — `[actor, verb, target, params?]`
3. **Canonicalization:** ordering rules per archetype (see `specs/A2A-Grammar.md` §7.2) make the same semantic message produce the same canonical bytes. **A7 is the only archetype that preserves emission order — do not sort A7.** All others have explicit sort keys.

## Invariants That Are Easy to Violate

These cut across files; flag any proposed change that would break them.

- **No information loss on relay.** Unknown role codes, etype/kind/dkey/mkey codes, and trailing positional fields MUST be preserved verbatim. Receivers must not "helpfully rewrite" unknown codes (`specs/A2A-Grammar.md` §8).
- **Prose ban between agents.** Markdown paragraphs, executive summaries, RCA narratives, apologies, and framing are invalid. Exceptions are narrow: short invariant strings inside `"G"` and labels inside `"R"` (`specs/A2A-Grammar.md` §9.1, `specs/A2A-Rulebook.md` Global Rules).
- **No secrets, ever.** Inventory `kind=7` carries metadata only.
- **Reject, don't repair.** Malformed messages must be rejected; readers never patch them up (`specs/A2A-Rulebook.md` Validation Rules).
- **Extension space starts at `1000+`** for every code registry (roles, etype, kind, dkey, mkey, rk). Do not propose extension codes below 1000.
- **Header `v` MUST equal `2`.** Trailing header fields may be omitted; intermediate fields cannot.
- **Determinism** means same semantic message ⇒ same bytes. Any change that introduces ordering ambiguity is a spec regression.

## Editing Guidance

- When extending registries (role codes, etype, mkey, etc.), add to the recommended list and reserve `1000+` for vendor extensions — do not renumber existing codes.
- When adding examples, encode them in the array-only wire format and verify they satisfy the per-archetype canonical ordering rules in §7.2.
- Keep changes deterministic and minimal. The spec is declared frozen at A2AL/2.0 in `Session.md` and `OpenSource.md` ("Freeze the seven archetypes and message grammar"); structural changes are a major-version event.
