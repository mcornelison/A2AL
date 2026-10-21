"""A2AL composition-time preview.

Two agents, independently, asked me the same thing before they'd adopt A2AL:
what does it actually buy me on THIS message, before I pay the cost of writing
it? This tool answers that.

Three subcommands:

  scan <draft.md>              Audit a Markdown draft for the padding A2AL drops
                               (spec section 4.1) and report how compressible it is.
  compare <draft.md> <msg.txt> Token counts for both renderings, the ratio, the
                               savings, and a verdict against a threshold.
  count <file> [...]           Token count per file.

Token counting
--------------
Everything runs without dependencies. Install tiktoken for a sharper answer:

    pip install tiktoken

No tokenizer is "exact" for Claude. Anthropic's vocabulary is not published,
so cl100k_base is the long-standing proxy (testing/tools/CROSS-LLM-RESULTS.md).
What makes the conclusion safe is that the A2AL/Markdown ratio held at 0.73-0.84
across four tokenizers, so it does not hinge on which one you pick. Use
--encoder to count with another (o200k_base, etc.).

`scan` is fine on the stdlib heuristic. It reports a *share within one
document* (padding tokens over total tokens, both counted the same way), so
the error cancels. Verified across this repo's corpus: the reported share moves
by at most 0.6 percentage points versus cl100k_base.

`compare` is different, because it divides one rendering by another and the
heuristic's error does NOT cancel across formats: measured on this corpus it
under-counts A2AL by ~9% and over-counts Markdown prose by ~2%, inflating the
ratio by ~11%. That is enough to report a real 26% saving as 34% and cross a 30%
threshold the wrong way. So without a tokenizer `compare` reports a +/-12 point
band instead of a point estimate, and returns "inconclusive" (exit 3) when the
threshold falls inside it. It doesn't guess.

This tool validates nothing about message shape. A2AL never validates messages,
by design. Only the library is validated (tools/validate_library.py). The
header check in `compare` is an advisory conformance note, not a gate.

Run: python tools/a2al_preview.py scan draft.md
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
import unicodedata

# --------------------------------------------------------------------------
# Token counting
# --------------------------------------------------------------------------

_TIKTOKEN_ENCODING = "cl100k_base"

# How far a heuristic-derived A2AL/Markdown ratio can be off, as a fraction.
# Measured against cl100k_base over this repo's corpus: the heuristic
# under-counts A2AL ~9% and over-counts Markdown prose ~2%, inflating the ratio
# ~11%. Rounded up. `compare` reports a band this wide rather than a crisp
# verdict when running without a real tokenizer.
_HEURISTIC_BAND = 0.12

# Splits text into BPE-ish chunks: a run of word characters (with any leading
# whitespace attached, which is how byte-pair encoders merge it), or a single
# non-word character.
_CHUNK_RE = re.compile(r"\s*\w+|\s*[^\w\s]|\s+")

# Word runs up to _FREE_CHARS cost one token; longer runs cost one more per
# _EXTRA_CHARS beyond that. Fitted against cl100k_base over this repo's corpus.
_FREE_CHARS = 12
_EXTRA_CHARS = 5


def estimate_tokens(text: str) -> int:
    """Heuristic token count. No dependencies.

    Charges one token per word run up to _FREE_CHARS, one more per _EXTRA_CHARS
    beyond that, one per punctuation character, and one per ~3 digits (numbers
    fragment more than letters). See the module docstring for measured accuracy
    and for why this is not used to compare two renderings.
    """
    if not text:
        return 0
    total = 0
    for chunk in _CHUNK_RE.findall(text):
        stripped = chunk.strip()
        if not stripped:
            continue  # pure whitespace merges into the next chunk
        if not stripped.isalnum() and len(stripped) == 1:
            total += 1
            continue
        if stripped.isdigit():
            total += max(1, math.ceil(len(stripped) / 3))
            continue
        if len(stripped) <= _FREE_CHARS:
            total += 1
        else:
            total += 1 + math.ceil((len(stripped) - _FREE_CHARS) / _EXTRA_CHARS)
    return total


def get_counter(encoding: str = _TIKTOKEN_ENCODING) -> tuple[callable, str, bool]:
    """Return (count_fn, backend_label, measured).

    `measured` is True when a real tokenizer is doing the counting and False
    when the stdlib heuristic is. Callers whose output depends on the
    difference must branch on it. This never exits on its own.

    No tokenizer here is "exact" for Claude: Anthropic's vocabulary is not
    published, so `cl100k_base` is the long-standing proxy (see
    testing/tools/CROSS-LLM-RESULTS.md). What makes that OK is that the
    A2AL/Markdown ratio held at 0.73-0.84 across four tokenizers, so the
    conclusion doesn't hinge on which one you pick.
    """
    try:
        import tiktoken
    except ImportError:
        return estimate_tokens, "stdlib heuristic (no tokenizer installed)", False

    try:
        enc = tiktoken.get_encoding(encoding)
    except Exception as e:  # unknown name, or vocab fetch needs network
        return estimate_tokens, f"stdlib heuristic ({encoding} unavailable: {e})", False

    return (lambda s: len(enc.encode(s))), f"tiktoken/{encoding}", True


# --------------------------------------------------------------------------
# Padding scan: spec section 4.1 "Drops"
# --------------------------------------------------------------------------

# (category, compiled pattern, note). Patterns are case-insensitive and matched
# on word boundaries so they do not fire inside identifiers or code.
_PADDING = [
    (
        "articles",
        re.compile(r"\b(the|a|an)\b", re.I),
        "1 token each; usually carries no signal between agents",
    ),
    (
        "linking verbs",
        re.compile(r"\b(is|are|was|were|has been|have been|will be)\b", re.I),
        "often droppable in declarative state: 'US-713 is done' -> 'US-713 done'",
    ),
    (
        "subjective framing",
        re.compile(
            r"\b(i think|i believe|i feel|we think|we believe|it seems|it appears|"
            r"in my opinion|arguably|presumably|probably worth|i'd say)\b",
            re.I,
        ),
        "bias signal, not information",
    ),
    (
        "politeness",
        re.compile(
            r"\b(please|thanks|thank you|kindly|could you|would you mind|"
            r"if you don't mind|whenever you get a chance|feel free|no rush|"
            r"sorry to bother|hope this helps|let me know if)\b",
            re.I,
        ),
        "inter-agent politeness is wasted tokens",
    ),
    (
        "filler",
        re.compile(
            r"\b(in order to|due to the fact that|at this point in time|"
            r"it is important to note that|it's worth noting that|just wanted to|"
            r"i wanted to|quick update|basically|actually|really|very|quite|"
            r"sort of|kind of|a bit of|going forward|as you know)\b",
            re.I,
        ),
        "pure padding",
    ),
    (
        "greetings / sign-off",
        re.compile(
            r"(^|\n)\s*(hi|hey|hello|good morning|good afternoon|dear)\b"
            r"|\b(best regards|regards|cheers|thanks again|talk soon)\b",
            re.I,
        ),
        "routing header carries sender/recipient; greetings duplicate it",
    ),
]


def scan_padding(text: str, count) -> dict:
    """Find droppable padding. Returns a report dict."""
    findings = []
    recoverable = 0
    for category, pattern, note in _PADDING:
        hits = [m.group(0).strip() for m in pattern.finditer(text)]
        if not hits:
            continue
        cost = sum(count(h) for h in hits)
        recoverable += cost
        # Preserve first-seen order, de-duplicated, for a readable sample.
        seen, sample = set(), []
        for h in hits:
            low = h.lower()
            if low not in seen:
                seen.add(low)
                sample.append(h)
        findings.append(
            {
                "category": category,
                "count": len(hits),
                "est_tokens": cost,
                "note": note,
                "sample": sample[:6],
            }
        )
    total = count(text)
    findings.sort(key=lambda f: -f["est_tokens"])
    return {
        "total_tokens": total,
        "padding_tokens": recoverable,
        "padding_share": (recoverable / total) if total else 0.0,
        "findings": findings,
    }


# --------------------------------------------------------------------------
# Routing header: spec section 3
# --------------------------------------------------------------------------

_REQUIRED_HEADER = ["from", "to", "date", "topic"]
_OPTIONAL_HEADER = [
    "audience", "urgency", "refs", "in-reply-to",
    "thread", "status", "cc", "priority", "evidence", "a2al",
]


def parse_header(first_line: str) -> dict | None:
    """Parse line 1 as a routing header. Returns field map, or None if it isn't one."""
    if "=" not in first_line:
        return None
    fields = {}
    for part in first_line.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        fields[key.strip().lower()] = value.strip()
    # A header must carry at least one required field to be recognised as one.
    if not any(k in fields for k in _REQUIRED_HEADER):
        return None
    return fields


