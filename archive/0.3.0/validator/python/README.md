# A2AL Reference Validator (Python)

Reference implementation tracking `specs/A2A-Core.md` and the per-profile rules in `profiles/*.md`.

## Requirements

Python 3.9+. Standard library only — no external dependencies.

## Validate a single message

```bash
echo '{"v":"0.3.0","from":["a","x"],"to":["b","y"],"id":"m","intent":"p","profile":"x/1.0"}' | python validate.py
# VALID

python validate.py path/to/msg.json
```

Exits 0 if valid, 1 with a reason on stderr if invalid.

## Run the conformance corpora

```bash
python test_corpus.py
```

Walks every corpus under `../corpus/` and runs:
- Core cases against `validate_core`
- Profile cases against `validate` (core + profile-aware)

## Modes

The validator has two modes:

| Mode | Function | Checks |
|---|---|---|
| Core | `validate_core(msg)` | Envelope shape, type bans, required fields |
| Profile-aware | `validate(msg)` | Core + per-profile rules when profile is recognized |

Unknown profiles are accepted (forward-compat per spec Section 8).

## Known profiles

| Profile | Handler |
|---|---|
| `project-coord/1.0` | canonical ordering for delta/status/decision/risk/gates/inventory; emission order for actions/refs |
| `social-post/1.0` | required fields per intent (post: title/submolt/body; comment/reply/edit/delete: in-reply-to) |
