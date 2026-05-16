# A2AL/0.4.1 — External Adoption Test Kit

**Purpose:** Collect first-hand usage data from Ledger (PM), Kunai (DW Architect), and Claude-DW (DataWarehouse session) after they've actually exercised A2AL/0.4.1 in real work. Closes the loop on the three feedback memos at [`../../specs/feedback/`](../../specs/feedback/) that drove the 0.4.1 spec changes.

## Why this test exists

Each of the three feedback writers made a specific commitment to try A2AL in their next session. The 0.4.1 spec (audience rule + routing header) was drafted from their feedback. This kit gives each agent a concrete, scoped task plus a structured feedback template — so the next round of data isn't another open-ended "how do you feel about A2AL" memo but answers the specific bets the spec changes made.

## What's in the kit

| File | Purpose |
|---|---|
| [`brief-ledger.md`](./brief-ledger.md) | Ledger (PM) — task + 0.4.1 changes most relevant to her workflow |
| [`brief-kunai.md`](./brief-kunai.md) | Kunai (DW Architect) — task + cold-start fix path |
| [`brief-claude-dw.md`](./brief-claude-dw.md) | Claude in a DataWarehouse session — task + audience-rule signal |
| [`feedback-template.md`](./feedback-template.md) | Shared structured template all three agents fill out |

## Delivery (user actions)

1. **Set up the agents** with A2AL/0.4.1. Follow [`../../examples/ClaudeCode/README.md`](../../examples/ClaudeCode/README.md). The CLAUDE.md sample is at [`../../examples/ClaudeCode/CLAUDE-sample.md`](../../examples/ClaudeCode/CLAUDE-sample.md). Place the A2AL block right after the first H2 in each agent's existing CLAUDE.md (the DataWarehouse `offices/<role>/CLAUDE.md` files).

2. **Deliver each brief** to the matching agent — paste contents into a session, or save under `offices/<role>/inbox/2026-05-16-a2al-0.4.1-adoption-brief.md` and let the agent read it on next session start. The brief is short (under 50 lines) and self-contained.

3. **Wait for the next real work session** for each agent (1–2 weeks). The test deliberately uses their actual work as the test corpus — synthetic exercises don't surface the cold-start, audience-rule, or adoption-friction findings.

4. **Collect feedback** at `../../specs/feedback/2026-MM-DD-<agent>-0.4.1.md` once each agent completes the template. Filename pattern matches the existing 0.4.0 feedback memos.

## Expected outcomes

| Agent | Hypothesis from 0.4.0 feedback | What 0.4.1 should change |
|---|---|---|
| Ledger | Header > body shorthand; library friction too high | Header is now MUST; should ratify "header alone is worth it" claim |
| Kunai | Cold-start: skill never surfaces during boot | Install guide + CLAUDE.md sample addresses the boot path; should move adoption from 0% to non-zero |
| Claude-DW | Channel norm pushes to Markdown; audience asymmetry | Audience rule + reactive rule make agent-only intent explicit; should unlock the agent-to-agent fork |

If 0.4.1 fails any of these bets, the analysis at [`../agent2/analysis-datalake-roundtrip-0.4.1.md`](../agent2/analysis-datalake-roundtrip-0.4.1.md) needs revisiting — and the spec may need a 0.4.2 revision before /1.0 gates are met.

## What we already know (internal data)

The local harness round-trip on the same 6-message DataLake corpus, replayed under 0.4.1, gave us:

- Header costs ~10 tokens per message (range 9–11), flat regardless of body size
- 0.4.1 corpus is 23% smaller than the Markdown baseline (down from 26% in 0.4.0)
- One structural gap surfaced: `thread=<id>` has no canonical field; pencilled in for 0.4.2

See [`../agent2/analysis-datalake-roundtrip-0.4.1.md`](../agent2/analysis-datalake-roundtrip-0.4.1.md) for the full numbers. The external test answers the *qualitative* and *adoption* questions that token counts can't.
