"""Tests for a2al_preview.py.

Stdlib only, same shape as test_validate_library.py: no pytest, prints one OK
line per case, exits 1 on the first failure.

Cases that need exact token counts are skipped when tiktoken is unavailable, so
this suite passes in a bare environment and covers more in CI.

Run: python tools/test_a2al_preview.py
"""
from __future__ import annotations

import io
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import a2al_preview as P  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent

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


def has_tiktoken() -> bool:
    try:
        import tiktoken
        tiktoken.get_encoding(P._TIKTOKEN_ENCODING)
        return True
    except Exception:
        return False


def write(tmp: pathlib.Path, name: str, text: str) -> str:
    p = tmp / name
    p.write_text(text, encoding="utf-8")
    return str(p)


# --------------------------------------------------------------------------

DRAFT = """Hi Byte,

Just wanted to give you a quick update. I think US-713 is now complete -- all of
the acceptance criteria are met, CI is green, and the PR is ready for your review
whenever you get a chance.

Could you please take a look and let me know if you're happy to merge?

Thanks again,
Ledger
"""

GOOD = (
    "from=Ledger(PM); to=Byte(DEV); date=2026-09-22; topic=US-713 closeout; "
    "audience=agent; thread=US-713\n"
    "US-713 done; AC met; CI green; PR ready -- merge?\n"
)

BAD = (
    "from=A(X); to=B(Y); date=2026-09-22; topic=t; frobnicate=yes\n"
    "US-1 cmplt ✓ prgm mrg rdy ⟳ all gud\n"
)


def test_estimate_tokens() -> None:
    check("estimate_tokens: empty string is 0", P.estimate_tokens("") == 0)
    check("estimate_tokens: monotonic in length",
          P.estimate_tokens("a b c d e") > P.estimate_tokens("a b"))
    check("estimate_tokens: punctuation costs tokens",
          P.estimate_tokens("a;b;c") > P.estimate_tokens("abc"))
    long_word = "supercalifragilistic"
    check("estimate_tokens: long words cost more than one",
          P.estimate_tokens(long_word) > 1)


def without_tiktoken():
    """Context manager making `import tiktoken` fail, to exercise the fallback."""
    import contextlib

    @contextlib.contextmanager
    def _cm():
        saved = sys.modules.get("tiktoken", "<absent>")
        sys.modules["tiktoken"] = None  # makes `import tiktoken` raise ImportError
        try:
            yield
        finally:
            if saved == "<absent>":
                sys.modules.pop("tiktoken", None)
            else:
                sys.modules["tiktoken"] = saved
    return _cm()


def test_heuristic_fallback() -> None:
    """get_counter falls back to the heuristic and says so. It never exits."""
    with without_tiktoken():
        fn, backend, measured = P.get_counter()
        check("get_counter: falls back to heuristic", fn is P.estimate_tokens, backend)
        check("get_counter: reports measured=False on the fallback", measured is False)
        check("get_counter: fallback label says heuristic", "heuristic" in backend, backend)

    if has_tiktoken():
        fn, backend, measured = P.get_counter()
        check("get_counter: reports measured=True with a real tokenizer", measured is True)
        check("get_counter: labels the encoding", "cl100k_base" in backend, backend)
        _, backend, measured = P.get_counter("not-a-real-encoding")
        check("get_counter: unknown encoding degrades instead of raising",
              measured is False and "heuristic" in backend, backend)
    else:
        skip("get_counter measured path", "needs tiktoken")


def test_scan_share_is_stable_without_tiktoken() -> None:
    """The claim that justifies letting `scan` use the heuristic.

    `scan` reports a share within ONE document, so the heuristic's bias should
    largely cancel. Measured over the real corpus the reported share must stay
    within one percentage point of the tokenizer's.
    """
    if not has_tiktoken():
        skip("scan share stability", "needs tiktoken for the reference")
        return
    exact, _, _ = P.get_counter()
    worst, worst_file = 0.0, None
    for f in sorted((REPO / "examples").glob("*.txt")) + [
        REPO / "specs" / "feedback" / "2026-05-13-ledger-pm-datawarehouse.md",
        REPO / "CONTRIBUTING.md",
    ]:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        a = P.scan_padding(text, exact)["padding_share"]
        b = P.scan_padding(text, P.estimate_tokens)["padding_share"]
        if abs(b - a) > worst:
            worst, worst_file = abs(b - a), f.name
    check("scan: heuristic share stays within 1 point of the tokenizer's",
          worst <= 0.01, f"worst {worst:.1%} on {worst_file}")


