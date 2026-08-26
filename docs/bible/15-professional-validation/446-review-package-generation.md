---
id: JM-BIBLE-446
title: Review Package Generation
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-425
  - JM-BIBLE-447
  - JM-BIBLE-448
implementation_status: current
professional_validation: not_required
normative: false
---

# Review Package Generation

This document describes the **generation mechanics** of a Professional
Review Package — how `build_review_package()`
(`backend/jewelmind/professional_validation/review_package.py`) actually
produces the ZIP a reviewer downloads. It does not restate the package's
full content contract (the file list, checksums, and manifest shape),
which belongs to the not-yet-written
`426-review-package-contract.md`; this document is scoped strictly to
control flow, staleness protection, and cleanup.

## Entry point

```
build_review_package(model_service, model_id, *, case_id, include_stone_reference=True)
    -> tuple[Path, ReviewPackageManifest]
```

Called from `backend/jewelmind/api/routes.py::review_package_route`
(`POST /api/professional-validation/review-package`), which itself first
calls `model_service.get_record(payload.modelId)` before invoking
`build_review_package()` — so a caller referencing an unknown `modelId`
fails before any package generation is attempted at all.

## Step 1: fetch the live model record first — the stale-model protection

The very first line of `build_review_package()`'s body is:

```python
record = model_service.get_record(model_id)
```

`ModelService.get_record()` raises `ModelNotFoundError` if `model_id`
does not correspond to an already-generated, in-memory model record. This
is the mechanism — not a separate staleness flag on the backend — that
prevents a review package from ever being built against a model that no
longer exists server-side. Because `model_id` is itself derived from the
generated model's content hash (per `jewelmind.utils.hashing.definition_hash`),
there is no server-side concept of "the same model, but now stale" to
protect against independently: a stale design in the frontend simply
produces a *different* `model_id` once regenerated, and the old
`model_id` either still points at the old (still internally consistent)
record or has been evicted, in which case `get_record()` fails cleanly.
The actual "does this match what's currently on screen" staleness check
is the frontend's `isStale` flag in `useProjectStore`
(`frontend/src/store/useProjectStore.ts`), gating whether the button is
even clickable in the first place — see
[`447-studio-professional-review-mode.md`](447-studio-professional-review-mode.md).
`backend/tests/test_review_package.py::TestStaleModelProtection::test_a_model_id_with_no_live_record_is_rejected`
verifies the backend-side half of this directly.

## Step 2: reuse the same real Foundry exporters — no new export logic

`build_review_package()` produces its STEP/STL/JDL/technical-specification
artifacts by calling the exact same `ModelService` methods every other
export endpoint calls:

```python
exported_step = model_service.export_step_file(model_id, include_stone=include_stone_reference)
exported_stl = model_service.export_stl_file(model_id, include_stone=include_stone_reference)
jdl_text = model_service.export_json_text(model_id)
spec_text = model_service.export_specification_text(model_id)
```

There is no separate STEP/STL-writing code path inside
`professional_validation/` — this module is a consumer of Foundry's
existing exporters, never a reimplementation of them. This is the direct
mechanical enforcement of CLAUDE.md's "never fake an export" rule and
FOUNDRY-GOV-002/008 at this specific call site: whatever a reviewer opens
in `model.step`/`model.stl` is byte-for-byte the same real CadQuery/
OpenCascade output any other export button would have produced for the
same `modelId` and `includeStoneReference` value.

## Step 3: assemble the non-exported content

Alongside the four reused exports, `build_review_package()` builds five
more package members directly from already-computed, real data — never
fabricated:

- `README.md` / `review-form.md` — generated prose (`_readme_text()`,
  `_review_form_text()`), including an explicit stone-inclusion note that
  branches on the real `include_stone_reference` value.
- `forge-report.json` — `_forge_report()` reads
  `record.validation_results` (the real Forge results already computed
  when the model was generated) and `_forge_registry_version()` (reads
  `specs/forge/v1/current-rule-registry.json::registryVersion` directly
  off disk, falling back to `"unknown"` only on an `OSError`).
- `geometry-metadata.json` — `_geometry_metadata()` reads real fields off
  `record.generated_model` (`definition_hash`, `generator_version`,
  `generation_duration_s`, `component_volumes()`,
  `combined_metal_volume_mm3`, `bounding_box.as_dict()`, `warnings`) —
  every value the actual geometry generation call already produced, never
  recomputed or approximated here.
- `component-manifest.json` — built from `record.preview_manifest`, the
  same manifest the frontend viewer consumes (VISION-GOV-011).

## Step 4: real SHA-256 checksums

For every entry already assembled (`entries: dict[str, bytes]`), the
function computes:

```python
digest = hashlib.sha256(content).hexdigest()
```

and records `ReviewPackageFile(name=name, sha256=digest, sizeBytes=len(content))`
for each one, before finally serializing `manifest.json` itself (which is
therefore the one file in the ZIP that is not, and cannot be, checksummed
against itself). `backend/tests/test_review_package.py::TestReviewPackageChecksums::test_every_included_file_checksum_matches_its_real_content`
and `test_checksums_dict_matches_included_files_list` verify these are
real digests of the real bytes written into the ZIP, not placeholder
values.

## Step 5: a real ZIP, written via `zipfile`

```python
fd, raw_zip_path = tempfile.mkstemp(prefix=f"jewelmind_{model_id}_review_", suffix=".zip")
os.close(fd)
zip_path = Path(raw_zip_path)
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for name, content in entries.items():
        zf.writestr(name, content)
```

The manifest (which needs every other file's checksum first) is added to
`entries` after the checksum loop, then written into the same ZIP —
so the ZIP handle is only ever opened once, with the complete, final file
set. `backend/tests/test_review_package.py::TestReviewPackageGeneration::test_zip_exists_and_is_non_empty`
and `test_all_required_artifacts_are_present` confirm the produced file is
a real, non-empty archive containing every expected member.

## Step 6: cleanup happens in a `finally` block, regardless of outcome

```python
finally:
    if exported_step is not None:
        exported_step.unlink(missing_ok=True)
    if exported_stl is not None:
        exported_stl.unlink(missing_ok=True)
```

The two temporary export files (`exported_step`, `exported_stl`) that
Foundry's exporters wrote to disk are deleted here whether generation
succeeded or raised — the `finally` block runs on both paths. This
mirrors FOUNDRY-GOV-015 ("clean up every temporary file ... on both the
success and failure path") applied specifically to the review-package
call site. Any failure anywhere in the `try` block is caught by a single
`except Exception` and re-raised as one honest
`ReviewPackageGenerationFailedError` — never a partial, silently-truncated
package.

## The ZIP itself is cleaned up after the HTTP response, the same way every export is

`review_package_route` returns the ZIP via `FileResponse(..., background=BackgroundTask(_delete_file, zip_path))` — identical to the pattern
`api/routes.py` already uses for STEP/STL exports. The ZIP file therefore
never persists on disk past the response completing; see
[`448-validation-security-and-privacy.md`](448-validation-security-and-privacy.md)
for the privacy implication of this.

## Cross-references

- [`447-studio-professional-review-mode.md`](447-studio-professional-review-mode.md) — the frontend surface that calls this endpoint.
- [`448-validation-security-and-privacy.md`](448-validation-security-and-privacy.md) — what happens to the generated ZIP after the response.
- `backend/jewelmind/professional_validation/review_package.py`, `backend/tests/test_review_package.py` (14 tests), `backend/tests/test_review_package_api.py` (5 tests).
