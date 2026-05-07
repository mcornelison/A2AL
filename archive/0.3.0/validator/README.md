# A2AL Reference Validator

Reference validator and conformance test corpus for A2AL/0.3.0.

## Layout

| Path | Contents |
|---|---|
| [`python/`](./python) | Reference validator (`validate.py`) and corpus runner (`test_corpus.py`) |
| [`corpus/core/`](./corpus/core) | Core conformance cases (envelope, type bans) — every validator MUST pass |
| [`corpus/profiles/<profile>/`](./corpus/profiles) | Profile-specific cases — runs only if validator claims to support that profile |

## Quick start

```bash
cd python
python test_corpus.py
```

## Scope

- **Validator** — checks core envelope, type bans, and (when profile is recognized) per-profile rules
- **Conformance corpus** — golden cases. Implementations in any language run against `corpus/**/*.json` directly; the corpus is the binding behavioral definition

## Non-Goals

- Repairing malformed messages — the rulebook explicitly forbids this
- Decoding into a domain object model — A2AL is intentionally schema-thin above the core
- Transport adapters (HTTP/WS/MQTT) — A2AL is transport-agnostic

## Other languages

Ports to TypeScript, Go, and Rust are welcome. Any port should pass the corpus untouched.
