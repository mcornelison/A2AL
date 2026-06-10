# A2AL Version History

| Version | Date | Brief Name | Description |
|---|---|---|---|
| 0.4.2 | 2026-05-28 | Idempotent Install Prompt | Adds `examples/ClaudeCode/INSTALL-PROMPT.md`, an AI-agent-consumable install flow that handles fresh installs and idempotent re-syncs in one file. Two phases: conversational decisions (identity, peers, scope, library mode) then deterministic execution (clone, copy, CLAUDE.md write/diff, verify). Re-sync mode short-circuits Phase 1 via file-existence detection and replaces the CLAUDE.md write with a section-by-section diff loop that normalizes operator placeholder fill-ins before diffing — so only genuine spec drift prompts the operator. This is the supported upgrade path for all 0.x.x. No protocol changes; no library content changes; no spec changes. See `examples/ClaudeCode/INSTALL-PROMPT.md`. |
| 0.4.1 | 2026-05-13 | Audience Rule + Routing Header | Two normative additions drawn from real-agent usage feedback (Ledger/PM, Kunai/DW-Arch, and a third Claude session): (1) **Audience rule** — agent-only audience → A2AL MUST; human in audience → Markdown; default Markdown when ambiguous. (2) **Routing header** — every A2AL message MUST begin with a single-line header (`from=...; to=...; date=...; topic=...` plus optional `audience`, `urgency`, `refs`, `in-reply-to`). Adds a reactive rule: agent-identified inbound → A2AL reply. No library content changes. Skill rewritten to lead with audience rule + header. See `specs/A2A-Core.md` §§2–3. |
| 0.4.0 | 2026-05-07 | Open Vocabulary Library | A2AL is now a plain-text shorthand spec + open vocabulary library at `library/*.yaml`. The /0.3.0 JSON envelope is deprecated and archived. Reference Python validator (`tools/validate_library.py`) enforces schema and cross-domain term uniqueness on every PR via GitHub Actions CI. Seed library: 117 entries across 6 files (core + programming + infrastructure + project-mgmt + security + ai-agents). |
| 0.3.1 | 2026-05-05 | Plain-text agent shorthand (sibling) | Sibling to A2AL/0.3.0 for short conversational messages. Style guide and recommended jargon palette designed to tokenize efficiently on Claude's tokenizer. Plain text — no envelope, no JSON. Decision rule: 5+ structured items = A2AL; below = shorthand. |
| 0.3.0 | 2026-05-05 | Flexible Object + Profiles (deprecated) | Flat-object format with descriptive envelope keys; positional section items; profile-extensible. Two reference profiles: `project-coord/1.0` and `social-post/1.0`. Reference Python validator runs in core + profile-aware modes. **Archived 2026-05-07** in favor of /0.4.0 after live test data showed the JSON envelope cost 1.46×–3.55× more tokens than plain Markdown. |
| 0.2.0 | (early 2026) | Conceptual prototype | Prototyped a few conceptual ideas; worked through basic logic and communication exchange. Later codified by CoPilot as an array-only positional A2AL/2.0 draft (preserved in git history). Superseded by 0.3.0. |
| 0.1.0 | (early 2026) | Idea hatched | Brainstorming on the agent-to-agent communication idea. No artifact beyond notes. |

## Companion Specs

Some entries in the version table are versioned independently of the core A2AL spec. They use a prefix:

- Core spec: bare version (`0.4.0`, `0.3.0`, `0.2.x`)
- Companion: `<name>/<version>` (e.g., `a2a-shorthand/0.1.0`)

The shorthand companion was promoted into the core spec at /0.4.0; there are currently no active companion specs. The /0.3.0 profiles (`project-coord/1.0`, `social-post/1.0`) are archived alongside their parent spec at tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0/profiles).

## Versioning Policy

A2AL follows semantic versioning:

- **MAJOR (x.0.0)** — breaking change to spec style rules, removing or renaming library terms, changing validator API
- **MINOR (0.x.0)** — new library entries, new domain extension files, new optional spec sections, new skill features
- **PATCH (0.0.x)** — typo fixes, doc clarifications, validator bug fixes, new examples

Pre-1.0 means breaking changes are expected. /1.0 is reached when:

- At least one production agent emits and consumes A2AL successfully
- Cross-LLM compatibility (Moltbook beta) has been demonstrated

Library entry additions are batched into periodic minor-version bumps (usually monthly when activity warrants). Each batch is recorded as a new row in this table.

## Roadmap

| Version | Theme |
|---|---|
| 0.4.3 | `thread=<id>` optional header field (surfaced by 0.4.1 adoption-test gap). Non-breaking. |
| 0.4.4 | Tokenization validator tooling (auto-populate `tokens: {claude, gpt, llama}` per entry) |
| 0.4.5 | Auto-harvested PR candidates from agent traffic |
| 0.4.6 | Library search/lookup CLI |
| 0.5.0 | Moltbook beta — cross-LLM validation (early data already arriving from shell-prompt's MoltBook field-test, see `specs/feedback/2026-05-16-shell-prompt-moltbook-fieldtest.md`) |
| 0.5.x | Cross-platform skill installations (OpenAI Assistants, raw API, etc.) |
| 1.0.0 | Production agents using A2AL successfully + Moltbook beta proven |
