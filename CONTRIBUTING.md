# Contributing to A2AL

Thanks for your interest in A2AL/0.5.0. Here's how to contribute.

## What you can contribute

| Type | Where it goes |
|---|---|
| **Library entries** (most common) | Add to `library/<domain>.yaml`. New domain? Open an issue first to propose it. |
| **Spec clarifications** | Edits to `specs/A2A-Core.md` |
| **Skill / command improvements** | `examples/ClaudeCode/skills/a2al/SKILL.md` or `examples/ClaudeCode/commands/a2al.md` |
| **Validator features or fixes** | `tools/validate_library.py` (with tests in `tools/test_validate_library.py`) |
| **Examples** | Add a `.txt` to `examples/` demonstrating a pattern not yet covered |
| **Documentation** | README, library/README, examples/README, etc. |

## Library entry workflow

This is the most common contribution. Walkthrough:

1. **Pick the right file.**
   - Universal term every agent should know? → `library/core.yaml`
   - Domain-specific? Pick the matching extension: `programming`, `infrastructure`, `project-mgmt`, `security`, `ai-agents`
   - Doesn't fit? Open an issue proposing a new domain before adding the file.

2. **Write the entry.** YAML format with required `term`, `expansion`, recommended `example`:

   ```yaml
   - term: SLO
     expansion: service level objective
     example: "SLO at 99.7% this quarter"
   ```

   See [`library/README.md`](./library/README.md) for the full schema.

3. **Validate locally:**

   ```bash
   pip install pyyaml
   python tools/validate_library.py
   ```

   Fix any errors. Run again until you see `OK: <N> entries across <M> files`.

4. **Open a PR.** Use the [PR template](./.github/PULL_REQUEST_TEMPLATE.md). Tick every box.

5. **CI runs automatically.** If validation fails, fix and push again — same branch is fine.

6. **Maintainer review** — usually within a few days. May suggest splits (PR with 5+ unrelated entries should be multiple PRs) or rejections (term doesn't tokenize well, expansion is ambiguous, etc.).

## What we look for in a library entry

- **Tokenizes well on Claude.** Common English words and standard tech jargon are usually 1 token. Creative abbreviations are often 2–3 tokens. The `term` should ideally be 1 token; if it's 2, justify it.
- **Unambiguous.** A term must have one canonical meaning across the whole library. If two domains genuinely use the same term differently, qualify (`sec-RBAC`, `infra-RBAC`) or promote to core under one canonical meaning.
- **Real-world usage.** Has the term been used 3+ times in actual agent traffic? Fast-track. Pure speculation? Slow-track.
- **No `--`.** Both `term` and `expansion` MUST NOT contain `--` — it's the spec's inline-rationale separator.
- **No newlines.** Entries are single-line.

## What we don't accept (yet)

- Arbitrary symbols (✓ ✗ ⟳ →) — usually multi-token in Claude's vocab
- Vowel-dropped abbreviations (`cmplt`, `prgm`) — usually tokenize as 2–3 tokens; the full word is 1
- Single-letter codes (`c`, `b`, `r`) — comprehension cost outweighs savings
- Re-defining canonical terms (don't add `PR=pull-request` — `PR` is already in core)
- Cross-domain duplicates (the validator will catch these)

## Spec or skill changes

Material edits to `specs/A2A-Core.md` or the `a2al` skill should:

- Cite the exact section being changed
- Note backward-compatibility impact (most spec changes are minor; structural changes are major version events)
- Update related artifacts: examples, library entries, README

## Validator improvements

Add a new check to `tools/validate_library.py`? Add a corresponding fixture to `tools/_test_fixtures/` and a test in `tools/test_validate_library.py`. CI runs the test harness on every PR.

## Versioning

- **PATCH** — typo fixes, doc clarifications, validator bug fixes, examples
- **MINOR** — new library entries, new domain extension, new optional spec sections, new skill features
- **MAJOR** — removing or renaming library terms, changing the spec's style rules, breaking the validator's API

Library minor-version bumps are batched into a periodic `VersionHistory.md` update — usually monthly when activity warrants.

## Code of Conduct

Be respectful. Disagreements are normal; treat fellow contributors charitably. The maintainer reserves the right to decline PRs without elaborate justification — usually because the term/edit doesn't fit the project's direction.

## License

By contributing, you agree your contribution is licensed under the project's [Apache-2.0 license](./LICENSE).
