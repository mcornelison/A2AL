# A2A Shorthand Examples

Plain-text agent-to-agent messages following the `a2a-shorthand/0.1.0` style guide. See [`specs/A2A-Shorthand.md`](../../specs/A2A-Shorthand.md).

## Files

| File | Pattern | Notes |
|---|---|---|
| [welcome.txt](./welcome.txt) | Handshake | The test-harness welcome that motivated the design |
| [sprint-status.txt](./sprint-status.txt) | Status report + state changes | Multi-fact compound message |
| [blocker.txt](./blocker.txt) | Blocker notification | Includes recommended next steps |
| [compound-update.txt](./compound-update.txt) | Mixed: state change + blocker + action directive | Realistic multi-topic update |

## When NOT to use shorthand

If your message has 5+ structured items, multiple section types, or formal-record characteristics (sprint closeout, decision log, risk brief with citations), use A2AL/0.3.0 instead. See [`examples/project-coord/`](../project-coord/) for those.

The two formats are complementary. Decision rule lives in [`specs/A2A-Shorthand.md`](../../specs/A2A-Shorthand.md) §2.
