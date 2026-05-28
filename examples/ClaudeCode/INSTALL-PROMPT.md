# A2AL Install Prompt (v0.4.2)

You are an AI agent that has been asked to install or re-sync A2AL on a host project. Follow this prompt end-to-end. It works for both fresh installs and re-syncs — re-running it is safe and is the supported upgrade path inside 0.x.x.

Reference design (read if confused): https://github.com/mcornelison/A2AL/blob/main/docs/superpowers/specs/2026-05-21-a2al-0.4.2-install-prompt-design.md

## How this prompt is structured

Two phases. Run them in order:

1. **Phase 1 — Decisions.** Detect existing-install state, then (if fresh) ask the operator five questions one at a time. Conversational.
2. **Phase 2 — Execution.** Clone the A2AL repo, copy files, write or diff the CLAUDE.md A2AL block, run a 3-prompt verification smoke test. Deterministic.

On re-sync, Phase 1 collapses to a single confirmation question, and Phase 2 step e4 becomes a section-by-section diff loop instead of a fresh write.

## Phase 1 — Decisions

Run q1 first (detection). It determines whether you ask q2–q5 (fresh) or skip them (re-sync).

### q1 — Detect existing install state (computed, not asked)

Run these probes in order:

1. Read `.claude/skills/a2al/SKILL.md` — if it exists, set `scope = project`.
2. Otherwise read `~/.claude/skills/a2al/SKILL.md` — if it exists, set `scope = user-global`.
3. Grep for `^## A2AL/0\.4` in the target CLAUDE.md — if it matches, set `claude_md_has_block = true`. (Target CLAUDE.md is `<project-root>/CLAUDE.md` for project scope, `~/.claude/CLAUDE.md` for user-global scope. If scope is unknown at this point, check the project location first.)

**Decision:**
- If `scope != none` OR `claude_md_has_block = true` → **re-sync mode**. Skip to "Re-sync condensation" below.
- Otherwise → **fresh mode**. Continue with q2.

Announce your decision in one line before continuing, e.g.:
> Detected `.claude/skills/a2al/` — running re-sync.

or

> No existing A2AL install detected — running fresh install.

### q2 — Identity (fresh only)

Ask the operator:
> What's this agent's name and role? Examples: `Hawkeye/QA`, `Byte/DEV`, `Ledger/PM`. Roles are free-form — pick whatever describes the agent's job on this project.

Parse their answer into `agent_name` and `agent_role`. Accept both `Name/Role` and `Name(Role)` forms.

### q3 — Peers (fresh only)

Ask the operator:
> Will this agent receive A2AL messages from peer agents? If yes, give me the absolute path to its inbox directory (e.g., `/Users/x/code/myproj/offices/qa/inbox`). If no, I'll omit the Inbox/outbox subsection from CLAUDE.md.

If they answer "yes" with a path, store `inbox_path`. Otherwise store `inbox_path = none`.

### q4 — Scope (fresh only)

Ask the operator:
> Project-scoped (`.claude/` in this project) or user-global (`~/.claude/`)?

Store `scope ∈ {project, user-global}`.

### q5 — Library location (fresh only)

Ask the operator:
> Should the library live (A) inside a cloned A2AL repo I keep at a stable path, or (B) copied into `.claude/a2al-library/` for self-containment? Most installs pick A.

Store `library_mode ∈ {clone-and-point, copy-locally}`.

### Re-sync condensation (re-sync mode only)

If q1 put you in re-sync mode, do NOT run q2–q5. Instead:

1. Read the existing CLAUDE.md target file.
2. Extract values from its A2AL block:
   - `agent_name`, `agent_role` from the Identity subsection (the `<Name>/<Role>` token).
   - `library_path` from the Library location subsection (the first absolute path on the line, ending in `/library/`).
   - `inbox_path` from the Inbox/outbox subsection's "Your inbox:" bullet (or `none` if subsection absent).
   - `library_mode`:
     - If `library_path` is under a directory whose `.git/config` remote URL matches `mcornelison/A2AL` → `clone-and-point`.
     - If `library_path` ends in `.claude/a2al-library/` (or `~/.claude/a2al-library/`) → `copy-locally`.
     - Otherwise → ask the operator which mode applies.
3. Show the operator a summary and ask one confirmation question:
   > Detected A2AL installed at `<scope>`, identity `<Name>/<Role>` from CLAUDE.md, library at `<path>` (`<library_mode>`). Proceed with re-sync? (yes / change something)
4. If "change something", offer them q2–q5 selectively for whichever items they want to update. If "yes", proceed directly to Phase 2.

## Phase 2 — Execution

