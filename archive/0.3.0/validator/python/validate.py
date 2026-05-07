"""A2AL/0.3.0 reference validator.

Two-mode validation:
  * core mode (default) — envelope shape, type bans, required fields
  * profile-aware mode — when profile is recognized, also runs profile rules

Reads one A2AL message as JSON from stdin (or a file path argument)
and exits 0 if valid, 1 with a reason on stderr if invalid.

Reference implementation tracking specs/A2A-Core.md and the per-profile
rules in profiles/*.md. Status: WIP.
"""

from __future__ import annotations

import json
import re
import sys

REQUIRED_ENVELOPE = ("v", "from", "to", "id", "intent", "profile")
RECOMMENDED_ENVELOPE = ("ts", "thread", "in-reply-to", "priority")

V_RE = re.compile(r"^0\.3\.\d+$")


class A2ALError(Exception):
    """Raised on any spec violation. Readers MUST reject, not repair."""


# ---------------------------------------------------------------- core mode

def validate_core(msg) -> None:
    """Run core checks: envelope shape, type bans, required fields."""
    if not isinstance(msg, dict):
        raise A2ALError("MSG must be a JSON object")
    _reject_forbidden_types(msg, "MSG")
    for f in REQUIRED_ENVELOPE:
        if f not in msg:
            raise A2ALError(f"missing required envelope field: {f}")
    v = msg["v"]
    if not (isinstance(v, str) and V_RE.match(v)):
        raise A2ALError(f"v must be string '0.3.x', got {v!r}")
    _validate_identity(msg["from"], "from")
    _validate_to(msg["to"])
    if not isinstance(msg["id"], str):
        raise A2ALError("id must be string")
    if not isinstance(msg["intent"], str):
        raise A2ALError("intent must be string")
    if not isinstance(msg["profile"], str):
        raise A2ALError("profile must be string")


def _reject_forbidden_types(node, path: str) -> None:
    """Recursively reject null and float (NaN/Infinity blocked by json.loads default)."""
    if node is None:
        raise A2ALError(f"null forbidden at {path}")
    if isinstance(node, float):
        raise A2ALError(f"float forbidden at {path}")
    if isinstance(node, dict):
        for k, v in node.items():
            _reject_forbidden_types(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, x in enumerate(node):
            _reject_forbidden_types(x, f"{path}[{i}]")


def _validate_identity(val, path: str) -> None:
    if not (isinstance(val, list) and len(val) == 2
            and isinstance(val[0], str) and isinstance(val[1], str)):
        raise A2ALError(f"{path} must be [name: str, role: str]")


def _validate_to(val) -> None:
    if not isinstance(val, list) or len(val) == 0:
        raise A2ALError("to must be a non-empty array")
    if isinstance(val[0], str):
        _validate_identity(val, "to")
    elif isinstance(val[0], list):
        for i, t in enumerate(val):
            _validate_identity(t, f"to[{i}]")
    else:
        raise A2ALError("to must be [name, role] or array of those")


# -------------------------------------------------- profile-aware mode

def validate_profile(msg) -> None:
    """Run profile-specific rules when profile is recognized.

    Unknown profiles are accepted (no-op). This function is called AFTER
    validate_core succeeds, not instead of it.
    """
    profile = msg.get("profile", "")
    handler = _PROFILE_HANDLERS.get(profile)
    if handler is not None:
        handler(msg)


def _project_coord_1_0(msg) -> None:
    SEV_RANK = {"crit": 4, "high": 3, "med": 2, "low": 1, "info": 0}

    def _sorted_asc(items, key, label):
        if items != sorted(items, key=key):
            raise A2ALError(f"project-coord/1.0: {label} not in canonical order")

    if "delta" in msg:
        _sorted_asc(msg["delta"], lambda it: (it[0], it[1]), "delta")
    if "status" in msg:
        _sorted_asc(msg["status"], lambda it: it[0], "status")
    if "decision" in msg:
        _sorted_asc(msg["decision"], lambda it: it[0], "decision")
    if "gates" in msg:
        _sorted_asc(msg["gates"], lambda it: (it[0], it[1]), "gates")
    if "inventory" in msg:
        _sorted_asc(msg["inventory"], lambda it: (it[0], it[1]), "inventory")
        for it in msg["inventory"]:
            kvs = it[2] if len(it) > 2 else []
            if kvs != sorted(kvs, key=lambda kv: kv[0]):
                raise A2ALError("project-coord/1.0: inventory KVs not sorted by k")
    if "risk" in msg:
        items = msg["risk"]
        expected = sorted(items, key=lambda it: (-SEV_RANK.get(it[0], -1), it[1]))
        if items != expected:
            raise A2ALError("project-coord/1.0: risk not sorted (sev desc, vector asc)")


def _social_post_1_0(msg) -> None:
    intent = msg.get("intent")
    if intent == "post":
        for f in ("title", "submolt", "body"):
            if f not in msg:
                raise A2ALError(f"social-post/1.0 post: missing required field {f}")
    elif intent in ("comment", "reply", "edit", "delete"):
        if "in-reply-to" not in msg:
            raise A2ALError(f"social-post/1.0 {intent}: missing in-reply-to")
        if intent != "delete" and "body" not in msg:
            raise A2ALError(f"social-post/1.0 {intent}: missing body")


_PROFILE_HANDLERS = {
    "project-coord/1.0": _project_coord_1_0,
    "social-post/1.0": _social_post_1_0,
}


# ------------------------------------------------------------------- main

def validate(msg) -> None:
    """Run core checks then profile-aware checks. Raises A2ALError on failure."""
    validate_core(msg)
    validate_profile(msg)


def _main() -> int:
    try:
        raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
        msg = json.loads(raw)
        validate(msg)
    except (OSError, json.JSONDecodeError, A2ALError) as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
