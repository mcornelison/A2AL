---
name: a2al
description: Use when an AI agent needs to send a short message to a peer agent, write a status update, ack a peer, compress a verbose report into shorthand, or read an A2AL message from another agent. A2AL is plain-text shorthand designed to tokenize as 1 token per concept on modern LLM tokenizers. Triggers on phrases like "send a quick update to agent2", "ack that", "compress this for agent X", "what does this A2AL message say", "tell agent2 X". NOT for messages to humans — write Markdown for that.
---

# A2AL Skill

A2AL/0.4.0 is a plain-text shorthand for agent-to-agent communication, paired with an open vocabulary library. This skill teaches the style guide and tells you how to load the right vocabulary for your domain.

Reference: https://github.com/mcornelison/A2AL — `specs/A2A-Core.md`, `library/`, `examples/`.

## When to use

- Sending a short message between agents (status update, ack, action request, blocker notification)
- Reading an A2AL message from a peer
- Compressing verbose Markdown into shorthand for agent consumption

## When NOT to use

- The recipient is a human → write Markdown
- The content is genuinely unstructured prose with no shorthand savings → plain text is fine
- You need a structured envelope (timestamps, signing, routing metadata) → that's transport, out of scope for A2AL

## Loading the vocabulary library

A2AL's vocabulary lives in `library/*.yaml` files. Always load `library/core.yaml` (~77 universal terms). Optionally load domain extensions for the conversation:

| Conversation theme | Load |
|---|---|
| General agent coordination | `library/core.yaml` only |
| Code review / dev process | + `library/programming.yaml` |
| Cloud / infrastructure / data pipelines | + `library/infrastructure.yaml` |
| Sprint, project, or program management | + `library/project-mgmt.yaml` |
| Security review / threat modeling | + `library/security.yaml` |
| LLM / agent / RAG topics | + `library/ai-agents.yaml` |

Loading is just reading the YAML file and using its terms. No special parser needed.

## Style rules

### Drop
- Articles (`the`, `a`, `an`)
- Helping/linking verbs (`is`, `are`, `was`) when state is unambiguous
- Subjective framing (`I think`, `it seems`)
- Politeness (`please`, `could you`)
- Filler (`in order to` → `to`)
- Repeated subjects across fragments — use `;`

### Use
- Sentence fragments
- Imperative mood for actions
- Past tense / status adjectives for state
- Standard tech jargon from the library
- IDs as bare tokens: `US-713`, `commit-98b483d`

### Punctuation
- `;` between related facts (same topic)
- `.` between unrelated facts
- `:` after subject to expand
- `/` for ratios
- `?` for questions
- `--` for inline rationale

### Avoid
- Creative abbreviations (`cmplt`, `prgm`) — usually 2–3 tokens
- Rare Unicode (✓ ⟳ ✗) — usually multi-token in Claude's vocab
- Single-letter codes (`c`, `b`, `r`) — ambiguous

## Patterns

| Pattern | Form | Example |
|---|---|---|
| State change | `<id> <state>` | `US-713 done` |
| Multi-fact state | `<id> <state>; <fact>; <fact>` | `US-713 done; AC met; CI green` |
| Status report | `<metric> <value>; ...` | `tests 21/21; preflight 878/878; build green` |
| Action | `<verb> <target>` or `<actor>: <verb> <target>` | `merge ralph/auth-fix` |
| Blocker | `<id> blocked: <reason>` | `US-718 blocked: no household source in Silver` |
| Question | `<verb>?` or `<id> <verb>?` | `merge?`, `US-713 sign-off?` |
| Decision | `<decision>: <id> -- <rationale>` | `approved: US-713 PRD -- 1 AC added` |
| Ack | `ack <id>` | `ack US-713 closeout` |

## Mode 1 — Read

When given a shorthand message:
1. Parse `term=expansion` definitions on first occurrence; remember them within the thread
2. Expand the message internally using your loaded library
3. Summarize key facts in 1–2 plain-English sentences for the user

## Mode 2 — Write

When the user asks to compose a message:
1. Identify the structural shape (state change / status / action / blocker / question / decision / ack)
2. Pick the matching pattern from the table above
3. Use canonical glossary terms from the loaded library where possible
4. Apply style rules — drop fillers, use fragments, semicolons between related facts
5. Output as plain text (no JSON wrapper, no envelope)

## Mode 3 — Vocabulary extension

If the user wants to introduce a new shortening:
1. Verify the term will be used 3+ times in the thread (else just write it out in full)
2. On first use, write `<term>=<expansion>` (no spaces in the expansion, no `--`)
3. After first use, use the bare term

Example: `DR=design-review. DR sched Tuesday; PR ready post-DR.`

If the term is broadly useful, suggest adding it to the library: open a PR adding an entry to `library/<domain>.yaml` and run `python tools/validate_library.py` to verify before submitting.

## Worked example — write

User: "Tell Agent1 the sprint hotfix is done — 713 needed no code change, 714 implemented warnOnly DQ flag, all tests pass, ready to merge."

You produce:

```
US-713 done; no code change -- already in main from US-671.
US-714 done; warnOnly DQ flag; 21/21 DQ tests; preflight 878/878.
merge ralph/pipeline-hotfix-2026-04-17?
```

You write that to the file/inbox the user specified, then summarize: "Wrote sprint hotfix update to Agent1. Three lines, ~30 tokens vs ~95 in verbose English. Asks Agent1 to merge."

## Worked example — read

User: "What does this say?" (provides `US-713 done; AC met; CI green; PR ready -- merge?`)

You reply: "US-713 is complete with acceptance criteria met and CI green. Sender's PR is ready and they're asking permission to merge."

## Reference

- Spec: `specs/A2A-Core.md`
- Library: `library/*.yaml`
- Examples: `examples/*.txt`
- Validator (for library contributions): `tools/validate_library.py`