def check_header(text: str) -> dict:
    """Advisory conformance note on the routing header."""
    first = text.lstrip("\n").split("\n", 1)[0].strip()
    fields = parse_header(first)
    if fields is None:
        return {
            "present": False,
            "missing": _REQUIRED_HEADER,
            "optional_used": [],
            "unknown": [],
        }
    return {
        "present": True,
        "missing": [f for f in _REQUIRED_HEADER if f not in fields],
        "optional_used": [f for f in _OPTIONAL_HEADER if f in fields],
        "unknown": [k for k in fields if k not in _REQUIRED_HEADER and k not in _OPTIONAL_HEADER],
    }


# --------------------------------------------------------------------------
# Shape detection: spec section 7 patterns
# --------------------------------------------------------------------------

_SHAPES = [
    ("blocker", re.compile(r"\bblocked\b\s*:", re.I)),
    ("decision", re.compile(r"^\s*(approved|rejected|chose|decided|selected)\b\s*:", re.I | re.M)),
    ("acknowledgment", re.compile(r"^\s*ack\b", re.I | re.M)),
    ("question / ask", re.compile(r"\?\s*$", re.M)),
    ("status report", re.compile(r"\b\d+\s*/\s*\d+\b")),
    # Directive verbs span industries on purpose: a delivery agent says "merge",
    # a programme agent says "escalate", a field agent says "inspect". Keeping
    # this list software-only made A2AL read as a software-only protocol.
    ("action directive", re.compile(
        r"^\s*(merge|deploy|ship|revert|run|fix|patch|update"            # delivery
        r"|review|verify|validate|inspect|audit|confirm"                 # assurance
        r"|approve|reject|sign-off|escalate|assign|schedule|reschedule"  # governance
        r"|submit|file|issue|send|notify|publish|procure|order"          # process
        r"|hold|release|close|reopen|prioritize|defer)\b",
        re.I | re.M)),
    ("multi-fact state", re.compile(r";")),
]


