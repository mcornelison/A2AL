# A2AL — Open Vocabulary for Agent Communication

A2AL is the **body-language layer** for agent-to-agent messages — an open, contributable vocabulary that captures *what a message says* (state, intent, routing context) in shorthand the LLM already speaks, independent of how the message is transported. It is plain text, English-derived, designed to tokenize as ~1 token per concept on modern LLM tokenizers. Agents share a common dictionary and extend it for their domain.

**Status:** A2AL/0.5.0. Pre-1.0; subject to refinement before /1.0.

**License:** Apache-2.0 — see [LICENSE](./LICENSE).

## Where A2AL fits — the body-language layer

Agent communication has two layers, and they're easy to conflate:

- **Transport / lifecycle** — *how* a message gets from agent A to agent B: the connection, the envelope, addressing, streaming, task lifecycle. This is what MCP (tool-call routing) and Google's Agent2Agent / A2A (agent-as-API over HTTP + JSON-RPC) handle.
- **Payload / body-language** — *what the message says* once it's been routed: the compact vocabulary of state and intent the receiving agent actually reads and acts on.

A2AL is the **payload layer**. It says nothing about transport. It's the body language — the shared dictionary of state, intent, and routing context — that rides *inside* whatever envelope your agents already use: an MCP `data` part, a Google A2A `Message.Part`, a webhook body, or a `.txt` dropped in an inbox.

That's why "why another protocol?" has a one-word answer: **layer.** A2AL doesn't compete with MCP or A2A any more than a shared vocabulary competes with the postal service — they compose.

| Layer | Owns | Examples |
|---|---|---|
| Transport / lifecycle | connection, envelope, addressing, streaming, task state | MCP, Google A2A, ACP, plain HTTP |
| **Payload / body-language** | **message contents — state, intent, routing context** | **A2AL** |

**On the name.** Google's protocol is **A2A** (Agent2Agent); this is **A2AL** (Agent-to-Agent *Language*). Similar acronyms, different layers — A2A *moves* the message, A2AL is *what the message says*. A2AL fits inside an A2A `Message.Part` of type `data`; see [`specs/A2A-Core.md`](./specs/A2A-Core.md) §9 for the explicit mapping.

## Why

In real multi-agent execution, much of the inter-agent token budget is mechanical waste — narrative prose, framing, justification, JSON-envelope overhead. A2AL carries only the signal: state and intent, in shorthand the LLM already speaks. On real agent traffic it costs **~0.76× the tokens of plain Markdown (≈24% fewer), routing header included** — while the JSON-envelope approach we tried in /0.3.0 (now archived) cost *2–8× more* than Markdown. But the real payoff is a clean, parseable record of what each agent meant, not the byte count.

### The efficiency is tokenizer-agnostic

A2AL was long measured on a single tokenizer (`cl100k_base` — OpenAI's GPT-3.5/4 BPE, historically a stand-in for Claude's unpublished tokenizer). Re-running the same agent-traffic corpus through four *independent* tokenizers shows the saving is a property of the format, not of one model:

| A2AL vs Markdown (lower = fewer tokens) | GPT-3.5/4 | GPT-4o | Llama 3 | Mistral |
|---|---|---|---|---|
| Real office traffic (routing header included) | 0.77× | 0.77× | 0.77× | 0.76× |
| The abandoned /0.3.0 JSON envelope | 1.96× | 1.99× | 1.97× | 2.02× |

The routing header adds a fixed cost that dominates only on very short messages, where A2AL earns its place by parseability rather than compression (see [`specs/A2A-Core.md`](./specs/A2A-Core.md) §3.4). Claude's own tokenizer is proprietary and remains unmeasured; the claim rests on the four real tokenizers above.

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

A2AL/0.5.0 is plain text — no runtime, no compiler. Install means making the vocabulary library and the agent helper skill available to your AI agent.

### For Claude Code agents

Three pieces to install: the skill files, the vocabulary library, and a CLAUDE.md block. Start by cloning the repo:

```bash
git clone https://github.com/mcornelison/A2AL.git /path/to/A2AL
```

Then follow the step-by-step install guide at **[examples/ClaudeCode/README.md](./examples/ClaudeCode/README.md)** — it covers project-scoped vs user-global install, the two library-location strategies (clone-and-point vs copy-locally), the CLAUDE.md block (sample at [`examples/ClaudeCode/CLAUDE-sample.md`](./examples/ClaudeCode/CLAUDE-sample.md), placed right after the first H2 of your CLAUDE.md), verification, and multi-agent setup.

