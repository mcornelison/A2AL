# Contributing to A2AL

Thanks for your interest in A2AL/0.5.1. Here's how to help.

## What you can contribute

| Type | Where it goes |
|---|---|
| Library entries (most common) | Add to `library/<domain>.yaml`. For a new domain, open an issue to propose it first. |
| Spec clarifications | Edits to `specs/A2A-Core.md` |
| Skill / command improvements | `examples/ClaudeCode/skills/a2al/SKILL.md` or `examples/ClaudeCode/commands/a2al.md` |
| Validator features or fixes | `tools/validate_library.py` (with tests in `tools/test_validate_library.py`) |
| Tooling | `tools/a2al_lookup.py` (vocabulary lookup) or `tools/a2al_preview.py` (savings preview), each with a matching `test_*.py` |
| Examples | Add a `.txt` to `examples/` showing a pattern that isn't covered yet |
| Documentation | README, library/README, examples/README, etc. |

## Adding a library entry

This is the most common contribution. Here's the process.

1. **Pick the right file.**
   - A universal term every agent should know goes in `library/core.yaml`.
   - A domain-specific term goes in the matching domain file: `programming`, `infrastructure`, `project-mgmt`, `security`, `ai-agents`.
   - If it doesn't fit any of them, open an issue proposing a new domain before you add the file.

2. **Write the entry.** It's YAML, with `term` and `expansion` required and `example` recommended:

   ```yaml
   - term: SLO
     expansion: service level objective
     example: "SLO at 99.7% this quarter"
   ```

   The full schema is in [`library/README.md`](./library/README.md).

   Before you write it, check that nothing already covers it:

   ```bash
   python tools/a2al_lookup.py check <term> [expansion]
   ```

   It exits 1 if the term is already in the library, is a near miss of an existing term, or means the same thing as an existing expansion.

3. **Validate locally:**

   ```bash
   pip install pyyaml
   python tools/validate_library.py
   ```

   Fix any errors and run it again until you see `OK: <N> entries across <M> files`.

4. **Open a PR.** Use the [PR template](./.github/PULL_REQUEST_TEMPLATE.md) and tick every box.

5. **CI runs automatically.** If validation fails, fix it and push again. The same branch is fine.

6. **I review it**, usually within a few days. I may ask you to split it (a PR with 5 or more unrelated entries should be several PRs) or decline it (the term doesn't tokenize well, the expansion is ambiguous, and so on).

## What I look for in a library entry

- It tokenizes well on Claude. Common English words and standard tech jargon are usually 1 token. Made-up abbreviations are often 2-3. Ideally the `term` is 1 token; if it's 2, say why.
- It's unambiguous. A term has one meaning across the whole library. If two domains really use the same term differently, qualify it (`sec-RBAC`, `infra-RBAC`) or move it to core with one agreed meaning.
- It's been used for real. If the term has shown up 3 or more times in actual agent traffic, it goes in quickly. If it's speculative, it waits.
- No `--`. Neither `term` nor `expansion` may contain `--`, because the spec uses it to separate inline rationale.
- No newlines. Entries are single-line.

## What I don't accept (yet)

- Arbitrary symbols (✓ ✗ ⟳ →). These are usually several tokens each in Claude's vocab.
- Abbreviations with the vowels dropped (`cmplt`, `prgm`). They usually come out as 2-3 tokens, and the full word is 1.
- Single-letter codes (`c`, `b`, `r`). They cost more in comprehension than they save.
- Redefinitions of existing terms (don't add `PR=pull-request`; `PR` is already in core).
- The same term in two domains (the validator will catch these).

## Spec or skill changes

If you're making a real change to `specs/A2A-Core.md` or the `a2al` skill:

- Cite the exact section you're changing
- Say what it does to backward compatibility (most spec changes are minor; structural changes mean a major version)
- Update whatever else it touches: examples, library entries, README

## Validator improvements

If you add a check to `tools/validate_library.py`, add a matching fixture to `tools/_test_fixtures/` and a test in `tools/test_validate_library.py`. CI runs the tests on every PR.

## Versioning

- PATCH: typo fixes, doc clarifications, validator bug fixes, examples
- MINOR: new library entries, a new domain file, new optional spec sections, new skill features
- MAJOR: removing or renaming library terms, changing the spec's style rules, breaking the validator's API

I batch library minor-version bumps into a periodic `VersionHistory.md` update, usually monthly when there's enough activity.

## Code of Conduct

Be respectful. Disagreements are normal, so give other contributors the benefit of the doubt. I may decline a PR without a long explanation, usually because the term or edit doesn't fit where the project is going.

## License

By contributing, you agree that your contribution is licensed under the project's [Apache-2.0 license](./LICENSE).
