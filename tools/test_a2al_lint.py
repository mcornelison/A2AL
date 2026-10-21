"""Tests for a2al_lint.py.

Stdlib only, same shape as test_a2al_preview.py: no pytest, prints one OK line
per case, exits 1 if anything failed.

Run: python tools/test_a2al_lint.py
"""
from __future__ import annotations

import contextlib
import io
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import a2al_lint as A  # noqa: E402
import a2al_preview as P  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent

_failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"OK: {name}")
    else:
        print(f"FAIL: {name}{(' -- ' + detail) if detail else ''}", file=sys.stderr)
        _failures.append(name)


def levels(findings, level):
    return [m for lv, m in findings if lv == level]


def has(findings, level, needle):
    return any(needle in m for m in levels(findings, level))


def run_main(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = A.main(argv)
    return code, out.getvalue()


GOOD = "from=Ledger(PM); to=Byte(DEV); date=2026-09-22; topic=US-713 closeout; audience=agent"

# --------------------------------------------------------------------------


def test_clean_header() -> None:
    f = A.lint_header(GOOD, "US-713 done; AC met; CI green -- merge?")
    check("clean header has no findings", f == [], str(f))
    f = A.lint_header("from=Kunai/DW-Arch; to=Byte(DEV), Hawkeye(QA); date=2026-05-13T15:30Z; topic=t")
    check("Name/Role, multi-recipient and datetime are clean", f == [], str(f))


def test_shared_field_lists() -> None:
    check("reuses a2al_preview's required fields", A.KNOWN_FIELDS >= set(P._REQUIRED_HEADER))
    check("supersedes is a known optional field (0.5.2)", "supersedes" in P._OPTIONAL_HEADER)
    f = A.lint_header(GOOD + "; supersedes=msg-41#2, msg-40")
    check("supersedes= raises no warning", f == [], str(f))


def test_no_header() -> None:
    f = A.lint_header("Hi Byte, quick update on US-713.")
    check("prose on line 1 is an ERROR", has(f, A.ERROR, "no routing header"), str(f))
    f = A.lint_header("")
    check("blank line 1 is an ERROR", has(f, A.ERROR, "blank"), str(f))


def test_missing_required() -> None:
    f = A.lint_header("from=A(X); to=B(Y); topic=t")
    check("missing date is an ERROR", has(f, A.ERROR, "missing required field 'date'"), str(f))
    f = A.lint_header("from=A(X); to=; date=2026-01-01; topic=t")
    check("empty to= is an ERROR", has(f, A.ERROR, "'to' is empty"), str(f))


def test_keyless_segment() -> None:
    # The real case: topic text containing '; ' splits into a bogus field.
    f = A.lint_header("from=A(X); to=B(Y); date=2026-06-18; topic=gate red; auth regression")
    check("'; ' inside topic is an ERROR",
          has(f, A.ERROR, "has no key -- is there a '; ' inside a value?"), str(f))


def test_duplicate_key() -> None:
    f = A.lint_header(GOOD + "; to=C(Z)")
    check("duplicate key is an ERROR", has(f, A.ERROR, "duplicate key 'to'"), str(f))
    f = A.lint_header(GOOD + "; Topic=x")
    check("duplicate key is case-insensitive", has(f, A.ERROR, "duplicate key 'topic'"), str(f))


def test_continuation_line() -> None:
    f = A.lint_header(GOOD, "cc=Audrey(SEC); thread=US-713")
    check("cc= on line 2 is an ERROR", has(f, A.ERROR, "a strict reader drops cc= on line 2"), str(f))
    f = A.lint_header(GOOD, "US-713 done; thread=US-713")
    check("'; thread=' inside line 2 is an ERROR", has(f, A.ERROR, "thread="), str(f))
    f = A.lint_header(GOOD, "deadline=2026-05-09T17:00; ASK=pick A|B")
    check("body key=value with unknown keys is not a continuation", f == [], str(f))
    f = A.lint_header(GOOD, None)
    check("header-only message is fine", f == [], str(f))


def test_dates() -> None:
    for d in ("2026-05-13", "2026-05-13T15:30Z", "2026-05-13T15:30:05+02:00", "2026-05-13T15:30"):
        f = A.lint_header(f"from=A(X); to=B(Y); date={d}; topic=t")
        check(f"date {d} accepted", f == [], str(f))
    for d in ("13/05/2026", "2026-13-01", "2026-02-30", "May 13", "2026-05-13 15:30", "2026-05-13T25:00Z"):
        f = A.lint_header(f"from=A(X); to=B(Y); date={d}; topic=t")
        check(f"date {d!r} rejected", has(f, A.ERROR, "ISO 8601"), str(f))


def test_unknown_field_is_warning() -> None:
    f = A.lint_header(GOOD + "; provenance=moltbook://post/8812")
    check("unknown field is a WARN, not an ERROR",
          has(f, A.WARN, "'provenance'") and not levels(f, A.ERROR), str(f))
    check("unknown-field warning says it is preserved", has(f, A.WARN, "preserve"), str(f))


def test_value_sets() -> None:
    f = A.lint_header("from=A(X); to=B(Y); date=2026-01-01; topic=t; audience=human; "
                      "urgency=asap; priority=P5")
    check("bad audience warns", has(f, A.WARN, "agent|mixed"), str(f))
    check("bad urgency warns", has(f, A.WARN, "low|medium|high|urgent"), str(f))
    check("bad priority warns", has(f, A.WARN, "P0|P1|P2|P3"), str(f))
    check("value-set problems are never errors", not levels(f, A.ERROR), str(f))


def test_long_topic() -> None:
    f = A.lint_header("from=A(X); to=B(Y); date=2026-01-01; topic=" + "x" * 61)
    check("61-char topic warns", has(f, A.WARN, "keep topic a label"), str(f))
    f = A.lint_header("from=A(X); to=B(Y); date=2026-01-01; topic=" + "x" * 60)
    check("60-char topic is fine", f == [], str(f))


def test_refs_count() -> None:
    f = A.lint_header(GOOD + "; refs=a, b, c, d")
    check("4 refs warns", has(f, A.WARN, "body `refs:` line"), str(f))
    f = A.lint_header(GOOD + "; refs=a, b, c")
    check("3 refs is fine", f == [], str(f))


def test_party_shape() -> None:
    f = A.lint_header("from=Ledger; to=Byte(DEV), hawkeye qa; cc=Audrey(SEC), x; date=2026-01-01; topic=t")
    check("bare from name warns", has(f, A.WARN, "from='Ledger'"), str(f))
    check("bad second to recipient warns", has(f, A.WARN, "to='hawkeye qa'"), str(f))
    check("bad cc recipient warns", has(f, A.WARN, "cc='x'"), str(f))


def test_markdown_inputs() -> None:
    block_md = ("# Note\n\nSome prose for the human.\n\n```a2al\n" + GOOD +
                "\nUS-718 blocked\n```\n")
    check("md with clean a2al block passes", A.lint_text(block_md, markdown=True) == [])
    bad_block = "# Note\n\n```a2al\nfrom=A(X); to=B(Y); topic=t\n```\n"
    f = A.lint_text(bad_block, markdown=True)
    check("md a2al block is linted, finding names the block",
          has(f, A.ERROR, "'date'") and has(f, A.ERROR, "a2al block at line 4"), str(f))
    header_md = GOOD + "\n\n## Context\n\nMarkdown body under an A2AL header.\n"
    check("md with header on line 1 is linted normally", A.lint_text(header_md, markdown=True) == [])
    f = A.lint_text("# Just Markdown\n\n```text\n" + GOOD + "\n```\n", markdown=True)
    check("md with no header and no a2al block is an ERROR", has(f, A.ERROR, "no routing header"), str(f))
    f = A.lint_text("# Prose\n\n```a2al\n" + GOOD + "\n```\n", markdown=False)
    check("a2al block fallback applies to .md only", has(f, A.ERROR, "no routing header"), str(f))
    check("BOM before the header is tolerated", A.lint_text("﻿" + GOOD) == [])


def test_cli() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        good = tmp / "good.txt"
        good.write_text(GOOD + "\nbody\n", encoding="utf-8")
        warn = tmp / "warn.txt"
        warn.write_text(GOOD + "; frobnicate=yes\nbody\n", encoding="utf-8")
        bad = tmp / "bad.txt"
        bad.write_text("hello\n", encoding="utf-8")

        code, out = run_main([str(good)])
        check("cli: clean file exits 0", code == 0, out)
        check("cli: prints a summary", "1 file(s) checked: 0 error(s), 0 warning(s)" in out, out)

        code, out = run_main([str(warn)])
        check("cli: warnings alone exit 0", code == 0, out)
        check("cli: finding format is 'path: LEVEL: message'", f"{warn}: WARN: unknown field" in out, out)

        code, _ = run_main(["--strict", str(warn)])
        check("cli: --strict makes warnings exit 1", code == 1)

        code, out = run_main([str(bad), str(good)])
        check("cli: an error exits 1", code == 1, out)

        code, out = run_main(["--quiet", str(warn), str(bad)])
        check("cli: --quiet hides warnings and keeps errors",
              "WARN" not in out and f"{bad}: ERROR:" in out, out)

        code, out = run_main([str(tmp / "missing.txt")])
        check("cli: unreadable file is an ERROR", code == 1 and "cannot read" in out, out)

        old = sys.stdin
        sys.stdin = io.StringIO(GOOD + "\ncc=X(Y)\n")
        try:
            code, out = run_main(["-"])
        finally:
            sys.stdin = old
        check("cli: '-' reads stdin", code == 1 and "<stdin>: ERROR: line 2" in out, out)


def test_repo_examples() -> None:
    txt = sorted((REPO / "examples").glob("*.txt"))
    errors = [(p.name, m) for p in txt for lv, m in A.lint_path(str(p)) if lv == A.ERROR]
    check("every examples/*.txt is lint-error-free", txt and not errors, str(errors[:3]))


def main() -> int:
    test_clean_header()
    test_shared_field_lists()
    test_no_header()
    test_missing_required()
    test_keyless_segment()
    test_duplicate_key()
    test_continuation_line()
    test_dates()
    test_unknown_field_is_warning()
    test_value_sets()
    test_long_topic()
    test_refs_count()
    test_party_shape()
    test_markdown_inputs()
    test_cli()
    test_repo_examples()

    if _failures:
        print(f"\n{len(_failures)} failure(s): {', '.join(_failures)}", file=sys.stderr)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
