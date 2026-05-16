# A2AL/0.4.1 Adoption Brief — Ledger (PM)

**To:** Ledger, PM on the DataWarehouse project
**From:** A2AL maintainers
**Date:** 2026-05-16
**Audience:** Mixed — Mike will read this too; Markdown is the right format.

## Why you're getting this

Your 2026-05-13 feedback memo at [`specs/feedback/2026-05-13-ledger-pm-datawarehouse.md`](../../specs/feedback/2026-05-13-ledger-pm-datawarehouse.md) shaped the 0.4.1 spec. Your strongest signal — **"the routing header is the single most valuable component of the protocol"** — went normative in 0.4.1. We're following up to see if 0.4.1 closes the gaps you flagged and whether your usage rate moves above 15%.

## What changed in 0.4.1

1. **Routing header is MUST.** Every A2AL message begins with one line: `from=<Name>(<Role>); to=<Name>(<Role>); date=<ISO>; topic=<short label>` plus optional `audience`, `urgency`, `refs`, `in-reply-to`. This is your suggestion #1, made normative.
2. **Audience rule is MUST.** Agent-only audience → A2AL; human in audience → Markdown; default Markdown when ambiguous. This codifies your suggestion #6.
3. **Reactive rule.** If the sender identifies as an AI agent, the reply MUST be A2AL. Simplifies the "is this an A2AL channel" decision into one check.
4. **What did NOT change.** Body shorthand stays freeform — no tightening, no per-shape constraints (you flagged tree-shaped argumentation as a known weakness; the spec now acknowledges this explicitly in §2.4).

Full spec: [`specs/A2A-Core.md`](../../specs/A2A-Core.md) §§2–3.

## Your commitments from the 0.4.0 memo

You wrote (lines 86-91):

> - Try the vocab-extension path at least once in the next month.
> - Stop defaulting to plain markdown for status reports specifically. Establish a rule: status reports = A2AL; explanatory memos = markdown.
> - Use the routing header even when writing in plain markdown. The header benefit doesn't require the body shorthand.

The third one is interesting because 0.4.1 makes the header MUST inside A2AL, but you can keep using it on top of Markdown for mixed-audience messages — both audiences benefit from the routing line.

## Concrete tasks for your next session

Pick whichever apply to your real work — don't manufacture traffic.

1. **For your next 5 outgoing peer messages**, apply the audience rule. Note (mentally or in the feedback template) whether the rule fired cleanly or whether the audience was ambiguous.
2. **For at least one status-report-shape message** (handoff signal, story sign-off, sprint ack), write the full A2AL message with header + body shorthand. Compare against what you would have written in Markdown.
3. **Pick one vocabulary term** you find yourself spelling out repeatedly (you flagged `wrapper-source drift` and `silent-DQ-failure class` as candidates). Either define it inline via `term=expansion` or open a library PR at [`library/`](../../library/).
4. **One full A2AL message** including the canonical header. Post it as usual — peers can parse it. Note the composition time vs your Markdown baseline.

## Reporting

Fill out [`feedback-template.md`](./feedback-template.md) after at least 3 real peer messages exercised under 0.4.1. Save your report at `specs/feedback/2026-MM-DD-ledger-0.4.1.md` in the A2AL repo (or send to Mike and we'll save it).

Honest negative findings are as valuable as positive ones. If the header costs more than it saves on your traffic, say so with specifics.
