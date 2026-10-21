# A2AL Examples

These are plain-text agent-to-agent messages that follow the A2AL/0.5.2 spec (routing header, then a shorthand or prose body). The spec is [`specs/A2A-Core.md`](../specs/A2A-Core.md).

## Files

Each `.txt` file below is one complete message: the routing header on line 1 (§3, required since 0.4.1) and the body under it. Most are shorthand bodies; `prose-ruling.txt` shows a prose body under the header, which 0.5.2 allows. The `.md` files are walkthroughs that include complete messages in fenced blocks.

I picked examples from several industries on purpose. A2AL is for coordinating work in general, and software is just one of the domains I've worked through. The software examples sit next to programme, campaign and engagement messages that use only `core.yaml` and `project-mgmt.yaml`.

| File | Pattern | Exercises |
|---|---|---|
| [welcome.txt](./welcome.txt) | Handshake | The test-harness welcome that started the design |
| [sprint-status.txt](./sprint-status.txt) | Status report + state changes | `status=`, `thread=` |
| [blocker.txt](./blocker.txt) | Blocker notification (§7.5) | `status=blocked`, `thread=` |
| [compound-update.txt](./compound-update.txt) | Mixed: state change + blocker + action directive | `urgency=`, `hotfix` |
| [triage-priority.txt](./triage-priority.txt) | Blocker + action directive, triage-shaped | `priority=`, `cc=`, `refs=`, multi-recipient `cc`; terms `heads-up`, `gate`, `spike`, `hotfix` |
| [supersede-notice.txt](./supersede-notice.txt) | Decision + scope change | multi-value `in-reply-to=`; terms `supersede`, `superseded`, `WITHDRAWN`, `PARTIAL`, `endorse` |
| [azure-access-review.txt](./azure-access-review.txt) | Status report, security review | the `azure` domain (all 22 terms), `status=pending` |
| [facility-go-live.txt](./facility-go-live.txt) | Blocker + directive, non-software | Cross-industry PM vocabulary: `milestone`, `critical-path`, `RFI`, `change-order`, `baseline`, `variance`, `deliverable`, `go-live` |
| [campaign-launch.txt](./campaign-launch.txt) | Status + scope change, non-software | `kickoff`, `WBS`, `RAID`, `scope-change`, `deliverable`, `go-live` |
| [engagement-closeout.txt](./engagement-closeout.txt) | Closeout, non-software | `SOW`, `lessons-learned`, `RCA`, `baseline`, `variance`, `stakeholder` |
| [attestation-handshake.md](./attestation-handshake.md) | Attestation handshake (§7.10) | A two-way commitment carried in the header, the main case where you really need the header; `evidence=`, `thread=`, `status=`, `cc=`, `in-reply-to=` |
| [embedded-block.md](./embedded-block.md) | Embedded A2AL block (§2.5.1) | A Markdown message carrying a fenced `a2al` block, which is allowed because the block doesn't repeat the prose |
| [item-correction.txt](./item-correction.txt) | Correction of one item (§3.2, §7.11) | `supersedes=<id>#<item>`, `# n.` section markers, `void-if` |
| [prose-ruling.txt](./prose-ruling.txt) | Ruling with a prose body (§2.1) | header over plain prose, verdict on line 1, `void-if`, `blocks` |
| [relay-and-ask.txt](./relay-and-ask.txt) | Relayed human words (§2.6) | `relay(<person>)`, `ASK(<person>)`, `default`, `cc=` that doesn't act |
| [version-skew.md](./version-skew.md) | Fail-soft decode (§3.5) | `a2al=`, and what a reader does with a field from a newer version |

## Conformance

[`tools/test_examples.py`](../tools/test_examples.py) runs in CI over this directory. It checks that every message here has a conformant routing header, that at least one example uses each header field the spec documents, and that at least one example uses each term a release adds. If a release ships vocabulary or a header field that no example uses, the build fails.

## Example: the welcome handshake

```text
from=Agent1(harness); to=Agent2(harness); date=2026-05-05T22:05Z; topic=inbox handshake; audience=agent
Welcome Agent2. Inbox live: 2026-05-05 22:05 CDT.
Reply when ready. -- Agent1
```

The body is 29 tokens, against 30 for the wordy Markdown it replaced. On a message this short the shorthand saves almost nothing, and the routing header brings the total to 66.

That's the real tradeoff, and it's why §3.4 argues for the header on routing value instead of token value. On a two-line handshake the header is pure overhead. It still pays for itself the first time an inbox router or an archive scan needs to know who sent this and what it's about without reading the body. The compression is a bonus. What you're really getting is messages you can read and route at a glance.

## Claude Code

See [`./ClaudeCode/`](./ClaudeCode/) for the Claude Code skill (`a2al`) and slash command (`/a2al`) that write and read A2AL messages.

## Decode preamble

If you're posting A2AL somewhere the reader might not know the format (first contact, or public and mixed channels like Moltbook), put the standard one-line [decode preamble](./decode-preamble.md) in front of it. Otherwise the effort of figuring out the format cold can make the reader skip the message.

## Older examples

The deprecated /0.3.0 JSON envelope examples (project-coord, social-post profiles, Markdown-to-A2AL transpilation) are at tag [`v0.3.0-archive`](https://github.com/mcornelison/A2AL/tree/v0.3.0-archive/archive/0.3.0/examples).
