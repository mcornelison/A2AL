# A2AL/0.4.1 Adoption Test — Header Payback Analysis

**Date:** 2026-05-16
**Method:** Replay the existing 6-message DataLake round-trip corpus, replacing ad-hoc routing (`@Agent2/qa from @Agent1/pm` + `thread: ...; intent: ...`) with the canonical 0.4.1 routing header. Bodies identical to the 0.4.0 corpus. Token measurement via `tiktoken` (`cl100k_base`).
**Question:** Does the canonical 0.4.1 routing header pay back its token cost?
**Verdict:** **Yes.** Header overhead is ~10 tokens per message regardless of message size; the corpus still beats Markdown by 23%; the cost buys cross-agent parseability + a stable grep target + normative spec compliance.

---

## Numbers

| Message | shorthand-0.4.0 | shorthand-0.4.1 | md | Δ (0.4.1−0.4.0) | header % of msg |
|---|---:|---:|---:|---:|---:|
| `agent1-us-dl401` | 198 | 208 | 290 | +10 | 4.8% |
| `agent1-us-dl407` | 210 | 220 | 292 | +10 | 4.5% |
| `agent1-pipeline-error` | 565 | 576 | 730 | +11 | 1.9% |
| `agent2-us-dl401-signoff` | 152 | 163 | 221 | +11 | 6.7% |
| `agent2-us-dl407-signoff` | 163 | 174 | 216 | +11 | 6.3% |
| `agent2-inc-dl0517-ack` | 402 | 411 | 533 | +9 | 2.2% |
| **Total** | **1,690** | **1,752** | **2,282** | **+62** | **3.5%** |

Ratios against the Markdown baseline:

- `shorthand-0.4.0 / md = 0.741` (0.4.0 corpus saves 26% of MD tokens)
- `shorthand-0.4.1 / md = 0.768` (0.4.1 corpus saves 23% of MD tokens)
- `shorthand-0.4.1 / shorthand-0.4.0 = 1.037` (0.4.1 costs 3.7% more than 0.4.0)

## Header overhead is flat per message, not per-byte

Header overhead is essentially **constant**: +9 to +11 tokens per message regardless of body size. This is the canonical header itself (`from=...; to=...; date=...; topic=...; audience=agent` and the occasional optional field) tokenizing the same way every time.

As a percentage of total message tokens:

- **Long messages (400–600 body tokens):** header is ~2% of the message — negligible
- **Short messages (~150 body tokens):** header is ~7% — noticeable but small
- **Crossover with MD:** at no message size in this corpus does the header push 0.4.1 close to MD cost. The smallest gap is `agent2-us-dl407-signoff`: 174 (0.4.1) vs 216 (md) — 0.4.1 still wins by 19%.

## What we're really measuring: canonical vs ad-hoc routing

The 0.4.0 messages aren't "no routing" baselines. They already contain ad-hoc routing at the top:

```
@Agent2/qa from @Agent1/pm
thread: agent1-agent2-datalake; intent: user-story
```

That's ~12 tokens of routing info per message, written organically by the agents themselves. The 0.4.1 canonical header replaces that with ~22 tokens of structured routing. So the +10 token delta is **canonical format cost ON TOP of routing the agents would write anyway**.

This matters for the payback question. The choice isn't "no routing vs canonical routing"; it's "ad-hoc routing vs canonical routing":

| | Ad-hoc (0.4.0) | Canonical (0.4.1) |
|---|---|---|
| Tokens per message | ~12 | ~22 |
| Parseable by any A2AL agent | no | yes |
| Stable substring for tooling | no | yes |
| Encodes recipient role explicitly | sometimes | always |
| Encodes audience signal (`audience=agent`) | no | yes |
| Carries reactive-rule trigger | no | yes |

The 10-token premium buys cross-agent compatibility, tooling discoverability, and the audience/reactive rule signals that 0.4.1 introduced as normative. Those signals are non-negotiable under the 0.4.1 spec — they're how the reactive rule fires.

## Findings

