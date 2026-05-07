# Profile: project-coord/1.0

**Status:** Reference profile.
**Domain:** Project, PMO, sprint, and inter-project coordination.
**Replaces:** A2AL/2.0 (array-only positional format; no working implementations; superseded).

## Reference

- Core spec: [`specs/A2A-Core.md`](../specs/A2A-Core.md)
- Examples: [`examples/project-coord/`](../examples/project-coord/)
- Conformance corpus: [`validator/corpus/profiles/project-coord-1.0/`](../validator/corpus/profiles/project-coord-1.0/)

## Intents

Recommended vocabulary. Unknown intents MUST be accepted; receivers dispatch best-effort.

| Intent | Purpose |
|---|---|
| `review-observations` | QA or architect feedback on a deliverable |
| `blocker` | Story or task is blocked; requires resolution before progress |
| `sprint-closeout` | End-of-sprint summary across multiple stories |
| `status-report` | Periodic status update (daily / weekly / sprint) |
| `risk-brief` | Threat or risk intelligence brief |
| `decision` | Recorded decision (approval, priority, scope, owner) |
| `next-actions` | Action directives to specific actors |
| `inventory-update` | Topology / service / dependency inventory snapshot |
| `gates-update` | Gate / invariant changes (CI, deploy, story-specific) |
| `closeout` | Generic closeout — feature, epic, project |

## Sections Used

**Common:** `delta`, `status`, `actions`, `decision`, `refs`, `body`
**Less common:** `risk`, `gates`, `inventory`

All section item shapes are defined in `specs/A2A-Core.md` Section 4.

## Canonical Ordering

Canonicalize before emit. `actions` and `refs` always preserve emission order — execution and citation sequence matters.

| Section | Sort key |
|---|---|
| `delta` | (`op`, `id`) ascending |
| `status` | `metric` ascending |
| `decision` | `key` ascending |
| `risk` | `sev` descending, `vector` ascending |
| `gates` | (`scope`, `invariant`) ascending |
| `inventory` | (`kind`, `id`); KVs by `k` ascending within each item |
| `actions` | emission order — DO NOT SORT |
| `refs` | emission order |

`sev` ordering uses the rank: `crit` > `high` > `med` > `low` > `info`.

## Recommended Roles

For `from` and `to` tuples. Free-form roles allowed.

`PM`, `QA`, `DEV`, `SEC`, `DEVOPS`, `ARCHITECT`, `PMO`

## Required Envelope Fields

No additions beyond the core minimum.

## Example

A complete sprint-closeout message — see [`examples/project-coord/sprint-closeout.json`](../examples/project-coord/sprint-closeout.json).
