# Validation rules

Validation is deterministic and runs in two places:

- **Backend (authoritative):** `backend/jewelmind/validation/engine.py`. Runs
  on every `POST /api/models/validate` and `POST /api/models/generate` call,
  and again defensively before every export. Its verdict always wins.
- **Frontend (mirror):** `shared/validation/engine.ts`. Gives the user
  instant feedback while typing, without a network round trip. Kept in sync
  with the backend rule-by-rule; if the two ever disagree, trust the
  backend response (surfaced automatically — see below).

A `ValidationResult` looks like:

```json
{
  "ruleId": "JM-BAND-002",
  "severity": "error | warning | information",
  "message": "Human-readable message",
  "parameter": "band.thickness",
  "suggestedValue": 1.6
}
```

`error` results block generation and export. `warning` and `information`
results are shown but never block anything.

## Rule reference

| Rule ID | Parameter(s) | Condition | Severity |
|---|---|---|---|
| `JM-RING-001` | `ring.innerDiameter` | Must be strictly between 10 mm and 30 mm. | error |
| `JM-RING-002` | `ring.size` | Must be strictly between 1 and 50. | error |
| `JM-RING-003` | `ring.innerDiameter` | EU size and inner diameter are converted via `size = (π × diameter) − 40` (see `docs/domain-model.md` and `sizing.py`) and compared; a discrepancy over 0.15 mm is `information`, over 0.5 mm is `warning`. Neither field is ever rewritten automatically. | information / warning |
| `JM-BAND-001` | `band.width` | Below 1.5 mm. | error |
| `JM-BAND-002` | `band.thickness` | Below 1.4 mm is an error; 1.4–1.6 mm (exclusive) is a warning. | error / warning |
| `JM-BAND-003` | `band.width` | Above 12 mm. | warning |
| `JM-STONE-001` | `stone.diameter` | Must be between 2 mm and 15 mm. | error |
| `JM-STONE-002` | `stone.depth` | Must be greater than 0.5 mm and less than `stone.diameter`. | error |
| `JM-PRONG-001` | `setting.prongCount` | Must be exactly 4 or 6. | error |
| `JM-PRONG-002` | `setting.prongDiameter` | Below 0.8 mm is an error; 0.8–1.0 mm (exclusive) is a warning. | error / warning |
| `JM-PRONG-003` | `setting.prongCount` | `stone.diameter` > 8 mm with 4 prongs. | warning |
| `JM-PRONG-004` | `setting.prongHeight` | Must be greater than `setting.basketHeight`. | error |
| `JM-SETTING-001` | `setting.basketHeight` | Must be positive. | error |
| `JM-SETTING-002` | `setting.basketHeight` | Above 8 mm. | warning |
| `JM-MANUFACTURING-001` | `band.thickness`, `band.width` | For `manufacturing.method = direct_resin_printing`, either dimension below 0.8 mm. (`setting.prongDiameter` is excluded here — `JM-PRONG-002` already errors below 0.8 mm regardless of manufacturing method.) | warning |
| `JM-GEOMETRY-001` | `band.thickness`, `band.width` | Defense-in-depth: rejects any combination that would produce a non-positive outer band dimension (e.g. zero/negative thickness or width), independent of the rules above. | error |

## Why the EU size ↔ diameter conversion is isolated

`ring.size` and `ring.innerDiameter` are both user-editable and can
legitimately disagree (different sizing conventions, a ring resized after
casting, deliberately loose/tight fit). JewelMind never silently overwrites
one from the other. The conversion itself lives in one place —
`backend/jewelmind/validation/sizing.py` and its TypeScript mirror
`shared/validation/sizing.ts` — so the convention is documented once and
reused by both the rule engine and (if needed later) any future UI helper
that suggests a consistent pair of values.

## Adding a new rule

1. Add a `JM-XXX-NNN` constant to `backend/jewelmind/validation/rules.py`
   and its mirror in `shared/validation/rules.ts`.
2. Implement the check in `backend/jewelmind/validation/engine.py`.
3. Mirror it in `shared/validation/engine.ts`.
4. Add a backend test in `backend/tests/test_validation.py` for every
   severity branch.
5. Update the table above.
