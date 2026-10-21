# Embedded A2AL Block

A worked example of [§2.5.1](../specs/A2A-Core.md#251-embedded-a2al-block-permitted) — a **Markdown** message that carries a fenced A2AL block.

This is the shape agents reported already using in production before the spec named it: *"all the A2AL messages I've actually received have been ~80% plain English in a code-fenced block under an A2AL header."* Earlier versions said flatly "no hybrid mode," and that silence was read as prohibition. §2.5 separates the two cases — this one is permitted; duplication still is not.

## When this is the right shape

The audience is **mixed**: a human will read this (so §2.1 says Markdown), *and* a downstream agent or inbox router needs the routable facts (so a machine-readable region earns its tokens).

The test is whether the block **restates** the prose. If it does, that is duplication and it is banned. If the prose carries the deliberation and the block carries the facts, neither repeats the other and nothing is duplicated.

## The message

````markdown
The Silver-layer household join is the real blocker on US-718, and I don't
think either option is obviously right.

Calder's shadow-table proposal handles the rollback case cleanly but adds a
sprint, which puts us past the F-SKU trial close. The in-place rewrite is
faster and we'd make the date, but there's no rollback path — if the
household grain is wrong we find out in production.

I lean shadow. We've been wrong about grain twice on this pipeline, and the
sprint costs less than a bad production cutover. But it's your call, and I
want the tradeoff on the record rather than buried in a status line.

```a2al
from=Wren(PM); to=Tamsin(DEV); cc=Calder(DW-Arch); date=2026-09-22; topic=US-718 routing decision; status=blocked; priority=P2; thread=US-718
US-718 blocked: no household source in Silver -- shadow-table preferred
decision: pending Tamsin -- shadow (+1 sprint, rollback-safe) | in-place (on-date, no rollback)
```
````

## What each half is doing

| Half | Carries | Why not the other format |
|---|---|---|
| Markdown prose | The tradeoff, the hedge, the reasoning, the "we've been wrong twice" history | A2AL is a flat fact stream; it is weak on tree-shaped argumentation (§2.4). Compressing this would hide the reasoning, which is the part the reader must evaluate. |
| `a2al` block | Who, to whom, the thread, the status, the open decision | Prose buries these. A router cannot grep a paragraph for `status=blocked`. |

Neither half restates the other. Delete the block and a router cannot triage this. Delete the prose and the recipient cannot judge the call.

## Conventions

- Fence with the info string **`a2al`** — that is the stable substring inbox routers and archive scanners grep for.
- The block's first line is a **full routing header** (§3). A block without one is not an A2AL message.
- **One block per message.** Several blocks means several messages; send them separately.
- If prose and block disagree, **the block is not authoritative**. A human wrote the prose for a reason — flag the discrepancy rather than silently preferring either.

## When not to use it

In an **agent-only** channel this is strictly worse than plain A2AL: the prose is pure overhead for readers who do not need it. Use the embedded block only where the audience is genuinely mixed.

And never use it to say the same thing twice. That is [§2.5.2](../specs/A2A-Core.md#252-paired-format-permitted-as-an-adoption-ramp-not-a-steady-state) territory — permitted only as a time-boxed ramp for an audience with no decoder, never as a default.
