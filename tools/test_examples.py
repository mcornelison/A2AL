"""Conformance tests for the example corpus.

A2AL never validates messages, by design: agents should be liberal in what
they accept. This suite doesn't change that. It validates *this repository's
own examples*. The examples are documentation, and documentation that
contradicts the spec is a bug.

Four assertions:

  1. Every A2AL message in examples/ carries a conformant routing header
     (spec section 3): required fields present, no unrecognised field names.

  2. Every header field the spec documents appears in at least one example.
     The field list is parsed out of specs/A2A-Core.md sections 3.1 and 3.2, so
     the test can't drift from the spec. Add a field to the spec table
     without using it in an example and this fails.

  3. Every term introduced by a release appears in at least one example.
     I added this after finding that 8 of the 10 terms added in 0.5.0 existed
     only inside the changelog that announced them.

  4. Every message passes tools/a2al_lint.py with no ERROR (warnings are
     allowed, since an unknown field is a warning by design).

Assertions 2 and 3 are the ones that fail on the *next* release, and I want
that. They turn "I shipped a feature" into something CI can check.

Run: python tools/test_examples.py
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import a2al_lint as LINT  # noqa: E402
import a2al_lookup as L  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = REPO / "examples"
SPEC = REPO / "specs" / "A2A-Core.md"
LIBRARY = REPO / "library"

# Terms introduced per release, and which must therefore be demonstrated.
# A whole new domain file is named by "domain:<name>" and expands to every term
# in it. Add a row when a release adds vocabulary.
NEW_IN_RELEASE: dict[str, list[str]] = {
    "0.5.0": [
        "ack", "endorse", "supersede", "superseded", "heads-up",
        "gate", "spike", "hotfix", "PARTIAL", "WITHDRAWN",
        "domain:azure",
    ],
    # 0.5.1 re-scoped project-mgmt from SRE/ops to cross-industry project
    # management. These carry the theme, so they must be demonstrated by
    # examples that are not software, since that's what the release is about.
    "0.5.1": [
        "milestone", "critical-path", "baseline", "variance", "kickoff",
        "go-live", "deliverable", "scope-change", "change-order", "SOW",
        "WBS", "stakeholder", "RAID", "RFI", "lessons-learned",
    ],
    # 0.5.2 named the body conventions agents were already using in the field
    # (spec 2.6 and 7.11).
    "0.5.2": ["ASK", "relay", "void-if", "blocks"],
}

# Directories under examples/ that are not message corpora.
SKIP_DIRS = {"ClaudeCode"}

# Fields that are undocumented ON PURPOSE, because the example's subject IS an
# unrecognised field. Narrowly scoped to file + field name so the check stays
# strict everywhere else: an accidental typo in any other example still fails.
INTENTIONAL_UNKNOWN_FIELDS: dict[str, set[str]] = {
    # Spec 3.5 is about what a reader does when the sender is on a newer
    # version. Demonstrating that requires a field this version does not know.
    "examples/version-skew.md": {"provenance"},
}

_failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"OK: {name}")
    else:
        print(f"FAIL: {name}{(' -- ' + detail) if detail else ''}", file=sys.stderr)
        _failures.append(name)


# --------------------------------------------------------------------------
# Extracting messages from the corpus
# --------------------------------------------------------------------------

# A routing header is a line that opens with from= and carries a date= field.
_HEADER_LINE = re.compile(r"^from=.*\bdate=")
_FENCE = re.compile(r"^\s*`{3,}")


def example_files() -> list[pathlib.Path]:
    out = []
    for p in sorted(EXAMPLES.rglob("*")):
        if p.is_dir() or p.suffix not in (".txt", ".md"):
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(EXAMPLES).parts):
            continue
        out.append(p)
    return out


def extract_messages(path: pathlib.Path) -> list[dict]:
    """Pull every A2AL message out of a file.

    A message starts at a routing-header line and runs until a fence, a blank
    line, the next header, or EOF. That covers both bare .txt messages and
    messages shown inside fenced blocks in .md walkthroughs.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    messages = []
    i = 0
    while i < len(lines):
        if not _HEADER_LINE.match(lines[i]):
            i += 1
            continue
        header = lines[i]
        body: list[str] = []
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if _FENCE.match(nxt) or _HEADER_LINE.match(nxt) or not nxt.strip():
                break
            body.append(nxt)
            j += 1
        messages.append({
            "file": str(path.relative_to(REPO)).replace("\\", "/"),
            "line": i + 1,
            "header": header,
            "body": "\n".join(body),
        })
        i = j
    return messages


