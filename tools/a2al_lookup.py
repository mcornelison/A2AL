"""A2AL library lookup.

Two agents reported the same gap in specs/feedback/: the library exists, and
neither of them ever opened it. Ledger -- "I have not actually consulted
library/*.yaml during composition" -- and Claude, who asked for "a list of the
concepts that have already been added, so I see what's there before writing
duplicates" and "a 'Did you mean...' reflex when I'm about to invent a new
term". Both had zero library contributions. Curation that nobody reads is
curation that is not paying off.

This makes the library cheap to consult at composition time:

  search <query>        find terms by term, expansion, example or notes
  check <candidate>     before you coin a shortening -- is it already covered?
  list [--domain X]     what is in here
  stats                 entry counts per domain

Stdlib only, deliberately. Needing `pip install` before you can check a word is
exactly the friction that produced the zero-consultation finding. The strict
schema check lives in validate_library.py (which does use PyYAML and runs in
CI); this reads the same files with a small parser and stays instantly runnable
anywhere the repo is checked out.

Run: python tools/a2al_lookup.py check design-review
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import sys

DEFAULT_LIBRARY = "library"

# The library files have a flat, regular shape that validate_library.py
# enforces in CI, so a line parser is sufficient and needs no YAML dependency:
#
#   entries:
#     - term: done
#       expansion: complete or finished
#       example: "US-713 done"
#
_ENTRY_START = re.compile(r"^\s*-\s+(\w+)\s*:\s*(.*)$")
_ENTRY_FIELD = re.compile(r"^\s+(\w+)\s*:\s*(.*)$")
_DOMAIN_LINE = re.compile(r"^domain\s*:\s*(.*)$")


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_library_file(path: pathlib.Path) -> tuple[str, list[dict]]:
    """Parse one library/*.yaml. Returns (domain, entries)."""
    domain = path.stem
    entries: list[dict] = []
    current: dict | None = None
    in_entries = False

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        m = _DOMAIN_LINE.match(raw)
        if m:
            domain = _unquote(m.group(1)) or domain
            continue

        if re.match(r"^entries\s*:", raw):
            in_entries = True
            continue
        if not in_entries:
            continue

        m = _ENTRY_START.match(raw)
        if m:
            if current:
                entries.append(current)
            current = {m.group(1): _unquote(m.group(2))}
            continue

        m = _ENTRY_FIELD.match(raw)
        if m and current is not None:
            current[m.group(1)] = _unquote(m.group(2))

    if current:
        entries.append(current)

    for e in entries:
        e["domain"] = domain
    return domain, entries


def load_library(library_dir: pathlib.Path) -> list[dict]:
    """All entries across every domain file, in filename order."""
    if not library_dir.is_dir():
        print(f"ERROR: not a directory: {library_dir}", file=sys.stderr)
        sys.exit(1)
    out: list[dict] = []
    for f in sorted(library_dir.glob("*.yaml")):
        try:
            _, entries = parse_library_file(f)
        except OSError as e:
            print(f"WARN: could not read {f}: {e}", file=sys.stderr)
            continue
        out.extend(entries)
    return out


# --------------------------------------------------------------------------
# search
# --------------------------------------------------------------------------

_SEARCH_FIELDS = ("term", "expansion", "example", "notes")


def search(entries: list[dict], query: str) -> list[dict]:
    """Substring match across term/expansion/example/notes, best field first."""
    q = query.lower()
    scored = []
    for e in entries:
        best = None
        for rank, field in enumerate(_SEARCH_FIELDS):
            value = e.get(field, "")
            if q in value.lower():
                exact = value.lower() == q
                best = (0 if exact else 1, rank)
                break
        if best is not None:
            scored.append((best, e))
    scored.sort(key=lambda s: (s[0], s[1]["term"].lower()))
    return [e for _, e in scored]


# --------------------------------------------------------------------------
# check -- the "did you mean" reflex
# --------------------------------------------------------------------------

_STOPWORDS = {"a", "an", "the", "of", "or", "and", "to", "in", "for", "is", "be"}


def check_candidate(entries: list[dict], candidate: str, expansion: str | None = None,
                    cutoff: float = 0.72) -> dict:
    """Is a proposed shortening already covered by the library?

    Three passes, cheapest first: exact term, near-miss term, and meaning
    overlap against existing expansions. The last is what catches the real
    duplicate -- coining `DR=design-review` when `design-review` already sits
    in some entry's expansion.
    """
    cand = candidate.strip().lower()
    by_term = {e["term"].lower(): e for e in entries}

    exact = by_term.get(cand)

    near = []
    for term, e in by_term.items():
        if term == cand:
            continue
        ratio = difflib.SequenceMatcher(None, cand, term).ratio()
        if ratio >= cutoff:
            near.append({"entry": e, "similarity": round(ratio, 3)})
    near.sort(key=lambda n: -n["similarity"])

    # Meaning overlap: compare the candidate's expansion (or the candidate
    # itself, if no expansion was given) against every entry's expansion.
    meaning_source = (expansion or candidate).lower()
    words = {w for w in re.split(r"[^a-z0-9]+", meaning_source) if w and w not in _STOPWORDS}
    overlap = []
    if words:
        for e in entries:
            exp = e.get("expansion", "").lower()
            if not exp:
                continue
            exp_words = {w for w in re.split(r"[^a-z0-9]+", exp) if w and w not in _STOPWORDS}
            if not exp_words:
                continue
            shared = words & exp_words
            if shared:
                score = len(shared) / len(words | exp_words)
                overlap.append({"entry": e, "score": round(score, 3),
                                "shared": sorted(shared)})
    overlap.sort(key=lambda o: -o["score"])

    return {
        "candidate": candidate,
        "expansion": expansion,
        "exact": exact,
        "near_misses": near[:5],
        "meaning_overlap": [o for o in overlap if o["score"] >= 0.3][:5],
    }


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def _fmt(e: dict, indent: str = "  ") -> str:
    line = f"{indent}{e['term']:<16} {e.get('expansion', '')}"
    tail = f"{indent}{'':<16} [{e.get('domain', '?')}]"
    if e.get("example"):
        tail += f'  e.g. "{e["example"]}"'
    return line + "\n" + tail


def cmd_search(args) -> int:
    entries = load_library(pathlib.Path(args.library_dir))
    hits = search(entries, args.query)
    if args.json:
        print(json.dumps({"query": args.query, "count": len(hits), "results": hits}, indent=2))
        return 0 if hits else 1
    if not hits:
        print(f"No entry matches {args.query!r} across {len(entries)} entries.")
        print("If you need it, add it to the right library/<domain>.yaml, then run")
        print("  python tools/validate_library.py")
        return 1
    print(f"{len(hits)} match(es) for {args.query!r}:\n")
    for e in hits[:args.limit]:
        print(_fmt(e))
        print()
    if len(hits) > args.limit:
        print(f"... and {len(hits) - args.limit} more (--limit to widen)")
    return 0


def cmd_check(args) -> int:
    entries = load_library(pathlib.Path(args.library_dir))
    r = check_candidate(entries, args.candidate, args.expansion)

    if args.json:
        print(json.dumps(r, indent=2))
        return 1 if (r["exact"] or r["near_misses"] or r["meaning_overlap"]) else 0

    if r["exact"]:
        print(f"ALREADY CANONICAL -- {args.candidate!r} is in the library.\n")
        print(_fmt(r["exact"]))
        print()
        print("Use it as-is. Do not redefine a canonical term inline (spec section 6.5).")
        return 1

    if r["near_misses"]:
        print(f"NEAR MISS -- nothing is spelled {args.candidate!r}, but this is close:\n")
        for n in r["near_misses"]:
            print(_fmt(n["entry"]))
            print(f"  {'':<16} similarity {n['similarity']}")
            print()

    if r["meaning_overlap"]:
        print("ALREADY COVERED? -- existing entries expand to something similar:\n")
        for o in r["meaning_overlap"]:
            print(_fmt(o["entry"]))
            print(f"  {'':<16} shares: {', '.join(o['shared'])}")
            print()

    if not r["near_misses"] and not r["meaning_overlap"]:
        print(f"CLEAR -- nothing in the library ({len(entries)} entries) covers "
              f"{args.candidate!r}.\n")
        print("Before coining it, check spec section 6.4: define a shortening only if you")
        print("will use it 3+ times in this thread. Fewer than that, spell it out.")
        print()
        print("If it earns a place, introduce it inline on first use:")
        exp = args.expansion or "<expansion>"
        print(f"  {args.candidate}={exp}. ...")
        print()
        print("A shortening used 5+ times across threads is a library PR candidate")
        print("(spec section 6.6).")
        return 0

    print("If none of these fit, coining a new shortening is reasonable -- see")
    print("spec section 6.4 for the 3-uses threshold.")
    return 1


def cmd_list(args) -> int:
    entries = load_library(pathlib.Path(args.library_dir))
    if args.domain:
        entries = [e for e in entries if e.get("domain") == args.domain]
        if not entries:
            print(f"No domain named {args.domain!r}.", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(entries, indent=2))
        return 0
    if args.terms_only:
        print(" ".join(sorted(e["term"] for e in entries)))
        return 0
    by_domain: dict[str, list[dict]] = {}
    for e in entries:
        by_domain.setdefault(e.get("domain", "?"), []).append(e)
    for domain in sorted(by_domain):
        rows = sorted(by_domain[domain], key=lambda e: e["term"].lower())
        print(f"== {domain} ({len(rows)}) ==")
        for e in rows:
            print(f"  {e['term']:<16} {e.get('expansion', '')}")
        print()
    return 0


def cmd_stats(args) -> int:
    entries = load_library(pathlib.Path(args.library_dir))
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.get("domain", "?")] = counts.get(e.get("domain", "?"), 0) + 1
    if args.json:
        print(json.dumps({"total": len(entries), "by_domain": counts}, indent=2))
        return 0
    width = max(len(d) for d in counts) if counts else 10
    for d in sorted(counts):
        print(f"  {d:<{width}}  {counts[d]:>4}")
    print(f"  {'TOTAL':<{width}}  {len(entries):>4}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="a2al_lookup.py",
        description="Make the A2AL vocabulary library cheap to consult while composing.",
    )
    p.add_argument("--library-dir", default=DEFAULT_LIBRARY,
                   help=f"directory of *.yaml library files (default: {DEFAULT_LIBRARY})")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_s = sub.add_parser("search", help="find terms by term, expansion, example or notes")
    p_s.add_argument("query")
    p_s.add_argument("--limit", type=int, default=20)
    p_s.set_defaults(func=cmd_search)

    p_c = sub.add_parser("check", help="before coining a shortening -- is it already covered?")
    p_c.add_argument("candidate")
    p_c.add_argument("expansion", nargs="?", default=None,
                     help="what you meant by it; sharpens the meaning-overlap check")
    p_c.set_defaults(func=cmd_check)

    p_l = sub.add_parser("list", help="list entries, optionally for one domain")
    p_l.add_argument("--domain")
    p_l.add_argument("--terms-only", action="store_true",
                     help="space-separated terms only, for piping")
    p_l.set_defaults(func=cmd_list)

    p_t = sub.add_parser("stats", help="entry counts per domain")
    p_t.set_defaults(func=cmd_stats)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
