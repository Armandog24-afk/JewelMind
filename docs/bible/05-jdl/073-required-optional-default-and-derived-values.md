---
id: JM-BIBLE-073
title: Required, Optional, Default, and Derived Values
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-064
related_documents:
  - JM-BIBLE-A09
  - JM-BIBLE-052
implementation_status: current
professional_validation: not_required
normative: true
---

# Required, Optional, Default, and Derived Values

## Classification key

| Class | Meaning |
|---|---|
| REQUIRED EXPLICIT | Must be present in the authored document; no default exists |
| REQUIRED WITH DEFAULT | Always present after parsing; if omitted, a documented default fills it |
| OPTIONAL | May be absent with no substitute value applied |
| DERIVED | Computed from other fields in the same document, never independently authored |
| GENERATED | Produced by the compiler/geometry pipeline, not part of the authored document at all |
| METADATA | Present in the document but does not currently drive geometry |
| RESERVED | Named and typed, but not yet given behavior |

## Every current field, classified

| Field | Class | Default (if any) | Basis |
|---|---|---|---|
| `schemaVersion` | REQUIRED WITH DEFAULT | `"0.1.0"` | `Literal["0.1.0"] = SCHEMA_VERSION` in `schema.py` |
| `project.name` | REQUIRED WITH DEFAULT, METADATA | `"Solitaire Ring"` | Does not affect geometry; free-text label only |
| `project.units` | REQUIRED WITH DEFAULT | `"mm"` (fixed) | `Literal["mm"]`; not a real choice today |
| `jewelry.category` | REQUIRED WITH DEFAULT | `"ring"` (fixed) | `Literal["ring"]` |
| `jewelry.style` | REQUIRED WITH DEFAULT | `"solitaire"` (fixed) | `Literal["solitaire"]` |
| `ring.sizeSystem` | REQUIRED WITH DEFAULT | `"EU"` (fixed) | `Literal["EU"]` |
| `ring.size` | REQUIRED WITH DEFAULT | `16.0` | Geometry-driving indirectly via `sizing_consistency()` cross-check against `innerDiameter`; not itself consumed by the CAD builders (band radius comes from `innerDiameter`, per `docs/geometry-conventions.md`) |
| `ring.innerDiameter` | REQUIRED WITH DEFAULT | `17.8` | Geometry-driving; sets the band's inner radius |
| `band.width` | REQUIRED WITH DEFAULT | `2.4` | Geometry-driving |
| `band.thickness` | REQUIRED WITH DEFAULT | `1.8` | Geometry-driving |
| `band.profile` | REQUIRED WITH DEFAULT | `"comfort_fit"` | Geometry-driving (selects the band's cross-section builder) |
| `stone.shape` | REQUIRED WITH DEFAULT | `"round"` (fixed) | Geometry-driving, reference-only (LAW-006) |
| `stone.diameter` | REQUIRED WITH DEFAULT | `6.5` | Geometry-driving, reference-only |
| `stone.depth` | REQUIRED WITH DEFAULT | `4.0` | Geometry-driving, reference-only |
| `setting.type` | REQUIRED WITH DEFAULT | `"prong"` (fixed) | Geometry-driving (selects the setting builder) |
| `setting.prongCount` | REQUIRED WITH DEFAULT | `6` | Geometry-driving |
| `setting.prongDiameter` | REQUIRED WITH DEFAULT | `1.1` | Geometry-driving |
| `setting.prongHeight` | REQUIRED WITH DEFAULT | `4.8` | Geometry-driving |
| `setting.basketHeight` | REQUIRED WITH DEFAULT | `3.5` | Geometry-driving |
| `material.metal` | REQUIRED WITH DEFAULT, METADATA | `"yellow_gold_18k"` | Confirmed non-geometry-driving in [`04-jewelry-domain/052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md); affects display/specification text only today |
| `manufacturing.method` | REQUIRED WITH DEFAULT, METADATA | `"lost_wax_casting"` | Affects which semantic-validation rule fires (`JM-MANUFACTURING-001`) but not geometry shape |
| `preview.meshTolerance` | REQUIRED WITH DEFAULT | `0.1` | Affects tessellation only, not the underlying B-Rep solid |
| `preview.angularTolerance` | REQUIRED WITH DEFAULT | `0.2` (radians) | Same as above |

**No field in the current schema is REQUIRED EXPLICIT, OPTIONAL, DERIVED, or RESERVED.** Every field has a Pydantic default, so a minimal document (`{"schemaVersion": "0.1.0"}` or even `{}`) is valid and canonicalizes identically to the full default document — see `specs/jdl/v1/examples/minimal-solitaire.json`.

## GENERATED values (outside the document, produced by the pipeline)

| Value | Source |
|---|---|
| `definitionHash` | `definition_hash()`, computed from the document, never authored |
| `generatorVersion` | `GENERATOR_VERSION` constant, a property of the running code, not the document |
| Component volumes, bounding boxes | Computed during geometry generation (`GeneratedComponent`, `GeneratedModel`) |
| `generated_at` timestamp | Assigned by `ModelService.generate()` at generation time; never part of the canonical document or its hash |

## Why `ring.size` is not DERIVED from `ring.innerDiameter` (or vice versa)

Both are independently stored and independently authorable. `sizing.py::sizing_consistency()` computes what `innerDiameter` *would be implied by* `size` (or vice versa) purely to raise an `information`/`warning`-severity consistency diagnostic (`JM-RING-003`) — it never overwrites either field. This is a deliberate design choice (documented in `sizing.py`'s own module docstring: "JewelMind never silently rewrites one field from the other") because sizing conventions vary by region/manufacturer, so neither field is more authoritative than the other. Classifying either as DERIVED would misstate current behavior.

## Correcting behavior vs. reporting it

Per the Sprint 3 brief, this document does not change any default value. Where a field's classification reveals something worth reconsidering (e.g., whether `material.metal` should someday affect geometry through density-driven mass estimates), that is recorded as an open question in [`086-open-jdl-questions.md`](086-open-jdl-questions.md), not acted on here.
