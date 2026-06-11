# A2AL — Claude Code Integration

Reference skill, slash command, and sample CLAUDE.md for Claude Code. After install, an agent in Claude Code can read and write A2AL/0.5.0 messages (routing header + body shorthand).

## For AI agents — automated install (v0.4.2+)

Two entry points for an AI agent to install A2AL on a host project end-to-end without the operator running each step manually. Both load the same prompt file ([`INSTALL-PROMPT.md`](./INSTALL-PROMPT.md)); pick the one that matches your environment.

### Primary — WebFetch

Operator pastes this into a fresh Claude Code session in the target project:

```
Fetch and follow this install prompt:
https://raw.githubusercontent.com/mcornelison/A2AL/main/examples/ClaudeCode/INSTALL-PROMPT.md
```

The agent fetches the file and follows it. Pulls whatever is currently on `main`.

### Fallback — inline paste

If WebFetch isn't available, the operator copies the full contents of [`INSTALL-PROMPT.md`](./INSTALL-PROMPT.md) from the GitHub UI and pastes the whole file as their first message in the chat. The agent reads it from the message and follows it. Self-contained; no network calls beyond the eventual `git clone`.

### Idempotent re-sync

Re-running the prompt against an already-installed project re-syncs the skill, command, and library files from upstream, then runs a section-by-section diff of the existing CLAUDE.md A2AL block against the current sample. Any drift is surfaced for operator review one subsection at a time; their legitimate placeholder fill-ins (agent identity, paths) are normalized out before diffing. This is the supported upgrade path for all 0.x.x versions.

The manual step-by-step instructions below are still the canonical reference for humans who prefer to do it themselves.

## Files in this folder

| Path | Purpose |
|---|---|
| [`skills/a2al/SKILL.md`](./skills/a2al/SKILL.md) | A2AL skill — auto-invoked when the agent reads or writes a peer-agent message |
| [`commands/a2al.md`](./commands/a2al.md) | Slash command `/a2al` — explicit invocation |
| [`CLAUDE-sample.md`](./CLAUDE-sample.md) | Sample CLAUDE.md with the A2AL block in placement context |

## What you install

Three independent pieces. Each can be project-scoped or user-global; the install paths just differ.

1. **Skill + slash command** — copied into `.claude/skills/a2al/` and `.claude/commands/a2al.md`.
2. **Vocabulary library** — either left inside a cloned A2AL repo and referenced by absolute path, or copied next to your skill files. Choose one (§ Library location).
3. **CLAUDE.md A2AL block** — tells the agent its identity, the library path, the audience rule, and (if peers exist) the inbox convention. Copied from [`CLAUDE-sample.md`](./CLAUDE-sample.md).

After all three are in place, restart Claude Code. The skill auto-discovers; no enable step.

## Step 1 — Pick a library location (clone-and-point vs copy-locally)

The library is plain YAML (`library/*.yaml` in this repo, ~117 entries across 6 files). The agent needs to be able to read these files at runtime. Two options:

### Option A — Clone-and-point (simpler, easier to update)

Clone this repo once at a stable path; CLAUDE.md references its `library/` folder by absolute path. To update vocabulary later, `git pull` the clone.

```bash
git clone https://github.com/mcornelison/A2AL.git /path/to/A2AL
```

CLAUDE.md library path becomes: `/path/to/A2AL/library/` (use forward slashes on Windows too — Claude Code handles them).

**Trade-offs:** single source of truth; library updates are one `git pull`; the spec, validator, and examples are also right there. Cost: requires the clone to stay at the path you point at.

### Option B — Copy-locally (self-contained, no external dependency)

Copy `library/` into your project's `.claude/` (or `~/.claude/`) directory. CLAUDE.md references the local copy.

```bash
# Project-scoped:
mkdir -p .claude/a2al-library
cp -r /path/to/cloned/A2AL/library/*.yaml .claude/a2al-library/

# User-global:
mkdir -p ~/.claude/a2al-library
cp -r /path/to/cloned/A2AL/library/*.yaml ~/.claude/a2al-library/
```

CLAUDE.md library path becomes: `<project-root>/.claude/a2al-library/` or `~/.claude/a2al-library/`.

**Trade-offs:** self-contained; works offline; doesn't depend on the clone surviving. Cost: stale unless you re-copy when the upstream library updates. No local access to `specs/`, `tools/`, or `examples/` unless you also clone the repo.

## Step 2 — Copy skill + slash command

Pick project-scoped or user-global. Skill and command paths are fixed by Claude Code (`.claude/skills/` and `.claude/commands/`). Library path is independent.

### Project-scoped (only this project's Claude Code sessions)

```bash
mkdir -p .claude/skills .claude/commands
cp -r /path/to/cloned/A2AL/examples/ClaudeCode/skills/a2al .claude/skills/
cp /path/to/cloned/A2AL/examples/ClaudeCode/commands/a2al.md .claude/commands/
```

End state:
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

End state:
```
~/.claude/skills/a2al/SKILL.md
~/.claude/commands/a2al.md
```

