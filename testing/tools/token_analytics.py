"""Token-analytics utilities for A2A format comparisons.

Reusable, parameterized: counts tokens for one or more files representing the
same logical message in different formats (A2AL JSON, MD, A2A Shorthand, etc.),
emits per-message analytics records and a roll-up summary.

Usage:
  # count one file
  python token_analytics.py count <path> [--encoder cl100k_base]

  # analyze a single logical message across N format files
  python token_analytics.py analyze \\
      --id agent1-greeting-1778500800 \\
      --label "Hello + Hump Day" \\
      --intent greeting \\
      --format a2al:path/to.json \\
      --format md:path/to.md \\
      --format shorthand:path/to.txt \\
      --shared-body a2al:body \\
      --baseline md \\
      --out testing/agent1/

  # batch via manifest
  python token_analytics.py batch --manifest testing/tools/manifests/test-2.json

  # roll up an analytics directory into a summary
  python token_analytics.py summary --in testing/agent1/ --out testing/agent1/summary.json

Manifest schema (batch mode):
  {
    "encoder": "cl100k_base",
    "out_dir": "<dir>",
    "baseline": "md",                          # optional, default "md"
    "summary": "summary-<name>.json",          # optional; if set, also write rollup
    "messages": [
      {
        "id": "<id>",
        "label": "<label>",
        "intent": "<intent>",
        "shared_body": {"format": "a2al", "key": "body"},   # optional
        "envelope_overhead_against": "shared_body",         # optional
        "formats": [
          {"name": "a2al", "path": "<file>"},
          {"name": "md",   "path": "<file>"}
        ]
      }
    ]
  }
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from typing import Any

import tiktoken


def get_encoder(name: str = "cl100k_base"):
    return tiktoken.get_encoding(name)


def count_file(path: str, enc) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return {
        "file": os.path.basename(path),
        "path": path,
        "tokens": len(enc.encode(text)),
        "chars": len(text),
    }


def extract_shared_body(formats: dict, spec: dict | None, enc) -> dict | None:
    """spec = {"format": "<name>", "key": "<json-key>"}; returns {tokens, source_format}."""
    if not spec:
        return None
    src = spec.get("format")
    key = spec.get("key", "body")
    if src not in formats:
        return None
    src_path = formats[src]["path"]
    try:
        with open(src_path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        body = obj.get(key, "")
        return {"source_format": src, "key": key, "tokens": len(enc.encode(body))}
    except (json.JSONDecodeError, OSError):
        return None


def analyze_message(
    id_: str,
    label: str,
    intent: str,
    formats: dict[str, str],
    enc,
    encoder_name: str,
    baseline: str | None = None,
    shared_body_spec: dict | None = None,
) -> dict:
    """formats: {format_name -> path}. Returns the analytics record."""
    counts = {name: count_file(p, enc) for name, p in formats.items()}

    shared_body = extract_shared_body(counts, shared_body_spec, enc)

    ratios: dict[str, float] = {}
    if baseline and baseline in counts:
        base_tok = counts[baseline]["tokens"] or 1
        for name, c in counts.items():
            if name == baseline:
                continue
            ratios[f"{name}/{baseline}"] = round(c["tokens"] / base_tok, 3)

    overhead: dict[str, int] = {}
    if shared_body:
        for name, c in counts.items():
            if name == shared_body["source_format"]:
                overhead[name] = c["tokens"] - shared_body["tokens"]

    return {
        "id": id_,
        "label": label,
        "intent": intent,
        "encoder": encoder_name,
        "formats": counts,
        "shared_body": shared_body,
        "ratios": ratios,
        "envelope_overhead_tokens": overhead,
    }


def write_record(record: dict, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"tokens-{record['id']}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return out_path


def summarize(records: list[dict], baseline: str | None = None) -> dict:
    """Roll up multiple records into a summary."""
    format_names: list[str] = []
    for r in records:
        for n in r["formats"]:
            if n not in format_names:
                format_names.append(n)

    totals = {n: 0 for n in format_names}
    rows = []
    for r in records:
        row = {
            "id": r["id"],
            "label": r["label"],
            "intent": r.get("intent"),
            "by_format": {n: r["formats"][n]["tokens"] for n in format_names if n in r["formats"]},
            "ratios": r.get("ratios", {}),
        }
        for n, t in row["by_format"].items():
            totals[n] += t
        rows.append(row)

    averages: dict[str, float] = {}
    if baseline and baseline in totals and totals[baseline]:
        for n in format_names:
            if n != baseline:
                averages[f"{n}/{baseline}"] = round(totals[n] / totals[baseline], 3)

    return {
        "encoder": records[0]["encoder"] if records else None,
        "baseline": baseline,
        "format_names": format_names,
        "messages": rows,
        "totals": totals,
        "averages_by_total": averages,
    }


def cmd_count(args):
    enc = get_encoder(args.encoder)
    print(json.dumps(count_file(args.path, enc), indent=2))


def cmd_analyze(args):
    enc = get_encoder(args.encoder)
    formats: dict[str, str] = {}
    for spec in args.format:
        if ":" not in spec:
            sys.exit(f"--format expects <name>:<path>, got {spec!r}")
        name, path = spec.split(":", 1)
        formats[name] = path

    shared_body_spec = None
    if args.shared_body:
        if ":" not in args.shared_body:
            sys.exit("--shared-body expects <format>:<json-key>")
        fmt, key = args.shared_body.split(":", 1)
        shared_body_spec = {"format": fmt, "key": key}

    record = analyze_message(
        id_=args.id,
        label=args.label,
        intent=args.intent,
        formats=formats,
        enc=enc,
        encoder_name=args.encoder,
        baseline=args.baseline,
        shared_body_spec=shared_body_spec,
    )
    out_path = write_record(record, args.out)
    print(f"wrote {out_path}")
    print(json.dumps(record, indent=2))


def _resolve(path: str, base_dir: str) -> str:
    """Resolve a manifest-relative path. Absolute paths pass through unchanged."""
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base_dir, path))


def cmd_batch(args):
    manifest_path = os.path.abspath(args.manifest)
    base_dir = os.path.dirname(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        m = json.load(f)
    encoder_name = m.get("encoder", "cl100k_base")
    enc = get_encoder(encoder_name)
    out_dir = _resolve(m["out_dir"], base_dir)
    baseline = m.get("baseline", "md")

    records = []
    for msg in m["messages"]:
        formats = {f["name"]: _resolve(f["path"], base_dir) for f in msg["formats"]}
        record = analyze_message(
            id_=msg["id"],
            label=msg["label"],
            intent=msg.get("intent", ""),
            formats=formats,
            enc=enc,
            encoder_name=encoder_name,
            baseline=baseline,
            shared_body_spec=msg.get("shared_body"),
        )
        out_path = write_record(record, out_dir)
        print(f"wrote {out_path}")
        records.append(record)

    if m.get("summary"):
        s = summarize(records, baseline=baseline)
        sum_path = os.path.join(out_dir, m["summary"])
        with open(sum_path, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
        print(f"wrote {sum_path}")
        print_summary_table(s)


def cmd_summary(args):
    records = []
    for fn in sorted(os.listdir(args.in_dir)):
        if fn.startswith("tokens-") and fn.endswith(".json"):
            with open(os.path.join(args.in_dir, fn), "r", encoding="utf-8") as f:
                records.append(json.load(f))
    s = summarize(records, baseline=args.baseline)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
        print(f"wrote {args.out}")
    print_summary_table(s)


def print_summary_table(s: dict):
    fmts = s["format_names"]
    print()
    print("=== Token Summary ===")
    header = f"{'id':40s} " + " ".join(f"{n:>10s}" for n in fmts)
    print(header)
    print("-" * len(header))
    for row in s["messages"]:
        line = f"{row['id']:40s} " + " ".join(f"{row['by_format'].get(n, 0):>10d}" for n in fmts)
        print(line)
    print("-" * len(header))
    print(f"{'TOTAL':40s} " + " ".join(f"{s['totals'].get(n, 0):>10d}" for n in fmts))
    if s.get("averages_by_total"):
        print()
        print("Ratios (totals):", "  ".join(f"{k}={v}" for k, v in s["averages_by_total"].items()))


def main(argv=None):
    p = argparse.ArgumentParser(description="A2A token-analytics utilities")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_count = sub.add_parser("count", help="count tokens in one file")
    p_count.add_argument("path")
    p_count.add_argument("--encoder", default="cl100k_base")
    p_count.set_defaults(func=cmd_count)

    p_an = sub.add_parser("analyze", help="analyze one logical message across N formats")
    p_an.add_argument("--id", required=True)
    p_an.add_argument("--label", required=True)
    p_an.add_argument("--intent", default="")
    p_an.add_argument("--format", action="append", required=True, help="<name>:<path>; repeat per format")
    p_an.add_argument("--shared-body", help="<format>:<json-key> to extract shared body and compute envelope overhead")
    p_an.add_argument("--baseline", default="md", help="format name to compute ratios against")
    p_an.add_argument("--encoder", default="cl100k_base")
    p_an.add_argument("--out", required=True)
    p_an.set_defaults(func=cmd_analyze)

    p_b = sub.add_parser("batch", help="run from a manifest file")
    p_b.add_argument("--manifest", required=True)
    p_b.set_defaults(func=cmd_batch)

    p_s = sub.add_parser("summary", help="summarize a directory of analytics records")
    p_s.add_argument("--in", dest="in_dir", required=True)
    p_s.add_argument("--out")
    p_s.add_argument("--baseline", default="md")
    p_s.set_defaults(func=cmd_summary)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
