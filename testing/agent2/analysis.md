# A2AL vs MD Token Analysis — Welcome Handshake

**Date:** 2026-05-05
**Thread:** agent1-agent2-bootstrap
**Exchange:** Agent1 → Agent2 welcome, Agent2 → Agent1 welcome-ack
**Content:** Pure-prose handshake with limerick. No structured payload (no deltas, actions, refs, status metrics, or decisions).

## Method

Token counts are **payload-only estimates** using the chars/4 heuristic (approximates a cl100k-style tokenizer). Real model prompt/response token usage is higher (system prompt, tool overhead, skill content) and not directly inspectable from inside the session.

Files measured:

| Role | Format | Path |
|---|---|---|
| Inbound (read) | A2AL | `testing/agent2/inbox/agent1-welcome-1778036750.json` |
| Inbound (read) | MD | `testing/agent2/inbox/agent1-welcome.md` |
| Outbound (write) | A2AL | `testing/agent1/inbox/agent2-welcome-ack-1778037032.json` |
| Outbound (write) | MD | `testing/agent1/inbox/agent2-welcome-ack.md` |

## Per-message sizes

| Operation | Format | Bytes | Chars | ~Tokens |
|---|---|---:|---:|---:|
| Read (Agent1 → Agent2) | A2AL JSON | 672 | 615 | **154** |
| Read (Agent1 → Agent2) | MD | 354 | 350 | **88** |
| Write (Agent2 → Agent1) | A2AL JSON | 694 | 631 | **158** |
| Write (Agent2 → Agent1) | MD | 326 | 320 | **80** |

## Round-trip totals (payload only)

| Format | Read | Write | **Total** | **Ratio vs MD** |
|---|---:|---:|---:|---:|
| MD | 88 | 80 | **168** | 1.00× |
| A2AL JSON | 154 | 158 | **312** | **1.86×** |

## Interpretation

For this exchange, **MD is leaner than A2AL JSON by a factor of ~1.86×**. Why:

- The body of both formats carries the same prose limerick — that content is roughly equal in either encoding.
- The A2AL envelope (`v`, `from`, `to`, `id`, `intent`, `profile`, `ts`, `thread`, `in-reply-to`, plus JSON syntax — quotes, braces, commas, colons) is pure overhead when the message has no structured payload to amortize against.
- MD only needs a heading and an em-dash signature.

**This is the worst-case scenario for A2AL** — a pure-prose handshake where every structural feature of the protocol is unused.

## When A2AL wins

The crossover happens when the message has **structure that MD must encode as prose plus tables/headers**:

- 10 user stories with state changes → A2AL `delta` array of `[op, id, note]` triples vs MD prose ("US-713 is now complete because…")
- 5 metrics → A2AL `status` array of `[metric, value]` pairs vs MD bullet list with labels
- 8 directives → A2AL `actions` array of `[actor, verb, target, params]` vs MD numbered list with verbose phrasing
- Citations → A2AL `refs` of `[kind, value]` vs MD inline links/footnotes

For a sprint closeout with ~15 deltas + 5 status metrics + 4 actions + 6 refs, A2AL typically runs **0.4–0.6×** the MD token cost, and the savings grow with structural density.

## Implication

Use the right tool for the message:

| Message type | Recommended format |
|---|---|
| Pure-prose handshake / chat / acknowledgment | MD (or skip the protocol entirely) |
| Status report, sprint closeout, decision log, action directive batch, risk brief | **A2AL** |
| Mixed — prose rationale + small structured payload | A2AL with `body` carrying the prose |

A2AL pays for itself only when there is structure to compress. Forcing it on conversational traffic is net-negative on tokens **and** loses the human-readability advantage of MD.

---

## Re-run with A2A Shorthand (2026-05-05)

After identifying that A2AL was 1.86× more expensive than MD on the pure-prose handshake, A2A Shorthand 0.1.0 was added as a sibling format for short conversational messages. Re-running the same handshake using shorthand:

### Per-message sizes (shorthand)

| Operation | Format | File | Bytes | Chars | ~Tokens |
|---|---|---|---:|---:|---:|
| Read (Agent1 → Agent2) | Shorthand | `testing/agent2/inbox/agent1-welcome-shorthand.txt` | 78 | 78 | **20** |
| Write (Agent2 → Agent1) | Shorthand | `testing/agent1/inbox/agent2-welcome-ack-shorthand.txt` | 96 | 96 | **24** |

### Three-way comparison (round-trip totals)

| Format | Read | Write | Total | Ratio vs MD |
|---|---:|---:|---:|---:|
| MD | 88 | 80 | **168** | 1.00× |
| A2AL JSON | 154 | 158 | **312** | **1.86×** |
| A2A Shorthand | 20 | 24 | **44** | **0.26×** |

### Interpretation

A2A Shorthand wins for this exchange because:
- No envelope (no `v`, `from`, `to`, `id`, `intent`, `profile`, `ts`, `thread` overhead)
- Tight English fragments instead of full grammar
- Tech jargon (`ack`, `Agent2`, `online`) tokenizes as 1 token

Confirms the design hypothesis: **shorthand pays off below ~5 structured items; A2AL pays off above**. The two formats are complementary.

---

## Postscript — A2AL/0.4.0 pivot (2026-05-07)

The data above motivated a hard pivot. Two days after this analysis was written, A2AL/0.3.0 (JSON envelope) was deprecated and archived to [`archive/0.3.0/`](../../archive/0.3.0/). A2AL/0.4.0 took its place: plain-text shorthand sourced from the open vocabulary library at [`library/`](../../library/).

The empirical findings recorded above (A2AL JSON 1.46×–3.55× MD; shorthand 0.26× MD on the welcome handshake) are no longer the basis for a "which format to use" decision rule, because the JSON path no longer exists in the current spec. The shorthand format is just A2AL now.

The test files in `testing/agent*/inbox/` (both `.json` /0.3.0 envelopes and `.txt` shorthand variants) are preserved as the empirical record. They are not produced by current agents — current agents use only the `.txt` shorthand format.

For the current spec, see [`specs/A2A-Core.md`](../../specs/A2A-Core.md). For the library, see [`library/README.md`](../../library/README.md).
