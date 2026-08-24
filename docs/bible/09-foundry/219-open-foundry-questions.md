---
id: JM-BIBLE-219
title: Open Foundry Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-218
related_documents:
  - JM-BIBLE-FOUNDRY-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Foundry Questions

| ID | Question | Impact | Provisional behavior | Priority | Blocking? | Decision mechanism |
|---|---|---|---|---|---|---|
| `FOUNDRY-OQ-001` | Should STEP export ever offer an AP214/AP242 schema choice? | Affects downstream tool compatibility for specific manufacturing workflows | CadQuery's default `exportStep()` schema is used, never chosen explicitly | Low | No | Revisit if a real downstream tool needs a specific AP variant |
| `FOUNDRY-OQ-002` | Should the STEP checksum instability (timestamp + translator counter) be worked around, e.g. by post-processing the file to zero those fields before hashing? | Would make STEP checksums stable like STL's, at the cost of a custom post-processing step outside CadQuery's own writer | Not worked around — the instability is documented, not hidden or "fixed" | Medium | No | Engineering decision, weighing the value of a stable checksum against introducing custom STEP-text post-processing |
| `FOUNDRY-OQ-003` | Should `includeComponents`/`excludeComponents` support per-sub-component selection (band-only, prongs-only)? | Would require un-fusing `combined_metal` at export time or restructuring Atlas's fuse step | Not possible today — only the single `includeStoneReference` toggle exists | Low | No | Design work, likely deferred unless a real use case appears |
| `FOUNDRY-OQ-004` | Should a unified export-bundle endpoint be built? | Directly resolves `FOUNDRY-GAP-001`/`FOUNDRY-GAP-002` | Each artifact is a separate endpoint call today | Medium | No | Product decision, informed by real frontend usage patterns |
| `FOUNDRY-OQ-005` | Should `ArtifactRecord`/`ArtifactManifest` become real, returned objects rather than only a machine-readable spec? | Affects API surface growth vs. richer caller-side introspection | Not implemented — the HTTP response carries only filename/media-type/checksum header | Medium | No | Engineering decision, likely paired with `FOUNDRY-OQ-004` |
| `FOUNDRY-OQ-006` | Should re-import/roundtrip validation ever run at request time for high-stakes exports (e.g. a final "approved" export)? | Would trade latency for a stronger per-request integrity guarantee | Never runs at request time today — test-suite only | Low | No | Product decision, only relevant if/when a "final approval" export flow exists |
| `FOUNDRY-OQ-007` | Should JewelMind pursue a real, recorded `IMPORT_TESTED` result against FreeCAD? | Directly resolves `FOUNDRY-GAP-007`, the highest-priority remaining gap | No external CAD application has ever opened a JewelMind file | High | No | Requires only installing FreeCAD and running the test described in [`210-step-interoperability-boundaries.md`](210-step-interoperability-boundaries.md) |
| `FOUNDRY-OQ-008` | Should `ExportVersionFingerprint` be assembled and attached to every export response? | Directly resolves `FOUNDRY-GAP-003` | Each field is independently queryable but never assembled together | Low | No | Engineering decision, low cost if pursued |
| `FOUNDRY-OQ-009` | Should the 5 diagnostic codes with no real `AppError` mapping (`FOUNDRY_COMPONENT_MISSING`, `FOUNDRY_JSON_FAILED`, `FOUNDRY_SPEC_FAILED`, `FOUNDRY_TEMPFILE_ERROR`, `FOUNDRY_OPTION_UNSUPPORTED`) get dedicated exception classes? | Directly resolves `FOUNDRY-GAP-004` | These failure modes currently surface as generic, unclassified 500s if they ever occur | Low | No | Any future error-handling-refinement sprint |
| `FOUNDRY-OQ-010` | Should Windows reserved device names (`CON`, `PRN`, etc.) be rewritten by `sanitize_filename()`? | Closes the one known low-risk gap in [`206-filename-and-path-safety.md`](206-filename-and-path-safety.md) | Passes through unmodified today | Low | No | Small, safe fix — candidate for the next Sprint that touches `exporters/filenames.py` |
| `FOUNDRY-OQ-011` | Should a periodic janitor process sweep crash-orphaned export temp files? | Directly resolves `FOUNDRY-GAP-008` | Relies entirely on happy-path/`except` cleanup today | Low | No | Any future operations-hardening sprint |
| `FOUNDRY-OQ-012` | Should Foundry ever be responsible for a real mesh-level STL roundtrip check, and if so, is a new dependency justified? | Directly resolves `FOUNDRY-GAP-006`, but tension exists with FOUNDRY-GOV-014's "no fragile dependency" spirit | Only a structural header/size check exists today | Low | No | Requires a deliberate dependency-tradeoff decision, not a quick fix |

## What this document is not

Not a roadmap and not a set of recommendations disguised as questions — each provisional behavior is exactly what the code does today, so a future decision-maker starts from the true current state.