def test_parse_header() -> None:
    h = P.parse_header("from=A(X); to=B(Y); date=2026-09-22; topic=t; thread=US-1")
    check("parse_header: extracts required fields",
          h is not None and h["from"] == "A(X)" and h["topic"] == "t", str(h))
    check("parse_header: extracts optional fields", h.get("thread") == "US-1")
    check("parse_header: rejects a prose line", P.parse_header("US-713 done; AC met") is None)
    check("parse_header: rejects an unrelated key=value line",
          P.parse_header("foo=bar; baz=qux") is None)

    r = P.check_header(GOOD)
    check("check_header: present with no missing fields",
          r["present"] and not r["missing"], str(r))
    check("check_header: reports optional fields used",
          set(r["optional_used"]) == {"audience", "thread"}, str(r))

    r2 = P.check_header("US-713 done\n")
    check("check_header: absent header lists all required as missing",
          not r2["present"] and set(r2["missing"]) == {"from", "to", "date", "topic"})

    r3 = P.check_header("from=A(X); date=2026-09-22\nack\n")
    check("check_header: reports partial header's missing fields",
          set(r3["missing"]) == {"to", "topic"}, str(r3))

    r4 = P.check_header(BAD)
    check("check_header: reports unknown fields", r4["unknown"] == ["frobnicate"], str(r4))

    # The 0.5.1 version field must be recognised, not reported as unknown.
    r5 = P.check_header("from=A(X); to=B(Y); date=2026-09-22; topic=t; a2al=0.5.1\nack\n")
    check("check_header: a2al= is a known optional field",
          "a2al" in r5["optional_used"] and not r5["unknown"], str(r5))


def test_detect_shapes() -> None:
    cases = [
        ("US-718 blocked: no source in Silver", "blocker"),
        ("approved: US-713 PRD -- 1 AC added", "decision"),
        ("ack US-713 closeout", "acknowledgment"),
        ("merge?", "question / ask"),
        ("tests 21/21; preflight 878/878", "status report"),
        ("merge ralph/auth-fix", "action directive"),
        # Directives aren't software-only (0.5.1's industry-neutral theme).
        ("escalate RFI-18 to the authority having jurisdiction", "action directive"),
        ("approve change-order 4", "action directive"),
        ("schedule the site inspection", "action directive"),
        ("notify stakeholder group before go-live", "action directive"),
        ("submit the permit package", "action directive"),
    ]
    for body, expected in cases:
        check(f"detect_shapes: {expected}", expected in P.detect_shapes(body),
              str(P.detect_shapes(body)))
    check("detect_shapes: always returns something",
          len(P.detect_shapes("qqq")) >= 1)


def test_library_terms() -> None:
    terms = P.load_library_terms(REPO / "library")
    check("load_library_terms: reads the real library without PyYAML",
          len(terms) > 100, f"got {len(terms)}")
    for t in ("ack", "hotfix", "spike", "green"):
        check(f"load_library_terms: contains {t!r}", t in terms)
    check("load_library_terms: missing dir returns empty set",
          P.load_library_terms(REPO / "does-not-exist") == set())


