"""Run the conformance corpora against the reference validator.

Loads:
  * validator/corpus/core/{valid,invalid}.json — core-mode cases
  * validator/corpus/profiles/<profile>/{valid,invalid}.json — profile-aware cases

Exits 0 if every positive case validates and every negative case fails,
1 otherwise.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate import A2ALError, validate, validate_core

CORPUS = pathlib.Path(__file__).resolve().parents[1] / "corpus"


def _load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def _run_corpus(label: str, valid_path: pathlib.Path, invalid_path: pathlib.Path,
                runner) -> tuple[int, list[str]]:
    failures: list[str] = []
    for case in _load(valid_path):
        try:
            runner(case["msg"])
        except A2ALError as e:
            failures.append(f"[{label}:valid:{case['name']}] expected VALID, got: {e}")
    for case in _load(invalid_path):
        try:
            runner(case["msg"])
        except A2ALError:
            continue
        failures.append(
            f"[{label}:invalid:{case['name']}] expected INVALID ({case['reason']}), but accepted"
        )
    n = len(_load(valid_path)) + len(_load(invalid_path))
    return n, failures


def main() -> int:
    total = 0
    all_failures: list[str] = []

    n, fs = _run_corpus("core", CORPUS / "core" / "valid.json",
                        CORPUS / "core" / "invalid.json", validate_core)
    total += n
    all_failures += fs

    profiles_root = CORPUS / "profiles"
    if profiles_root.exists():
        for profile_dir in sorted(profiles_root.iterdir()):
            if not profile_dir.is_dir():
                continue
            label = profile_dir.name
            n, fs = _run_corpus(
                label,
                profile_dir / "valid.json",
                profile_dir / "invalid.json",
                validate,
            )
            total += n
            all_failures += fs

    if all_failures:
        for f in all_failures:
            print(f, file=sys.stderr)
        print(f"\n{len(all_failures)} failure(s) of {total} cases", file=sys.stderr)
        return 1

    print(f"OK: {total} cases passed across core + all profiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
