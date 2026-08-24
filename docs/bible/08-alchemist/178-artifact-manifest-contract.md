---
id: JM-BIBLE-178
title: Artifact Manifest Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-177
related_documents:
  - JM-BIBLE-A30
implementation_status: partial
professional_validation: not_required
normative: true
---

# Artifact Manifest Contract

The normative shape is `specs/alchemist/v1/artifact-manifest.schema.json`; real per-artifact entries for the default definition are in `specs/alchemist/v1/test-vectors/artifact-manifest-vectors.json`.

## No unified manifest exists

`ModelRecord.preview_manifest` is the only real, current manifest, and it covers `PREVIEW_MESH` only — there is no aggregate structure that also lists STEP/STL/JSON/specification results, because those artifacts are never generated as a batch; each is a separate on-demand call with its own independent response.

## Field mapping

| Field | Status |
|---|---|
| `artifactId` | PLANNED — no current artifact has a distinct ID |
| `artifactType` | CURRENT, implicit — determined by which endpoint was called |
| `status` | CURRENT, implicit — HTTP 200 vs. an error status |
| `filename` | CURRENT — `sanitize_filename(project.name) + extension` |
| `mimeType` | CURRENT — `application/step`, `model/stl`, `application/json`, `text/markdown` |
| `byteSize` | PLANNED — never reported as a structured field |
| `sourceDefinitionHash` | CURRENT — implicit via `modelId` |
| `compilationHash` | PLANNED |
| `includedComponents` / `excludedComponents` | CURRENT, implicit — `includeStoneReference` determines this, but it is never itself returned as an explicit list |
| `generationDuration` | PLANNED — no per-artifact timing exists |
| `warnings` | CURRENT for `PREVIEW_MESH` (per-component `warnings` in the manifest); **not returned at all** for STEP/STL/JSON/specification exports |
| `error` | CURRENT, implicit — via the HTTP error envelope, not a field on a successful manifest entry |
| `createdAt` | PLANNED for exports; CURRENT for the underlying model (`ModelRecord.generated_at`) |

## Internal temporary paths are never exposed

Confirmed by inspection: every export response uses `FileResponse`/`Response` with a caller-facing `filename`, never the server-side temp path (`tempfile.mkstemp()`'s raw path) — this was already a hardening-sprint fix from the original build phase, reconfirmed here as still correct.

## Real example, condensed

From `specs/alchemist/v1/test-vectors/artifact-manifest-vectors.json`: `PREVIEW_MESH` for `band` → `band.stl`, `model/stl`; `STEP` for the default definition → `includedComponents: ["band", "prongs", "basket_support"]`, `excludedComponents: ["stone_reference"]` — matching LAW-006's default exclusion exactly.
