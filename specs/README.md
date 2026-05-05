# A2AL Specification

Normative documents defining A2AL/2.0.

| File | Status | Description |
|---|---|---|
| [A2A-Grammar.md](./A2A-Grammar.md) | Normative | Wire format, archetypes, canonicalization, forward-compat |
| [A2A-Rulebook.md](./A2A-Rulebook.md) | Normative | Reader and Writer agent obligations |

The grammar is the source of truth for any structural question. The rulebook governs agent behavior on top of the grammar.

## Conformance

An implementation is **A2AL/2.0 conformant** if and only if it:

1. Emits messages whose canonical bytes match `A2A-Grammar.md` §7 for every input.
2. Validates incoming messages per `A2A-Grammar.md` §1–§6, **rejecting** (not repairing) malformed input.
3. Preserves unknown role codes, archetype-extension codes, and trailing positional fields verbatim when relaying (§8).
4. Never emits prose between agents except where explicitly permitted by §9.1.
5. Never emits secret values; inventory carries metadata only (§9.2).

A future `validator/` module will provide automated conformance checks against a golden test corpus.

## Stability

A2AL/2.0 is frozen. Adding new archetypes is a major-version change; new codes within existing registries (etype, mkey, vec, verb, etc.) MUST use the reserved `1000+` extension space and MUST NOT renumber existing codes.
