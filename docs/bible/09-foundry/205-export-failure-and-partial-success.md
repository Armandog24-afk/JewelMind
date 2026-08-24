---
id: JM-BIBLE-205
title: Export Failure and Partial Success
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-204
related_documents:
  - JM-BIBLE-173
implementation_status: planned
professional_validation: not_required
normative: true
---

# Export Failure and Partial Success

## The target vocabulary

| Overall status | Meaning |
|---|---|
| `ALL_REQUESTED_SUCCEEDED` | Every requested artifact generated and passed its integrity checks |
| `PARTIAL_SUCCESS` | At least one non-required artifact failed, but every required artifact succeeded |
| `FAILED_REQUIRED_ARTIFACT` | At least one required artifact failed, regardless of the others' outcomes |
| `NO_ARTIFACTS_GENERATED` | Nothing was requested, or every request failed |

Full outcome vectors, covering every combination of required/optional × succeeded/failed, are in `specs/foundry/v1/test-vectors/partial-success-vectors.json`.

## Current reality: no code computes this vocabulary

**No current code returns any of these four values explicitly.** Each of the 4 export endpoints is called and evaluated completely independently by the caller — typically the frontend, issuing separate HTTP requests for STEP and STL. The caller (not JewelMind's backend) is the one that currently determines "partial success" by observing which of its own independent calls succeeded or failed. This is the identical finding Sprint 6 made at the compilation level for preview-vs-export coupling — see [`08-alchemist/173-partial-compilation-policy.md`](../08-alchemist/173-partial-compilation-policy.md) — restated here for artifact-level requests specifically.

## Why this matters even though nothing is broken today

A future unified "export bundle" endpoint (requesting STEP + STL + JSON + specification in one call) would need this vocabulary to report back honestly which artifacts succeeded. Building that endpoint without first deciding this vocabulary risks exactly the failure mode FOUNDRY-GOV-017 warns against: reporting "success" for a response that silently omitted a required file. This document exists so that decision is made deliberately, in advance, rather than accidentally when the endpoint is eventually built.

## No `required` flag exists today

Every current request is implicitly "required" in the sense that a failure always raises an exception the caller must handle — there is no artifact type today that fails "softly." The `required: true/false` distinction only becomes meaningful once multiple artifacts can be requested together; seeing [`193-artifact-request-contract.md`](193-artifact-request-contract.md) for the same PLANNED status on the request side.
