---
id: JM-BIBLE-015
title: Success Metrics
version: 1.0.0
status: draft
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-014
implementation_status: partial
---

# Success Metrics

This document is marked `draft` and `partial` deliberately: JewelMind has
no users beyond its own development and testing yet, so there is no real
usage data to report. What follows is the measurable, code-verifiable
state today, plus what would need to be instrumented to answer the
questions a founder or partner would actually ask next.

## What can be measured today (from the repository itself)

| Metric | Current value | Source |
|---|---|---|
| Backend automated test count | 139 | `cd backend && pytest -q` |
| Frontend automated test count | 41 | `cd frontend && npm run test` |
| Validation rules implemented | 16 | `docs/validation-rules.md` |
| Supported band profiles | 2 (flat, comfort-fit) | `docs/domain-model.md` |
| Supported prong counts | 2 (four, six) | `docs/domain-model.md` |
| Supported metals (cosmetic) | 5 | `docs/domain-model.md` |
| API endpoints | 9 | [`appendices/api-inventory.md`](../appendices/api-inventory.md) |
| CI jobs run per push/PR to `main` | 3 (backend, frontend, docker-smoke-test) | `.github/workflows/ci.yml` |

## What is not yet measured (requires instrumentation not present today)

These would need product analytics, error monitoring, or usage logging
that does not currently exist in JewelMind — none of the numbers below can
be honestly reported yet:

- How long a real user takes to go from opening the app to a successful
  export.
- How often generation fails for reasons other than validation errors
  (i.e. genuine `MODEL_GENERATION_FAILED` events) in real usage.
- How often a definition is regenerated after being marked stale versus
  abandoned.
- Any measure of whether an exported file was actually used downstream
  (JewelMind has no visibility past the download).

## Proposed direction for a future metrics document

When JewelMind has real users, this document should be revised (MAJOR
version bump, per `000-bible-governance.md`) to include: adoption
(distinct definitions generated), reliability (error rate by error code
from `appendices/api-inventory.md`), and completion (percentage of
generated models that reach a successful export). Until that
instrumentation exists, this document should not claim metrics it cannot
back with a data source.
