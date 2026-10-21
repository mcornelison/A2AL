# We built a JSON format for agents to talk to each other, measured it, and deleted it

*A field report on making AI agents communicate efficiently — and the three things that turned out to matter, none of which we expected going in.*

## The setup

When you run more than one AI agent and they have to coordinate, they talk to each other in the same way they talk to you: in fluent, padded, human-shaped prose. "Hi Byte, just wanted to give you a quick update — US-713 is now complete, all acceptance criteria are met, CI is green, and the PR is ready for your review whenever you get a chance." That sentence is ~35 tokens of which maybe 8 carry signal. Multiply by every handoff in a multi-agent workflow and a meaningful fraction of your token budget is spent on politeness and framing that no agent needs.

A2AL (Agent-to-Agent *Language*) started as an attempt to fix that. The interesting part isn't the fix — it's how wrong our first instinct was, and what the measurements forced us to admit.

## Wrong turn #1: the envelope

The obvious move, if you come from an API background, is to define a structured wire format. So /0.3.0 was a JSON envelope: typed fields, composable sections, a schema, a validator. Clean. Parseable. Professional-looking.

Then we measured it against the plain Markdown it was supposed to replace.

The envelope cost **2× to 8× more tokens than just writing Markdown.** On short messages it was catastrophic — an 8× blowup on a three-word acknowledgement, because the structural scaffolding dwarfed the content. The JSON keys, the braces, the quoting: all of it tokenizes, and none of it is signal. We had built a format that made the exact problem we were trying to solve *worse.*

So we deleted it. /0.4.0 threw out the envelope entirely and became a plain-text shorthand: one routing header line, then a terse body drawn from an open vocabulary the LLM already knows. No JSON. No parser. The message above becomes:

```
from=Byte(DEV); to=Ledger(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

## Wrong turn #2: thinking compression was the point

We assumed the win was byte count. It wasn't. Three independent agents using A2AL in real workflows converged, unprompted, on the same feedback: **the routing header is more valuable than the body shorthand.** Not because it's shorter — it's actually pure overhead on a tiny message — but because it turns every message into something with a stable, greppable structure: who, to whom, when, about what, in one line. Tooling can route on it. Archives can scan it. A reader reconstructs context without parsing prose.

That reframed the whole project. A2AL isn't a compression scheme with a header bolted on; it's a *convention for making agent messages legible*, whose body happens to also be cheaper. The compression is a bonus. The legibility is the product.

## The number we had to correct

For a long time our headline claim was that A2AL cost "~0.26× the tokens of Markdown" — a 74% reduction. When we re-ran the corpus carefully, that number didn't reproduce anywhere. It turned out to be a transcription error: 0.26 was the *saving fraction* (≈26% fewer), which is a **0.74× cost ratio**, not a 0.26× one. The honest number is less flashy: about a **quarter fewer tokens** on real traffic, header included. We'd rather ship the number that survives a reader trying to reproduce it.

## The measurement that actually mattered: does it generalize?

Every efficiency number we had was measured on one tokenizer — OpenAI's `cl100k_base`, which we'd also been using as a stand-in for Claude's (unpublished) tokenizer. A fair critic's first question is: *is this just an artifact of one BPE vocabulary?* If A2AL only saves tokens on the tokenizer you tested it on, it's a parlor trick.

So we ran the same agent-traffic corpus through four independent tokenizers: GPT-3.5/4 (cl100k), GPT-4o (o200k), Llama 3 (128k BPE), and Mistral (32k SentencePiece — deliberately the smallest vocabulary, which fragments English the most and is the worst case for a shorthand).

| A2AL vs Markdown (lower = fewer tokens) | GPT-3.5/4 | GPT-4o | Llama 3 | Mistral |
|---|---|---|---|---|
| Real office traffic (header included) | 0.77× | 0.77× | 0.77× | 0.76× |
| The abandoned /0.3.0 JSON envelope | 1.96× | 1.99× | 1.97× | 2.02× |

The saving is **flat across all four** — it's a property of the format, not the model. And the JSON envelope's 2× penalty reproduced everywhere too, so killing it was the right call on every tokenizer, not just ours. The honest caveats: Claude's actual tokenizer is proprietary and still unmeasured, and on very short messages the mandatory header can push A2AL *above* Markdown — which is fine, because on those messages you're paying for legibility, not compression.

## Wrong turn #3: thinking you can grow a protocol on a social feed

We also tried to drive adoption by posting about A2AL on an agent social platform — thousands of AI agents, surely some would pick it up. The structural result was decisive and worth stating plainly: **agent social platforms are fire-and-forget.** Agents engage a post once while it's fresh in the feed, then never return — not even to a named, direct reply. There are no persistent threads, so there's no place to build the sustained back-and-forth that adopting a standard actually requires. Propagation is reach-gated, and reach is unmanufacturable. A social feed is a discovery surface, not an adoption channel. Vocabulary adoption turned out to be *downstream* of virality, and virality isn't something you can engineer.

## Where this leaves A2AL

A2AL is the **payload / body-language layer** for agent communication: the compact vocabulary of state and intent that rides *inside* whatever transport your agents already use — an MCP data part, a Google A2A `Message.Part`, a webhook body, a file in an inbox. It doesn't compete with those transports any more than a shared vocabulary competes with the postal service. It composes with them. And it isn't a software protocol: the example above happens to be a dev handoff, but the header, the audience rule and the vocabulary are built for any two agents coordinating work, whether that's a facility go-live, a campaign launch or a sprint. Software is one worked domain, not the reference one.

Three things we'd tell anyone building in this space:

1. **Measure before you structure.** Our instinct toward a typed envelope was exactly backwards; a token counter caught it and nothing else would have.
2. **Legibility beats compression.** The durable value is a parseable record of what each agent meant — the byte savings are a side effect.
3. **A format's efficiency has to generalize across tokenizers, or it isn't real.** One-tokenizer numbers are a red flag; make the multi-tokenizer table part of the claim.

A2AL is open source (Apache-2.0) at [github.com/mcornelison/A2AL](https://github.com/mcornelison/A2AL). The spec is a few pages, the vocabulary is contributable YAML, and there's no runtime to install.

---

*A2AL is pre-1.0. Tokenizer-level cross-LLM parity is shown; the next milestone is a non-Claude agent emitting and consuming A2AL end-to-end. If you run agents on a non-Claude model and want to try it, that's the experiment we most want to see.*
