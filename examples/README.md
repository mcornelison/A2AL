# A2AL Examples

Plain-text agent-to-agent messages following the A2AL/0.5.0 spec (routing header + style guide). See [`specs/A2A-Core.md`](../specs/A2A-Core.md).

## Files

Every file below is a **complete message**: routing header on line 1 (§3, MUST since 0.4.1), shorthand body beneath. The `.md` files are walkthroughs that embed complete messages in fenced blocks.

The corpus deliberately spans industries. A2AL is a coordination protocol, not a software protocol — the software examples are **one worked domain**, shown alongside programme, campaign and engagement messages that use only `core.yaml` and `project-mgmt.yaml`.

| File | Pattern | Exercises |
|---|---|---|
| [welcome.txt](./welcome.txt) | Handshake | The test-harness welcome that motivated the design |
| [sprint-status.txt](./sprint-status.txt) | Status report + state changes | `status=`, `thread=` |
| [blocker.txt](./blocker.txt) | Blocker notification (§7.5) | `status=blocked`, `thread=` |
| [compound-update.txt](./compound-update.txt) | Mixed: state change + blocker + action directive | `urgency=`, `hotfix` |
| [triage-priority.txt](./triage-priority.txt) | Blocker + action directive, triage-shaped | `priority=`, `cc=`, `refs=`, multi-recipient `cc`; terms `heads-up`, `gate`, `spike`, `hotfix` |
| [supersede-notice.txt](./supersede-notice.txt) | Decision + scope change | multi-value `in-reply-to=`; terms `supersede`, `superseded`, `WITHDRAWN`, `PARTIAL`, `endorse` |
| [azure-access-review.txt](./azure-access-review.txt) | Status report, security review | the `azure` domain (all 22 terms), `status=pending` |
| [facility-go-live.txt](./facility-go-live.txt) | Blocker + directive, **non-software** | Cross-industry PM vocabulary: `milestone`, `critical-path`, `RFI`, `change-order`, `baseline`, `variance`, `deliverable`, `go-live` |
| [campaign-launch.txt](./campaign-launch.txt) | Status + scope change, **non-software** | `kickoff`, `WBS`, `RAID`, `scope-change`, `deliverable`, `go-live` |
| [engagement-closeout.txt](./engagement-closeout.txt) | Closeout, **non-software** | `SOW`, `lessons-learned`, `RCA`, `baseline`, `variance`, `stakeholder` |
| [attestation-handshake.md](./attestation-handshake.md) | Attestation handshake (§7.10) | Bilateral commitment carried in the header — the canonical require-the-header case; `evidence=`, `thread=`, `status=`, `cc=`, `in-reply-to=` |
| [embedded-block.md](./embedded-block.md) | Embedded A2AL block (§2.5.1) | A Markdown message carrying a fenced `a2al` block — permitted because the block does not restate the prose |
| [version-skew.md](./version-skew.md) | Fail-soft decode (§3.5) | `a2al=`, and what a reader does with a field from a newer version |

## Conformance

[`tools/test_examples.py`](../tools/test_examples.py) runs in CI over this directory and asserts that every message here carries a conformant routing header, that every header field the spec documents is demonstrated by at least one example, and that every term a release adds is demonstrated by at least one example. A release that ships vocabulary or a header field nothing exercises fails the build.

## Example: the welcome handshake

```text
from=Agent1(harness); to=Agent2(harness); date=2026-05-05T22:05Z; topic=inbox handshake; audience=agent
Welcome Agent2. Inbox live: 2026-05-05 22:05 CDT.
Reply when ready. -- Agent1
```

The body is 29 tokens against 30 for the verbose Markdown it replaced — on a message this short the shorthand saves almost nothing, and the routing header takes the total to 66.

That is the honest shape of the tradeoff, and it is why §3.4 argues the header on *routing* value rather than token value: on a two-line handshake the header is pure overhead, and it still pays for itself the first time an inbox router or archive scan has to answer "who sent this, and about what?" without reading the body. Compression is the bonus; legibility is the product.

## ClaudeCode integration

See [`./ClaudeCode/`](./ClaudeCode/) for the Claude Code skill (`a2al`) and slash command (`/a2al`) that produce and consume A2AL messages.

## Decode preamble

When posting A2AL where the reader may not know the format (first contact, public/mixed channels like Moltbook), prepend the canonical one-line [decode preamble](./decode-preamble.md) so the cold-start decode cost doesn't make the message skippable.

## Historical examples

For the deprecated /0.3.0 JSON envelope examples (project-coord, social-post profiles, Markdown-to-A2AL transpilation), see tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0/examples).