Five steps. Run e1–e5 in order. In re-sync mode, e4 is replaced by the diff loop (see "Re-sync diff loop" section below).

### e1 — Acquire the A2AL repo

**Fresh mode:**

1. If `~/A2AL` does not exist on disk, run:
   ```
   git clone https://github.com/mcornelison/A2AL.git ~/A2AL
   ```
   Use `$HOME\A2AL` on Windows; either path notation is fine.
2. If `~/A2AL` exists, check whether it is the A2AL clone:
   ```
   git -C ~/A2AL remote get-url origin
   ```
   Expected: a URL ending in `mcornelison/A2AL` (or `mcornelison/A2AL.git`).
   - If it matches: run `git -C ~/A2AL pull --ff-only`. If the pull fails, warn but continue — the existing checkout is still usable.
   - If it does not match (or the directory isn't a git repo at all): STOP. Ask the operator for an alternate clone path. Do not overwrite an unknown directory. After they answer, retry from step 1 with the new path. Store the chosen path as `clone_path`.

By the end of e1, you have `clone_path` (defaulting to `~/A2AL`) pointing at an A2AL working tree on `main` or close to it.

**Re-sync mode:**

- Read `library_path` from Phase 1.
- If `library_mode == clone-and-point`: the clone is at `dirname(dirname(library_path))`. Run `git -C <clone-path> pull --ff-only`. Warn but continue on failure.
- If `library_mode == copy-locally`: there is no clone tied to the install. Use a scratch clone at `~/A2AL` (or clone there if missing) so e3 has fresh upstream library files to copy from.

### e2 — Copy skill + command into chosen scope

Compute the destination scope dir:
- `scope == project` → `<project-root>/.claude/`
- `scope == user-global` → `~/.claude/`

Create the dirs if missing:
```
mkdir -p <scope-dir>/skills/a2al
mkdir -p <scope-dir>/commands
```

Copy these two files unconditionally (overwrite if they exist):
```
<clone_path>/examples/ClaudeCode/skills/a2al/SKILL.md  ->  <scope-dir>/skills/a2al/SKILL.md
<clone_path>/examples/ClaudeCode/commands/a2al.md      ->  <scope-dir>/commands/a2al.md
```

If you suspect the operator hand-edited either file (you can't actually tell from here; this is informational), add a single line to the final summary: "If you edited `skills/a2al/SKILL.md` or `commands/a2al.md` directly, those edits were overwritten."

### e3 — Place library files

- If `library_mode == clone-and-point`: do nothing. The library is at `<clone_path>/library/`. Record `library_path = <clone_path>/library/` for CLAUDE.md.

- If `library_mode == copy-locally`: copy every `.yaml` file from `<clone_path>/library/` into `<scope-dir>/a2al-library/`, overwriting unconditionally:
  ```
  mkdir -p <scope-dir>/a2al-library
  cp <clone_path>/library/*.yaml <scope-dir>/a2al-library/
  ```
  Record `library_path = <scope-dir>/a2al-library/` for CLAUDE.md.

### e4 — Write or update CLAUDE.md A2AL block

The target CLAUDE.md depends on scope:
- `scope == project` → `<project-root>/CLAUDE.md`
- `scope == user-global` → `~/.claude/CLAUDE.md`

In **re-sync mode**, jump to the "Re-sync diff loop" section below.

In **fresh mode**, handle one of these two cases:

**Case A — Target CLAUDE.md does not exist.**

Copy the full sample to the target:
```
cp <clone_path>/examples/ClaudeCode/CLAUDE-sample.md  <target-claude-md-path>
```

Then fill in placeholders using the answers from q2/q3/q5. The placeholders to substitute are listed in the table below.

**Case B — Target CLAUDE.md exists but has no A2AL block** (i.e., q1 found no `^## A2AL/0\.4` match but a skill or command somewhere on disk was missing too — this is the rare partial state; fresh-mode handles it as a clean insert).

Extract the A2AL block from `<clone_path>/examples/ClaudeCode/CLAUDE-sample.md`:
1. Find the first H2 line matching `^## A2AL/0\.4\.\d+ — `.
2. Capture from that line up to (but not including) the next H2 line, or end of file if none.

Find the **first H2** in the target CLAUDE.md (the project-identity heading). Insert the extracted A2AL block immediately after that H2's body but before the next H2. If the target CLAUDE.md has no H2 at all, insert the block at the very top of the file and add a note to the final summary: "no existing H2 found in CLAUDE.md — A2AL block placed at the top; you may want to add a project-identity H2 above it."

**Placeholder substitution table (both cases):**

| Sample placeholder | Substitute with |
|---|---|
| `[AgentName]` | `agent_name` from q2 |
| `[role]` | `agent_role` from q2 |
| `[/absolute/path/to/A2AL]` (in Library location and Reference subsections) | `dirname(library_path)` if `clone-and-point`, else the literal path inside the scope dir (e.g., `~/.claude/`) — see note below |
| `[/absolute/path/to/your-inbox/]` | `inbox_path` from q3 |
| `[Project Name]` (only relevant in Case A) | the host project's name — ask the operator if it's not obvious from the directory name |

Note on library path: the sample has placeholders both for the parent A2AL repo (used in Reference subsection) and for the library directly. In `copy-locally` mode, there is no A2AL clone to point at for the Reference subsection — replace those lines with the GitHub URL fallback documented in `examples/ClaudeCode/README.md` Step 3 ("If you chose Option B and don't have the A2AL repo cloned, replace the spec / validator paths in the Reference subsection with the GitHub URLs").

If `inbox_path == none`, delete the entire `### Inbox / outbox` subsection from the inserted block instead of substituting.

### e5 — Verify

Run the three smoke-test probes in the same chat session (no restart needed for the agent driving the install; the operator can restart their Claude Code session separately afterwards to pick up the new skill and command for normal use):

1. Read `<library_path>/core.yaml` (or `<clone_path>/library/core.yaml`). Report the entry count (expect ~77) and three sample term names from the file (`done`, `merge`, `PR` are likely to appear; whatever is actually there is fine).
2. Compose a one-message A2AL test message from `<agent_name>(<agent_role>)` to `Agent2` saying "tests pass; build green; PR ready -- merge?". Show the two-line output (header + body) to the operator.
3. Confirm `/a2al` is registered (you can describe what the slash command does as a way of showing it's loaded; the operator can confirm by typing `/` in their own session after restarting).

If any probe fails, print the matching troubleshooting row from `examples/ClaudeCode/README.md`:
- Probe 1 fail → "the library path in CLAUDE.md is wrong, or files weren't copied"
- Probe 2 fail → "the skill wasn't loaded (check `.claude/skills/a2al/SKILL.md` exists; restart Claude Code)"
- Probe 3 fail → "the command wasn't loaded (check `.claude/commands/a2al.md` exists; restart Claude Code)"

## Re-sync diff loop (Phase 2 step e4 alternate)

This replaces e4's "Case A / Case B" write logic when you are in re-sync mode. The goal: refresh the operator's CLAUDE.md A2AL block to match the current sample, but surface real spec changes for operator review while ignoring their own legitimate placeholder fill-ins.

### Step 1 — Extract both sides at section granularity

The A2AL block has six H3 subsections (per `CLAUDE-sample.md`):

```
### Identity for A2AL routing headers
### Library location
### When to use A2AL (audience rule)
### Routing header
### Inbox / outbox (only if you have peer agents)
### Reference
```

Parse both the existing CLAUDE.md A2AL block and `<clone_path>/examples/ClaudeCode/CLAUDE-sample.md` into a `{subsection_heading -> body_text}` map. Treat subsections by their heading text verbatim; do not fuzzy-match.

### Step 2 — Normalize placeholders before diffing

Without normalization, every install would show every subsection as drifted (operator put real values where the sample has `[bracketed]` placeholders). Do a one-time extraction pass over the operator's existing block to learn their substitutions:

| Sample placeholder | Read from operator's CLAUDE.md |
|---|---|
| `[AgentName]`, `[role]` | Identity subsection — the `<Name>/<Role>` token |
| `[/absolute/path/to/A2AL]` | Library location subsection — the absolute path before `/library/` |
| `[/absolute/path/to/your-inbox/]` | Inbox/outbox subsection — the "Your inbox:" path |
| `[Project Name]` | The CLAUDE.md file's first H1 (if present) |

Build a `placeholder_map = { '[AgentName]': 'Byte', '[role]': 'DEV', ... }`. In the operator's block, replace each real value back with its placeholder. Both sides now use bracketed tokens.

### Step 3 — Diff section-by-section

For each subsection in the sample (and also each subsection present in operator's block but missing from sample):

- **Equal** (after collapsing trailing whitespace on both sides): silent. No operator prompt. Mark this subsection "unchanged" for the summary.

- **In sample, not in operator's block:** prompt:
  > A new subsection `### <heading>` has been added in the current sample. Paste it into your CLAUDE.md? (yes / no — keep yours unchanged)
  
  If yes, append the new subsection to the operator's A2AL block (with placeholder substitution from `placeholder_map` re-applied). Mark "new subsection added" for the summary.

- **In operator's block, not in sample:** prompt:
  > The subsection `### <heading>` exists in your CLAUDE.md but has been removed from the current sample. Keep it or drop it? (keep / drop)
  
  Mark "kept removed-subsection" or "dropped" for the summary.

- **Both present, normalized bodies differ:** show a unified diff (or line-by-line if the diff is short) and prompt:
  ```
  === Subsection: <heading> ===
  Differences (your CLAUDE.md vs current sample):

    - <removed line>
    + <added line>

  How do you want to handle this?
    1. Take the new version (replace yours with the sample text)
    2. Keep yours (do nothing; you've customized this on purpose)
    3. Merge manually (show me both and I'll dictate the final text)
  ```
  
  After operator chooses:
  - Option 1: write the sample's body for this subsection, with `placeholder_map` re-substituted, back into CLAUDE.md.
  - Option 2: leave operator's body unchanged.
  - Option 3: print the operator's full subsection body and the sample's full subsection body; ask the operator to dictate the final text; write what they dictate, with `placeholder_map` re-substituted.

  Mark this subsection's resolution for the summary ("TOOK NEW", "KEPT YOURS", "MERGED MANUALLY").

### Step 4 — Update the H2 version heading

After the per-subsection loop, look at the operator's H2 heading line (`## A2AL/0.4.X — Agent-to-Agent Communication`). Compare its version-suffix against the sample's. If the sample is higher, rewrite the operator's heading line to match the sample's. (For 0.4.2, where the sample's H2 may still say 0.4.1, this is a no-op.)

### Step 5 — Summary

Print:

```
A2AL re-sync complete.
  Skill, command, library: refreshed.
  CLAUDE.md A2AL block: <old-version> -> <new-version>.
    Identity: <unchanged | TOOK NEW | KEPT YOURS | MERGED MANUALLY>
    Library location: <...>
    Audience rule: <...>
    Routing header: <...>
    Inbox/outbox: <...>
    Reference: <...>
```

### What this loop deliberately does NOT do

- No automatic merging. Every substantive difference is operator-confirmed.
- No structural edits outside the A2AL block. The rest of CLAUDE.md is untouched.
- No fuzzy matching of H3 headings. A renamed subsection is treated as removed + new (fail-safe).
- No saved progress mid-loop. If the operator interrupts during "merge manually" and re-runs the install later, the diff loop re-fires for whatever subsections are still drifted — idempotency comes from re-reading the file, not from saved state.

## Verification

Verification is Phase 2 step e5 above. After e5 completes successfully, print a summary like:

```
A2AL install complete.
  Scope:           <scope>
  Identity:        <Name>/<Role>
  Library:         <library_path> (<library_mode>)
  Skill+command:   <scope-dir>/.claude/
  CLAUDE.md:       <target-claude-md-path> (block added/updated)

Restart Claude Code to load the new skill and command for normal use.
```

## Error handling

Six failure modes have defined behavior. Anything outside these is unexpected — surface the actual error to the operator and stop.

| # | Failure | What you do |
|---|---|---|
| 1 | `git clone` fails (network, auth, disk) | Stop. Print the git error verbatim, then print the manual clone command for the operator to run themselves. Do not proceed to Phase 2. |
| 2 | `~/A2AL` exists but is not the A2AL repo | Stop. Ask the operator for an alternate clone path. Do not overwrite. Retry e1 with their answer. |
| 3 | `git pull --ff-only` fails (local commits in clone, divergent history, etc.) | Warn but continue. Library files in the existing clone are still usable. Add this line to the final summary: "your clone is N commits behind upstream — `git pull` it manually when convenient." |
| 4 | Target CLAUDE.md exists but has no H2 sections at all (fresh-mode Case B) | Insert the A2AL block at the very top of the file. Add this line to the final summary: "no existing H2 found in CLAUDE.md — A2AL block placed at the top; you may want to add a project-identity H2 above it." |
| 5 | Diff loop — operator picks "Merge manually" then disconnects without finishing | Do not write anything for that subsection. The next run of the install will re-fire the diff for any subsection still drifted (file-state-driven idempotency). |
| 6 | e5 verification step fails one of the three probes | Print the matching troubleshooting row from `examples/ClaudeCode/README.md`. Do not roll back; partial installs are recoverable by re-running. |

### What does NOT have automatic recovery

- Operator hand-edited `skills/a2al/SKILL.md` or `commands/a2al.md` directly — these files are deterministic mirrors of upstream and were overwritten without warning. (The final summary always notes this is a possibility.)
- Library YAML files hand-edited in `copy-locally` mode — overwritten without warning. Clone-and-point operators have git as their backup.

### No rollback

Phase 2's file operations are write-once and deterministic. If the operator hits Ctrl+C mid-install, re-running the prompt picks up cleanly — that's what "idempotent" buys. Do not implement backup files; they would only add confusion.
