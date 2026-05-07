# A2AL — Claude Code Integration

Reference skill and slash command for Claude Code that let an agent read, write, and compress A2AL/0.4.0 messages.

## Files

| Path | Purpose |
|---|---|
| [`skills/a2al/SKILL.md`](./skills/a2al/SKILL.md) | A2AL skill — invoked when sending or reading agent-to-agent messages |
| [`commands/a2al.md`](./commands/a2al.md) | Slash command `/a2al` — explicit user invocation of the A2AL skill |

## Installing

**Per-project (recommended for adoption tests):**

```bash
mkdir -p .claude/skills .claude/commands
cp -r examples/ClaudeCode/skills/a2al .claude/skills/
cp examples/ClaudeCode/commands/a2al.md .claude/commands/
```

**User-global (any project):**

```bash
mkdir -p ~/.claude/skills ~/.claude/commands
cp -r examples/ClaudeCode/skills/a2al ~/.claude/skills/
cp examples/ClaudeCode/commands/a2al.md ~/.claude/commands/
```

After installing, restart Claude Code. The skill triggers automatically when an agent communicates with a peer; you can also invoke it explicitly via `/a2al`.

## What it does

- **Read:** parse a `.txt` shorthand message; expand `term=expansion` definitions; summarize in plain English
- **Write:** take user intent, compose in A2AL shorthand using the loaded vocabulary library; output plain text (no JSON wrapper)
- **Vocabulary extension:** introduce new shortenings inline via `term=expansion` syntax; suggest library promotions when terms become broadly useful

The skill references the public spec at https://github.com/mcornelison/A2AL.

## Historical

The /0.3.0 JSON-envelope skill and command are archived at [`../../archive/0.3.0/examples/ClaudeCode/`](../../archive/0.3.0/examples/ClaudeCode/) for reference.
