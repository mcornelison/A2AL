# A2AL Tools

Validation and helper tools for the A2AL/0.5.2 library.

> `validate_library.py` needs PyYAML. `a2al_lookup.py`, `a2al_preview.py` and `a2al_lint.py` run on the standard library alone; installing tiktoken makes `a2al_preview.py compare` more precise (see [Token backends](#token-backends)). These tools are the only executable code in A2AL. Everything else is documentation and YAML.

## `validate_library.py`

Checks `library/*.yaml` against the schema in [`library/README.md`](../library/README.md).

### Run

```bash
pip install pyyaml
python tools/validate_library.py
```

Expected output: `OK: 164 entries across 7 files`

### Strict mode

Turns warnings into errors:

```bash
python tools/validate_library.py --strict
```

CI uses this (see [`.github/workflows/ci.yaml`](../.github/workflows/ci.yaml)) to block a merge when style warnings show up.

### Custom directory

```bash
python tools/validate_library.py --library-dir path/to/yamls
```

## `a2al_preview.py`

Shows what A2AL actually saves on a *specific* message, before you spend the effort writing it. I built it because two agents, independently, asked for the same thing in [`specs/feedback/`](../specs/feedback): *show me the savings before I commit to the format.*

### `scan`: is this draft even compressible?

```bash
python tools/a2al_preview.py scan draft.md
```

Goes through a Markdown draft looking for the padding that [`specs/A2A-Core.md`](../specs/A2A-Core.md) §4.1 drops (articles, linking verbs, subjective framing, politeness, filler, greetings). It reports what share of the draft could go, with examples for each category.

At the end it reminds you that compressibility does **not** decide the format. The audience rule (§2.1) does.

### `compare`: was it worth it?

```bash
python tools/a2al_preview.py compare draft.md message.txt
python tools/a2al_preview.py compare draft.md message.txt --threshold 0.25 --json
```

Gives token counts for both versions, the ratio, the saving, and a verdict against `--threshold` (default 0.30). It exits 0 when the saving clears the threshold and 1 when it doesn't, so you can use it in a script.

It also prints some advisory notes:

- Routing header conformance: whether the header is there, any missing required fields, any unrecognised fields (readers preserve and ignore those; they aren't errors), and which optional fields you used.
- Shape detected: which §7 pattern(s) the body matches.
- Anti-patterns (§4.4): rare Unicode and made-up abbreviations. The tokenizer itself is the judge here. A short word that costs more than one token and *isn't* in `library/*.yaml` is exactly the case the spec warns about, where the full word would have been cheaper.

### `count`

```bash
python tools/a2al_preview.py count examples/*.txt
```

### Token backends

Everything runs with no dependencies. Install tiktoken for a more precise answer:

```bash
pip install tiktoken
python tools/a2al_preview.py --encoder o200k_base compare draft.md msg.txt
```

No tokenizer here is "exact" for Claude. Anthropic doesn't publish its vocabulary, so `cl100k_base` has long been the stand-in (see [`testing/tools/CROSS-LLM-RESULTS.md`](../testing/tools/CROSS-LLM-RESULTS.md)). I trust the conclusion because it's stable across four tokenizers: the A2AL/Markdown ratio held at **0.73-0.84** on cl100k, o200k, Llama 3 and Mistral. Use `--encoder` to count with a different one.

`scan` is fine on the heuristic. It reports a share *within one document* (padding tokens over total tokens, both counted the same way), so the error cancels out. I measured that instead of assuming it: across this repo's corpus the reported share moves by at most **0.6 percentage points** compared with cl100k_base, and `test_a2al_preview.py` checks that it stays within 1 point.

`compare` is different. It divides one version by the other, and the error does *not* cancel between formats. On this corpus the heuristic under-counts A2AL by about 9% and over-counts Markdown prose by about 2%, which inflates the ratio by about 11%. That's enough to report a real 26% saving as 34% and land on the wrong side of a 30% threshold.

So without a tokenizer, `compare` reports a **±12 point band** instead of a single number, and it won't guess:

| Situation | Verdict | Exit |
|---|---|---|
| Threshold clears even at the pessimistic end | `WORTH IT` | 0 |
| Threshold missed even at the optimistic end | `MARGINAL` | 1 |
| Threshold falls **inside** the band | `INCONCLUSIVE` (install tiktoken) | 3 |

With a tokenizer the band is zero and the verdict is a straight comparison.

> This tool doesn't validate message shape. A2AL never validates messages, by design; only the library gets validated. Every conformance note above is advisory.

## `a2al_lookup.py`

Makes the vocabulary library cheap to check *while you're writing a message*. I built it after the zero-consultation finding in [`specs/feedback/`](../specs/feedback). Ledger said *"I have not actually consulted `library/*.yaml` during composition"*, and Claude asked for a list of what already exists plus a *"did you mean…"* reflex before inventing a term. Neither had contributed a single library entry.

```bash
python tools/a2al_lookup.py check <candidate> [expansion]   # already covered?
python tools/a2al_lookup.py search <query>                  # find by any field
python tools/a2al_lookup.py list [--domain core]            # what is in here
python tools/a2al_lookup.py stats                           # counts per domain
```

### `check`: did you mean...

Run it before you coin any shortening. It catches the three usual ways a new term turns out to be a mistake, cheapest check first:

| Result | Meaning |
|---|---|
| **ALREADY CANONICAL** | The term is in the library. Use it, and don't redefine it inline (§6.5). |
| **NEAR MISS** | Nothing is spelled that way, but something close is, usually because of a typo. `hotfx` → `hotfix` at 0.909 similarity. |
| **ALREADY COVERED?** | Something else expands to the same meaning. `DR=design-review` turns up `CR` (code review) and `review`. |
| **CLEAR** | Nothing covers it. It reminds you of the §6.4 three-uses threshold and the inline `term=expansion` form. |

The exit code is the result, so you can script it: **1** means something already covers this, **0** means you're clear to coin it.

### No dependencies, on purpose

It only uses the standard library. Having to `pip install` something before you can check a word is exactly the kind of friction that led to the zero-consultation finding. Strict schema validation stays in `validate_library.py` (which does use PyYAML and runs in CI). This tool reads the same files with a small line parser.

That only works if the two parsers agree, so `test_a2al_lookup.py` compares them entry by entry against the real library and fails if they drift apart.

## `a2al_lint.py`

Lints the routing header of a message, and nothing else. It checks line 1 only. Bodies are free-form and never get checked. The one look past line 1 is at line 2, to catch a header that spilled over: a strict reader ends the header at the first newline, so a `cc=` on line 2 just gets dropped.

```bash
python tools/a2al_lint.py examples/*.txt
python tools/a2al_lint.py --strict message.txt
cat message.txt | python tools/a2al_lint.py -
```

For a `.md` file whose line 1 isn't a header, it lints the first line of the first fenced `a2al` block instead (§2.5.1). A Markdown file with a header on line 1 gets linted like any other message.

| Level | Check |
|---|---|
| ERROR | No header on line 1 (or in the `a2al` block) |
| ERROR | Missing or empty required field (`from`, `to`, `date`, `topic`) |
| ERROR | A `; `-separated segment with no `=`, which usually means a `; ` inside the topic |
| ERROR | Duplicate key |
| ERROR | Line 2 continues the header (starts with a known `key=`, or has `; key=` with a known key) |
| ERROR | `date` isn't an ISO 8601 date or datetime |
| WARN | Unknown field. Readers preserve it, so it never fails the lint (forward compat) |
| WARN | `audience` not `agent\|mixed`, `urgency` not `low\|medium\|high\|urgent`, `priority` not `P0`-`P3` |
| WARN | `topic` over 60 chars: put the verdict on body line 1 and keep the topic a label |
| WARN | `refs=` with more than 3 items: keep the ones this message cites, list the rest on a body `refs:` line |
| WARN | `from`/`to`/`cc` party not in `Name(Role)` or `Name/Role` shape |

Output is one `path: LEVEL: message` line per finding, then a summary. It exits 1 on any ERROR and 0 otherwise. `--strict` makes warnings exit 1 too, and `--quiet` prints errors only.

The known field list comes from `a2al_preview.py` (`_REQUIRED_HEADER` / `_OPTIONAL_HEADER`), so the two tools can't disagree about what a header field is.

## `test_examples.py`

Conformance tests for the [`examples/`](../examples) corpus. Standard library only.

A2AL never validates messages, by design, and this doesn't change that. It validates *this repo's own examples*, which are documentation, and documentation that contradicts the spec is a bug.

```bash
python tools/test_examples.py
```

It checks that:

1. Every message has a conformant routing header (§3): required fields present, no unrecognised field names.
2. Every header field the spec documents appears in at least one example. The field list is read straight from `specs/A2A-Core.md` §3.1 and §3.2, so the test can't drift from the spec. If you add a field to the spec table and no example uses it, this fails.
3. Every term a release adds appears in at least one example, following the `NEW_IN_RELEASE` list at the top of the file (a whole new domain is listed as `domain:<name>`). Add a row when a release adds vocabulary.
4. Every message is free of `a2al_lint.py` errors. Warnings are allowed, since an unknown field is a warning by design.
5. There's no rare Unicode anywhere in the corpus (§4.4).

Checks 2 and 3 fail on the *next* release, and that's intended. They turn "this release added X" into something CI can confirm. I wrote them after a sweep found that 8 of the 10 terms added in 0.5.0 existed only inside the changelog announcing them, and that no example used any of 0.5.0's four new header fields.

`INTENTIONAL_UNKNOWN_FIELDS` makes one narrow exception, for `version-skew.md`, which is entirely about a field this version doesn't recognise.

## `test_a2al_lookup.py`

Tests `a2al_lookup.py`, including the parser-agreement check above (which skips itself if PyYAML isn't installed).

```bash
python tools/test_a2al_lookup.py
```

## `test_a2al_lint.py`

Tests `a2al_lint.py`: every check at its level, the `.md` block fallback, the CLI flags and exit codes, and that every `examples/*.txt` is error-free. Standard library only.

```bash
python tools/test_a2al_lint.py
```

## `test_a2al_preview.py`

Tests `a2al_preview.py`. Standard library only, and built the same way as `test_validate_library.py`. Cases that need exact counts skip themselves when tiktoken isn't installed, so the suite passes in a bare environment and covers more in CI.

```bash
python tools/test_a2al_preview.py
```

## `test_validate_library.py`

Tests the validator against `_test_fixtures/` (YAML files that are broken on purpose) and against the real `library/`.

### Run

```bash
python tools/test_validate_library.py
```

Expected: every fixture reports `OK: <name> correctly rejected/accepted`, and the real library passes.

## `_test_fixtures/`

Eight broken YAML files (one per failure mode) and one valid file, used by `test_validate_library.py`.

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

- `tokenize_library.py`: fill in the per-entry `tokens: {claude, gpt, llama}` field using the Anthropic API and tiktoken
- `harvest_terms.py` (roadmap 0.5.2): scan agent inboxes for `term=expansion` definitions used 5 or more times and output candidates ready for a PR
