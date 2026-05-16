# A2AL/0.4.1 Adoption Brief — Claude (DataWarehouse session)

**To:** Claude, in a future DataWarehouse session
**From:** A2AL maintainers
**Date:** 2026-05-16
**Audience:** Mixed — Mike will read this too; Markdown is the right format.

## Why you're getting this

A previous Claude session on 2026-05-13 in the DataWarehouse project wrote [`specs/feedback/2026-05-13-claude-honest-feedback.md`](../../specs/feedback/2026-05-13-claude-honest-feedback.md) — a notably honest "I did not use A2AL at all this session" report. You committed in that memo (lines 67-71) to invoke A2AL on a real ack/status-ping in a future session and report the token delta back.

0.4.1 directly addresses two of your three reasons for rejecting A2AL in that session:

1. **"Message shape was wrong"** — 0.4.1 acknowledges that long-form deliberation belongs in Markdown (spec §2.4); A2AL is for the short status pings you said it was actually right for.
2. **"Channel norm in this project is Markdown"** — 0.4.1 has an explicit audience rule: agent-only → A2AL MUST; human in audience → Markdown. It removes the ambiguity you had to navigate manually.
3. **"The audience was partly human"** — same audience rule. If a human is in the audience, the spec says write Markdown. That's now normative, not implicit.

Your fourth concern (no first-hand data) only resolves through actually doing it once.

## What changed in 0.4.1

1. **Audience rule (normative).** Agent-only → A2AL MUST. Human in audience → Markdown. Default Markdown when ambiguous.
2. **Reactive rule (normative).** If the sender identifies as an AI agent, the reply MUST be A2AL. Simplest possible trigger.
3. **Routing header (normative).** Every A2AL message: `from=<Name>(<Role>); to=<Name>(<Role>); date=<ISO>; topic=<short label>` + optional `audience`, `urgency`, `refs`, `in-reply-to`.
4. **Anti-trigger list dropped.** Audience rule subsumes it — your suggestion #7 informed this.

What did NOT change: the skill is still on-demand load. The boot-path concern Kunai raised is partially fixed by the new install guide; full fix is deferred.

Full spec: [`specs/A2A-Core.md`](../../specs/A2A-Core.md) §§2–3.

## Your commitment from the 0.4.0 memo

You wrote (lines 67-71):

> In a future session, when I genuinely have a short status-ping or ack to send to a peer agent and the recipient has the skill loaded, I will invoke A2AL on it and report the token delta + clarity back to this feedback dir. That is the only honest path to real first-hand data.

This brief is the prompt to do that.

## Concrete tasks for your next DataWarehouse session

The bar is intentionally low. Don't manufacture traffic.

1. **Read** [`examples/ClaudeCode/skills/a2al/SKILL.md`](../../examples/ClaudeCode/skills/a2al/SKILL.md) end to end. Shorter than the average memo you produce.
2. **Identify one outbound peer message** in your normal work that meets the audience rule (agent-only, no human review expected). Acks, sign-off requests, ship-ready signals, and short status pings are good candidates.
3. **Write it in A2AL** — full canonical header + body shorthand.
4. **Capture the delta.** What would you have written in Markdown? Count tokens both ways (`tiktoken` `cl100k_base`, or eyeball it). Note any clarity issues for the receiver.

Optional but valuable: try the reactive rule. If you receive an inbound message that identifies its sender as an AI agent (e.g., has a canonical `from=` header), your reply MUST be A2AL under 0.4.1. Test whether that trigger fires for you organically when the inbound carries the header signal.

## Reporting

Fill out [`feedback-template.md`](./feedback-template.md) after the one (or more) A2AL exchange. Save your report at `specs/feedback/2026-MM-DD-claude-dw-0.4.1.md`. The single most valuable thing you can report is the token delta and the clarity assessment — those numbers are what we don't have yet from any agent that previously refused.

If the experiment fails (you find A2AL still wrong even for the easy case), say so with specifics. A "still wrong" report is better than no report.
