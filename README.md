# A2AL: a shared language for agents talking to agents

When I started running several AI agents on the same projects, I noticed they wrote to each other the way they write to me: long, polite, padded prose. Every handoff opened with a greeting and a recap before it got to the point. It was hard to scan, hard to route, and it burned tokens on words no agent needed.

A2AL is my attempt to fix that. It's two things:

1. **A one-line routing header** at the top of every agent message: who it's from, who it's to, the date, and what it's about.
2. **A shared vocabulary** of short, plain-English terms for state and intent (`done`, `blocked`, `ack`, `RISK`, `ACTION`), kept in YAML files anyone can extend.

It's plain text. There's no runtime, no parser and no JSON. If your agents can read a text file, they can use it.

**Status:** A2AL/0.5.2. It's pre-1.0, so expect changes.
**License:** Apache-2.0, see [LICENSE](./LICENSE).

## What a message looks like

```text
from=Tamsin(DEV); to=Wren(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

The first line is the header, and it's required. Everything after it is the body. For status updates, acks, handoffs and blockers, write the body in short phrases from the vocabulary, like the one above. When the message carries reasoning, exact wording or a table, write the body in plain prose under the same header; shorthand drops exactly the words that matter there. Either way, put the verdict on the first body line.

It isn't only for software. Here's part of a building handover (the full message is in [`examples/facility-go-live.txt`](./examples/facility-go-live.txt)):

```text
from=Meridian(programme-lead); to=Castell(site-lead); cc=Nadia(compliance); date=2026-10-02; topic=Bldg-C go-live readiness; audience=agent; status=blocked; priority=P1
go-live 2026-10-19 at risk. milestone 3 done; milestone 4 blocked.
RFI-18 open 9d -- fire-suppression sign-off sits on critical-path.
escalate RFI-18 to the authority having jurisdiction today.
```

And a security alert:

```text
from=Sable(SEC); to=Tamsin(DEV); date=2026-05-13; topic=CVE-2026-30856; audience=agent; urgency=urgent
crit: RCE in MCP stdio config -- patch ASAP. CVE-2026-30856.
```

There are more in [`examples/`](./examples).

## What it's actually good for

I'll be straight about this, because I got it wrong the first time.

**The header is the part that matters most.** One stable line on every message means you can grep an inbox, route messages with a script, rebuild a thread from `refs=` and `in-reply-to=`, and see who said what without reading the body. Agents keep using the header even when they write the body as plain prose:

- A five-agent team on one of my projects put the header on all 632 of its messages over four months. It was required there, but it never slipped, even as the bodies drifted back into prose.
- A six-agent fleet, which nobody asked to do this, used it on about 99% of its notes.

**The token saving is real but modest.** On real agent traffic an A2AL message costs about **0.76× the tokens of the same message in Markdown**, roughly 24% fewer, header included. That held across four different tokenizers:

| A2AL vs Markdown (lower = fewer tokens) | GPT-3.5/4 | GPT-4o | Llama 3 | Mistral |
|---|---|---|---|---|
| Real office traffic (header included) | 0.77× | 0.77× | 0.77× | 0.76× |
| My original 0.3.0 JSON format (since deleted) | 1.96× | 1.99× | 1.97× | 2.02× |

That second row is why there's no JSON. My first version wrapped messages in a JSON envelope, and when I measured it, it cost 2 to 8 times more than plain Markdown. So I threw it out.

Some caveats you should know about:

- On very short messages, like a bare `ack`, the header can make A2AL cost more than Markdown. You're paying for the structure there, not saving tokens.
- The measured corpus is small (about 15 paired messages). The direction has been consistent; the exact numbers are indicative.
- Claude's tokenizer isn't public, so it hasn't been measured directly.
- So far only Claude-based agents have written and read A2AL end to end. Getting a non-Claude agent doing it is the next milestone.

## Where it fits

A2AL is about *what a message says*, not *how it gets there*. It doesn't replace MCP, Google's A2A or anything else that moves messages around. You put an A2AL message inside whatever your agents already use: an MCP data part, an A2A `Message.Part`, a webhook body, or a text file dropped in an inbox.

| Layer | Handles | Examples |
|---|---|---|
| Transport | connections, addressing, delivery, task state | MCP, Google A2A, ACP, plain HTTP |
| **Message content** | **state, intent, who and what** | **A2AL** |

About the name: Google's protocol is **A2A** (Agent2Agent). Mine is **A2AL** (Agent-to-Agent *Language*). The names are close, but they do different jobs: A2A moves the message, A2AL is the message. [`specs/A2A-Core.md`](./specs/A2A-Core.md) §9 shows how they fit together.

## When to use A2AL and when to use Markdown

The rule is simple: if a person will read it, write Markdown.

| Situation | Format |
|---|---|
| Agent to agent, no person reading | A2AL (required) |
| Replying to a message from another agent | A2AL (required) |
| A person will read or review it | Markdown |
| Not sure who'll read it | Markdown |
| RCAs, design docs, decisions people will come back to | Markdown |

A common pattern that works well is a short A2AL note pointing at a Markdown document that holds the detail. If a person also reads an agent message, mark it `audience=mixed` and write the body for them.

One rule matters more than it looks: when an agent passes on something a person said, it's a proposal until that person confirms it. Agents mark it `relay(<person>): "..."`, and questions only a person can answer go on their own line as `ASK(<person>): ...`. That came straight from a real mix-up in the field.

## Installing it

There's nothing to compile. Installing means giving your agent the vocabulary files and, for Claude Code, a skill that knows the rules.

### Claude Code

```bash
git clone https://github.com/mcornelison/A2AL.git /path/to/A2AL
```

Then follow [examples/ClaudeCode/README.md](./examples/ClaudeCode/README.md). It walks through installing for one project or for your whole user profile, where to keep the library, the block to add to your CLAUDE.md (there's a sample in [`CLAUDE-sample.md`](./examples/ClaudeCode/CLAUDE-sample.md)), how to check it worked, and setting up several agents.

Once it's installed, you just describe the message:

> "Send Agent2 a quick update: US-713 is done, all tests pass, PR is ready to merge."

and the `a2al` skill writes the header and body for you. To read an incoming message, hand the file to the skill. You can also call it directly with `/a2al`.

### Any other platform

The vocabulary in `library/*.yaml` is plain YAML. Load `core.yaml` and whichever domain files you need into your agent's system prompt. The rules in [`specs/A2A-Core.md`](./specs/A2A-Core.md) don't depend on any particular model or tool.

### Domain vocabularies

`core.yaml` is always loaded. The domain files are optional:

| File | Covers |
|---|---|
| `project-mgmt.yaml` | project and program management in any industry |
| `programming.yaml` | code review and development |
| `infrastructure.yaml` | cloud, ops, data |
| `security.yaml` | security review, threat modeling |
| `ai-agents.yaml` | LLM, agent and RAG topics |
| `azure.yaml` | Azure, identity, compliance |

Adding an industry means adding a file. The spec doesn't change.

## Tools

| Command | What it tells you |
|---|---|
| `python tools/a2al_lookup.py check <term>` | Is this term already in the library? (no dependencies) |
| `python tools/a2al_lookup.py search <query>` | What terms already exist for this idea? |
| `python tools/a2al_preview.py scan draft.md` | How much of this draft is padding? |
| `python tools/a2al_preview.py compare draft.md msg.txt` | Was writing it in A2AL worth it? |
| `python tools/a2al_lint.py msg.a2al` | Is the header line well-formed? (checks line 1 only, never the body) |
| `python tools/validate_library.py` | Is the library well-formed? (CI runs this) |

Details are in [`tools/README.md`](./tools/README.md).

## What's in the repo

| Path | What it is |
|---|---|
| [`specs/A2A-Core.md`](./specs/A2A-Core.md) | The spec: audience rule, routing header, style rules |
| [`library/`](./library) | The vocabulary: `core.yaml` plus 6 domain files |
| [`examples/`](./examples) | Worked examples |
| [`examples/ClaudeCode/`](./examples/ClaudeCode) | Claude Code skill, slash command and install guide |
| [`tools/`](./tools) | Library validator, term lookup, savings preview, all tested |
| [`docs/why-a2al.md`](./docs/why-a2al.md) | The story of how A2AL got here, including what I got wrong |
| [`.github/`](./.github) | PR template, CI, issue templates |

If you're new, read [`specs/A2A-Core.md`](./specs/A2A-Core.md) first, then [`library/README.md`](./library/README.md).

## Contributing

The vocabulary grows from real use, and I'd love your help.

1. Pick the file: universal terms go in `core.yaml`, everything else in the matching domain file.
2. Check it isn't there already: `python tools/a2al_lookup.py check <term>`. It catches existing terms, typos and near-duplicates.
3. Add an entry with `term`, `expansion` and `example` (the schema is in [`library/README.md`](./library/README.md)).
4. Run `python tools/validate_library.py`. CI runs it too and blocks the merge if it fails, so running it first saves you a round trip.
5. Open a PR using the [template](./.github/PULL_REQUEST_TEMPLATE.md).

The most useful thing you can send me is field data: how your agents actually used A2AL, what worked and what didn't. Open an issue. Many of the open ones came from exactly that. [`CONTRIBUTING.md`](./CONTRIBUTING.md) covers spec changes, tools and new domains.

## Versions and roadmap

Adding vocabulary is a minor version bump. Renaming or removing a term, or changing the spec's rules, is a major one. Until 1.0, breaking changes can happen. I'll call it 1.0 once agents are using it in production and a non-Claude agent has written and read it end to end.

| Version | What it was | Status |
|---|---|---|
| 0.3.0 | JSON envelope | dropped; kept at tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0) |
| 0.4.0 | Switched to plain-text shorthand | replaced by 0.4.1 |
| 0.4.1 | Audience rule and required routing header | replaced by 0.5.0 |
| 0.4.2 | Install prompt (the same flow installs and re-syncs) | shipped |
| 0.5.0 | Optional header fields (`thread`, `status`, `cc`, `priority`), more vocabulary, `azure` domain | replaced by 0.5.1 |
| 0.5.1 | Industry-neutral: project management re-scoped for any industry, `a2al=` version field, `evidence=`, embedded-block rule, lookup and preview tools | replaced by 0.5.2 |
| **0.5.2** | **Field feedback: header required, body free (shorthand or prose), `audience=mixed` defined, relayed-human-words rule, `supersedes=`, header lint, body conventions** | **current** |
| 0.6.0 | A non-Claude agent writing and reading A2AL end to end; decide the remaining proposed header fields on field data | next |
| 1.0.0 | Agents using it in production | when the field data says so |

The full history is in [`VersionHistory.md`](./VersionHistory.md).
