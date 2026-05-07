# A2AL/0.3.0 — Archived

This directory contains the complete A2AL/0.3.0 specification and tooling. As of 2026-05-07, /0.3.0 is **deprecated and not maintained**.

## Why archived?

A2AL/0.3.0 used a flat-object JSON envelope with structured sections (delta, status, actions, decision, risk, gates, inventory, refs, body). It was elegant on paper but failed in practice: the envelope cost ~150 tokens minimum, which was 1.46×–3.55× more expensive than plain Markdown across realistic agent-to-agent traffic. On a structured review-observations message the envelope was 89% pure overhead.

The current A2AL/0.4.0 spec replaces the JSON envelope with an open vocabulary library and a plain-text shorthand style guide. See the [top-level README](../../README.md) and [`specs/A2A-Core.md`](../../specs/A2A-Core.md) for the current spec.

## What's in here

| Path | Contents |
|---|---|
| `specs/` | The /0.3.0 normative core spec, rulebook, and implementer guide |
| `profiles/` | The /0.3.0 profiles registry plus `project-coord/1.0` and `social-post/1.0` |
| `examples/` | Worked /0.3.0 examples (project-coord JSON, social-post JSON, Markdown-to-A2AL transpilation) |
| `examples/ClaudeCode/` | The /0.3.0 Claude Code skill and slash command |
| `validator/` | Python reference validator and conformance test corpus |

## Can I still use it?

You can read it for reference. The reference Python validator at `validator/python/validate.py` still runs and the corpus still passes (44/44 cases). But:

- It is not the path A2AL is on going forward
- New profiles, terms, or features will not be added
- Cross-LLM tokenizer work is happening on /0.4.0

Anyone who genuinely needs structured envelope semantics can fork this archive. The /0.4.0 vocabulary library at `../../library/` covers the conversational and short-message cases that motivated A2AL in the first place.

## Test data preserved

The agent-to-agent test exchanges at `../../testing/agent*/inbox/` and the analysis at `../../testing/agent2/analysis.md` use the /0.3.0 JSON format. They are kept in place (not moved here) as the empirical record that motivated the pivot.
