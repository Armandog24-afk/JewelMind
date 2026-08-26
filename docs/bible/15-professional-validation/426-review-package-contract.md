---
id: JM-BIBLE-426
title: Review Package Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-425
  - JM-BIBLE-446
  - JM-BIBLE-447
implementation_status: current
professional_validation: not_required
normative: true
---

# Review Package Contract

This document is the real, implemented contract of `backend/jewelmind/professional_validation/review_package.py::build_review_package()` — every file it lists below is produced by that real function, verified by reading its source, not inferred.

## What every package contains

| File | Produced by | Purpose |
|---|---|---|
| `README.md` | `_readme_text()` | Explains what JewelMind is, what's being reviewed, known prototype limitations, and that current software validation is not manufacturability certification. States plainly whether the stone reference is included or excluded in *this* package. |
| `review-form.md` | `_review_form_text()` | The exact 10 non-leading questions from the original brief, plus open "observations" and "overall assessment" sections — no scoring system. |
| `design.json` | `model_service.export_json_text()` — the SAME real Foundry (Sprint 7) JSON exporter, not a new one | The canonical `JewelryDefinition` for this exact model. |
| `technical-specification.md` | `model_service.export_specification_text()` — the SAME real Foundry specification builder | The full technical specification, including its permanent manufacturing-readiness disclaimer. |
| `forge-report.json` | `_forge_report()` | The real `record.validation_results` (every Forge rule outcome for this model) plus the real Forge registry version. |
| `geometry-metadata.json` | `_geometry_metadata()` | Real values from the generated `GeneratedModel`: definition hash, generator version, generation duration, per-component volumes, combined metal volume, bounding box, warnings. |
| `component-manifest.json` | Built inline in `build_review_package()` from `record.preview_manifest` | Which named components exist and their geometry role. |
| `model.step` | `model_service.export_step_file()` — the SAME real Foundry STEP exporter | The real solid geometry, re-tessellated fresh, never read back from a cached mesh (ATLAS-GOV-009). |
| `model.stl` | `model_service.export_stl_file()` — the SAME real Foundry STL exporter | The real tessellated mesh. |
| `manifest.json` | `ReviewPackageManifest.model_dump_json()` | The package's own real SHA-256 checksum for every file above, plus known limitations. |

## What is deliberately not included

`presentation.png` is not produced by the backend generator. This is documented honestly in the real generated manifest, quoted directly from `review_package.py`:

> `"presentation.png (Vision capture is browser-only; not produced by the backend)"`

Vision's Presentation-View capture (Sprint 8) is a client-side canvas screenshot — there is no server-side rendering pipeline to reproduce it from, and this document does not pretend otherwise (ATLAS-GOV/VISION-GOV boundary preserved).

## Known limitations, stated inside every package

Also quoted directly from the real generated manifest:

> `"Prong/basket geometry is a simplified prototype, not a reviewed setting design."`
> `"No external CAD import of this exact package has been professionally verified."`

## This is not a replacement for Foundry's exports

`POST /api/professional-validation/review-package` (`backend/jewelmind/api/routes.py::review_package_route`) is an **additional** bundling capability, layered entirely on top of Foundry's existing per-artifact export endpoints (`/api/models/export/step`, `/export/stl`, `/export/json`, `/specification`, all unchanged since Sprint 7). It introduces zero new export-format logic and zero new geometry-generation logic — every byte of `model.step`/`model.stl`/`design.json`/`technical-specification.md` content is byte-for-byte identical to what those existing endpoints would produce for the same `modelId` and `includeStoneReference` setting. See [`446-review-package-generation.md`](446-review-package-generation.md) for the generation mechanics.

## Cross-references

- [`425-review-case-model.md`](425-review-case-model.md) — the reproducible unit a package is generated for.
- [`446-review-package-generation.md`](446-review-package-generation.md) — how the ZIP is actually assembled, checksummed, and cleaned up.
- [`447-studio-professional-review-mode.md`](447-studio-professional-review-mode.md) — the real Studio UI that triggers this.
- `specs/professional-validation/v1/review-package-manifest.schema.json` — the manifest's machine-readable shape.
