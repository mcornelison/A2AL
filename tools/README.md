# A2AL Tools

Validation and helper tooling for the A2AL/0.5.0 library.

> Requires PyYAML (`pip install pyyaml`). The validator is the only part of A2AL that is executable code; everything else is documentation and YAML.

## `validate_library.py`

Validates `library/*.yaml` against the schema documented in [`library/README.md`](../library/README.md).

### Run

```bash
pip install pyyaml
python tools/validate_library.py
```

Expected output: `OK: 149 entries across 7 files`

### Strict mode

Promote warnings to errors:

```bash
python tools/validate_library.py --strict
```

Used by CI (see [`.github/workflows/ci.yaml`](../.github/workflows/ci.yaml)) to block merges when style warnings appear.

### Custom directory

```bash
python tools/validate_library.py --library-dir path/to/yamls
```

## `a2al_preview.py`

Shows what A2AL actually buys on a *specific* message, before you pay the composition cost. Built in response to the same request from two independent agents in [`specs/feedback/`](../specs/feedback): *show me the savings before I commit to the format.*

### `scan` — is this draft even compressible?

```bash
python tools/a2al_preview.py scan draft.md
```

Audits a Markdown draft for the padding [`specs/A2A-Core.md`](../specs/A2A-Core.md) §4.1 drops — articles, linking verbs, subjective framing, politeness, filler, greetings — and reports what share of the draft is recoverable, with examples per category.

Ends by restating that compressibility does **not** decide the format. The audience rule (§2.1) does.

### `compare` — was it worth it?

```bash
python tools/a2al_preview.py compare draft.md message.txt
python tools/a2al_preview.py compare draft.md message.txt --threshold 0.25 --json
```

Token counts for both renderings, the ratio, the saving, and a verdict against `--threshold` (default 0.30). Exits 0 when the saving clears the threshold, 1 when it does not — so it composes into a script.

Also reports, as advisory notes:

- **Routing header conformance** — present, missing required fields, unrecognised fields (which are preserved-and-ignored by readers, not errors), and which optional fields are in use.
- **Shape detected** — which §7 pattern(s) the body matches.
- **Anti-patterns (§4.4)** — rare Unicode, and invented abbreviations. It uses the tokenizer itself as the oracle: a short word costing more than one token that is *not* in `library/*.yaml` is exactly the case the spec warns about, where the full word would have been cheaper.

### `count`

```bash
python tools/a2al_preview.py count examples/*.txt
```

### Token backends

`compare` **requires** tiktoken, because its verdict turns on a threshold and a threshold needs exact counts:

```bash
pip install tiktoken
```

`scan` works without it, falling back to a stdlib heuristic. That fallback is sound for `scan` because it reports a share *within one document* — both numbers measured the same way, so the error cancels.

It is deliberately **not** trusted for `compare`. Measured against `cl100k_base` over this repo's own corpus, the heuristic under-counts A2AL by ~9% and over-counts Markdown prose by ~2%, inflating an A2AL/Markdown ratio by ~11% — enough to report a real 26% saving as 34% and cross a 30% threshold in the wrong direction.

> This tool validates nothing about message shape. A2AL never validates messages, by design — only the library is validated. Every conformance note above is advisory.

## `test_a2al_preview.py`

Tests `a2al_preview.py`. Stdlib only; same shape as `test_validate_library.py`. Cases needing exact counts self-skip when tiktoken is absent, so the suite passes in a bare environment and covers more in CI.

```bash
python tools/test_a2al_preview.py
```

## `test_validate_library.py`

Tests the validator against `_test_fixtures/` (intentionally-broken YAML files) plus the real `library/`.

### Run

```bash
python tools/test_validate_library.py
```

Expected: every fixture reports `OK: <name> correctly rejected/accepted` and the real library passes.

## `_test_fixtures/`

Eight broken YAML files (one per failure mode) plus one valid fixture. Used by `test_validate_library.py`.

| File | Failure mode |
|---|---|
| `missing-domain.yaml` | top-level `domain` key missing |
| `wrong-domain-name.yaml` | `domain` value doesn't match filename stem |
| `missing-entries.yaml` | top-level `entries` key missing |
| `empty-entries.yaml` | `entries: []` |
| `missing-term.yaml` | entry has no `term` |
| `missing-expansion.yaml` | entry has no `expansion` |
| `term-with-dash-dash.yaml` | `term` contains `--` |
| `expansion-with-newline.yaml` | `expansion` contains a newline |
| `valid.yaml` | clean fixture (happy path) |

## Future tools

- `tokenize_library.py` — auto-populate per-entry `tokens: {claude, gpt, llama}` field using the Anthropic API and tiktoken
- `harvest_terms.py` (roadmap 0.5.2) — scan agent inboxes for `term=expansion` definitions used 5+ times, output PR-ready candidates
- `search.py` (roadmap 0.5.3) — quick lookup across all library files
