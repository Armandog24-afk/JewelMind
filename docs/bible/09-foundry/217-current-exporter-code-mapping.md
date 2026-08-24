---
id: JM-BIBLE-217
title: Current Exporter Code Mapping
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-183
related_documents:
  - JM-BIBLE-A39
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Exporter Code Mapping

## Every export-adjacent file, classified

| File | Classification | Notes |
|---|---|---|
| `exporters/step_exporter.py` | FOUNDRY | As of this Sprint, no longer imports `cadquery` directly — delegates shape selection to `exporters/selection.py`. |
| `exporters/stl_exporter.py` | FOUNDRY | Same change; also reads `JewelryDefinition.preview.meshTolerance`/`angularTolerance`, a JDL-owned value, but only as a pass-through default, never interpreting it. |
| `exporters/selection.py` | FOUNDRY, with one named CAD-kernel exception | New this Sprint. Owns `cq.Compound.makeCompound()` — the one currently-tolerated exception named in [`08-alchemist/168-atlas-execution-contract.md`](../08-alchemist/168-atlas-execution-contract.md) and CLAUDE.md's ALCHEMIST RULES, now consolidated into a single, explicitly-documented location instead of duplicated across two files. |
| `exporters/json_exporter.py` | FOUNDRY | Clean — no geometry, no cadquery import. |
| `exporters/specification.py` | FOUNDRY | Clean — reads already-computed `GeneratedModel`/`ValidationResult` values, never recomputes them. |
| `exporters/filenames.py` | FOUNDRY | Clean — pure string sanitization. |
| `exporters/integrity.py` | FOUNDRY | New this Sprint. Clean — file-level checks only (`hashlib`, `struct`, `pathlib`), no geometry or jewelry-domain logic. |
| `services/model_service.py::export_step_file()`/`export_stl_file()` | MIXED (API/FOUNDRY/ATLAS-adjacent) | Orchestrates temp-path allocation (Alchemist-like), calls into Foundry exporters, and now (Sprint 7) calls `validate_non_empty()` directly rather than the exporters doing so themselves — a deliberate choice, not an oversight: the exporter functions stay pure (shape in, file out), while integrity validation is a caller-level concern, matching how `ModelService` already owns cache/temp-directory lifecycle. |
| `api/routes.py`'s export routes | API/FOUNDRY-adjacent | Computes `sha256_checksum()` and attaches it as a response header — a thin, correctly-scoped API-layer use of a Foundry-owned function, not a duplication of Foundry logic. |

## Resolving part of Sprint 6's finding

Sprint 6's [`183-current-backend-to-compiler-mapping.md`](../08-alchemist/183-current-backend-to-compiler-mapping.md) counted **3 mixed-responsibility modules**: `ModelService.generate()`, `step_exporter.py`, and `stl_exporter.py` — the latter two specifically because each independently imported `cadquery` and called `cq.Compound.makeCompound()` inline, duplicating identical logic. This Sprint's extraction of `selection.py` resolves that specific finding for both files: neither imports `cadquery` any longer, and the one CAD-kernel operation both needed is now a single, named, tested, documented function — the same "tolerated exception" CLAUDE.md already anticipated, just no longer duplicated. **Mixed-responsibility modules remaining: 1** (`ModelService.generate()`, unchanged — out of this Sprint's explicitly scoped hardening list, and still correct/fully tested, just architecturally concentrated).

## Not touched, and why

`ModelService.generate()`'s coupling of preview generation to core geometry generation (Sprint 6's other major finding) is unchanged. Untangling that coupling is a larger behavioral change than this Sprint's "preserve existing behaviour" constraint permits — it remains tracked in [`08-alchemist/187-alchemist-gap-analysis.md`](../08-alchemist/187-alchemist-gap-analysis.md), not re-solved here.
