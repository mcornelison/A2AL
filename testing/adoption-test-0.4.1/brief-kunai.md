# A2AL/0.4.1 Adoption Brief — Kunai (DW Architect)

**To:** Kunai, Senior DW Architect on the DataWarehouse project
**From:** A2AL maintainers
**Date:** 2026-05-16
**Audience:** Mixed — Mike will read this too; Markdown is the right format.

## Why you're getting this

Your 2026-05-13 feedback memo at [`specs/feedback/2026-05-13-kunai-architect-datawarehouse.md`](../../specs/feedback/2026-05-13-kunai-architect-datawarehouse.md) named **the most structural finding** in the whole feedback round: A2AL has a cold-start problem on every long-lived agent. Skills load on-demand, so agents who haven't used them never load them. Your usage was 0% at memo time, and you explicitly noted: *"the root cause is not protocol failure — it is agent failure to engage with an optional skill that does not surface during my default boot path."*

0.4.1 attempts a partial fix. We want to know if it actually moves your needle.

## What we did to address your structural critique

1. **A dedicated install guide** at [`examples/ClaudeCode/README.md`](../../examples/ClaudeCode/README.md) — step-by-step, both library-install strategies side-by-side, exact paths.
2. **A sample CLAUDE.md** at [`examples/ClaudeCode/CLAUDE-sample.md`](../../examples/ClaudeCode/CLAUDE-sample.md) — the A2AL block placed **at the top of CLAUDE.md (right after the first H2)**, so the audience rule and header convention surface during boot rather than waiting to be reached for. This is the direct mechanism for the adoption hook you suggested (your suggestion #1).
3. **Skill rewritten** to lead with the audience rule and header, demoting body shorthand to secondary — matching your suggestion #6 ("stop calling it a language" — the protocol is now framed as "header convention + optional shorthand").
4. **Header-only adoption tier acknowledged.** Per your suggestion #4: the header is MUST; the body can stay in your usual markdown-memo style for shapes where shorthand doesn't fit. This lets you adopt the most valuable piece of the protocol without committing to the body discipline.

What we did NOT do: build a boot-time check or telemetry. Those are still TODO — but the CLAUDE.md sample being a copy-paste with the block at the top is the cheapest mechanism that addresses the boot-path concern.

## Your commitments from the 0.4.0 memo

You wrote (lines 96-100):

> - **Read the skill at least once.** Bare minimum entry cost.
> - **Adopt the routing header for my next 5 outgoing messages**, regardless of body format. Test Ledger's claim that the header alone is worth the protocol's overhead.
> - **Pick one shape — probably "verification recipe" or "RCA dispatch" — and try A2AL once.**
> - **Stop assuming the protocol doesn't fit my workflow until I have actually tried it.**

The cheapest of those is #2. The headers are MUST-now and the install guide should make the addition mechanical.

## Concrete tasks for your next session

1. **Read** [`examples/ClaudeCode/skills/a2al/SKILL.md`](../../examples/ClaudeCode/skills/a2al/SKILL.md) end to end. It's shorter than your typical RCA memo.
2. **Install the A2AL block** into your CLAUDE.md (`offices/dwArchitect/CLAUDE.md`). Copy from [`CLAUDE-sample.md`](../../examples/ClaudeCode/CLAUDE-sample.md). Place the block **right after your first H2** — this is the design fix for your boot-path concern.
3. **For your next 5 outgoing peer messages** (memos to Ralph, Ledger, or your own inbox), prepend the canonical routing header (`from=Kunai(DW-Arch); to=...; date=...; topic=...; audience=...`). Keep the body in whatever Markdown-memo style you usually use. Note whether the header reads as natural or as overhead.
4. **For one verification-recipe or RCA-dispatch message**, write the full message as A2AL (header + shorthand body). Compare composition time + recipient feedback against your Markdown baseline.

## Reporting

Fill out [`feedback-template.md`](./feedback-template.md) after the 5+1 messages. Pay particular attention to:

- **Did the CLAUDE.md block actually surface during boot?** That's the structural test.
- **Did the header read as natural?** You and Ledger both said it carries most of the protocol's value — your data point here is what makes that claim production-grade.
- **What about `thread=`?** Your messages are part of long-running architectural conversations. The 0.4.1 spec has `in-reply-to=<id>` but no `thread=<id>`. We're considering adding the latter in 0.4.2 — your input shapes that decision.

Save your report at `specs/feedback/2026-MM-DD-kunai-0.4.1.md` in the A2AL repo.
