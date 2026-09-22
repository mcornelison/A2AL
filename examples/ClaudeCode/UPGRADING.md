# Upgrading an A2AL Install

How to move an existing A2AL install to a newer version. This applies to any upgrade inside the 0.x.x line (e.g. 0.5.0 → 0.5.1).

## TL;DR

A2AL releases inside 0.x.x are **additive and backward-compatible**. Upgrading means re-syncing three things — the **library**, the **skill/command**, and your **CLAUDE.md version heading** — then verifying. No message rewrites, ever.

```
1. Pull canonical:   git -C <A2AL clone> pull   (or check out the version tag, e.g. v0.5.0)
2. Re-sync library:  copy the updated core.yaml + any NEW domain files into the library your agent ACTUALLY LOADS
3. Bump skill:       re-copy examples/ClaudeCode/skills/a2al/SKILL.md + commands/a2al.md
4. Bump heading:     CLAUDE.md "## A2AL/<old>" → "## A2AL/<new>"
5. Verify:           python tools/validate_library.py   → expect "OK: 164 entries across 7 files" at 0.5.1
```

Or run [`INSTALL-PROMPT.md`](./INSTALL-PROMPT.md) in re-sync mode, which automates steps 2–4 **for the clone-and-point and copy-locally modes** (see the library-mode caveat below).

## Backward-compatibility guarantee

Within 0.x.x, every release is purely additive:

- **Existing messages never need migration.** A 0.4.x message is a valid 0.5.x message.
- **New header fields are optional.** Unknown header fields are preserved-and-ignored by older readers (forward-compat invariant).
- **New vocabulary is additive.** No terms are renamed or removed in a minor bump; unknown tokens are relayed verbatim.
- **Nothing new is mandatory.** You can adopt new fields/terms at your own pace.

The only things that change in a major bump (e.g. a future 1.0) are spec rules — those will be called out explicitly in `VersionHistory.md`.

## Know your library mode (this determines step 2)

Where your agent loads vocabulary from decides what you re-sync. There are **three** modes:

| Mode | Library lives at | Re-sync action |
|---|---|---|
| **clone-and-point** | the canonical clone's `library/` (your CLAUDE.md points at it) | `git pull` the clone — done. |
| **copy-locally** | a per-project copy (e.g. `.claude/a2al-library/`) | copy updated `core.yaml` + new domain files into that copy. |
| **shared-vendored** | a project-relative dir outside `.claude/` (e.g. `offices/library/`), often shared by several agents | copy updated files into that shared dir **once** — it upgrades every agent that loads it. |

> **The false-GREEN trap (real field failure).** Verify the library your agent **actually loads**, not the clone you just pulled. If you `git pull` the clone but your agent loads a *vendored* copy, running the validator against the clone reports the new count and passes — while your agent is still on the old vocabulary. **Always run `validate_library.py` against the path in your CLAUDE.md "Library location", and confirm the entry count matches the new version.** A version heading that says 0.5.0 over a library that still has the 0.4.x entry count is a broken install.

## Step-by-step

1. **Pull canonical.** `git -C <clone> pull`, or `git -C <clone> checkout <tag>` for a pinned version (tags: `v0.5.1`, `v0.5.0`, …).
2. **Re-sync the library** into the path your agent loads (see your mode above). Copy the updated `core.yaml` and any **new** domain files (a release may add a whole new domain — e.g. 0.5.0 added `azure.yaml`). Other domain files are unchanged unless the changelog says otherwise.
3. **Bump the skill + command.** Re-copy `examples/ClaudeCode/skills/a2al/SKILL.md` and `examples/ClaudeCode/commands/a2al.md` wholesale — don't hand-edit the version banner; the canonical copies already carry the new fields and domain rows.
4. **Bump your CLAUDE.md heading.** `## A2AL/<old> — Agent-to-Agent Communication` → the new version. (Claude Code may need a session restart to register refreshed skill/command files.)
5. **Verify.** `python tools/validate_library.py` against your loaded library. Expect `OK: <N> entries across <F> files`. This validates the **library**, not messages — A2AL never validates message shape, by design, so there is no header-field linter.

## Domain loading after upgrade

A new domain file is opt-in. Load it per-topic like the others — **unless** that domain *is* your daily traffic, in which case bundle it into your always-load set alongside `core.yaml`. Workspaces with no footprint in a domain can skip its file entirely; the validator does not require a fixed set of files.

## What changed in 0.5.1

- **Industry-neutral release.** A2AL is a coordination protocol, not a software protocol. Nothing in the spec mechanics changed meaning; the positioning and vocabulary did.
- **`project-mgmt.yaml` re-scoped.** It previously held SRE/service-ops terms despite its name. Those moved to `infrastructure.yaml`; `EM` and `TPM` moved to `programming.yaml`; `project-mgmt.yaml` now holds cross-industry project vocabulary (+15: `milestone`, `deliverable`, `change-order`, `RFI`, `RAID`, `WBS`, `stakeholder`, `baseline`, `variance`, `go-live`, `critical-path`, `kickoff`, `scope-change`, `SOW`, `lessons-learned`).
  > **Action required if you load `project-mgmt.yaml` for SRE terms.** `SRE`, `SLA`, `SLO`, `SLI` and `MTTR` are now in `infrastructure.yaml` — add it to your load set. No term was removed or renamed, and unknown tokens relay verbatim, so nothing breaks in the meantime.
- **2 optional header fields:** `a2al=<version>` (§3.5, lets an older reader say it is behind instead of degrading silently) and `evidence=` (§3.2, verifiable record for attestation traffic).
- **§2.5 settles the embedded-block question.** A fenced ` ```a2al ` block inside a Markdown message is permitted when it does not restate the prose. Duplication is still banned.
- **Library 149 → 164.** Expected post-upgrade count: **164 entries across 7 files**.
- **New tools:** `a2al_lookup.py` (check a term before coining it), `a2al_preview.py` (what A2AL buys on this message), `test_examples.py` (corpus conformance in CI).

## What changed in 0.5.0

- **4 optional header fields:** `thread` (stable conversation/topic-group key, distinct from `in-reply-to`), `status`, `cc`, `priority` (P0–P3, distinct from `urgency`); plus multi-value `in-reply-to`.
- **Vocabulary 117 → 149:** +10 core terms (`ack`, `endorse`, `supersede`, `superseded`, `heads-up`, `gate`, `spike`, `hotfix`, `PARTIAL`, `WITHDRAWN`) and a new `azure` domain (22 terms). Skip `azure.yaml` if you have no Azure/Microsoft footprint.
- Expected post-upgrade count: **149 entries across 7 files** (148 if you skip `azure`: 127 across 6).

Full detail: [`VersionHistory.md`](../../VersionHistory.md) and [`specs/A2A-Core.md`](../../specs/A2A-Core.md) §3.2.
