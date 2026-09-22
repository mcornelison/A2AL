# A2AL Tools

Validation and helper tooling for the A2AL/0.5.0 library.

> `validate_library.py` requires PyYAML; `a2al_preview.py compare` requires tiktoken. `a2al_lookup.py` and `a2al_preview.py scan` are stdlib-only. These tools are the only executable code in A2AL; everything else is documentation and YAML.

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

## `a2al_lookup.py`

Makes the vocabulary library cheap to consult *while composing*. Built for the zero-consultation finding in [`specs/feedback/`](../specs/feedback): Ledger — *"I have not actually consulted `library/*.yaml` during composition"* — and Claude, who asked for a list of what already exists plus a *"did you mean…"* reflex before inventing a term. Both had zero library contributions.

```bash
python tools/a2al_lookup.py check <candidate> [expansion]   # already covered?
python tools/a2al_lookup.py search <query>                  # find by any field
python tools/a2al_lookup.py list [--domain core]            # what is in here
python tools/a2al_lookup.py stats                           # counts per domain
```

### `check` — the did-you-mean reflex

Run it before coining any shortening. It catches the three ways a new term is usually a mistake, cheapest check first:

| Result | Meaning |
|---|---|
| **ALREADY CANONICAL** | The term is in the library. Use it; don't redefine it inline (§6.5). |
| **NEAR MISS** | Nothing is spelled that way, but something close is — usually a typo. `hotfx` → `hotfix` at 0.909 similarity. |
| **ALREADY COVERED?** | Something else expands to the same meaning. `DR=design-review` surfaces `CR` (code review) and `review`. |
| **CLEAR** | Nothing covers it — with a reminder of the §6.4 three-uses threshold and the inline `term=expansion` form. |

Exit code is the signal, so it scripts: **1** = something already covers this, **0** = clear to coin.

### No dependencies, on purpose

Stdlib only. Needing `pip install` before you can check a word is exactly the friction that produced the zero-consultation finding. Strict schema validation stays in `validate_library.py` (which does use PyYAML, and runs in CI); this reads the same files with a small line parser.

That is only safe if the two parsers agree, so `test_a2al_lookup.py` compares them entry by entry against the real library and fails on any drift.

## `test_examples.py`

Conformance tests for the [`examples/`](../examples) corpus. Stdlib only.

A2AL never validates messages, by design. This does not change that — it validates *this repository's own examples*, which are documentation, and documentation that contradicts the spec is a bug.

```bash
python tools/test_examples.py
```

Asserts:

1. **Every message carries a conformant routing header** (§3) — required fields present, no unrecognised field names.
2. **Every header field the spec documents appears in at least one example.** The field list is parsed out of `specs/A2A-Core.md` §3.1 and §3.2, so the test cannot drift from the spec: add a field to the spec table without exercising it and this fails.
3. **Every term a release adds appears in at least one example**, per the `NEW_IN_RELEASE` manifest at the top of the file (a whole new domain is named `domain:<name>`). Add a row when a release adds vocabulary.
4. No rare Unicode anywhere in the corpus (§4.4).

Checks 2 and 3 fail on the *next* release, which is the point — they turn "we shipped a feature" into something CI can prove. They were written after a sweep found that 8 of the 10 terms added in 0.5.0 existed only inside the changelog announcing them, and that none of 0.5.0's four new header fields was demonstrated anywhere.

`INTENTIONAL_UNKNOWN_FIELDS` narrowly exempts `version-skew.md`, whose whole subject is a field this version does not recognise.

## `test_a2al_lookup.py`

Tests `a2al_lookup.py`, including the parser-agreement check above (which self-skips if PyYAML is absent).

```bash
python tools/test_a2al_lookup.py
```

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
