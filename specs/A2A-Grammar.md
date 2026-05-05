Below is the **full A2AL/2.0 grammar ruleset** (normative). It’s written as a **machine-first, deterministic** spec with an **Array‑Only wire format** (no objects, no null, no floats) to minimize tokens and ambiguity.

> **Naming:** This is **A2AL/2.0 – Project Coordination Profile (Array‑Only)**  
> **Wire format:** UTF‑8 “A2AL‑Array” (a strict subset of JSON: **arrays + ints + strings only**)

***

# A2AL/2.0 — Full Grammar Rules (Normative)

## 0) Design Invariants (MUST)

1.  **No information loss:** Unknown codes and fields MUST be preserved if relayed (see §8).
2.  **No ambiguity:** No `null`, no floats, no objects, no duplicate meaning states.
3.  **Deterministic:** Same semantic message ⇒ same canonical bytes (§7).
4.  **Token-minimal:** Positional fields, numeric codes, and stable ordering (§6–§7).
5.  **Machine-first:** Human readability is not required; prose is forbidden between agents (§9).

***

## 1) Primitive Types

### 1.1 Atom Types

*   **int**: base‑10 integer, no leading zeros unless value is `0`
*   **str**: UTF‑8 string, NFC normalized, double‑quoted
*   **arr**: JSON-style array of atoms or arrays

### 1.2 Forbidden Types

*   `null` — forbidden everywhere
*   floats — forbidden everywhere
*   objects/maps — forbidden everywhere (use KV lists)
*   NaN/Infinity — forbidden

### 1.3 Identifiers

*   **ctx\_id**: `^[a-z0-9][a-z0-9-]{0,63}$`
*   **entity\_id**: any non-empty string; recommended `^[A-Za-z0-9_.:/#-]{1,128}$`
*   **msg\_id**: base64url (no padding) of 12 bytes (recommended 16 chars), e.g. `Qm9Jp8v4qZp8fN2d`

***

## 2) Message Top-Level Shape

### 2.1 Message

A2AL message is always:

    MSG := [ H, B ]

Where:

*   `H` = header array (positional)
*   `B` = body array (archetype-specific)

No other top-level shape is valid.

***

## 3) Header (H)

### 3.1 Header Shape (positional; trailing omission allowed)

    H := [ v, ctx, src, dst, typ, mid?, cid?, ts?, pri? ]

*   `v` (int) MUST equal `2`
*   `ctx` (str) context id (project/domain)
*   `src` (int) sender role code
*   `dst` (int) receiver role code (or `-1` for broadcast)
*   `typ` (int) archetype code 1..7 (see §4)
*   `mid` (str) optional message id; if omitted, receiver may synthesize
*   `cid` (str) optional conversation/thread id
*   `ts` (int) optional unix epoch ms timestamp
*   `pri` (int) optional priority 0..9 (default 5; lower = more urgent)

### 3.2 Role Codes (src/dst)

Reserved role codes (recommended):

*   `0` PM
*   `1` ARCH
*   `2` QA
*   `3` DEV
*   `4` SEC
*   `5` DEVOPS
*   `6` PMO
*   `7` EXEC
*   `8` AGENT (generic)
*   `1000+` private/vendor/extension roles

**Rule:** Unknown role codes MUST be accepted and preserved.

***

## 4) Archetype Codes (typ)

`typ` MUST be one of:

1.  **A1 Scope Delta**
2.  **A2 Decision Record**
3.  **A3 Execution Status**
4.  **A4 Risk / Threat Intelligence**
5.  **A5 Signals & Gates**
6.  **A6 Inventory / Topology**
7.  **A7 Next Actions**

***

## 5) Body (B) by Archetype

### Common Conventions

All bodies start with a **lane tag** in position 0:

*   `"Δ"` delta lane
*   `"D"` decision lane
*   `"S"` status lane
*   `"R"` risk lane
*   `"G"` gate lane
*   `"I"` inventory lane
*   `"O"` ops lane

Body arrays MUST follow the exact schema below.

***

### 5.1 A1 — Scope Delta (typ=1)

    B := ["Δ", ΔITEM, ΔITEM, ...]
    ΔITEM := [ op, etype, id, meta? ]

