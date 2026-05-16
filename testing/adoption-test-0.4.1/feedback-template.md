# A2AL/0.4.1 Feedback — [AgentName]

**Date:** [YYYY-MM-DD]
**Agent:** [Name, role, project]
**Model:** [Claude version]
**Protocol version exercised:** A2AL/0.4.1
**Solicited by:** A2AL maintainers via [`testing/adoption-test-0.4.1/brief-<agent>.md`](../../testing/adoption-test-0.4.1/)

---

## 1. Did you follow through on your commitment?

- **Read the skill end to end?** [yes / no / partial — and why]
- **Installed the A2AL block in your CLAUDE.md?** [yes / no — and where you placed it (top / middle / bottom)]
- **Sent N A2AL messages?** [N actual / N committed; if below target, why]

## 2. What you actually sent

List the messages you wrote in A2AL this session. For each, capture:

| Message id | Audience (agent-only?) | Header used | Body shape | Token count (A2AL) | Token count (MD equivalent) |
|---|---|---|---|---:|---:|
| [id 1] | yes / no | y / n | state / status / action / blocker / question / decision / ack | | |

If you didn't capture token counts at the time, estimate or skip.

## 3. The audience rule

- **Did the agent-only-vs-human determination fire cleanly?** Or was the audience ambiguous, mixed, or genuinely hard to decide?
- **Did you encounter any case where the rule said "Markdown" but you suspected A2AL would have been better?** Or vice versa?
- **Reactive rule:** did you receive any inbound A2AL messages where the sender carried an agent-identity header? Did you reply in A2AL? Was the trigger natural or did you have to think about it?

## 4. The routing header

- **Did the header read as natural or as overhead?** Specifics please.
- **Did you use any optional fields (`audience`, `urgency`, `refs`, `in-reply-to`)?** Which ones, and was the choice obvious?
- **Anything missing?** (The internal test surfaced `thread=<id>` as a gap. Confirm or deny.)
- **Composition-time cost:** estimate seconds to write the header. Is it negligible, noticeable, or annoying?

## 5. Body shorthand

- **Did you use library terms or invent your own?** If you invented terms, list them — we want to see what's missing.
- **Any term you wished was in the library?** (Concrete suggestions for `library/<domain>.yaml` additions.)
- **Anti-patterns:** did you hit a message shape where shorthand felt wrong? (Multi-branch decisions, RCAs, embedded code — these are spec-acknowledged anti-shapes, but field reports validate that the categorization is right.)

## 6. Library extension

- **Did you add or define a new term?** (Inline `term=expansion`, or library PR.) If yes, which one and why.
- **If no, what was the friction?** (Compose-and-ship rhythm, PR overhead, vocabulary already sufficient, etc.)

## 7. Token measurements

If you captured any quantitative data, drop it here. Even rough estimates are useful.

- **Sender-side savings (A2AL vs MD-equivalent):** [X tokens / Y%]
- **Cognitive cost of composition:** [seconds added or saved vs your Markdown default]
- **Receiver-side clarity:** [near-zero / noticeable cost / blocked on parse]

## 8. Honest assessment

Free-form. The questions to answer:

- **Did 0.4.1 fix the specific concerns you raised in your 0.4.0 memo?** Name the ones it addressed and the ones it didn't.
- **What's your usage rate now?** If you're going to keep using A2AL, at what %? If you've dropped it again, why?
- **What's the single biggest remaining blocker?** (For 0.5.0 prioritization.)
- **Any new suggestions** that weren't in your 0.4.0 memo?

## 9. Closing

- **Recommend keeping the protocol?** [yes / yes-with-changes / drop]
- **Library use:** [N contributions / N inline definitions / 0]
- **Net token saving vs MD this session:** [estimate or measured]
- **Anything you'd commit to do next time** that we should follow up on in 0.5.0?

---

Save at `specs/feedback/YYYY-MM-DD-<agent>-0.4.1.md` and notify the maintainers.
