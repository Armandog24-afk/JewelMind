---
id: JM-BIBLE-200
title: Technical Specification Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-079
related_documents:
  - JM-BIBLE-005
implementation_status: current
professional_validation: not_required
normative: true
---

# Technical Specification Contract

## Current format, exactly

`build_specification(definition, model, validation_results, generated_at) -> str` in `backend/jewelmind/exporters/specification.py` produces a single Markdown (`.md`) document with these sections, in order: title, schema version, generator version, generated-at timestamp, definition hash, units; Ring; Band; Stone (explicitly labeled "reference only, not a gemological reproduction"); Setting; Material & manufacturing; Model volumes (per-component plus the combined-metal figure); Bounding box; Validation results; Known generation warnings; and the professional-review disclaimer (`PROFESSIONAL_REVIEW_NOTICE` from `jewelmind.domain.disclaimer`).

- **`generated_at` is threaded through explicitly, never re-computed at export time** — repeated downloads of the same cached model produce byte-identical specification text. This was a targeted hardening fix from an earlier sprint and remains a load-bearing invariant Foundry preserves.
- **Stone inclusion**: dimensions only (diameter, depth), always present, always metadata — never a metal-volume figure, and the stone is never included in the "Model volumes" section's combined-metal number.
- **This is documentation, not a certification.** The document must never claim professional manufacturing certification, a licensed engineer's sign-off, or compliance with any named industry standard unless a real entry exists in [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md) — today, no such entry exists for any threshold this document reports.

## Why Markdown, and why this is honestly PARTIAL as a "specification"

The current format is plain Markdown text, chosen for simplicity and human readability, not for interchange with any external documentation or PLM system. It is not a structured, machine-parseable specification format (no schema governs its prose sections), and it is not paginated, versioned as a document series, or digitally signed. Anyone calling this artifact a "technical specification" in the professional engineering-document sense should understand it as PARTIAL relative to that expectation — accurate and complete for what it reports, but a simple generated report, not a formal deliverable.

## Never a placeholder

`build_specification()` always computes every reported value (volumes, bounding box, validation results) from the real `GeneratedModel` and real `validate_definition()` output passed into it — no section is ever templated with a sample or hardcoded value.
