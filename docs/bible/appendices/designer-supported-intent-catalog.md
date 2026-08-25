---
id: JM-BIBLE-A56
title: "Appendix: Designer Supported Intent Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGNER-README
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-296
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Designer Supported Intent Catalog

The 19 real JDL dotted field paths in `backend/jewelmind/designer/capability.py::KNOWN_JDL_FIELD_PATHS` — the complete set of fields Designer may ever propose a value for (DESIGNER-GOV-004). Anything outside this set is rejected as `DESIGNER_CAPABILITY_MISMATCH` regardless of what a provider returns.

| JDL field path | Capability-set key / kind | Example natural-language phrase(s) (from `normalizer.py`) |
|---|---|---|
| `project.name` | free text (no enum/numeric gate) | (any project-name phrase; not a synonym table) |
| `ring.size` | numeric (Forge-validated) | "Make the ring size ..." |
| `ring.innerDiameter` | numeric (Forge-validated) | (numeric dimension phrasing) |
| `ring.sizeSystem` | `ringSizeSystem` (enum) | (no synonym table implemented yet — see `297-supported-language-scope.md`) |
| `band.width` | numeric (Forge-validated) | "Make it 2.5 mm wide", "Fascia larga 3mm" |
| `band.thickness` | numeric (Forge-validated) | "spessore 2mm" |
| `band.profile` | `bandProfile` (enum) | "comfort fit", "comfortevole", "fascia piatta" -> `flat` |
| `stone.diameter` | numeric (Forge-validated) | "Stone diameter: ..." |
| `stone.depth` | numeric (Forge-validated) | (numeric dimension phrasing) |
| `stone.shape` | `stoneShape` (enum) | "round", "rotondo", "tondo" -> `round` |
| `setting.prongCount` | `prongCount` (enum, numeric-typed) | "sei griffe" -> 6, "quattro griffe" -> 4, "six prongs" -> 6 |
| `setting.prongDiameter` | numeric (Forge-validated) | "Set the prong diameter to ..." |
| `setting.prongHeight` | numeric (Forge-validated) | (numeric dimension phrasing) |
| `setting.basketHeight` | numeric (Forge-validated) | (numeric dimension phrasing) |
| `setting.type` | `settingType` (enum) | "prong", "griffe", "a griffe" -> `prong` |
| `material.metal` | `metal` (enum) | "oro giallo" -> `yellow_gold_18k`, "oro rosa" -> `rose_gold_18k`, "platino" -> `platinum`, "argento" -> `silver` |
| `manufacturing.method` | `manufacturingMethod` (enum) | "casting", "fusione a cera persa" -> `lost_wax_casting`; "resin printing", "stampa in resina" -> `direct_resin_printing` |
| `jewelry.category` | `jewelryCategory` (enum) | (no synonym table implemented yet — see `297-supported-language-scope.md`) |
| `jewelry.style` | `jewelryStyle` (enum) | (no synonym table implemented yet — see `297-supported-language-scope.md`) |

Notes, verified directly against the code:

- The enum-to-capability-key mapping is `capability.py::_ENUM_FIELD_CAPABILITY_KEY`; it covers 9 of the 19 fields. The remaining 10 fields are either numeric (Forge-validated range, no enum capability set — capability-awareness has nothing to say about them per `is_supported_enum_value()`'s `key is None` branch) or `project.name` (free text).
- Three enum fields currently have no synonym table in `normalizer.py::_ENUM_SYNONYM_TABLES` (`ring.sizeSystem`, `jewelry.category`, `jewelry.style`): they are capability-gated and part of the JDL contract, but a natural-language phrase for them normalizes only if it already matches the canonical token exactly (`normalize_enum_token()` returns `None` for anything not found in its field's table, or falls through with no table at all — see `_ENUM_SYNONYM_TABLES.get(field)` returning `None`). This is an honest current gap, not a documented feature.
- `setting.prongCount` is schema-numeric but treated as a closed, word-mapped enum via `PRONG_COUNT_WORDS` (`4`/`four`/`quattro` -> 4, `6`/`six`/`sei` -> 6); its capability set (`SUPPORTED_PRONG_COUNTS = (4, 6)`) is not a schema `Literal` — see `capability.py`'s own comment on why it is hardcoded here rather than imported.
