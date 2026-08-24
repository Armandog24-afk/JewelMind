---
id: JM-BIBLE-184
title: Compiler Observability
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-170
related_documents: []
implementation_status: planned
professional_validation: not_required
normative: true
---

# Compiler Observability

## Proposed structured events (none implemented)

`COMPILATION_STARTED`, `NORMALIZATION_COMPLETED`, `FORGE_EVALUATED`, `PLAN_CREATED`, `COMPONENT_STARTED`, `COMPONENT_COMPLETED`, `COMPONENT_FAILED`, `INSPECTION_COMPLETED`, `ARTIFACT_STARTED`, `ARTIFACT_COMPLETED`, `ARTIFACT_FAILED`, `COMPILATION_COMPLETED`, `COMPILATION_FAILED`.

Each conceptually carries: `requestId`, `compilationId`, `definitionHash`, `stage`, `component`, `duration`, `status`.

## Current observability, exactly

`backend/jewelmind/utils/logging.py` provides `get_logger()` (structlog-based); `services/model_service.py` emits exactly one structured log event per generation: `logger.info("model_generated", model_id=..., duration_s=..., warnings=len(...))`. **No other stage of the pipeline emits any structured event today** — no `COMPONENT_STARTED`/`COMPONENT_COMPLETED` per builder, no `ARTIFACT_STARTED`/`ARTIFACT_COMPLETED` per export, no `FORGE_EVALUATED` event distinct from the HTTP response itself.

## No private design contents logged

Confirmed: the one current log event logs only `model_id` (a hash, not the definition itself), a duration, and a warning count — never the definition's field values (`project.name`, dimensions, etc.). Any future event instrumentation should preserve this discipline: log identifiers and metrics, never design content, per general privacy-by-default practice (this codebase has no user-account model, but a project name is still user-authored free text worth not logging by default).

## Not implemented in this Sprint

Per this Sprint's explicit scope, no new logging call was added — this document defines a target event vocabulary for a future observability pass, not a change made now.
