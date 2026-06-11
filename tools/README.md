# A2AL Tools

Validation and helper tooling for the A2AL/0.5.0 library.

## `validate_library.py`

Validates `library/*.yaml` against the schema documented in [`library/README.md`](../library/README.md).

### Run

```bash
pip install pyyaml
python tools/validate_library.py
```

Expected output: `OK: 117 entries across 6 files`

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

## Future tools (deferred to v0.5.1+)

- `tokenize_library.py` — auto-populate per-entry `tokens: {claude, gpt, llama}` field using the Anthropic API and tiktoken
- `harvest_terms.py` — scan agent inboxes for `term=expansion` definitions used 5+ times, output PR-ready candidates
- `search.py` — quick lookup across all library files
