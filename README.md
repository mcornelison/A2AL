# A2AL — Open Vocabulary for Agent Communication

A2AL is an open, contributable vocabulary library that lets AI agents communicate in token-efficient shorthand. It is plain text, English-derived, designed to tokenize as 1 token per concept on modern LLM tokenizers. Agents share a common dictionary and extend it for their domain.

**Status:** A2AL/0.4.1. Pre-1.0; subject to refinement before /1.0.

**License:** Apache-2.0 — see [LICENSE](./LICENSE).

## Why

In real multi-agent execution, 60–90% of inter-agent tokens are mechanical waste — narrative prose, framing, justification, JSON envelope overhead. A2AL strips that out and exchanges only state and intent in tight shorthand the LLM already speaks. Empirically, A2AL is **~0.26× the token cost** of plain Markdown on a typical handshake — and far less than the JSON-envelope approach we tried in /0.3.0 (now archived).

## How A2AL looks

A complete agent-to-agent message — one routing header line, then the body:

```text
from=Byte(DEV); to=Ledger(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

That's the whole format. No envelope. No JSON. Plain text. The receiving agent has the vocabulary library loaded into its context, expands the shorthand internally, and acts. The header is mandatory (see `specs/A2A-Core.md` §3); the body uses the style guide and library.

For a domain example (security):

```text
from=Audrey(SEC); to=Byte(DEV); date=2026-05-13; topic=CVE-2026-30856; audience=agent; urgency=urgent
crit: RCE in MCP stdio config -- patch ASAP. CVE-2026-30856.
```

For a status report:

```text
from=Byte(DEV); to=Ledger(PM); date=2026-05-13; topic=preflight status; audience=agent
tests 21/21; preflight 878/878; ruff pass; build green.
```

See [`examples/`](./examples) for full worked examples.

## When to write A2AL vs Markdown

A2AL is **mandatory** when the audience is agent-only and **wrong** when a human is in the audience. No hybrid mode; no duplication.

| Situation | Format |
|---|---|
| Agent → agent, no human review expected | A2AL MUST |
| Sender identified itself as an AI agent in an inbound message | A2AL MUST (reactive rule) |
| Human will read or review the message at any point | Markdown |
| Audience ambiguous or mixed | Markdown (default) |
| RCAs, ADRs, design specs, long-form deliberation | Markdown (humans return to these) |

Channels can also be declared agent-only by convention (e.g., paths under `agent-channel/`, `.a2a/`, `*/inbox-internal/`).

## How to install

A2AL/0.4.1 is plain text — no runtime, no compiler. Install means making the vocabulary library and the agent helper skill available to your AI agent.

### For Claude Code agents

Three pieces to install: the skill files, the vocabulary library, and a CLAUDE.md block. Start by cloning the repo:

```bash
git clone https://github.com/mcornelison/A2AL.git /path/to/A2AL
```

Then follow the step-by-step install guide at **[examples/ClaudeCode/README.md](./examples/ClaudeCode/README.md)** — it covers project-scoped vs user-global install, the two library-location strategies (clone-and-point vs copy-locally), the CLAUDE.md block (sample at [`examples/ClaudeCode/CLAUDE.md.sample`](./examples/ClaudeCode/CLAUDE.md.sample), placed right after the first H2 of your CLAUDE.md), verification, and multi-agent setup.

### For other LLM platforms

The vocabulary library at `library/*.yaml` is plain YAML — load any subset into your agent's system prompt. The `specs/A2A-Core.md` style guide is normative and platform-agnostic.

### For library contributors

```bash
git clone https://github.com/mcornelison/A2AL.git
cd A2AL
pip install pyyaml
python tools/validate_library.py
```

## How to use

### Sending a message to a peer agent

In Claude Code, just describe the message:

> "Send Agent2 a quick update — US-713 is done, all tests pass, PR ready to merge."

The `a2al` skill kicks in and produces a header + body:

```text
from=Byte(DEV); to=Agent2; date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

Drop that text into the peer's inbox (or send via whatever transport the agents share).

### Reading a peer agent message

Hand the `.txt` file to the skill (or paste the content). The agent expands shorthand to plain English internally and acts on the meaning.

### Slash command

Explicit invocation: `/a2al` — useful when you want to specifically request shorthand output, or to read a file by path.

### Loading domain extensions

The skill loads `library/core.yaml` automatically. To add domain vocabulary (e.g., when working on infrastructure or security), instruct the agent: "Load `library/security.yaml` for this thread." The agent merges that vocabulary into its dictionary for the session.

## Repository Layout

| Path | Purpose |
|---|---|
| [`specs/A2A-Core.md`](./specs/A2A-Core.md) | Normative A2AL/0.4.1 spec (audience rule, routing header, style guide) |
| [`library/`](./library) | Vocabulary library — `core.yaml` + 5 domain extensions |
| [`examples/`](./examples) | Worked shorthand examples |
| [`examples/ClaudeCode/`](./examples/ClaudeCode) | Claude Code install guide — skill, slash command, sample CLAUDE.md |
| [`tools/`](./tools) | Validator (`validate_library.py`) + tests |
| [`.github/`](./.github) | PR template, CI workflow, issue templates |
| [`testing/`](./testing) | Local agent test harness (gitignored .claude/, tracked test inputs) |
| [`archive/0.3.0/`](./archive/0.3.0) | Deprecated /0.3.0 JSON envelope spec — historical reference |

Start with [`specs/A2A-Core.md`](./specs/A2A-Core.md) for the style guide and [`library/README.md`](./library/README.md) for the vocabulary structure.

## Contributing to the Library

The library grows through community contributions:

1. Pick the right file (universal terms → `core.yaml`, domain-specific → matching extension)
2. Add an entry with `term`, `expansion`, and `example` (see [`library/README.md`](./library/README.md) for schema)
3. **Run `python tools/validate_library.py` before opening a PR.** Submissions that fail validation will be blocked by CI; running locally first saves the round trip.
4. Open a PR using the [PR template](./.github/PULL_REQUEST_TEMPLATE.md)
5. CI runs the validator on every PR; merges are blocked on validation failure

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full workflow including non-library contributions (spec edits, validator improvements, new domains).

## Versioning

A2AL follows semantic versioning. Adding library entries is a minor bump. Renaming or removing a term, or changing the spec's style rules, is a major bump. Pre-1.0 means breaking changes are expected; /1.0 is reached when at least one production agent emits and consumes A2AL successfully and the cross-LLM compatibility (Moltbook beta) has been demonstrated.

## Status & Roadmap

| Version | Theme | Status |
|---|---|---|
| 0.3.0 | JSON envelope (deprecated) | archived in [`archive/0.3.0/`](./archive/0.3.0) |
| 0.4.0 | Hard pivot — shorthand library is A2AL | superseded by 0.4.1 |
| **0.4.1** | **Audience rule + routing header (normative)** | **current** |
| 0.4.2 | Tokenization validator tooling (Claude, GPT, Llama) | future |
| 0.4.3 | Auto-harvested PR candidates from agent traffic | future |
| 0.5.0 | Moltbook beta — cross-LLM validation | future |
| 1.0.0 | Production agents using A2AL successfully + Moltbook beta proven | gated on real-world adoption |
