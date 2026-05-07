# A2AL Specification

Normative documents defining A2AL/0.3.0.

| File | Status | Description |
|---|---|---|
| [A2A-Core.md](./A2A-Core.md) | Normative | Envelope, sections, type bans, canonicalization, validation |
| [A2A-Rulebook.md](./A2A-Rulebook.md) | Normative | Reader, writer, and relay agent obligations |
| [IMPLEMENTING.md](./IMPLEMENTING.md) | Implementer guide | Writer / reader algorithms and validation pipeline |

The core defines the wire format and contract; profiles in [`../profiles/`](../profiles) define domain vocabulary and ordering rules.

## Conformance

An implementation is **A2AL/0.3.0 conformant** if it:

1. Validates every positive case in `validator/corpus/core/valid.json`
2. Rejects every negative case in `validator/corpus/core/invalid.json`
3. For every profile it claims to support: passes that profile's `valid.json` and rejects its `invalid.json`
4. Preserves unknown intents, profiles, sections, and envelope fields verbatim when relaying (forward-compat per `A2A-Core.md` §7)
5. Rejects malformed messages — never repairs

The corpus is the binding behavioral definition; the prose specification is its rationale.

## Stability

A2AL/0.3.0 is pre-1.0. Breaking changes are expected before /1.0 is reached. Profiles version independently from the core (e.g. `project-coord/1.0`).
