"""A2AL routing-header linter.

Checks the one line of an A2AL message that a machine has to parse: the
routing header (spec section 3). Nothing else.

The principle
-------------
It checks line 1 only. Bodies are free-form and are never checked; A2AL
doesn't validate message shape, by design. The single exception is that I look
at line 2 to see whether it is a header spilling over (a `cc=` or `; thread=`
on line 2), because a strict reader ends the header at the first newline and
drops those fields.

Unknown fields are warnings, never errors. Forward compat is the load-bearing
invariant: a reader on an older version preserves fields it doesn't know, so a
newer sender's fields must not be rejected here either.

Input
-----
File paths, or `-` for stdin. For a `.md` file whose line 1 is not a header,
I lint the first line of its first fenced ```a2al block instead (spec section
2.5.1). A Markdown file whose line 1 *is* a header (header over a Markdown
body) is linted like any other message.

Levels
------
  ERROR  no header; missing or empty required field; a segment with no key;
         duplicate key; header continued on line 2; date not ISO 8601.
  WARN   unknown field; audience/urgency/priority outside their value sets;
         topic over 60 chars; refs= with more than 3 items; from/to/cc not in
         Name(Role) or Name/Role shape.

Output is one line per finding, `path: LEVEL: message`, then a summary.
Exit 1 if any ERROR, else 0. `--strict` makes warnings exit 1 as well;
`--quiet` prints errors only.

Run: python tools/a2al_lint.py examples/*.txt
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from a2al_preview import _OPTIONAL_HEADER, _REQUIRED_HEADER  # noqa: E402

ERROR = "ERROR"
WARN = "WARN"

KNOWN_FIELDS = set(_REQUIRED_HEADER) | set(_OPTIONAL_HEADER)

AUDIENCE_VALUES = {"agent", "mixed"}
URGENCY_VALUES = {"low", "medium", "high", "urgent"}
PRIORITY_VALUES = {"P0", "P1", "P2", "P3"}

TOPIC_MAX = 60
REFS_MAX = 3

# ISO 8601 date, or date + time with optional seconds, fraction and offset.
_ISO_DATE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})"
    r"(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$"
)

# Name(Role) or Name/Role. Role is free-form inside the parens.
_PARTY = re.compile(r"^[^\s(),;/=]+(?:\([^()]+\)|/[^\s(),;/=]+)$")

# A fence opening an embedded block: ```a2al (or ~~~a2al), any fence length >= 3.
_A2AL_FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*a2al\s*$", re.I)

# A line-2 segment that looks like a header field: `key=` at the start of the
# line or after a `;`. I only flag keys the header knows, so ordinary body
# key=value facts (deadline=, ASK=) never trip it.
_LEADING_KEY = re.compile(r"^\s*([A-Za-z][\w-]*)\s*=")
_INNER_KEY = re.compile(r";\s*([A-Za-z][\w-]*)\s*=")


def _segments(line: str) -> list[str]:
    return [s.strip() for s in line.split(";") if s.strip()]


def looks_like_header(line: str) -> bool:
    """True when the line carries at least one required header field."""
    for seg in _segments(line):
        key, eq, _ = seg.partition("=")
        if eq and key.strip().lower() in _REQUIRED_HEADER:
            return True
    return False


def _valid_iso(value: str) -> bool:
    m = _ISO_DATE.match(value)
    if not m:
        return False
    try:
        datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return False
    if m.group(4) is not None:
        hh, mm = int(m.group(4)), int(m.group(5))
        ss = int(m.group(6)) if m.group(6) else 0
        if hh > 23 or mm > 59 or ss > 60:  # 60 allows a leap second
            return False
    return True


def _parties(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def lint_header(line1: str, line2: str | None = None) -> list[tuple[str, str]]:
    """Lint one routing header. Returns (level, message) findings.

    line2 is only used for the continuation check; its content is never linted.
    """
    findings: list[tuple[str, str]] = []
    line1 = line1.rstrip("\r\n")

    if not looks_like_header(line1):
        what = "line 1 is blank" if not line1.strip() else "line 1 is not a routing header"
        findings.append((ERROR, f"no routing header: {what} (spec 3 needs "
                                "from=; to=; date=; topic= on line 1)"))
        return findings

    fields: dict[str, str] = {}
    for seg in _segments(line1):
        key, eq, value = seg.partition("=")
        if not eq or not key.strip():
            findings.append((ERROR, f"segment {seg!r} has no key -- "
                                    "is there a '; ' inside a value?"))
            continue
        key = key.strip().lower()
        value = value.strip()
        if key in fields:
            findings.append((ERROR, f"duplicate key {key!r}"))
            continue
        fields[key] = value

    for req in _REQUIRED_HEADER:
        if req not in fields:
            findings.append((ERROR, f"missing required field {req!r}"))
        elif not fields[req]:
            findings.append((ERROR, f"required field {req!r} is empty"))

    if fields.get("date") and not _valid_iso(fields["date"]):
        findings.append((ERROR, f"date {fields['date']!r} is not an ISO 8601 date "
                                "or datetime (e.g. 2026-05-13 or 2026-05-13T15:30Z)"))

    if line2 is not None:
        lead = _LEADING_KEY.match(line2)
        keys = ([lead.group(1)] if lead else []) + _INNER_KEY.findall(line2)
        spilled = [k.lower() for k in keys if k.lower() in KNOWN_FIELDS]
        if spilled:
            findings.append((ERROR, f"line 2 continues the header ({spilled[0]}=): "
                                    "the header is one line; a strict reader drops "
                                    f"{spilled[0]}= on line 2"))

    for key in fields:
        if key not in KNOWN_FIELDS:
            findings.append((WARN, f"unknown field {key!r} (readers preserve it, "
                                   "not rejected; check the spelling)"))

    if "audience" in fields and fields["audience"] not in AUDIENCE_VALUES:
        findings.append((WARN, f"audience={fields['audience']!r} is not agent|mixed"))
    if "urgency" in fields and fields["urgency"] not in URGENCY_VALUES:
        findings.append((WARN, f"urgency={fields['urgency']!r} is not low|medium|high|urgent"))
    if "priority" in fields and fields["priority"] not in PRIORITY_VALUES:
        findings.append((WARN, f"priority={fields['priority']!r} is not P0|P1|P2|P3"))

    topic = fields.get("topic", "")
    if len(topic) > TOPIC_MAX:
        findings.append((WARN, f"topic is {len(topic)} chars (> {TOPIC_MAX}): "
                               "put the verdict on body line 1; keep topic a label"))

    if "refs" in fields:
        refs = _parties(fields["refs"])
        if len(refs) > REFS_MAX:
            findings.append((WARN, f"refs= has {len(refs)} items (> {REFS_MAX}): keep the "
                                   "1-3 this message cites; list the rest on a body "
                                   "`refs:` line"))

    for key in ("from", "to", "cc"):
        for party in _parties(fields.get(key, "")):
            if not _PARTY.match(party):
                findings.append((WARN, f"{key}={party!r} is not in Name(Role) "
                                       "or Name/Role shape"))

    return findings


def lint_text(text: str, markdown: bool = False) -> list[tuple[str, str]]:
    """Lint a whole message. For Markdown, fall back to the first a2al block."""
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.splitlines()
    line1 = lines[0] if lines else ""
    line2 = lines[1] if len(lines) > 1 else None

    if markdown and not looks_like_header(line1):
        for i, line in enumerate(lines):
            m = _A2AL_FENCE.match(line)
            if not m:
                continue
            fence = m.group(1)[0]
            block = []
            for inner in lines[i + 1:]:
                if inner.strip().startswith(fence * 3):
                    break
                block.append(inner)
            where = f" (a2al block at line {i + 2})"
            b1 = block[0] if block else ""
            b2 = block[1] if len(block) > 1 else None
            return [(lvl, msg + where) for lvl, msg in lint_header(b1, b2)]

    return lint_header(line1, line2)


def lint_path(path: str) -> list[tuple[str, str]]:
    if path == "-":
        return lint_text(sys.stdin.read())
    p = pathlib.Path(path)
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [(ERROR, f"cannot read file: {e.strerror or e}")]
    return lint_text(text, markdown=p.suffix.lower() in (".md", ".markdown"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="a2al_lint.py",
        description="Lint the routing header (line 1) of A2AL messages. Bodies are never checked.",
    )
    ap.add_argument("files", nargs="+", help="message files; '-' reads stdin")
    ap.add_argument("--quiet", action="store_true", help="print errors only")
    ap.add_argument("--strict", action="store_true", help="warnings also exit 1")
    args = ap.parse_args(argv)

    errors = warnings = 0
    for path in args.files:
        name = "<stdin>" if path == "-" else path
        for level, msg in lint_path(path):
            if level == ERROR:
                errors += 1
            else:
                warnings += 1
                if args.quiet:
                    continue
            print(f"{name}: {level}: {msg}")

    if not args.quiet:
        n = len(args.files)
        print(f"{n} file(s) checked: {errors} error(s), {warnings} warning(s)")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
