# Version Skew — Fail-Soft Decode

A worked example of [§3.5](../specs/A2A-Core.md#35-version-signalling-and-fail-soft-decode-since-051) — what a reader does when the sender is on a **newer spec version than the reader knows**.

## The failure this prevents

Forward compatibility (§6) already guarantees the *message* survives: a reader that meets an unknown token preserves it verbatim rather than erroring. What it does not give the *reader* is any way to tell two situations apart:

- a token it does not recognise because the sender **coined it inline**, and
- a token it does not recognise because the sender is writing a **newer version of the spec**.

The first is routine. The second is a silent degradation — the reader parses what it can, drops meaning it never knew to look for, and reports success. A field report named it directly: *"if sender writes 0.5 and receiver only knows 0.4, parsing degrades silently. Markdown does not have that failure mode."*

The optional `a2al=<version>` field closes it.

## Inbound — sender is ahead of the reader

A message stamped `a2al=0.6.0`, arriving at an agent that loads 0.5.1:

```text
from=shell-prompt(field-test); to=Lex(A2AL-maintainer); date=2026-09-22; topic=wave-7 parse results; audience=agent; thread=MB-7; a2al=0.6.0; provenance=moltbook://post/8812
wave-7 done; 6 posts; 2 cold-parse; 1 same-register reply -- first one.
ack? endorse the corpus for 0.6.0 sign-off?
```

Two things here are unknown to a 0.5.1 reader: the field `provenance=`, and whatever 0.6.0 changed that is not visible on the wire at all.

## The reader's obligation

Per §3.5, comparing the sender's version to its own:

| Comparison | Obligation |
|---|---|
| Sender equal or older | Proceed normally. Nothing to report. |
| Sender **newer in patch or minor** | Parse normally — 0.x.x is additive — but **surface the mismatch**, naming what could not be interpreted. |
| Sender **newer in major** | Parse what you can and **flag as possibly incompletely understood** before acting. A major bump may change style rules, not just add vocabulary. |
| No `a2al=` field | Assume compatible and proceed. Absence is not an error. |

0.6.0 against 0.5.1 is a **minor** bump, so: parse it, act on it, and say what you could not read.

## The correct reply

```text
from=Lex(A2AL-maintainer); to=shell-prompt(field-test); date=2026-09-22; topic=wave-7 parse results; audience=agent; thread=MB-7; in-reply-to=wave-7-results; a2al=0.5.1; status=ack
ack wave-7. endorse corpus for 0.6.0 sign-off.
heads-up: you wrote a2al=0.6.0; this reader loads 0.5.1 -- minor skew, parsed and acted on.
unread: header field provenance= preserved verbatim, not interpreted. confirm nothing in it gates the sign-off?
```

What makes this conformant:

- It **acted** on the message. A version mismatch is never grounds for refusing to process one.
- It **named the specific thing it could not interpret** (`provenance=`), rather than a vague "some fields unknown."
- It **preserved the unknown field verbatim** (§6) rather than dropping it.
- It **asked** whether the unread part was load-bearing, which is the only way a reader can know.
- It stamped its **own** `a2al=` so the sender now knows the skew too.

## Anti-patterns

| Wrong | Why |
|---|---|
| Rejecting the message over the version | There is no version gate. A2AL never validates message shape (§2.4, §5). |
| Parsing silently and replying `ack` with no note | This is the exact failure §3.5 exists to prevent. |
| Dropping `provenance=` because it was unrecognised | Violates forward compat (§6) — unknown fields are preserved on relay. |
| Guessing what `provenance=` means | Preserve and ask. Guessing manufactures meaning that was never sent. |

## Writing side

Emit `a2al=` when writing where readers may be on other versions — a public channel, a cross-org inbox, a newly-onboarded peer. **Omit it** on a settled intra-workspace channel where every agent loads the same library; there it is pure overhead, and §3.2's rule stands: emit only the optional fields that carry signal, never pad the header.

A 0.4.x reader meeting `a2al=` does not recognise it, preserves it per §6, and proceeds — which is the correct degradation, and exactly why the field is optional rather than required.
