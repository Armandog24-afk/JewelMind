---
id: JM-BIBLE-179
title: Preview Generation Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-178
related_documents:
  - JM-BIBLE-144
implementation_status: current
professional_validation: not_required
normative: true
---

# Preview Generation Integration

Restates and cross-references Sprint 5's [`07-atlas/144-preview-mesh-contract.md`](../07-atlas/144-preview-mesh-contract.md) at the compiler-orchestration level — this document does not duplicate the mesh-tessellation detail, only where preview sits in the compilation flow.

## Current flow

`ModelService.generate()` → `write_component_previews(generated_model, definition, temp_dir)` → per-component STL files + a manifest dict, all inline, in the same call that produced the geometry. Component selection is implicit (every component in `GeneratedModel.components` is previewed, always). Tessellation options are the definition's own `preview.meshTolerance`/`angularTolerance`, with no per-request override.

## Result manifest

`ModelRecord.preview_manifest` — see [`178-artifact-manifest-contract.md`](178-artifact-manifest-contract.md).

## Failure independence from source B-Rep — currently absent

**This is the gap this Sprint keeps surfacing.** A tessellation failure for one component (hypothetical — never observed) would currently fail the entire `generate()` call, not just that one preview mesh. The B-Rep geometry itself would have been perfectly valid.

## Stale-model semantics and last-successful preview

Both are **frontend-only** concepts (`useProjectStore.ts`'s `isStale` and `lastSuccessfulPreview` fields) — the backend has no notion of preview staleness; every `generate()` call produces a fresh, complete preview manifest with no relationship to any previous one. This was already noted in Sprint 5's [`06-forge/107-export-precondition-rules.md`](../06-forge/107-export-precondition-rules.md) for exports; the same gap applies identically to preview.

## No frontend rendering redesign (as of Sprint 6)

Per Sprint 6's explicit instruction, this document did not propose or make any change to `frontend/src/components/ModelViewport.tsx` or `useComponentGeometries.ts` — it only documented where preview generation sits in the backend compilation flow.

## Sprint 8 update: the manifest gained explicit component-identity fields

`write_component_previews()` now also emits `geometryRole`, `productionRole`, `meshSource`, and `generationStatus` per component — a small, additive extension to the same manifest this document describes, made specifically so the frontend's new Vision layer never has to infer a component's role from its name. See [`10-vision/223-atlas-to-vision-contract.md`](../10-vision/223-atlas-to-vision-contract.md). This did not change the flow described above: the manifest is still produced inline inside `ModelService.generate()`, and the failure-independence gap noted above is unchanged.
