# A2AL Version History

| Version | Date | Brief Name | Description |
|---|---|---|---|
| 0.4.0 | 2026-05-07 | Open Vocabulary Library | A2AL is now a plain-text shorthand spec + open vocabulary library at `library/*.yaml`. The /0.3.0 JSON envelope is deprecated and archived. Reference Python validator (`tools/validate_library.py`) enforces schema and cross-domain term uniqueness on every PR via GitHub Actions CI. Seed library: 118 entries across 6 files (core + programming + infrastructure + project-mgmt + security + ai-agents). |
| 0.3.1 | 2026-05-05 | Plain-text agent shorthand (sibling) | Sibling to A2AL/0.3.0 for short conversational messages. Style guide and recommended jargon palette designed to tokenize efficiently on Claude's tokenizer. Plain text — no envelope, no JSON. Decision rule: 5+ structured items = A2AL; below = shorthand. |
| 0.3.0 | 2026-05-05 | Flexible Object + Profiles (deprecated) | Flat-object format with descriptive envelope keys; positional section items; profile-extensible. Two reference profiles: `project-coord/1.0` and `social-post/1.0`. Reference Python validator runs in core + profile-aware modes. **Archived 2026-05-07** in favor of /0.4.0 after live test data showed the JSON envelope cost 1.46×–3.55× more tokens than plain Markdown. |
| 0.2.0 | (early 2026) | Conceptual prototype | Prototyped a few conceptual ideas; worked through basic logic and communication exchange. Later codified by CoPilot as an array-only positional A2AL/2.0 draft (preserved in git history). Superseded by 0.3.0. |
| 0.1.0 | (early 2026) | Idea hatched | Brainstorming on the agent-to-agent communication idea. No artifact beyond notes. |

## Companion Specs

Some entries in the version table are versioned independently of the core A2AL spec. They use a prefix:

- Core spec: bare version (`0.4.0`, `0.3.0`, `0.2.x`)
- Companion: `<name>/<version>` (e.g., `a2a-shorthand/0.1.0`)

The shorthand companion was promoted into the core spec at /0.4.0; there are currently no active companion specs. The /0.3.0 profiles (`project-coord/1.0`, `social-post/1.0`) are archived alongside their parent spec at [`archive/0.3.0/profiles/`](./archive/0.3.0/profiles/).

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
| 0.4.1 | Tokenization validator tooling (auto-populate `tokens: {claude, gpt, llama}` per entry) |
| 0.4.2 | Auto-harvested PR candidates from agent traffic |
| 0.4.3 | Library search/lookup CLI |
| 0.5.0 | Moltbook beta — cross-LLM validation |
| 0.5.x | Cross-platform skill installations (OpenAI Assistants, raw API, etc.) |
| 1.0.0 | Production agents using A2AL successfully + Moltbook beta proven |
