"""Tests for a2al_lookup.py.

Stdlib only, same shape as the other suites in this directory.

The test that matters most is `test_parser_agrees_with_pyyaml`. a2al_lookup.py
reads the library with a hand-rolled line parser so it needs no dependency.
That's only safe if the parser agrees with the real YAML parser. When PyYAML is
available the two are compared entry by entry; when it is not, that case skips.

Run: python tools/test_a2al_lookup.py
"""
from __future__ import annotations

import io
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import a2al_lookup as L  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
LIB = REPO / "library"

_failures: list[str] = []
_skipped = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"OK: {name}")
    else:
        print(f"FAIL: {name}{(' -- ' + detail) if detail else ''}", file=sys.stderr)
        _failures.append(name)


def skip(name: str, why: str) -> None:
    global _skipped
    _skipped += 1
    print(f"SKIP: {name} ({why})")


def run_cli(argv: list[str]) -> int:
    real, sys.stdout = sys.stdout, io.StringIO()
    try:
        return L.main(argv)
    finally:
        sys.stdout = real


# --------------------------------------------------------------------------

def test_parser_agrees_with_pyyaml() -> None:
    """The dependency-free parser must not drift from the real YAML parser."""
    try:
        import yaml
    except ImportError:
        skip("parser agrees with PyYAML", "PyYAML not installed")
        return

    mine = {}
    for e in L.load_library(LIB):
        mine[(e["domain"], e["term"])] = e

    theirs = {}
    for f in sorted(LIB.glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        for e in data["entries"]:
            theirs[(data["domain"], e["term"])] = e

    check("parser: same entry count as PyYAML",
          len(mine) == len(theirs), f"{len(mine)} vs {len(theirs)}")
    check("parser: same set of (domain, term) keys",
          set(mine) == set(theirs),
          f"only-mine={sorted(set(mine) - set(theirs))[:5]} "
          f"only-theirs={sorted(set(theirs) - set(mine))[:5]}")

    mismatched = [
        k for k in set(mine) & set(theirs)
        if mine[k].get("expansion") != theirs[k].get("expansion")
    ]
    check("parser: expansions match PyYAML byte for byte",
          not mismatched, str(mismatched[:5]))


def test_load_library() -> None:
    entries = L.load_library(LIB)
    check("load_library: reads the real library", len(entries) > 100, str(len(entries)))
    check("load_library: every entry has term and expansion",
          all(e.get("term") and e.get("expansion") for e in entries))
    check("load_library: every entry is tagged with its domain",
          all(e.get("domain") for e in entries))
    domains = {e["domain"] for e in entries}
    check("load_library: finds all seven domains", len(domains) == 7, str(sorted(domains)))
    check("load_library: domain matches filename stem",
          domains == {f.stem for f in LIB.glob("*.yaml")}, str(sorted(domains)))


def test_parse_edge_cases() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "sample.yaml"
        p.write_text(
            "# a comment\n"
            "domain: sample\n"
            "description: A sample domain for tests.\n"
            "\n"
            "entries:\n"
            "  # states\n"
            "  - term: alpha\n"
            "    expansion: first letter\n"
            '    example: "alpha done"\n'
            "  - term: beta\n"
            "    expansion: second letter\n"
            "    notes: has no example\n",
            encoding="utf-8",
        )
        domain, entries = L.parse_library_file(p)
        check("parse: reads the domain key", domain == "sample", domain)
        check("parse: skips comments and blank lines", len(entries) == 2, str(entries))
        check("parse: strips quotes from values",
              entries[0]["example"] == "alpha done", str(entries[0]))
        check("parse: keeps optional fields", entries[1]["notes"] == "has no example")
        check("parse: entry without optional field is fine",
              "example" not in entries[1], str(entries[1]))


def test_search() -> None:
    entries = L.load_library(LIB)
    hits = L.search(entries, "identity")
    check("search: finds entries by expansion text", len(hits) >= 3, str(len(hits)))
    check("search: results carry their domain", all(h.get("domain") for h in hits))

    exact = L.search(entries, "ack")
    check("search: exact term match ranks first",
          exact and exact[0]["term"].lower() == "ack", str(exact[:1]))
    check("search: no match returns empty", L.search(entries, "zzzqqq") == [])


def test_check_candidate() -> None:
    entries = L.load_library(LIB)

    r = L.check_candidate(entries, "ack")
    check("check: exact canonical term is reported",
          r["exact"] is not None and r["exact"]["term"] == "ack", str(r["exact"]))

    r = L.check_candidate(entries, "hotfx")
    terms = [n["entry"]["term"] for n in r["near_misses"]]
    check("check: near-miss catches a typo of a real term", "hotfix" in terms, str(terms))
    check("check: near-misses are sorted by similarity descending",
          all(r["near_misses"][i]["similarity"] >= r["near_misses"][i + 1]["similarity"]
              for i in range(len(r["near_misses"]) - 1)))

    r = L.check_candidate(entries, "DR", "design-review")
    overlap = [o["entry"]["term"] for o in r["meaning_overlap"]]
    check("check: meaning overlap finds an existing term with the same sense",
          any(t in overlap for t in ("CR", "review")), str(overlap))

    r = L.check_candidate(entries, "zzqqxx", "entirely unrelated nonsense phrase")
    check("check: a genuinely novel term comes back clear",
          r["exact"] is None and not r["near_misses"], str(r))


def test_cli() -> None:
    check("cli: stats exits 0", run_cli(["stats"]) == 0)
    check("cli: list exits 0", run_cli(["list"]) == 0)
    check("cli: list --domain exits 0", run_cli(["list", "--domain", "core"]) == 0)
    check("cli: list --domain rejects an unknown domain",
          run_cli(["list", "--domain", "nope"]) == 1)
    check("cli: search with a hit exits 0", run_cli(["search", "identity"]) == 0)
    check("cli: search with no hit exits 1", run_cli(["search", "zzzqqq"]) == 1)

    # `check` uses its exit code as the signal: 1 = something already covers
    # this, 0 = clear to coin. That is what makes it scriptable.
    check("cli: check on a canonical term exits 1", run_cli(["check", "ack"]) == 1)
    check("cli: check on a novel term exits 0",
          run_cli(["check", "zzqqxx", "entirely unrelated nonsense"]) == 0)

    check("cli: --json is accepted", run_cli(["--json", "stats"]) == 0)


def main() -> int:
    for fn in (
        test_parser_agrees_with_pyyaml,
        test_load_library,
        test_parse_edge_cases,
        test_search,
        test_check_candidate,
        test_cli,
    ):
        fn()

    print()
    if _failures:
        print(f"{len(_failures)} failure(s): {', '.join(_failures)}", file=sys.stderr)
        return 1
    print(f"All checks passed ({_skipped} skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
