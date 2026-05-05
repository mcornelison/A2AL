# A2AL Reference Validator

Reference validator and conformance test corpus for A2AL/2.0.

> **Status:** Planned. Language and packaging TBD.

## Scope

- **Validator** — given an A2AL message, verify type bans, archetype shape, ordering, and forward-compat preservation rules per `specs/A2A-Grammar.md`.
- **Conformance corpus** — golden positive and negative test cases that any compliant implementation should pass / reject. The corpus is the binding behavioral definition of conformance, complementing the prose specification.

## Non-Goals

- Repairing malformed messages — the rulebook explicitly forbids this.
- Decoding into a domain object model — A2AL is intentionally schema-less above the grammar layer.
- Transport adapters (HTTP/WS/MQTT/etc.) — A2AL is transport-agnostic; transports belong to integrating implementations.
