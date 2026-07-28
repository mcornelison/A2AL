# A2AL Examples

Plain-text agent-to-agent messages following the A2AL/0.5.0 spec (routing header + style guide). See [`specs/A2A-Core.md`](../specs/A2A-Core.md).

## Files

| File | Pattern | Notes |
|---|---|---|
| [welcome.txt](./welcome.txt) | Handshake | The test-harness welcome that motivated the design |
| [sprint-status.txt](./sprint-status.txt) | Status report + state changes | Multi-fact compound message |
| [blocker.txt](./blocker.txt) | Blocker notification | Includes recommended next steps |
| [compound-update.txt](./compound-update.txt) | Mixed: state change + blocker + action directive | Realistic multi-topic update |
| [attestation-handshake.md](./attestation-handshake.md) | Attestation handshake (§7.10) | Bilateral commitment carried in the header — the canonical require-the-header case; uses `evidence=` |

## Example: the welcome handshake

```text
Welcome Agent2. Inbox live: 2026-05-05 22:05 CDT.
Reply when ready. -- Agent1
```

13 tokens. The verbose Markdown equivalent was 30 tokens.

## ClaudeCode integration

See [`./ClaudeCode/`](./ClaudeCode/) for the Claude Code skill (`a2al`) and slash command (`/a2al`) that produce and consume A2AL messages.

## Decode preamble

When posting A2AL where the reader may not know the format (first contact, public/mixed channels like Moltbook), prepend the canonical one-line [decode preamble](./decode-preamble.md) so the cold-start decode cost doesn't make the message skippable.

## Historical examples

For the deprecated /0.3.0 JSON envelope examples (project-coord, social-post profiles, Markdown-to-A2AL transpilation), see tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0/examples).
