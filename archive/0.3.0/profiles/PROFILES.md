# A2AL Profiles Registry

A profile defines intents, sections, ordering rules, and recommended roles for a domain. Each profile is versioned independently of the core spec.

This registry indexes all known profiles. To register a new profile, write `profiles/<name>-<version>.md` and PR it into this file.

## Registered Profiles

| Profile | Version | Status | Domain | File |
|---|---|---|---|---|
| `project-coord` | 1.0 | Reference | Project / PMO / sprint coordination | [project-coord-1.0.md](./project-coord-1.0.md) |
| `social-post` | 1.0 | Reference | Agent-to-agent social posts (Moltbook-style) | [social-post-1.0.md](./social-post-1.0.md) |

## Profile Versioning

Profiles follow semver:
- **MAJOR** — breaking change to required fields or section semantics
- **MINOR** — new optional intents, sections, or recommended roles
- **PATCH** — clarifications

A message references a profile via `"profile": "<name>/<major>.<minor>"`.

## Adding a New Profile

1. Write `profiles/<name>-<version>.md` describing intents, sections, ordering, and recommended roles
2. Add a row to this table
3. (Recommended) Add a corpus directory at `validator/corpus/profiles/<name>-<version>/` with `valid.json` and `invalid.json`
4. (Recommended) Add example messages at `examples/<name>/`
5. PR all of the above together

## Naming Conventions

- Lowercase, hyphenated profile names: `project-coord`, not `ProjectCoord`
- Vendor-specific profiles SHOULD prefix with org: `acme-corp/code-review`
