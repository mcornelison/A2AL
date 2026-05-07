# testing/tools

Reusable utilities for the A2A test harness.

## token_analytics.py

Counts tokens (tiktoken cl100k_base by default) across multiple format files
representing the **same logical message** — A2AL JSON, plain MD, A2A Shorthand,
etc. — and emits one analytics record per message plus an optional roll-up.

Designed for fair format-comparison tests where the same prose is wrapped in
different envelopes; computes per-format token counts, pairwise ratios against
a baseline format, and (when the bodies are isomorphic) the envelope overhead
of structured formats.

### Modes

| Mode | What it does |
|---|---|
| `count` | Token count for a single file |
| `analyze` | One logical message, N format files → one analytics JSON |
| `batch` | Many messages from a manifest → many analytics JSONs + optional summary |
| `summary` | Roll up an existing directory of `tokens-*.json` records |

### Manifest example

See `manifests/test-2.json` — three logical messages (greeting, limerick,
review-request), each with three formats (a2al, md, shorthand). Outputs go to
`testing/agent1/`.

```bash
python testing/tools/token_analytics.py batch \
  --manifest testing/tools/manifests/test-2.json
```

Each output record has the shape:

```json
{
  "id": "agent1-greeting-1778500800",
  "label": "...",
  "intent": "greeting",
  "encoder": "cl100k_base",
  "formats": {
    "a2al":      {"file": "...json", "tokens": 135, "chars": 481},
    "md":        {"file": "...md",   "tokens": 38,  "chars": 181},
    "shorthand": {"file": "...txt",  "tokens": 25,  "chars": 95}
  },
  "shared_body": {"source_format": "a2al", "key": "body", "tokens": 38},
  "ratios": {"a2al/md": 3.553, "shorthand/md": 0.658},
  "envelope_overhead_tokens": {"a2al": 97}
}
```

### Adding a new format

Drop the file alongside the others, add a `{"name": ..., "path": ...}` entry
under that message's `formats`, rerun batch. No code change needed.

### Adding a new test

Copy an existing manifest, swap ids/paths, point `out_dir` wherever you want
the analytics to land. **Paths in `out_dir` and `formats[].path` may be
absolute or relative to the manifest file** — relative is preferred for
portability across machines.

See `manifests/agent2-inbox-reads.json` for an example using relative paths.

### Encoder notes

`cl100k_base` is OpenAI's tokenizer — close to but not identical to Anthropic's.
Counts are stable across runs (deterministic) and good for **relative**
comparisons within a test. For absolute Anthropic-token billing estimates,
swap in the `anthropic` SDK's `count_tokens` API; the `analyze_message()`
function takes the encoder as a parameter, so a small adapter can replace
tiktoken without changing the schema.
