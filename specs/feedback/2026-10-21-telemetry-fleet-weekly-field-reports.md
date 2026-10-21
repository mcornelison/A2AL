# A2AL Feedback -- a 6-agent Claude Code fleet, weekly field reports 2026-09-22 .. 2026-10-21

**Date:** 2026-10-21
**Reporter:** the PM agent (Marcus) of a 6-agent Claude Code fleet on a hobby automotive-telemetry project. Roles: architect (Atlas), PM (Marcus), tuning SME (Spool), developer (Ralph, headless loop), UI (Iris), QA.
**Model:** Claude (Opus family), all agents
**Protocol versions exercised:** A2AL/0.4.1 mirror until 2026-10-15 (SME) / 2026-10-19 (rest of fleet), then A2AL/0.5.0
**Solicited by:** the project owner, as a standing weekly "comment pass" started 2026-09-22: every office is asked each week for positive, negative or neutral A2AL observations, and "nothing to report" must list what the office did write, so no friction can be told apart from no use.
**Disposition:** compiled from the offices' own notes. Quotes are real messages with project detail redacted (`<story>`, `<sprint>`, `<path>`). Numbers are as the reporting agent measured them; "recalled" is marked where it applies.

---

## Why this file exists

Most of these reports were already filed as GitHub issues (#6 to #20 and comments on #6, #7, #10, #11, #15). This file is the archive copy, kept next to the earlier field reports in `specs/feedback/`, and it does three things the issues cannot:

1. **One index** of every report, from every office, from the first pass to today, with where each one went.
2. **The roll-up**, including the "nothing to report" weeks and usage counts, which never became issues.
3. **The items that were reported to the PM but never filed** (section 4), in full.

---

## 1. Headline findings (all weeks, all offices)

1. **The routing header is adopted almost totally. The terse body is not.** The architect measured 79/79 (2026-09-22), 138/140 (2026-10-01), 22/22 (week of 10-12) and 59/59 (week of 10-19) of its notes carrying the header on line 1. Nearly every body is Markdown: evidence tables, verbatim strings, reasoning a human also reads. The fleet uses **A2AL as the envelope and Markdown as the payload**. → #6
2. **`topic=` keeps absorbing the verdict.** Every agent that measured it found the same pattern: the median is a fine label, the tail is a paragraph (max 804 chars). When an agent caps its topic, the verdict moves into the filename slug instead. → #7
3. **The fields that earn their keep:** `to=`/`cc=` (#9), `in-reply-to=` (#13, #14), `refs=` (section 4.1), `urgency=` plus a trailing "Blocks X." line (#20), and numbered item ids in the body (#15).
4. **The gaps agents filled with prose:** corrections (#10), void conditions (#11), relays to headless agents (#12), message ids (#13), blocking approvals (#16), silence-means-default (#18), per-recipient asks (#9).
5. **Threading took hold once it was spec'd and visible.** The architect's `in-reply-to=` use went from 1 of 22 notes (week of 10-12) to 48 of 59 (week of 10-19). (section 4.4)

---

## 2. Participation roll-up

| Week of | Architect (Atlas) | SME (Spool) | UI (Iris) | Developer (Ralph) | PM (Marcus) | QA |
|---|---|---|---|---|---|---|
| 09-22 | 5 items (79/79 header) | #1: 5 items | no report (quiet office) | 1 report (upgrade + 2 views) | 1 standing neutral (superseded, see 3.6) | no report |
| 09-29 | 3 items (138/140 header) | #2: 6 items (1 day late) | no report (quiet office) | -- | filed #6-#13 on 10-07 | no report |
| 10-05 | 1 item (16/16 header) | none (no session ran) | no report (quiet office) | -- | -- | no report |
| 10-12 | **nothing to report**: 22 notes, 22/22 header, topic median 86 / max 200, `in-reply-to` 1/22 | #3: 4 items + 1 local (7 days late) | 3 items, ~22 A2AL notes written | not asked (sprint running) | filed #14-#17 + comments | no report |
| 10-19 | 2 items + 1 positive; 59/59 header, `in-reply-to` 48/59 | #4 (10-15): 6 items; #5 (10-19): 4 items | 2 items, 8 inbox notes + ~8 live-pipe messages | -- | filed #18-#20 + comments | no report |

**Process note (neutral, about running a feedback loop, not the protocol):** a weekly pass only fires if a session boots. The SME's report was 7 days late once because no session ran for ten days; a cloud scheduler cannot help, because it cannot reach the share the inboxes live on. The ledger habit (append the observation the moment it happens, and make the weekly send a read of the ledger) is what made the architect's numbers measured rather than recalled.

---

## 3. Every report and where it went

### 3.1 Architect (Atlas)

| Date | Kind | Subject | Where |
|---|---|---|---|
| 09-22 | neutral | header + Markdown body on 79/79 notes; name the hybrid | #6 |
| 09-22 | neutral | `topic=` carries a summary; the tail is the evidence (p90 622, max 804) | #7 |
| 09-22 | neutral | `audience=mixed` is the honest label for the hybrid; fold into #6 | #6 |
| 09-22 | negative | example names are unmarked archetype placeholders | #8 |
| 09-22 | positive | `to=`/`cc=` split routed two notes with no body read | #9 |
| 09-29 | positive + gap | two recipients, two actions; proposed `ask=` | #9 |
| 09-29 | neutral | bodies get longer as rulings get more load-bearing | #6 |
| 09-29 | neutral | 138/140 header; both misses are human-facing documents | #6 |
| 10-05 | positive + neutral | `in-reply-to=` closed every merge loop; message id undefined, proposed `id=` | #13 |
| 10-12 | nothing to report | usage listed (section 2) | this file only |
| 10-19 | negative (mild) | topic median 86 → 149 in a week; proposed `verdict=`/`tldr=` | comment on #7 |
| 10-19 | neutral | silence-means-default has no term; proposed `default=` + `by=` | #18 |
| 10-19 | positive | header parsed the same over a file drop and a live session pipe | #19 |
| 10-19 | positive | `in-reply-to=` uptake 1/22 → 48/59 | **section 4.4 (not filed)** |

### 3.2 SME (Spool)

| Date | Kind | Subject | Where |
|---|---|---|---|
| 09-22 | positive | `refs=` makes "which items does this touch" a grep, and survives archiving | **section 4.1 (not filed)** |
| 09-22 | negative | skill content changed with no version bump | **section 4.2 (not filed)** |
| 09-22 | negative | `cc=` used daily but undefined; cost a real miss | 0.5.0 now defines `cc=`; residual in **section 4.3** |
| 09-22 | neutral | library path base unstated | not filed: the path was in this fleet's local mirror text, not upstream |
| 09-22 | neutral | evidence-bearing traffic stays Markdown; a ruling cannot be separated from its corpus | #6 |
| 09-30 | negative | `audience=mixed` read as agent-only; invented `audience=human+agent` 3 times | #6 (0.5.0 later clarified it; SME withdrew 10-15) |
| 09-30 | negative | no field to mark a correction | #10 |
| 09-30 | neutral | proposed `void_if=` | #11 |
| 09-30 | neutral | proposed `relay=` | #12 |
| 09-30 | neutral | Markdown better for verbatim artefacts and human-read proposals | #6 |
| 09-30 | positive | verdict-first `topic=` made an urgent correction fast to act on (anecdote) | #7 |
| 10-13 | positive | comma-list `in-reply-to=` with two parents worked before it was spec'd | #14 |
| 10-13 | negative | `audience=agent` while a human is cc'd, 4th instance | comment on #6 |
| 10-13 | negative | section-level supersede: `supersedes=<msg>#<section>` | comment on #10 |
| 10-13 | neutral | Markdown right for a review read by a human decider | comment on #6 |
| 10-13 | (not A2AL) | a dead path in the project's own docs | not filed: project-local |
| 10-15 | positive | `refs=` with file:line + evidence path: 0 follow-ups on 4/4 ruling threads | **section 4.1 (not filed)** |
| 10-15 | negative (self) | own topics ran 120-200 chars; proposed soft cap ~60 | **section 4.5 (not filed)**, related #7 |
| 10-15 | neutral | `# <n>.` section markers in multi-ruling bodies, cited back as §n | **section 4.6 (not filed)**, related #15 |
| 10-15 | neutral | live session pings in plain prose; durable copy in the inbox | #19 |
| 10-15 | positive | 0.5.0 closes `audience=mixed` and specs `cc=` | recorded here |
| 10-15 | mirror defect | the fleet's own text said cite "0.5.1"; upstream tag is v0.5.0 | not filed: our mirror was wrong; see 4.2 |
| 10-19 | positive | "VOID IF" + `# n.` sections: 7/7 folded, 0 follow-ups | comment on #11 |
| 10-19 | negative (self) | capped topic → verdict moved to the slug | comment on #7 |
| 10-19 | neutral | supports `default=`; keep distinct from VOID IF | #18 |
| 10-19 | neutral | live ping + inbox file worked 7/7 | #19 |

### 3.3 UI (Iris)

| Date | Kind | Subject | Where |
|---|---|---|---|
| 10-13 | positive/neutral | numbered `ASK-n` ids made multi-ask replies addressable | #15 |
| 10-13 | neutral | no term for a blocking approval; proposed `ratify` | #16 |
| 10-13 | negative | `refs=` lists of 10+ ids make the header unreadable | #17 |
| 10-20 | negative (self) | header over Markdown prose, 8/8 notes; asks for a `body=prose` marker | comment on #6 |
| 10-20 | positive | `urgency=` + trailing "Blocks X." made triage one read | #20 |

### 3.4 Developer (Ralph)

| Date | Kind | Subject | Where |
|---|---|---|---|
| 09-22 | negative | the kit's examples were de-branded to archetype names | #8 |
| 09-22 | neutral | `audience=mixed` is correct as-is; needs one line on which dialect wins | **section 4.7 (not filed)** |
| 09-22 | negative | `topic=` wants a `summary=`; his own note's topic ran ~430 chars | #7 |
| 09-22 | neutral | Markdown body under an A2AL header is what real traffic looks like | #6 |

### 3.5 QA

No report in any week.

### 3.6 PM (Marcus)

| Date | Kind | Subject | Where |
|---|---|---|---|
| 09-22 | neutral | "most of our agent traffic is Markdown, not A2AL" | **not filed as written.** The architect measured 79/79 header adoption and refuted the framing. The corrected version is #6. |

---

## 4. Reports never filed as issues

### 4.1 Positive: `refs=` makes triage a grep, and it is the field that survives archiving (SME, 09-22 and 10-15)

**Version:** A2AL/0.4.1. Real headers, redacted:

```text
refs=<item>,<item>,<item>,<item>,<item>,<item>,<item>,<item>,<item>,<item>
```

```text
from=Spool(tuner); to=Atlas(architect); cc=Marcus(pm); date=2026-10-13; topic=TEXT for <spec> battery gate :87 + :381 + :373; ...; refs=<story>,<rule>,<rule>,<ticket>,<ticket>,<evidence-file>.md
```

- **What it saved (09-22):** the note changed the state of three items in a running sprint. With `refs=`, "which of my items does this touch" became a grep, not a read. The recipient sorted ten ids without opening a 6 KB note. It is also the only field that is still useful after archiving: every note that ever touched one item can be found without full-text search.
- **What it saved (10-15):** refs carrying a `file:line` and an evidence path. 0 follow-up questions on 4 of 4 ruling threads. The receivers folded the rulings straight from the refs.
- **Relation to #17:** #17 (long refs lists are unreadable) is the same field's cost. Both hold. The value is in the ids; the cost is in the header's one-line scan. A rule that moves the tail of a long list into the body (as #17 proposes) keeps both.

### 4.2 Negative: a mirror cannot tell that it is stale (SME, 09-22; repeated 10-15)

**Version:** A2AL/0.4.1 before and after.

- **What happened:** the fleet's copy of the skill went from 189 lines to 206, gaining a new section, with the version string unchanged and no date in the file. Six offices ran a stale copy for an unknown period. The only way to detect it was a byte-compare of every office against the source.
- **Repeated in a different form, 10-15:** the fleet's text told agents to cite `A2AL/0.5.1`. Upstream's latest tag is `v0.5.0`, the spec and skill say `A2AL/0.5.0`, and the README marks 0.5.1 "in progress". The upstream state is consistent; our mirror read the latest commit title as a release. It still shows that a consumer has no cheap answer to "which version am I on, and is it current?"
- **Expected:** a one-line check.
- **Proposal (either):** bump the version on any normative change to the skill text, or put a machine-readable stamp in the skill file, e.g. `<!-- a2al-skill: 0.5.0+2026-06-11 -->`. Either turns staleness detection into one comparison.

### 4.3 Negative, mostly resolved: `cc=` semantics (SME, 09-22)

**Version:** A2AL/0.4.1. Real header, redacted:

```text
from=Atlas(architect); to=Marcus(pm); cc=<owner>, Spool(tuner), <qa>; date=2026-09-22; topic=... PLUS the <story> sigma ruling you asked for ...
```

- **What happened:** the note carried a ruling on a question addressed to the SME six minutes earlier. The SME was `cc`, read it as awareness only, and did not act; two items stayed blocked overnight.
- **What 0.5.0 fixed:** §3.2 now defines `cc=` as *"Informational (copy) recipients"*. That answers the main question.
- **What is still open:** (a) does `audience=agent` bind `cc` recipients, or only `to`? (b) when the body answers a `cc` recipient's own open question, should the sender have put that recipient in `to=`? The fleet now uses a local rule, which the SME wrote into a later note: *"A ruling or action aimed at someone belongs in `to=`, never `cc=`."* One sentence like that in §3.2 would close it.

### 4.4 Positive: `in-reply-to=` adoption jumped once the reply partner used it (architect, week of 10-19)

**Measured from the architect's outbox:** `in-reply-to=` on **1 of 22** notes (10-08..10-12), then **48 of 59** (10-13..10-19). Its inbox the same week: 21 of 48. The architect's mirror was still 0.4.1 that week, so this was habit, not a spec change: the PM had been threading every merge confirmation back to its ready note (see #13), and the architect picked it up.

- No action requested. It is evidence that the field spreads when the reply partner models it.

### 4.5 Negative (self): a soft length cap for `topic=` (SME, 10-15)

**Version:** A2AL/0.4.1. Real topic, redacted:

```text
topic=WARNINGS <story>/<story>/<story> domain rulings: STOP = coolant only; RPM + battery reds = WATCH; dwell/clear; words; stored codes never STOP
```

- **Expected:** a length guide in the style guide. **What happened:** the SME's topics ran 120-200 chars and duplicated the filename slug, which already carries the long form. In a file-drop channel the filename is a second subject line.
- **Proposal:** a soft cap (~60 chars) in the style guide for `topic=`. The SME's follow-up (10-19, comment on #7) shows the cost: with the cap held, the verdict moved into the slug. So a cap works only if the verdict gets its own home (#7's `summary=`/`verdict=`).

### 4.6 Neutral: `# <n>.` section markers in multi-ruling bodies (SME, 10-15)

- Notes carrying 4-6 independent rulings used `# 1.`, `# 2.` headings. Receivers cited them back by number ("§3"), and the PM's acknowledgements restated each item by number.
- The style guide says nothing about structuring a body with several independent decisions.
- **Proposal:** allow `# <n>.` section markers in the body guide. It is the section-level form of #15's item ids, and it is what a section-level `supersedes=<msg>#<n>` (comment on #10) would point at.

### 4.7 Neutral: when a `mixed` message's two dialects conflict, which wins? (developer, 09-22)

- The headless developer's stop notes genuinely have two readers: a human checking whether the loop died, and the PM parsing what it did. Writing the content twice is worse, so `audience=mixed` is the honest label.
- **Proposal:** one line of guidance for `mixed`: *the human reader wins on structure (the body); A2AL wins on the header.* That is what this fleet does in practice (see #6).

---

## 5. Index of what is already upstream from this fleet

| Issue | Kind | Subject |
|---|---|---|
| #6 | neutral + negative | header-over-Markdown hybrid vs §2.1 "no hybrid mode"; `audience=mixed` (+ 2 comments) |
| #7 | neutral | `summary=` header field (+ 1 comment: `verdict=`) |
| #8 | negative | example names are unmarked placeholders |
| #9 | positive + gap | `to=`/`cc=` triage; `ask=` |
| #10 | negative | `corrects=`/`supersedes=` (+ 2 comments: section- and item-level) |
| #11 | neutral | `void_if=` (+ 1 comment: VOID IF 7/7) |
| #12 | neutral | `relay=` for headless recipients |
| #13 | positive + neutral | `in-reply-to=` closed merge loops; `id=` |
| #14 | positive | comma-list `in-reply-to=` before 0.5.0 |
| #15 | positive | numbered body item ids (+ 1 comment) |
| #16 | neutral | `ratify` |
| #17 | negative | long `refs=` lists |
| #18 | neutral | `default=` + `by=` |
| #19 | positive | transport independence; ping + durable file |
| #20 | positive | `urgency=` + "Blocks X." |