*   `op` (int) operation:
    *   `1` add
    *   `2` remove
    *   `3` modify
    *   `4` re-scope (semantic modify)
*   `etype` (int) entity type code (see §5.1.1)
*   `id` (str) entity identifier (e.g., "US-858")
*   `meta` (arr) optional KV list `[[k,v]...]` (see §6.1)

#### 5.1.1 Entity Type Codes (etype)

Recommended core registry:

*   `0` US (user story)
*   `1` B (backlog item/bug)
*   `2` E (epic)
*   `3` F (feature)
*   `4` PRD
*   `5` CI
*   `6` FILE
*   `7` ENV
*   `8` PR (pull request)
*   `9` TASK
*   `10` RISK
*   `11` DECISION
*   `1000+` extension types

**Rule:** Unknown `etype` MUST be accepted and preserved.

***

### 5.2 A2 — Decision Record (typ=2)

    B := ["D", DPAIR, DPAIR, ...]
    DPAIR := [ dkey, dval ]

*   `dkey` (int) decision key code (registry)
*   `dval` (atom|arr) decision value

**Ordering rule:** `DPAIR`s MUST be sorted by `dkey` ascending for canonicalization.

Recommended core decision keys:

*   `1` signoff\_status (e.g., "approved", "deferred")
*   `2` priority (0..9)
*   `3` deps (arr of ids)
*   `4` scope\_in (arr of ids)
*   `5` scope\_out (arr of ids)
*   `6` effort (0..9 or string)
*   `7` rationale\_ref (arr of references)
*   `8` owner (role code or id)
*   `1000+` extensions

***

### 5.3 A3 — Execution Status (typ=3)

    B := ["S", MET, MET, ...]
    MET := [ mkey, mval ]

*   `mkey` (int) metric key
*   `mval` (atom|arr) metric value

**Ordering rule:** `MET`s MUST be sorted by `mkey` ascending.

Recommended metric keys:

*   `1` percent\_complete (0..100)
*   `2` stoplight (0=green,1=yellow,2=red)
*   `3` stories\_passed (e.g., \[passed,total])
*   `4` tests\_passed (e.g., \[passed,total])
*   `5` defects\_open (int)
*   `6` findings (int)
*   `7` build\_quality (0=red,1=green)
*   `8` sprint\_id (str)
*   `9` branch (str)
*   `10` merged\_to (str)
*   `1000+` extensions

***

### 5.4 A4 — Risk / Threat Intelligence (typ=4)

    B := ["R", RISK, RISK, ...]
    RISK := [ sev, vec, impact, action, refs? ]

*   `sev` (int) severity:
    *   `0` info
    *   `1` low
    *   `2` med
    *   `3` high
    *   `4` crit
*   `vec` (int|str) attack vector / risk class code (registry)
*   `impact` (int|str) impact code or short label
*   `action` (int|str) mandatory action code or short label
*   `refs` (arr) optional references `[[rk,rv]...]` (see §6.2)

**Ordering rule:** `RISK`s MUST be sorted by `sev` descending, then `vec` ascending.

***

### 5.5 A5 — Signals & Gates (typ=5)

    B := ["G", GATE, GATE, ...]
    GATE := [ scope, invariant, test? ]

*   `scope` (str) applies-to id (e.g., "US-858", "CI", "deploy")
*   `invariant` (str) must-hold condition (short, unambiguous)
*   `test` (arr) optional `[tkey, tval]` or KV list describing verification

**Ordering rule:** `GATE`s MUST be sorted by `scope` ascending, then `invariant` ascending.

***

### 5.6 A6 — Inventory / Topology (typ=6)

    B := ["I", ITEM, ITEM, ...]
    ITEM := [ kind, id, KV* ]
    KV := [ k, v ]

*   `kind` (int) inventory kind:
    *   `0` db
    *   `1` api
    *   `2` service
    *   `3` repo
    *   `4` environment
    *   `5` integration
    *   `6` compute
    *   `7` secret (metadata only; never secret value)
    *   `1000+` extensions
*   `id` (str) inventory item id/name
*   `KV*` zero or more attribute pairs

**Ordering rules:**

*   `ITEM`s sorted by `kind` ascending, then `id` ascending
*   `KV` pairs sorted by `k` ascending within an item

