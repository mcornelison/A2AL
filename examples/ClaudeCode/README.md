# A2AL for Claude Code

This folder has a skill, a slash command and a sample CLAUDE.md for Claude Code. Once they're installed, an agent in Claude Code can read and write A2AL/0.5.1 messages (routing header plus body shorthand).

> Already installed on an older version? See [`UPGRADING.md`](./UPGRADING.md) for how to upgrade from one version to the next: re-syncing the library, the three library modes, and the verify step that can pass when it shouldn't (the false-GREEN trap).

## Letting an agent install it (v0.4.2+)

You can have an AI agent install A2AL on a project from start to finish, so you don't have to run each step yourself. There are two ways to start it. Both load the same prompt file, [`INSTALL-PROMPT.md`](./INSTALL-PROMPT.md), so pick whichever fits your setup.

### First choice: WebFetch

Paste this into a fresh Claude Code session in the target project:

```
Fetch and follow this install prompt:
https://raw.githubusercontent.com/mcornelison/A2AL/main/examples/ClaudeCode/INSTALL-PROMPT.md
```

The agent fetches the file and follows it. You get whatever is on `main` right now.

### Fallback: paste it in

If WebFetch isn't available, copy the full contents of [`INSTALL-PROMPT.md`](./INSTALL-PROMPT.md) from the GitHub UI and paste the whole file as your first message in the chat. The agent reads it from the message and follows it. It's self-contained, and nothing goes over the network until the `git clone`.

### Re-running it is safe

If you run the prompt again on a project that already has A2AL, it re-syncs the skill, command and library files from upstream. Then it compares the A2AL block in your CLAUDE.md with the current sample, section by section, and shows you any drift one subsection at a time for you to review. Your own placeholder values (agent identity, paths) are normalized out before the diff, so they don't show up as drift. This is how I support upgrades across all 0.x.x versions.

The manual steps below are still the reference if you'd rather do it yourself.

## Files in this folder

| Path | Purpose |
|---|---|
| [`skills/a2al/SKILL.md`](./skills/a2al/SKILL.md) | The A2AL skill. Claude Code invokes it automatically when the agent reads or writes a message to or from a peer agent |
| [`commands/a2al.md`](./commands/a2al.md) | The `/a2al` slash command, for calling it directly |
| [`CLAUDE-sample.md`](./CLAUDE-sample.md) | A sample CLAUDE.md showing where the A2AL block goes |

## What you install

There are three separate pieces. Each one can be installed for one project or for your whole user profile; only the paths differ.

1. The skill and slash command, copied into `.claude/skills/a2al/` and `.claude/commands/a2al.md`.
2. The vocabulary library. Either leave it inside a cloned A2AL repo and point at it by absolute path, or copy it next to your skill files. Pick one (see Step 1).
3. The A2AL block in CLAUDE.md. It tells the agent its identity, the library path, the audience rule and, if it has peers, the inbox convention. You copy it from [`CLAUDE-sample.md`](./CLAUDE-sample.md).

Once all three are in place, restart Claude Code. The skill is picked up automatically; there's nothing to enable.

## Step 1: Pick a library location (clone-and-point or copy-locally)

The library is plain YAML (`library/*.yaml` in this repo, 164 entries across 7 files). The agent has to be able to read these files while it runs. You have two options.

### Option A: Clone-and-point (simpler, easier to update)

Clone this repo once at a path that won't move, and have CLAUDE.md point at its `library/` folder by absolute path. To pick up new vocabulary later, `git pull` the clone.

```bash
git clone https://github.com/mcornelison/A2AL.git /path/to/A2AL
```

The library path in CLAUDE.md is then `/path/to/A2AL/library/`. Use forward slashes on Windows too; Claude Code handles them.

Trade-offs: there's one source of truth, updating the library is one `git pull`, and the spec, validator and examples are right there too. The cost is that the clone has to stay at the path you pointed at.

### Option B: Copy-locally (self-contained, no external dependency)

Copy `library/` into your project's `.claude/` (or `~/.claude/`) directory and point CLAUDE.md at the copy.

```bash
# Project-scoped:
mkdir -p .claude/a2al-library
cp -r /path/to/cloned/A2AL/library/*.yaml .claude/a2al-library/

# User-global:
mkdir -p ~/.claude/a2al-library
cp -r /path/to/cloned/A2AL/library/*.yaml ~/.claude/a2al-library/
```

The library path in CLAUDE.md is then `<project-root>/.claude/a2al-library/` or `~/.claude/a2al-library/`.

Trade-offs: it's self-contained, works offline and doesn't depend on a clone staying put. The cost is that it goes stale unless you copy it again when the upstream library changes. You also won't have `specs/`, `tools/` or `examples/` locally unless you clone the repo as well.

## Step 2: Copy the skill and slash command

Choose project-scoped or user-global. Claude Code fixes where skills and commands live (`.claude/skills/` and `.claude/commands/`). The library path is separate from that.

### Project-scoped (only this project's Claude Code sessions)

```bash
mkdir -p .claude/skills .claude/commands
cp -r /path/to/cloned/A2AL/examples/ClaudeCode/skills/a2al .claude/skills/
cp /path/to/cloned/A2AL/examples/ClaudeCode/commands/a2al.md .claude/commands/
```

You should end up with:
```
<project-root>/.claude/skills/a2al/SKILL.md
<project-root>/.claude/commands/a2al.md
```

### User-global (every Claude Code project on this machine)