def detect_shapes(body: str) -> list[str]:
    """Which spec section 7 patterns the body appears to use. Advisory only."""
    found = [name for name, pattern in _SHAPES if pattern.search(body)]
    return found or ["single-fact state change (or unrecognised)"]


# --------------------------------------------------------------------------
# Anti-patterns: spec section 4.4
# --------------------------------------------------------------------------

# Matches `  - term: foo` in library/*.yaml without needing PyYAML.
_TERM_RE = re.compile(r"^\s*-\s*term:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", re.M)

# Punctuation the spec actively uses; anything else non-ASCII is suspect.
_OK_NON_ASCII = set("—–…")

# A word run, but never the letter part of an ID like US-713 or T-202.
_WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z']*\b(?!-?\d)")


def load_library_terms(library_dir: pathlib.Path) -> set[str]:
    """Read sanctioned terms from library/*.yaml. Regex-based; no PyYAML needed."""
    terms: set[str] = set()
    if not library_dir.is_dir():
        return terms
    for f in sorted(library_dir.glob("*.yaml")):
        try:
            terms.update(m.group(1).strip().lower() for m in _TERM_RE.finditer(
                f.read_text(encoding="utf-8")))
        except OSError:
            continue
    return terms


def check_antipatterns(body: str, count, library_dir: pathlib.Path) -> dict:
    """Flag spec section 4.4 anti-patterns that cost tokens rather than saving them.

    Uses the tokenizer as the judge: a short word that costs more than one
    token isn't something the vocabulary handles well. If it's also missing
    from the library, it's an invented abbreviation. That's the case the spec
    warns about, where the full word would have been cheaper.
    """
    terms = load_library_terms(library_dir)

    unicode_hits = {}
    for ch in body:
        if ord(ch) > 127 and ch not in _OK_NON_ASCII:
            unicode_hits[ch] = unicode_hits.get(ch, 0) + 1

    abbrev = []
    seen = set()
    for m in _WORD_RE.finditer(body):
        w = m.group(0)
        low = w.lower()
        if low in seen or low in terms or len(w) > 7 or len(w) < 3:
            continue
        seen.add(low)
        cost = count(" " + w)
        if cost > 1:
            abbrev.append({"token": w, "cost": cost})

    return {
        "rare_unicode": [
            {
                "char": c,
                "codepoint": f"U+{ord(c):04X}",
                "name": unicodedata.name(c, "unnamed"),
                "count": n,
                "cost": count(c),
            }
            for c, n in sorted(unicode_hits.items(), key=lambda kv: -kv[1])
        ],
        "invented_abbreviations": sorted(abbrev, key=lambda a: -a["cost"]),
        "library_terms_loaded": len(terms),
    }


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def _read(path: str) -> str:
    return pathlib.Path(path).read_text(encoding="utf-8")


def _bar(fraction: float, width: int = 28) -> str:
    filled = max(0, min(width, round(fraction * width)))
    return "#" * filled + "." * (width - filled)