The skill and command files do **not** have hardcoded library paths. They rely on CLAUDE.md to tell the agent where the library lives, so you don't need to edit them after copying.

## Step 3 — Create or update CLAUDE.md

### New project (no CLAUDE.md yet)

Copy [`CLAUDE-sample.md`](./CLAUDE-sample.md) to your project root as `CLAUDE.md`, then fill in every `[bracketed placeholder]`. Add any project-specific sections after the `## A2AL/0.5.0` block.

### Existing CLAUDE.md

Open [`CLAUDE-sample.md`](./CLAUDE-sample.md) and copy only the `## A2AL/0.5.0 — Agent-to-Agent Communication` section and all its subsections (Identity, Library location, Audience rule, Routing header, Inbox / outbox, Reference).

**Where to paste:** immediately AFTER your first H2 (the project identity / overview heading) and BEFORE any workflow, conventions, or build/test sections.

Why that placement: the audience rule and routing-header conventions need to be loaded early so the agent decides format before composing. Putting them at the bottom risks the agent producing Markdown to a peer agent because it hasn't reached the A2AL section yet.

Example structure:

```markdown
# [Project Name]

## Project Identity
You are [AgentName], ...

## A2AL/0.5.0 — Agent-to-Agent Communication        ← INSERT HERE
... (entire A2AL block from the sample) ...

## Workflow / Conventions / Build / Test
... your existing sections ...
```

### Fill in the placeholders

- `[AgentName]` and `[role]` — your agent's name and what it does (e.g., `Hawkeye` and `QA`)
- `[/absolute/path/to/A2AL]/library/` — the library path you chose in Step 1:
  - Option A: `/path/to/cloned/A2AL/library/`
  - Option B: `<project-root>/.claude/a2al-library/` or `~/.claude/a2al-library/`
- `[/absolute/path/to/your-inbox/]` — only if peers can send you messages; otherwise delete the Inbox / outbox subsection

If you chose **Option B (copy-locally)** and don't have the A2AL repo cloned, replace the spec / validator paths in the Reference subsection with the GitHub URLs:

- Spec: `https://github.com/mcornelison/A2AL/blob/main/specs/A2A-Core.md`
- Validator: not applicable (you don't have local `tools/`); use the upstream PR check instead

## Step 4 — Verify

Restart Claude Code, then prompt the agent:

```
Verify A2AL is wired up:
1. Read [library path]/core.yaml and report how many entries it has plus 3 sample terms.
2. Compose this as an A2AL message to peer "Agent2": "all tests pass, build is green, PR ready to merge". Include the routing header.
3. Confirm /a2al is registered as a slash command.
```

Expected:
- ~77 entries reported (sample terms like `done`, `merge`, `PR`)
- Two-line output: `from=<You>; to=Agent2; date=...; topic=...; audience=agent` then `tests pass; build green; PR ready -- merge?`
- `/a2al` recognized

If any step fails:
- Step 1 fail → the library path in CLAUDE.md is wrong, or files weren't copied
- Step 2 fail → the skill wasn't loaded (check `.claude/skills/a2al/SKILL.md` exists; restart Claude Code)
- Step 3 fail → the command wasn't loaded (check `.claude/commands/a2al.md` exists; restart Claude Code)

## Updating if the library moves

The skill and command files have no hardcoded library paths. Only CLAUDE.md does. If you change the library location:

1. Edit your CLAUDE.md — find the `### Library location` subsection inside the `## A2AL/0.5.0` block; update the path on the first line. Also update the path in the `### Reference` subsection if applicable.
2. No changes to `skills/a2al/SKILL.md` or `commands/a2al.md`.
3. Restart Claude Code so the new CLAUDE.md is reloaded.

## Multi-agent setup

If multiple agents talk peer-to-peer in the same workspace, each agent has its own `.claude/` directory (or shares a user-global `~/.claude/`) with its own CLAUDE.md. The path to the A2AL library is the same across agents (one copy serves all of them); only `[AgentName]/[role]` and inbox paths differ per agent.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Agent writes Markdown to a peer when it should write A2AL | A2AL block missing or placed too late in CLAUDE.md (move it to right after the first H2) |
| Agent doesn't recognize a vocabulary term | Library file for that term's domain not loaded — instruct: "Load `library/<domain>.yaml`" |
| `/a2al` not recognized | Command file not in `.claude/commands/` or Claude Code not restarted |
| Skill never triggers | Skill file not in `.claude/skills/a2al/SKILL.md` or Claude Code not restarted |
| Agent writes A2AL when a human will read | A human is in the audience; switch to Markdown — the audience rule is binary |

## Reference

- Spec: [`../specs/A2A-Core.md`](../../specs/A2A-Core.md)
- Library: [`../library/`](../../library)
- Library schema: [`../library/README.md`](../../library/README.md)
- Validator: `python tools/validate_library.py` (run from the cloned A2AL repo root)

## Historical

The /0.3.0 JSON-envelope skill and command are archived at tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0/examples/ClaudeCode) for reference.