```bash
mkdir -p ~/.claude/skills ~/.claude/commands
cp -r /path/to/cloned/A2AL/examples/ClaudeCode/skills/a2al ~/.claude/skills/
cp /path/to/cloned/A2AL/examples/ClaudeCode/commands/a2al.md ~/.claude/commands/
```

You should end up with:
```
~/.claude/skills/a2al/SKILL.md
~/.claude/commands/a2al.md
```

The skill and command files don't have library paths hardcoded in them. They rely on CLAUDE.md to tell the agent where the library is, so you don't need to edit them after copying.

## Step 3: Create or update CLAUDE.md

### New project (no CLAUDE.md yet)

Copy [`CLAUDE-sample.md`](./CLAUDE-sample.md) to your project root as `CLAUDE.md`, then fill in every `[bracketed placeholder]`. Put any project-specific sections after the `## A2AL/0.5.1` block.

### Existing CLAUDE.md

Open [`CLAUDE-sample.md`](./CLAUDE-sample.md) and copy just the `## A2AL/0.5.1 — Agent-to-Agent Communication` section with all its subsections (Identity, Library location, Audience rule, Routing header, Inbox / outbox, Reference).

Paste it right after your first H2 (the project identity or overview heading) and before any workflow, conventions or build/test sections.

The placement matters because the agent needs the audience rule and the routing-header conventions early, so it picks the format before it starts writing. If the block is at the bottom, the agent may write Markdown to a peer agent because it hasn't got to the A2AL section yet.

Example structure:

```markdown
# [Project Name]

## Project Identity
You are [AgentName], ...

## A2AL/0.5.1 — Agent-to-Agent Communication        ← INSERT HERE
... (entire A2AL block from the sample) ...

## Workflow / Conventions / Build / Test
... your existing sections ...
```

### Fill in the placeholders

- `[AgentName]` and `[role]`: your agent's name and what it does (for example `Hawkeye` and `QA`)
- `[/absolute/path/to/A2AL]/library/`: the library path you chose in Step 1
  - Option A: `/path/to/cloned/A2AL/library/`
  - Option B: `<project-root>/.claude/a2al-library/` or `~/.claude/a2al-library/`
- `[/absolute/path/to/your-inbox/]`: only if peers can send you messages. Otherwise delete the Inbox / outbox subsection.

If you chose Option B (copy-locally) and don't have the A2AL repo cloned, replace the spec and validator paths in the Reference subsection with the GitHub URLs:

- Spec: `https://github.com/mcornelison/A2AL/blob/main/specs/A2A-Core.md`
- Validator: not applicable, since you don't have `tools/` locally. Rely on the upstream PR check instead.

## Step 4: Check it worked

Restart Claude Code, then give the agent this prompt:

```
Verify A2AL is wired up:
1. Read [library path]/core.yaml and report how many entries it has plus 3 sample terms.
2. Compose this as an A2AL message to peer "Agent2": "all tests pass, build is green, PR ready to merge". Include the routing header.
3. Confirm /a2al is registered as a slash command.
```

You should see:
- About 87 entries reported, with sample terms like `done`, `merge` and `PR`
- Two lines of output: `from=<You>; to=Agent2; date=...; topic=...; audience=agent` and then `tests pass; build green; PR ready -- merge?`
- `/a2al` recognized

If a step fails:
- Step 1 fails: the library path in CLAUDE.md is wrong, or the files weren't copied
- Step 2 fails: the skill didn't load (check that `.claude/skills/a2al/SKILL.md` exists, then restart Claude Code)
- Step 3 fails: the command didn't load (check that `.claude/commands/a2al.md` exists, then restart Claude Code)

## If the library moves

Only CLAUDE.md has the library path. The skill and command files don't. If you move the library:

1. Edit your CLAUDE.md. Find the `### Library location` subsection inside the `## A2AL/0.5.1` block and update the path on its first line. Update the path in the `### Reference` subsection too, if it's there.
2. Leave `skills/a2al/SKILL.md` and `commands/a2al.md` alone.
3. Restart Claude Code so it reloads CLAUDE.md.

## Several agents

If several agents talk to each other in the same workspace, each one has its own `.claude/` directory (or they share a user-global `~/.claude/`) with its own CLAUDE.md. The library path is the same for all of them, since one copy serves everyone. Only `[AgentName]/[role]` and the inbox paths change from agent to agent.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Agent writes Markdown to a peer when it should write A2AL | The A2AL block is missing or too far down in CLAUDE.md (move it to right after the first H2) |
| Agent doesn't recognize a vocabulary term | The library file for that term's domain isn't loaded. Tell it: "Load `library/<domain>.yaml`" |
| `/a2al` not recognized | The command file isn't in `.claude/commands/`, or Claude Code wasn't restarted |
| Skill never triggers | The skill file isn't at `.claude/skills/a2al/SKILL.md`, or Claude Code wasn't restarted |
| Agent writes A2AL when a person will read it | A person is in the audience, so switch to Markdown. The audience rule has no middle ground |

## Reference

- Spec: [`../specs/A2A-Core.md`](../../specs/A2A-Core.md)
- Library: [`../library/`](../../library)
- Library schema: [`../library/README.md`](../../library/README.md)
- Validator: `python tools/validate_library.py` (run it from the root of your A2AL clone)

## Older versions

The /0.3.0 JSON-envelope skill and command are kept at tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0/examples/ClaudeCode) if you want to look at them.