def cmd_scan(args) -> int:
    count, backend, _ = get_counter(args.encoder)
    text = _read(args.file)
    report = scan_padding(text, count)

    if args.json:
        report["file"] = args.file
        report["backend"] = backend
        print(json.dumps(report, indent=2))
        return 0

    share = report["padding_share"]
    print(f"Draft:     {pathlib.Path(args.file).name}")
    print(f"Tokens:    {report['total_tokens']}  [{backend}]")
    print(f"Padding:   {report['padding_tokens']} tokens ({share:.0%})  {_bar(share)}")
    print()

    if not report["findings"]:
        print("No droppable padding matched. This draft is already terse -- A2AL's")
        print("style rules would recover little. The routing header may still be worth it.")
    else:
        print("Droppable per spec section 4.1:")
        print()
        for f in report["findings"]:
            print(f"  {f['category']:<22} {f['count']:>3}x  ~{f['est_tokens']:>4} tok   {f['note']}")
            print(f"  {'':<22}      {', '.join(f['sample'])}")
            print()

    print("-" * 72)
    if share >= 0.20:
        print(f"Compressible: ~{share:.0%} of this draft is padding A2AL drops mechanically.")
    elif share >= 0.08:
        print(f"Marginal: ~{share:.0%} padding. Body shorthand buys little here.")
    else:
        print(f"Not compressible: ~{share:.0%} padding. Body shorthand is not the win.")
    print()
    print("Compressibility does NOT decide the format. The audience rule does")
    print("(spec section 2.1): agent-only -> A2AL MUST; human anywhere in the")
    print("audience -> Markdown, however compressible this draft is.")
    return 0


def cmd_compare(args) -> int:
    count, backend, measured = get_counter(args.encoder)
    md_text = _read(args.markdown)
    a2al_text = _read(args.a2al)

    md_tokens = count(md_text)
    a2al_tokens = count(a2al_text)
    if md_tokens == 0:
        print("ERROR: Markdown side is empty; nothing to compare.", file=sys.stderr)
        return 1

    ratio = a2al_tokens / md_tokens
    saving = 1.0 - ratio

    # Without a real tokenizer the saving carries a known bias, so the verdict
    # is decided on the band rather than the point estimate. A result inside
    # the band is reported as inconclusive rather than guessed at.
    band = 0.0 if measured else _HEURISTIC_BAND
    low, high = saving - band, saving + band
    if measured:
        verdict = "meets" if saving >= args.threshold else "misses"
    elif low >= args.threshold:
        verdict = "meets"
    elif high < args.threshold:
        verdict = "misses"
    else:
        verdict = "inconclusive"
    meets = verdict == "meets"

    header = check_header(a2al_text)
    lines = a2al_text.lstrip("\n").split("\n")
    body = "\n".join(lines[1:]) if header["present"] else a2al_text
    shapes = detect_shapes(body)
    anti = check_antipatterns(body, count, pathlib.Path(args.library_dir))

    if args.json:
        print(json.dumps({
            "markdown": {"file": args.markdown, "tokens": md_tokens},
            "a2al": {"file": args.a2al, "tokens": a2al_tokens},
            "ratio": round(ratio, 4),
            "saving": round(saving, 4),
            "threshold": args.threshold,
            "meets_threshold": meets,
            "verdict": verdict,
            "measured": measured,
            "uncertainty_band": band,
            "saving_range": [round(low, 4), round(high, 4)],
            "header": header,
            "shapes": shapes,
            "antipatterns": anti,
            "backend": backend,
        }, indent=2))
        return {"meets": 0, "misses": 1, "inconclusive": 3}[verdict]

    md_name, a2al_name = pathlib.Path(args.markdown).name, pathlib.Path(args.a2al).name
    width = max(len(md_name), len(a2al_name))
    print(f"Backend:   {backend}")
    print()
    print(f"  Markdown  {md_name:<{width}}  {md_tokens:>6} tok")
    print(f"  A2AL      {a2al_name:<{width}}  {a2al_tokens:>6} tok")
    print()
    print(f"  Ratio     {ratio:.3f}x        {_bar(min(ratio, 1.0))}")
    print(f"  Saving    {saving:+.1%}  ({md_tokens - a2al_tokens:+d} tokens)")
    print()

    print("-" * 72)
    if verdict == "inconclusive":
        print(f"INCONCLUSIVE: saving is {low:.0%}-{high:.0%}, and the {args.threshold:.0%}")
        print("threshold falls inside that range. The stdlib heuristic is not precise")
        print("enough to call this one -- it under-counts A2AL and over-counts Markdown")
        print("prose, which inflates the ratio by roughly 12 points.")
        print()
        print("    pip install tiktoken      # then re-run for a decisive answer")
    elif meets:
        if measured:
            print(f"WORTH IT: {saving:.0%} saving clears the {args.threshold:.0%} threshold.")
        else:
            print(f"WORTH IT: saving is {low:.0%}-{high:.0%}, clearing the "
                  f"{args.threshold:.0%} threshold even at the pessimistic end.")
    elif saving > 0:
        if measured:
            print(f"MARGINAL: {saving:.0%} saving is below the {args.threshold:.0%} threshold.")
        else:
            print(f"MARGINAL: saving is {low:.0%}-{high:.0%}, short of the "
                  f"{args.threshold:.0%} threshold even at the optimistic end.")
        print("The body shorthand is not paying for its composition cost here.")
        print("The routing header may still be worth it on its own (spec section 3.4).")
    else:
        print(f"NEGATIVE: the A2AL rendering costs {-saving:.0%} MORE than the Markdown.")
        print("Check for creative abbreviations or rare Unicode (spec section 4.4) --")
        print("both tokenize worse than the plain word.")
    print()
    if not measured:
        print("Counting with the stdlib heuristic. Ranges above are the measured")
        print("uncertainty, not a confidence interval.")
        print()

    # Advisory conformance notes.
    if not header["present"]:
        print("NOTE: no routing header on line 1. The header is MUST (spec section 3);")
        print("      a message without one is non-conformant.")
    else:
        if header["missing"]:
            print(f"NOTE: routing header is missing required field(s): {', '.join(header['missing'])}")
        if header["unknown"]:
            print(f"NOTE: unrecognised header field(s): {', '.join(header['unknown'])}")
            print("      Unknown fields are preserved-and-ignored by readers, not errors.")
        if header["optional_used"]:
            print(f"      Optional fields used: {', '.join(header['optional_used'])}")
    print(f"      Shape(s) detected: {', '.join(shapes)}")

    if anti["rare_unicode"] or anti["invented_abbreviations"]:
        print()
        print("Anti-patterns (spec section 4.4) -- these COST tokens, they do not save them:")
        for u in anti["rare_unicode"]:
            print(f"      rare Unicode {u['codepoint']} {u['name'].lower()} x{u['count']} "
                  f"-- {u['cost']} tokens each; use ASCII")
        for a in anti["invented_abbreviations"]:
            print(f"      invented abbreviation {a['token']!r} -- {a['cost']} tokens; "
                  f"the full word is usually 1")
        if not anti["library_terms_loaded"]:
            print(f"      (no library found at {args.library_dir}; abbreviation check ran without it)")
    return {"meets": 0, "misses": 1, "inconclusive": 3}[verdict]