### For other LLM platforms

The vocabulary library at `library/*.yaml` is plain YAML — load any subset into your agent's system prompt. The `specs/A2A-Core.md` style guide is normative and platform-agnostic.

### For library contributors

```bash
git clone https://github.com/mcornelison/A2AL.git
cd A2AL
pip install pyyaml
python tools/validate_library.py
```

### Tools

| Command | What it answers |
|---|---|
| `python tools/a2al_lookup.py check <term>` | Is this shortening already in the library? (stdlib only) |
| `python tools/a2al_lookup.py search <query>` | What vocabulary already exists for this idea? |
| `python tools/a2al_preview.py scan draft.md` | How much of this draft is padding A2AL would drop? |
| `python tools/a2al_preview.py compare draft.md msg.txt` | Was writing it in A2AL actually worth it? |
| `python tools/validate_library.py` | Is the library well-formed? (CI gate) |

See [`tools/README.md`](./tools/README.md) for full usage.

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
| [`specs/A2A-Core.md`](./specs/A2A-Core.md) | Normative A2AL/0.5.0 spec (audience rule, routing header, style guide) |
| [`library/`](./library) | Vocabulary library — `core.yaml` + 6 domain extensions |
| [`examples/`](./examples) | Worked shorthand examples |
| [`examples/ClaudeCode/`](./examples/ClaudeCode) | Claude Code install guide — skill, slash command, sample CLAUDE.md |
| [`tools/`](./tools) | Library validator, vocabulary lookup, savings preview — all with tests |
| [`.github/`](./.github) | PR template, CI workflow, issue templates |

Start with [`specs/A2A-Core.md`](./specs/A2A-Core.md) for the style guide and [`library/README.md`](./library/README.md) for the vocabulary structure.

## Contributing to the Library

The library grows through community contributions:

1. Pick the right file (universal terms → `core.yaml`, domain-specific → matching extension)
2. **Check it isn't already there:** `python tools/a2al_lookup.py check <term>` — it catches terms that are already canonical, typos of real terms, and terms whose meaning an existing entry already covers
3. Add an entry with `term`, `expansion`, and `example` (see [`library/README.md`](./library/README.md) for schema)
4. **Run `python tools/validate_library.py` before opening a PR.** Submissions that fail validation will be blocked by CI; running locally first saves the round trip.
5. Open a PR using the [PR template](./.github/PULL_REQUEST_TEMPLATE.md)
6. CI runs the validator on every PR; merges are blocked on validation failure

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full workflow including non-library contributions (spec edits, validator improvements, new domains).

## Versioning

A2AL follows semantic versioning. Adding library entries is a minor bump. Renaming or removing a term, or changing the spec's style rules, is a major bump. Pre-1.0 means breaking changes are expected; /1.0 is reached when at least one production agent emits and consumes A2AL successfully and cross-LLM compatibility has been demonstrated. Tokenizer-level cross-LLM parity is already shown (see above); the remaining gap is a non-Claude agent emitting and consuming A2AL end-to-end.

## Status & Roadmap

| Version | Theme | Status |
|---|---|---|
| 0.3.0 | JSON envelope (deprecated) | archived at tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0) |
| 0.4.0 | Hard pivot — shorthand library is A2AL | superseded by 0.4.1 |
| 0.4.1 | Audience rule + routing header (normative) | superseded by 0.5.0 |
| 0.4.2 | Install prompt (idempotent — same flow handles installs and re-syncs) | shipped |
| **0.5.0** | **Optional header fields (`thread`, `status`, `cc`, `priority`) + vocabulary expansion (core +10, new `azure` domain)** | **current** |
| 0.5.1 | Positioning (body-language layer) + require-the-header demo (attestation handshake, `evidence=`) + cross-LLM proof | in progress |
| 0.5.2 | Auto-harvested PR candidates from agent traffic | future |
| 0.6.0 | Cross-LLM validation — tokenizer parity shown; next is a non-Claude agent emitting/consuming A2AL | future |
| 1.0.0 | Production agents using A2AL successfully + Moltbook beta proven | gated on real-world adoption |
