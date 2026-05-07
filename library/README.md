# A2AL Vocabulary Library

The open vocabulary for A2AL/0.4.0 agent-to-agent communication. Each file is a YAML list of `term`/`expansion` entries that an agent loads into its system prompt to enable shorthand emit and decode.

## Files

| File | Purpose | Entries |
|---|---|---:|
| [`core.yaml`](./core.yaml) | Universal terms — always load | 77 |
| [`programming.yaml`](./programming.yaml) | Code review and dev process | 7 |
| [`infrastructure.yaml`](./infrastructure.yaml) | Cloud, orchestration, data pipelines | 10 |
| [`project-mgmt.yaml`](./project-mgmt.yaml) | Specialized roles, SRE/ops | 8 |
| [`security.yaml`](./security.yaml) | Security threats and controls | 10 |
| [`ai-agents.yaml`](./ai-agents.yaml) | AI/LLM/agent terms | 5 |
| **Total** | | **117** |

## Loading model

Agents always load `core.yaml`. Domain extensions are opt-in by conversation context:

| Conversation theme | Load |
|---|---|
| General agent coordination | `core.yaml` only |
| Code review / dev process | + `programming.yaml` |
| Cloud / infrastructure / data pipelines | + `infrastructure.yaml` |
| Sprint, project, or program management | + `project-mgmt.yaml` |
| Security review / threat modeling | + `security.yaml` |
| LLM / agent / RAG topics | + `ai-agents.yaml` |

The skill at [`../examples/ClaudeCode/skills/a2al/SKILL.md`](../examples/ClaudeCode/skills/a2al/SKILL.md) tells the agent how to load. The agent decides which extensions are relevant per session.

## Entry schema

Every entry is a YAML object with these fields:

| Field | Required | Type | Purpose |
|---|---|---|---|
| `term` | yes | string | Shortened form. Must be unique across the entire library. Case-sensitive. |
| `expansion` | yes | string | Full meaning. Single phrase, no `--`, no newlines. |
| `example` | recommended | string | One canonical usage in a real shorthand sentence. |
| `notes` | optional | string | When to use, when to avoid, ambiguity warnings. |

Future fields (auto-populated by tooling in v0.4.1+, don't write today):

- `tokens: {claude: int, gpt: int, llama: int}` — per-tokenizer cost
- `usage_count: int` — frequency in real agent traffic
- `accepted_date: string` — PR merge date

## File structure

```yaml
domain: <name>           # required, must match filename stem
description: <one-line>  # required, ≥ 10 chars
entries:                 # required, non-empty list
  - term: PR
    expansion: pull request
    example: "PR ready -- merge?"
  - term: AC
    expansion: acceptance criteria
    example: "US-713 done; AC met"
```

## Cross-domain uniqueness

A `term` must be unique across the **entire library** — `core.yaml` and all extensions combined. The validator enforces this. Reasons:

- Predictable interpretation: `RBAC` always means the same thing regardless of which extensions an agent loaded
- Prevents agents from getting different expansions when they load different extension sets
- Library is searchable as one logical glossary

If two domains genuinely need the same term to mean different things, qualify the term: `sec-RBAC`, `infra-RBAC`. Or promote the term to core under one canonical meaning.

## Splitting rules

| Goes in `core.yaml` | Goes in a domain extension |
|---|---|
| Anyone in tech understands it (`PR`, `AC`, `done`, `merge`) | Domain-specific (`SSRF`, `IaC`, `DAG`, `RAG`) |
| State words (`done`, `passed`, `blocked`, `green`, `red`) | Domain-specific verbs/nouns |
| Severity levels (`crit`, `high`, `med`, `low`, `info`) | Specialized roles (`SRE`, `oncall-primary`) |
| Common roles (`PM`, `QA`, `DEV`, `SEC`) | Project-specific (`product-area-lead`) |

Rule of thumb: if a term shows up in two or more domain extensions, promote it to `core.yaml`. If it's only meaningful within one domain, it lives there.

## Contributing

1. Pick the right file. If your term is universal (every agent should know it), it belongs in `core.yaml`. Otherwise pick the matching domain.
2. Add an entry with `term`, `expansion`, and `example`. The expansion must be a single phrase with no `--` or newlines.
3. Run `python tools/validate_library.py` from the repo root. Fix any errors.
4. Open a PR using the PR template at [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md).
5. CI runs the validator on every PR. Merges are blocked on validation failure.

See the top-level [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the full workflow.

## Anti-patterns (avoid)

- ❌ **Creative abbreviations** like `cmplt`, `prgm`, `mrg` — usually 2–3 tokens; the full word is often 1
- ❌ **Single-letter codes** — `c`, `b`, `r` — comprehension cost outweighs token savings
- ❌ **Rare Unicode** — ✓ ✗ ⟳ — usually multi-token in Claude's vocab
- ❌ **Re-defining a canonical term** — don't write `PR=pull-request`; `PR` is already in core
- ❌ **Cross-domain duplicates** — caught by the validator

## Versioning

The library follows the parent A2AL version. Adding new entries is a minor version bump (e.g., A2AL/0.4.0 → A2AL/0.4.1). Renaming or removing a term is a major bump.

`VersionHistory.md` records library additions per release.