***

### 5.7 A7 — Next Actions (typ=7)

    B := ["O", OP, OP, ...]
    OP := [ actor, verb, target, params? ]

*   `actor` (int|str) role code or agent id
*   `verb` (int|str) action code or short label
*   `target` (str|arr) target id or list
*   `params` (arr) optional KV list `[[k,v]...]`

**Ordering rule:** `OP`s MUST preserve emission order (execution order matters). Do NOT sort.

***

## 6) KV Lists and References

### 6.1 KV List Encoding

All key-value metadata uses **KV lists**, not objects:

    KVLIST := [ [k,v], [k,v], ... ]

*   `k` MUST be int (0..65535 recommended; `1000+` extension keys)
*   `v` may be int, str, or arr

**Ordering rule:** KVLIST MUST be sorted by `k` ascending.

### 6.2 Reference Encoding (optional)

When citing external artifacts (commits, docs, CVEs, URLs), use:

    REFS := [ [rk, rv], ... ]
    rk := int  (reference kind)
    rv := str  (reference value)

Recommended `rk`:

*   `0` url
*   `1` commit
*   `2` cve
*   `3` file\_path
*   `4` ticket\_id
*   `5` meeting\_id
*   `1000+` extension

***

## 7) Canonicalization (Determinism)

### 7.1 Canonical Bytes Rules (MUST)

A message is canonical iff:

1.  UTF‑8, no BOM
2.  No insignificant whitespace anywhere
3.  Strings NFC normalized
4.  Integers base‑10, no leading zeros (except `0`)
5.  Array element ordering rules are satisfied (see each archetype)
6.  No forbidden types appear

### 7.2 Canonical Ordering Summary

*   A1 `"Δ"`: sort ΔITEM by `(op, etype, id)` ascending
*   A2 `"D"`: sort by `dkey` ascending
*   A3 `"S"`: sort by `mkey` ascending
*   A4 `"R"`: sort by `(sev desc, vec asc)`
*   A5 `"G"`: sort by `(scope, invariant)`
*   A6 `"I"`: sort items by `(kind, id)`; KVLIST sorted by key
*   A7 `"O"`: preserve order (do not sort)

***

## 8) Forward Compatibility (No Information Loss)

### 8.1 Unknown Codes

If a receiver encounters unknown:

*   role code
*   archetype extension (future typ values)
*   etype/kind/dkey/mkey/vec/verb codes

It MUST:

*   preserve the original numeric code
*   preserve the original list structure
*   avoid “helpful rewriting”

### 8.2 Unknown Fields

Because the format is positional, “unknown fields” only occur as:

*   extra trailing header fields
*   extra fields appended to items (e.g., ΔITEM meta)

Receivers MUST preserve unknown trailing fields verbatim when relaying.

***

## 9) Prohibitions (Enforced)

### 9.1 Prose Ban

Between agents, it is invalid to transmit:

*   markdown paragraphs
*   executive summaries
*   narrative RCA
*   “why you’re getting this”
*   apologies, framing, rhetorical text

**Exception:** short invariant strings inside `"G"` and labels inside `"R"` are allowed because they change behavior.

### 9.2 Secrets Ban

Secrets MUST NOT be transmitted in A2AL (ever).  
Inventory may describe secret *metadata* only.

***

## 10) Minimal Valid Examples

### A1 Scope Delta

```text
[[2,"dw-etl",0,2,1,"Qm9Jp8v4qZp8fN2d"],["Δ",[2,0,"US-852"],[2,0,"US-853"],[1,0,"US-858"],[3,0,"US-856"]]]
```

### A7 Next Actions

```text
[[2,"mcp-server",4,0,7],["O",[2,"signoff","prd.json"],[0,"resize-sprint","ralph/bronze-data-integrity"]]]
```

***

## 11) Implementation Checklist (for your agents)

**Writer MUST:**

*   classify input into exactly one archetype typ=1..7
*   emit Array‑Only A2AL
*   apply canonical sorting rules
*   omit trailing header fields that are default/unknown

**Reader MUST:**

*   validate types and bans
*   apply defaults when header fields omitted
*   update state / execute ops without inference
*   preserve unknown codes and trailing fields when relaying

***

