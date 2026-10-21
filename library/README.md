# A2AL Vocabulary Library

This is the shared vocabulary for A2AL/0.5.1 messages between agents. Each file is a YAML list of `term`/`expansion` entries. An agent loads them into its system prompt so it can write and read the shorthand.

> **Note on 0.4.1 (2026-05-13):** No library content changed in 0.4.1. That release only added the audience rule and the routing header to the spec. Header fields (`from`, `to`, `date`, `topic`, `audience`, `urgency`, `refs`, `in-reply-to`) are part of the spec's structure, not vocabulary, and they're defined in [`specs/A2A-Core.md`](../specs/A2A-Core.md) §3.
>
> **Note on 0.5.0 (2026-06-11):** Added 10 core terms and a new `azure` domain (22 terms), taking the library from 117 to 149 entries. The spec also gained four optional header fields (`thread`, `status`, `cc`, `priority`, §3.2). Like the other header fields, those belong to the spec, not the library.

## Files

| File | Purpose | Entries |
|---|---|---:|
| [`core.yaml`](./core.yaml) | Universal coordination terms. Always load it | 87 |
| [`programming.yaml`](./programming.yaml) | Software development, code review, engineering roles | 9 |
| [`infrastructure.yaml`](./infrastructure.yaml) | Cloud, orchestration, data pipelines, service operations | 15 |
| [`project-mgmt.yaml`](./project-mgmt.yaml) | Cross-industry project and program management | 16 |
| [`security.yaml`](./security.yaml) | Security threats and controls | 10 |
| [`ai-agents.yaml`](./ai-agents.yaml) | AI/LLM/agent terms | 5 |
| [`azure.yaml`](./azure.yaml) | Azure identity, compliance, Fabric data-platform | 22 |
| **Total** | | **164** |

## Industry scope

A2AL is for coordinating work in any field, not just software. I wrote `core.yaml` and `project-mgmt.yaml` to be industry-neutral: state, blockers, decisions, milestones, deliverables and change control mean the same thing on a construction programme, a clinical rollout, a legal matter or a software sprint.

The other domain files are industry-specific by design. The current set leans toward software because that's where A2AL got its first real use: technology teams pick up new tooling quickly, and they produced the first real traffic. Software just happens to be the first domain I worked through. It isn't the template the others have to follow. A domain file for field services, clinical operations, underwriting or logistics is just as welcome, and adding one doesn't need a spec change. Please propose a new industry domain in an issue first.

> **Changed in 0.5.1.** Despite its name, `project-mgmt.yaml` used to hold SRE and service-operations vocabulary (`SRE`, `SLA`, `SLO`, `SLI`, `MTTR`). A project manager outside software who opened the file named for their role found nothing they'd use. Those terms moved to `infrastructure.yaml`, the software roles `EM` and `TPM` moved to `programming.yaml`, and `project-mgmt.yaml` now holds cross-industry project vocabulary. No term was removed or renamed, so no message needs rewriting. But if an agent loads `project-mgmt.yaml` for SRE terms, it now needs to load `infrastructure.yaml` as well.

## Loading model

Agents always load `core.yaml`. The domain files are optional and depend on what the conversation is about:

| Conversation theme | Load |
|---|---|
| General agent coordination | `core.yaml` only |
| Software development / code review | + `programming.yaml` |
| Cloud / infrastructure / data / service ops | + `infrastructure.yaml` |
| Sprint, project, or program management | + `project-mgmt.yaml` |
| Security review / threat modeling | + `security.yaml` |
| LLM / agent / RAG topics | + `ai-agents.yaml` |
| Azure / identity / compliance / Fabric | + `azure.yaml` |

The skill at [`../examples/ClaudeCode/skills/a2al/SKILL.md`](../examples/ClaudeCode/skills/a2al/SKILL.md) tells the agent how to load them. The agent decides which domain files it needs each session.

## Entry schema

Every entry is a YAML object with these fields:

| Field | Required | Type | Purpose |
|---|---|---|---|
| `term` | yes | string | The short form. Must be unique across the entire library. Case-sensitive. |
| `expansion` | yes | string | What it means in full. A single phrase, no `--`, no newlines. |
| `example` | recommended | string | One typical use in a real shorthand sentence. |
| `notes` | optional | string | When to use it, when not to, and any ambiguity to watch for. |

Fields planned for later (tooling will fill these in from v0.4.2+, so don't write them by hand yet):

- `tokens: {claude: int, gpt: int, llama: int}`: cost on each tokenizer
- `usage_count: int`: how often it shows up in real agent traffic
- `accepted_date: string`: the date the PR merged

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

A `term` has to be unique across the whole library, `core.yaml` and every domain file together. The validator enforces this, for a few reasons:

- `RBAC` always means the same thing, whichever domain files an agent loaded
- Two agents that loaded different sets of files can't get different expansions for the same term
- You can search the library as one glossary

If two domains really do need the same term to mean different things, qualify it (`sec-RBAC`, `infra-RBAC`), or move it to core with one agreed meaning.

## Where a term goes

| Goes in `core.yaml` | Goes in a domain file |
|---|---|
| Anyone in tech understands it (`PR`, `AC`, `done`, `merge`) | Domain-specific (`SSRF`, `IaC`, `DAG`, `RAG`) |
| State words (`done`, `passed`, `blocked`, `green`, `red`) | Domain-specific verbs/nouns |
| Severity levels (`crit`, `high`, `med`, `low`, `info`) | Specialized roles (`SRE`, `oncall-primary`) |
| Common roles (`PM`, `QA`, `DEV`, `SEC`) | Project-specific (`product-area-lead`) |

Rule of thumb: if a term turns up in two or more domain files, move it to `core.yaml`. If it only means something within one domain, it stays there.

## Contributing

1. Pick the right file. If every agent should know your term, it goes in `core.yaml`. Otherwise use the matching domain file.
2. Add an entry with `term`, `expansion` and `example`. The expansion must be a single phrase with no `--` and no newlines.
3. Run `python tools/validate_library.py` from the repo root and fix any errors.
4. Open a PR using the template at [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md).
5. CI runs the validator on every PR, and a failure blocks the merge.

The full workflow is in the top-level [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## What to avoid

- ❌ Made-up abbreviations like `cmplt`, `prgm`, `mrg`. They're usually 2-3 tokens, and the full word is often 1.
- ❌ Single-letter codes like `c`, `b`, `r`. They cost more in comprehension than they save in tokens.
- ❌ Rare Unicode like ✓ ✗ ⟳. These are usually several tokens each in Claude's vocab.
- ❌ Redefining a standard term. Don't write `PR=pull-request`; `PR` is already in core.
- ❌ The same term in two domains. The validator catches these.

## Versioning

The library follows the A2AL version. Adding entries is a minor version bump (for example A2AL/0.4.1 to A2AL/0.4.2). Renaming or removing a term is a major bump.

`VersionHistory.md` records what each release added to the library.
