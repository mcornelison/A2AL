## Library contribution checklist

- [ ] I'm adding/changing entries in `library/<domain>.yaml`
- [ ] Each new entry has `term`, `expansion`, and `example`
- [ ] `term` is unique across the entire library (I checked `core.yaml` + all extensions)
- [ ] `term` and `expansion` contain no `--` (would clash with spec separator)
- [ ] I ran `python tools/validate_library.py` locally and it passed
- [ ] If I added 5+ entries, they're related (one PR per logical theme)

## What's the term and why is it useful?

- **Term:** `<your term>`
- **Domain:** `<core | programming | infrastructure | project-mgmt | security | ai-agents | new-domain>`
- **Why this term?** <one sentence>

## Tokenization claim (optional but encouraged)

If you've verified `<term>` is 1 token on Claude/GPT/etc., note it here. Future tooling (v0.5.1+) will auto-validate.

## Other contributions (skill, spec, validator)

If your PR is not a library entry — e.g. you're updating the spec, the skill, or the validator — describe the change and link any relevant issue.
