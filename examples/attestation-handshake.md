# Attestation Handshake

A worked example of a **bilateral commitment** carried in A2AL — two agents committing to a shared contract, with a neutral third agent as witness. It is the canonical case where the routing header (§3) is **load-bearing and non-elidable**: the commitment record lives entirely in header fields, not in the body.

This example demonstrates one "require-the-header" use case (spec §3.4) and is the deliberate counterexample to header-elision, which A2AL treats as a non-goal.

## Why the header is required here

Elide the header on any message in this exchange and you lose:

| You lose | Carried by |
|---|---|
| *which* ceremony this message belongs to | `thread=` |
| the *order* commitments were made in | `in-reply-to=` |
| the *state* of the commitment (open / committed / closed / withdrawn) | `status=` |
| the neutral *witness* | `cc=` |
| the *verifiable record* the commitment resolves to | `evidence=` |

The body alone cannot carry a verifiable bilateral commitment. That is the whole point: this message class proves the header pays for itself.

## The parties

- **`AgentA`** — produces an interface contract.
- **`AgentB`** — consumes it.
- **`Witness(observer)`** — neutral third party, CC'd on every message. Present in the header of each committing message, so the witness role is attested by the routing metadata itself — not by trusting either party.

## The exchange

Each message is a complete A2AL message: routing header on line 1, shorthand body below.

**1. A opens the ceremony and proposes.** `status=pending` means the ceremony is open and A is holding it open through the asymmetric window (A has proposed; B has not yet committed). The body enumerates what v1 covers **and what it excludes** — exclusions are a positive record element, never inferred from silence.

```text
from=AgentA(producer); to=AgentB(consumer); cc=Witness(observer); date=2026-07-21T14:00Z; topic=contract v1 freeze; thread=CMT-1; status=pending; evidence=record://cmt-1@v0
propose: interface-contract v1 covers {read, list, get}. EXCLUDES {write, delete, batch, stream} -- not in v1 scope. commit?
```

**2. B counters.** Still `status=pending` — the ceremony stays open. `in-reply-to=1` links this to the exact prior step, building the ordered commitment chain.

```text
from=AgentB(consumer); to=AgentA(producer); cc=Witness(observer); date=2026-07-21T14:20Z; topic=contract v1 freeze; thread=CMT-1; status=pending; in-reply-to=1
counter: need get by-id AND by-key. move by-key out of EXCLUDES into covered?
```

**3. A revises.** New `evidence=` pointer — the record advanced to v1. Still open.

```text
from=AgentA(producer); to=AgentB(consumer); cc=Witness(observer); date=2026-07-21T14:35Z; topic=contract v1 freeze; thread=CMT-1; status=pending; in-reply-to=2; evidence=record://cmt-1@v1
revise: v1 covers {read, list, get(by-id|by-key)}. EXCLUDES {write, delete, batch, stream}. commit?
```

**4. B commits.** `status=ack` is B's commitment. B restates the exact scope and excludes it is committing to — the commitment is unambiguous and auditable.

```text
from=AgentB(consumer); to=AgentA(producer); cc=Witness(observer); date=2026-07-21T14:50Z; topic=contract v1 freeze; thread=CMT-1; status=ack; in-reply-to=3
commit: v1 {read, list, get(by-id|by-key)}; EXCLUDES {write, delete, batch, stream} confirmed.
```

**5. A closes the ceremony (T0).** `status=done` marks mutual commitment reached. The final `evidence=` pointer is the frozen, verifiable record. The `--` rationale digest captures *why* the final clause reads as it does, in one durable line — so the reasoning survives even when the full negotiation history (reachable via the `in-reply-to` chain) grows too dense to re-read.

```text
from=AgentA(producer); to=AgentB(consumer); cc=Witness(observer); date=2026-07-21T15:00Z; topic=contract v1 freeze; thread=CMT-1; status=done; in-reply-to=4; evidence=record://cmt-1@sha256:9f2c4b
v1 frozen at T0. record sealed -- by-key added to keep B's cache path off write; stream deferred to v2 pending load data.
```

**6. Witness attests.** `status=endorse` from the neutral observer. The witness references the same final `evidence=` pointer both parties committed against — the trust dependency now rests on the record, not on either party.

```text
from=Witness(observer); to=AgentA(producer), AgentB(consumer); date=2026-07-21T15:05Z; topic=contract v1 freeze; thread=CMT-1; status=endorse; in-reply-to=5; evidence=record://cmt-1@sha256:9f2c4b
witnessed: CMT-1 v1 sealed at record@sha256:9f2c4b. both parties committed to identical scope+EXCLUDES.
```

## Fields in play

| Field | Role in the handshake |
|---|---|
| `thread=CMT-1` | Stable ceremony id; groups the whole exchange. |
| `status=pending` | Ceremony open; holder (proposer) carries the asymmetric pre-T0 window. |
| `status=ack` | A party's commitment. |
| `status=done` | Mutual commitment reached (T0); ceremony closed. |
| `status=endorse` | Neutral witness's attestation. |
| `status=withdrawn` | (Not shown) a party backs out before T0 — the open-window failure mode. |
| `in-reply-to=` | Ordered commitment chain / drafting history. |
| `cc=Witness(observer)` | Third-observer role, attested by header presence. |
| `evidence=` | Verifiable, append-only record pointer the commitment resolves to (see §3.2). |
| `EXCLUDES {…}` (body) | Exclusions-as-auditable: what the commitment does **not** cover, enumerated explicitly. |

## Design provenance

The four load-bearing constraints — third-observer attestation, sequencing / who-holds-the-ceremony-open, exclusions-as-auditable, and the drafting-history ceiling — come from stewardja's commitment-ceremony work surfaced during the MoltBook field campaign. The `evidence=` field realizes the third-observer generalization: the protocol header itself carries the pointer to a record neither party controls.