def test_scan_padding() -> None:
    report = P.scan_padding(DRAFT, P.estimate_tokens)
    cats = {f["category"] for f in report["findings"]}
    for expected in ("politeness", "filler", "articles", "subjective framing"):
        check(f"scan_padding: finds {expected}", expected in cats, str(cats))
    check("scan_padding: padding share is a sane fraction",
          0.0 < report["padding_share"] < 1.0, str(report["padding_share"]))
    check("scan_padding: findings sorted by cost descending",
          all(report["findings"][i]["est_tokens"] >= report["findings"][i + 1]["est_tokens"]
              for i in range(len(report["findings"]) - 1)))

    terse = P.scan_padding("US-713 done; AC met; CI green", P.estimate_tokens)
    check("scan_padding: terse A2AL body has little padding",
          terse["padding_share"] < 0.15, str(terse["padding_share"]))


def test_antipatterns() -> None:
    if not has_tiktoken():
        skip("antipatterns", "needs tiktoken for the token-cost oracle")
        return
    count, _, _ = P.get_counter()
    lib = REPO / "library"

    anti = P.check_antipatterns(BAD.split("\n", 1)[1], count, lib)
    found = {a["token"] for a in anti["invented_abbreviations"]}
    for t in ("cmplt", "prgm", "mrg", "rdy", "gud"):
        check(f"antipatterns: flags invented {t!r}", t in found, str(found))
    check("antipatterns: does not flag the letters of an ID (US-1)",
          "US" not in found and "US-" not in found, str(found))
    cps = {u["codepoint"] for u in anti["rare_unicode"]}
    check("antipatterns: flags rare Unicode", {"U+2713", "U+27F3"} <= cps, str(cps))

    clean = "US-713 done; ack; hotfix shipped; spike done; CI green; gate passed"
    anti2 = P.check_antipatterns(clean, count, lib)
    check("antipatterns: library terms are not flagged",
          not anti2["invented_abbreviations"],
          str(anti2["invented_abbreviations"]))
    check("antipatterns: clean body has no rare Unicode", not anti2["rare_unicode"])


def run_cli(argv: list[str]) -> int:
    """Invoke main() with stdout captured, so the suite's own output stays readable."""
    real, sys.stdout = sys.stdout, io.StringIO()
    try:
        return P.main(argv)
    finally:
        sys.stdout = real


def test_cli() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        draft = write(tmp, "draft.md", DRAFT)
        good = write(tmp, "good.txt", GOOD)

        rc = run_cli(["scan", draft])
        check("cli: scan exits 0", rc == 0, f"rc={rc}")

        if not has_tiktoken():
            skip("cli compare", "needs tiktoken")
            return

        rc = run_cli(["compare", draft, good, "--threshold", "0.10"])
        check("cli: compare exits 0 when the saving clears the threshold", rc == 0, f"rc={rc}")

        rc = run_cli(["compare", draft, good, "--threshold", "0.99"])
        check("cli: compare exits 1 when it does not", rc == 1, f"rc={rc}")

        # Without a tokenizer the verdict is decided on a band, and a threshold
        # inside that band must come back inconclusive rather than guessed.
        with without_tiktoken():
            rc = run_cli(["compare", draft, good, "--threshold", "0.01"])
            check("cli: heuristic still decides a clear-cut case", rc == 0, f"rc={rc}")

            rc = run_cli(["compare", draft, good, "--threshold", "0.99"])
            check("cli: heuristic still rejects a hopeless case", rc == 1, f"rc={rc}")

            # The measured saving on this pair sits near 23%, so a threshold
            # right on it falls inside the +/-12 band.
            rc = run_cli(["compare", draft, good, "--threshold", "0.23"])
            check("cli: heuristic returns inconclusive (exit 3) inside the band",
                  rc == 3, f"rc={rc}")

        rc = run_cli(["count", draft, good])
        check("cli: count exits 0", rc == 0, f"rc={rc}")

        # An empty Markdown side must error rather than divide by zero.
        empty = write(tmp, "empty.md", "")
        rc = run_cli(["compare", empty, good])
        check("cli: compare rejects an empty baseline", rc == 1, f"rc={rc}")


def main() -> int:
    for fn in (
        test_estimate_tokens,
        test_heuristic_fallback,
        test_scan_share_is_stable_without_tiktoken,
        test_parse_header,
        test_detect_shapes,
        test_library_terms,
        test_scan_padding,
        test_antipatterns,
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
