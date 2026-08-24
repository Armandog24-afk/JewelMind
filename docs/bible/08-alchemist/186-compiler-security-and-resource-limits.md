---
id: JM-BIBLE-186
title: Compiler Security and Resource Limits
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-184
related_documents:
  - JM-BIBLE-083
implementation_status: current
professional_validation: not_required
normative: true
---

# Compiler Security and Resource Limits

Restates and extends Sprint 3's [`05-jdl/083-security-and-resource-limits.md`](../05-jdl/083-security-and-resource-limits.md) at the compiler-orchestration level — no protection documented there has changed; this document adds the compiler-specific angles that document didn't cover.

| Risk | Current status |
|---|---|
| Huge JDL payloads | **NOT MITIGATED** — same finding as Sprint 3; no request body size limit exists |
| Pathological dimensions | PARTIAL — `allow_inf_nan=False` blocks non-finite values; finite-but-extreme values are not structurally capped (Sprint 3 finding, unchanged) |
| Geometry-operation denial of service | **NOT MITIGATED** — no generation timeout exists; an extreme-but-valid dimension could in principle produce an expensive OCCT operation with no cutoff |
| Excessive tessellation detail | PARTIAL — `meshTolerance`/`angularTolerance` require `gt=0`, but no upper bound on how small (expensive) a tolerance can be requested |
| Excessive simultaneous compilation | **NOT MITIGATED** — no concurrency limit or request queue exists; FastAPI/uvicorn's own default worker model is the only bound, not a JewelMind-specific control |
| Cache exhaustion | **MITIGATED** — `MAX_CACHED_MODELS = 20` with LRU eviction |
| Temporary-file exhaustion | **MITIGATED** — unique per-request export temp files, `BackgroundTask`-scheduled deletion, plus eviction-time `shutil.rmtree` for preview directories |
| Artifact request abuse | **NOT SEPARATELY MITIGATED** — no rate limit exists on export endpoints beyond the shared cache/temp-file protections above |
| Path traversal | **MITIGATED** — `exporters/filenames.py::sanitize_filename()` |
| Repeated failing jobs | **NOT MITIGATED** — no backoff, retry limit, or failure-rate tracking exists; a caller can retry a failing generation indefinitely |

## Nothing new introduced or fixed

Per this Sprint's explicit scope, this document only restates and organizes existing findings (most already recorded in Sprint 3) at the compiler-orchestration angle — no new protection was added, and no new gap beyond what Sprint 3 already identified was discovered in this Sprint's inspection.