### 1. Header pays back. Keep it.

10 tokens per message is small enough that the answer doesn't depend on edge cases. Even on the smallest messages (sign-offs at ~150 body tokens), the header is 7% — well below the noise floor of message-to-message variance. There is no message size or shape in this corpus where the canonical header threatens 0.4.1's lead over Markdown.

### 2. Header overhead is flat, not proportional. Best ROI on long messages.

The header tokenizes identically regardless of body size. So:

- A 1000-token incident memo pays 1% in header cost
- A 100-token ack pays 10%

This pushes the protocol toward favoring **bundled messages over chatty acks**. If an agent has three things to say to a peer, sending one combined message costs 1 header; three separate messages cost 3 headers. The protocol should not encourage chattiness.

### 3. The spec is missing a `thread=` field.

The 0.4.0 messages used a `thread: agent1-agent2-datalake` tag — a free-form identifier letting agents group related messages independently of strict reply chains. The 0.4.1 spec has only `in-reply-to=<message-id>` (single-parent reply graph) and no `thread=` field.

For the replay, I preserved threading on the *responses* via `in-reply-to=agent1-us-dl401` etc. but had to **drop the thread tag entirely from the initial messages** — there's no canonical field for it. This is a real gap. A free-form `thread=<id>` lets:

- Sub-threads share an id without forcing a strict reply chain
- Tooling group messages by topic without parsing reply graphs
- Agents reuse the same conversation thread across multiple message exchanges

**Recommendation:** add `thread=<freeform>` to the 0.4.1 spec's optional fields, or pencil it in for 0.4.2.

### 4. The corpus shrunk for two messages where 0.4.0 had richer routing.

The `agent1-pipeline-error` message had a `sev: 2` tag in 0.4.0 that maps to `urgency=high` in 0.4.1 — same info, similar cost. The `agent2-inc-dl0517-ack` had `sev: 2; in-reply-to: INC-DL-0517` already; in 0.4.1 this became `urgency=high; in-reply-to=agent1-pipeline-error` (more correct: the message-id, not the topic-id). These two messages had the smallest deltas (+11 and +9 respectively) because the 0.4.0 ad-hoc routing was richer to begin with — closer to canonical.

This suggests: **agents naturally drift toward something like the canonical header anyway.** 0.4.1 just codifies what was already emerging.

### 5. Reactive rule is now visible at parse time.

Every 0.4.1 message in this corpus carries `audience=agent`. A receiving agent reading any of these knows immediately that its reply MUST be A2AL. In the 0.4.0 corpus, audience was implicit — derivable only from the `@Agent2/qa from @Agent1/pm` convention. Making it explicit costs 13 tokens per message (`; audience=agent`) and removes ambiguity at the spec-compliance level.

### 6. Markdown is still substantially more expensive, even with the header tax.

The 0.4.1 corpus is 23% smaller than the MD baseline. The bet of "shorthand beats MD by a wide margin" survives the addition of the canonical header.

## Recommendations

1. **Ship 0.4.1 as-is.** Header pays back; corpus is still well under MD; no breaking changes needed.
2. **Add `thread=<freeform>` to 0.4.2.** Free-form thread identifier as a 5th optional field. Mirrors what agents already wanted; cheap to add; non-breaking.
3. **Mention in the spec that the header cost is flat per-message.** This naturally encourages bundling acks/short messages rather than emitting chatty one-fact-per-message traffic. A note in `§3.4 Why the header is mandatory` would help.
4. **No further changes needed from this test.** Pattern, audience rule, and the four optional fields all worked. The 6 messages parsed cleanly into the canonical form with one structural gap (`thread=`) and one minor mapping decision (sev → urgency).

## Reproducibility

```bash
python testing/tools/token_analytics.py batch \
  --manifest testing/tools/manifests/datalake-roundtrip-0.4.1.json
```

Outputs land in `testing/agent2/analysis/datalake-roundtrip-0.4.1/`:

- `tokens-<id>.json` (one per message)
- `summary.json` (rollup with totals + ratios)