def cmd_count(args) -> int:
    count, backend, _ = get_counter(args.encoder)
    rows = [(f, count(_read(f))) for f in args.files]
    if args.json:
        print(json.dumps({
            "backend": backend,
            "files": [{"file": f, "tokens": n} for f, n in rows],
            "total": sum(n for _, n in rows),
        }, indent=2))
        return 0
    names = [pathlib.Path(f).name for f, _ in rows]
    width = max(len(n) for n in names)
    print(f"[{backend}]")
    for name, (_, n) in zip(names, rows):
        print(f"  {name:<{width}}  {n:>6} tok")
    if len(rows) > 1:
        print(f"  {'TOTAL':<{width}}  {sum(n for _, n in rows):>6} tok")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="a2al_preview.py",
        description="Show what A2AL buys on a specific message, before composing it.",
    )
    p.add_argument("--encoder", default=_TIKTOKEN_ENCODING,
                   help=f"tiktoken encoding to count with (default: {_TIKTOKEN_ENCODING}); "
                        "falls back to the stdlib heuristic if unavailable")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="audit a Markdown draft for droppable padding")
    p_scan.add_argument("file")
    p_scan.add_argument("--json", action="store_true")
    p_scan.set_defaults(func=cmd_scan)

    p_cmp = sub.add_parser("compare", help="token counts, ratio and saving for two renderings")
    p_cmp.add_argument("markdown")
    p_cmp.add_argument("a2al")
    p_cmp.add_argument("--threshold", type=float, default=0.30,
                       help="minimum saving to call it worth it (default 0.30)")
    p_cmp.add_argument("--library-dir", default="library",
                       help="library dir used to tell sanctioned terms from invented ones")
    p_cmp.add_argument("--json", action="store_true")
    p_cmp.set_defaults(func=cmd_compare)

    p_cnt = sub.add_parser("count", help="count tokens in one or more files")
    p_cnt.add_argument("files", nargs="+")
    p_cnt.add_argument("--json", action="store_true")
    p_cnt.set_defaults(func=cmd_count)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