# --------------------------------------------------------------------------
# The spec is the source of truth for field names
# --------------------------------------------------------------------------

_TABLE_FIELD = re.compile(r"^\|\s*`([^`]+)`\s*\|")


def spec_header_fields() -> tuple[set[str], set[str]]:
    """(required, optional) header field names, parsed from spec 3.1 and 3.2."""
    text = SPEC.read_text(encoding="utf-8")

    def rows_between(start: str, end: str) -> set[str]:
        a = text.index(start)
        b = text.index(end, a)
        names = set()
        for line in text[a:b].splitlines():
            m = _TABLE_FIELD.match(line)
            if not m:
                continue
            # "audience=agent\|mixed" -> "audience"; "from" -> "from"
            name = m.group(1).split("=", 1)[0].replace("\\", "").strip()
            if name:
                names.add(name)
        return names

    required = rows_between("### 3.1 Required fields", "### 3.2 Optional fields")
    optional = rows_between("### 3.2 Optional fields", "### 3.3 Example")
    return required, optional


def parse_header(header: str) -> dict[str, str]:
    fields = {}
    for part in header.split(";"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            fields[k.strip()] = v.strip()
    return fields


def release_terms(release: str) -> set[str]:
    """Expand a NEW_IN_RELEASE row, resolving any domain:<name> entries."""
    out = set()
    for item in NEW_IN_RELEASE[release]:
        if item.startswith("domain:"):
            domain = item.split(":", 1)[1]
            entries = L.load_library(LIBRARY)
            found = {e["term"] for e in entries if e.get("domain") == domain}
            if not found:
                _failures.append(f"release manifest names unknown domain {domain!r}")
            out |= found
        else:
            out.add(item)
    return out


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

def test_corpus_is_non_empty(messages: list[dict]) -> None:
    check("corpus: examples/ contains messages", len(messages) >= 8, str(len(messages)))
    files = {m["file"] for m in messages}
    txt = {str(p.relative_to(REPO)).replace("\\", "/") for p in EXAMPLES.glob("*.txt")}
    missing = sorted(txt - files)
    check("corpus: every .txt example yields a parseable message",
          not missing, f"no header found in: {missing}")


def test_every_message_has_a_conformant_header(messages: list[dict],
                                               required: set[str],
                                               optional: set[str]) -> None:
    known = required | optional
    bad_missing, bad_unknown = [], []
    for m in messages:
        fields = parse_header(m["header"])
        deliberate = INTENTIONAL_UNKNOWN_FIELDS.get(m["file"], set())
        missing = sorted(required - set(fields))
        unknown = sorted(set(fields) - known - deliberate)
        where = f"{m['file']}:{m['line']}"
        if missing:
            bad_missing.append(f"{where} missing {missing}")
        if unknown:
            bad_unknown.append(f"{where} unknown {unknown}")

    check("header: every message has all required fields (spec 3.1)",
          not bad_missing, "; ".join(bad_missing[:4]))
    check("header: no message uses an undocumented field name",
          not bad_unknown, "; ".join(bad_unknown[:4]))


def test_header_field_names_are_well_formed(messages: list[dict]) -> None:
    """Fields are separated by '; ' and the header is a single line."""
    bad = []
    for m in messages:
        if "\n" in m["header"]:
            bad.append(f"{m['file']}:{m['line']} header spans lines")
        # A ';' not followed by a space is a formatting slip that breaks naive splitters.
        if re.search(r";(?!\s)", m["header"]):
            bad.append(f"{m['file']}:{m['line']} ';' not followed by space")
    check("header: separated by '; ' and confined to one line", not bad, "; ".join(bad[:4]))


def test_every_documented_field_is_exercised(messages: list[dict],
                                             required: set[str],
                                             optional: set[str]) -> None:
    used = set()
    for m in messages:
        used |= set(parse_header(m["header"]))

    unexercised_req = sorted(required - used)
    unexercised_opt = sorted(optional - used)

    check("coverage: every REQUIRED header field appears in an example",
          not unexercised_req, str(unexercised_req))
    check("coverage: every OPTIONAL header field appears in an example",
          not unexercised_opt,
          f"documented in spec 3.2 but demonstrated nowhere: {unexercised_opt}")


def test_every_new_term_is_exercised(messages: list[dict]) -> None:
    corpus = "\n".join(m["header"] + "\n" + m["body"] for m in messages)
    for release in sorted(NEW_IN_RELEASE):
        terms = release_terms(release)
        unused = sorted(
            t for t in terms
            if not re.search(rf"(?<![A-Za-z0-9]){re.escape(t)}(?![A-Za-z0-9])", corpus)
        )
        check(f"coverage: every term new in {release} appears in an example",
              not unused,
              f"{len(unused)}/{len(terms)} demonstrated nowhere: {unused}")


def test_every_message_is_lint_error_free(messages: list[dict]) -> None:
    """The linter and the examples must agree. Warnings are allowed."""
    bad = []
    for m in messages:
        body = m["body"].splitlines()
        for level, msg in LINT.lint_header(m["header"], body[0] if body else None):
            if level == LINT.ERROR:
                bad.append(f"{m['file']}:{m['line']} {msg}")
    # Whole-file view too: a .txt message is linted from its literal line 1.
    for p in sorted(EXAMPLES.glob("*.txt")):
        for level, msg in LINT.lint_path(str(p)):
            if level == LINT.ERROR:
                bad.append(f"{p.relative_to(REPO).as_posix()} {msg}")
    check("lint: every example is free of a2al_lint.py errors", not bad, "; ".join(bad[:4]))


def test_bodies_avoid_spec_anti_patterns(messages: list[dict]) -> None:
    """Spec 4.4 bans rare Unicode outright; the corpus must model that."""
    allowed = set("—–…")
    bad = []
    for m in messages:
        for ch in m["header"] + m["body"]:
            if ord(ch) > 127 and ch not in allowed:
                bad.append(f"{m['file']}:{m['line']} U+{ord(ch):04X}")
                break
    check("style: no rare Unicode in any example (spec 4.4)", not bad, "; ".join(bad[:4]))


def main() -> int:
    required, optional = spec_header_fields()
    check("spec: parsed the required-field table", required == {"from", "to", "date", "topic"},
          str(sorted(required)))
    check("spec: parsed the optional-field table", len(optional) >= 8, str(sorted(optional)))

    messages = []
    for f in example_files():
        messages.extend(extract_messages(f))

    test_corpus_is_non_empty(messages)
    test_every_message_has_a_conformant_header(messages, required, optional)
    test_header_field_names_are_well_formed(messages)
    test_every_documented_field_is_exercised(messages, required, optional)
    test_every_new_term_is_exercised(messages)
    test_every_message_is_lint_error_free(messages)
    test_bodies_avoid_spec_anti_patterns(messages)

    print()
    print(f"{len(messages)} message(s) across {len({m['file'] for m in messages})} file(s).")
    if _failures:
        print(f"\n{len(_failures)} failure(s): {', '.join(_failures)}", file=sys.stderr)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
