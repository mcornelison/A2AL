# I built a JSON format for agents to talk to each other, measured it, and deleted it

*A field report on getting AI agents to communicate efficiently, and the three things that turned out to matter. I didn't expect any of them going in.*

## The setup

When you run more than one AI agent and they have to coordinate, they talk to each other the same way they talk to you: in fluent, padded, human-shaped prose. "Hi Tamsin, just wanted to give you a quick update: US-713 is now complete, all acceptance criteria are met, CI is green, and the PR is ready for your review whenever you get a chance." That sentence is about 35 tokens, and maybe 8 of them carry signal. Multiply that by every handoff in a multi-agent workflow and a real share of your token budget goes on politeness and framing that no agent needs.

A2AL (Agent-to-Agent *Language*) started as my attempt to fix that. The fix itself is less interesting than how wrong my first instinct was, and what the measurements made me admit.

## Wrong turn #1: the envelope

If you come from an API background, the obvious move is to define a structured wire format. So /0.3.0 was a JSON envelope: typed fields, composable sections, a schema, a validator. It was clean, parseable and professional-looking.

Then I measured it against the plain Markdown it was supposed to replace.

The envelope cost **2× to 8× more tokens than just writing Markdown.** On short messages it was terrible: an 8× blowup on a three-word acknowledgement, because the structure was so much bigger than the content. The JSON keys, the braces and the quoting all cost tokens, and none of it is signal. I'd built a format that made the exact problem I was trying to solve *worse.*

So I deleted it. /0.4.0 threw out the envelope entirely and became a plain-text shorthand: one routing header line, then a short body drawn from an open vocabulary the LLM already knows. No JSON and no parser. The message above becomes:

```
from=Tamsin(DEV); to=Wren(PM); date=2026-05-13; topic=US-713 closeout; audience=agent
US-713 done; AC met; CI green; PR ready -- merge?
```

## Wrong turn #2: thinking compression was the point

I assumed the win was the smaller message. It wasn't. The first agent to use A2AL in real work told me **the routing header was more valuable than the body shorthand**, and everything since has backed that up. Readers on an agent social platform picked up the header and ignored the body. A six-agent fleet that nobody asked kept the header on about 99% of its notes while writing the body in plain Markdown. A five-agent estate kept it on all 632 messages over four months. They didn't keep it because it's shorter. On a tiny message it's pure overhead. They kept it because it gives every message a stable structure you can grep: who, to whom, when and about what, in one line. Tooling can route on it, archives can scan it, and a reader can rebuild the context without parsing prose.

That changed how I saw the whole project. A2AL is a convention for making agent messages easy to read and route, and its body also happens to be cheaper. I'd been treating it as a compression scheme with a header attached, and I had that backwards. The compression is a bonus. The legibility is what people actually use.

## The number I had to correct

For a long time my headline claim was that A2AL cost "~0.26× the tokens of Markdown", a 74% reduction. When I re-ran the corpus carefully, that number didn't reproduce anywhere. It turned out to be a transcription error. 0.26 was the *saving fraction* (≈26% fewer), which is a **0.74× cost ratio**, not 0.26×. The honest number is less exciting: about a **quarter fewer tokens** on real traffic, header included. I'd rather publish a number that holds up when a reader tries to reproduce it.

## The measurement that actually mattered: does it generalize?

Every efficiency number I had was measured on one tokenizer, OpenAI's `cl100k_base`, which I'd also been using as a stand-in for Claude's (unpublished) tokenizer. A fair critic would ask first whether this is just a quirk of one BPE vocabulary. If A2AL only saves tokens on the tokenizer I tested it on, it's a parlor trick.

So I ran the same agent-traffic corpus through four independent tokenizers: GPT-3.5/4 (cl100k), GPT-4o (o200k), Llama 3 (128k BPE) and Mistral (32k SentencePiece). I picked Mistral on purpose because it has the smallest vocabulary, which breaks English into the most pieces and is the worst case for a shorthand.

| A2AL vs Markdown (lower = fewer tokens) | GPT-3.5/4 | GPT-4o | Llama 3 | Mistral |
|---|---|---|---|---|
| Real office traffic (header included) | 0.77× | 0.77× | 0.77× | 0.76× |
| The abandoned /0.3.0 JSON envelope | 1.96× | 1.99× | 1.97× | 2.02× |

The saving is **flat across all four**, so it comes from the format, not the model. The JSON envelope's 2× penalty showed up on every tokenizer too, so dropping it was the right call everywhere, not just on the one I'd been using. The caveats: Claude's actual tokenizer is proprietary and still unmeasured, and on very short messages the required header can push A2AL *above* Markdown. I'm fine with that, because on those messages you're paying for legibility, not compression.

## Wrong turn #3: thinking you can grow a protocol on a social feed

I also tried to drive adoption by posting about A2AL on an agent social platform. With thousands of AI agents there, I figured some would pick it up. The result was clear, so I'll just say it: **agent social platforms are fire-and-forget.** Agents engage with a post once while it's fresh in the feed and never come back, not even to a direct reply addressed to them by name. There are no persistent threads, so there's nowhere for the ongoing back-and-forth that adopting a standard needs. How far a post spreads depends on reach, and you can't manufacture reach. A social feed is a place to be discovered, not a place to get adopted. Vocabulary adoption turned out to depend on going viral first, and going viral isn't something you can engineer.

## Where this leaves A2AL

A2AL is the **payload / body-language layer** for agent communication: a compact vocabulary of state and intent that travels *inside* whatever transport your agents already use, whether that's an MCP data part, a Google A2A `Message.Part`, a webhook body or a file in an inbox. It doesn't compete with those transports any more than a shared vocabulary competes with the postal service. It works alongside them. It also isn't only for software. The example above happens to be a dev handoff, but the header, the audience rule and the vocabulary are built for any two agents coordinating work, whether that's a facility go-live, a campaign launch or a sprint. Software is one domain I've worked through, and it isn't meant to be the template for the others.

What I'd tell anyone building in this space:

1. **Measure before you structure.** My instinct toward a typed envelope was exactly backwards. A token counter caught it, and nothing else would have.
2. **Legibility beats compression.** What lasts is a record you can parse of what each agent meant. The token savings come along with it.
3. **A format's efficiency has to hold across tokenizers, or it isn't real.** Numbers from one tokenizer are a red flag. Make the multi-tokenizer table part of the claim.

A2AL is open source (Apache-2.0) at [github.com/mcornelison/A2AL](https://github.com/mcornelison/A2AL). The spec is a few pages, the vocabulary is YAML you can contribute to, and there's no runtime to install.

---

*A2AL is pre-1.0. I've shown parity across LLM tokenizers. The next milestone is a non-Claude agent writing and reading A2AL end to end. If you run agents on a non-Claude model and want to try it, that's the experiment I most want to see.*
