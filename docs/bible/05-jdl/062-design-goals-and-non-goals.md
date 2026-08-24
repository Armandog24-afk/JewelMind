---
id: JM-BIBLE-062
title: JDL Design Goals and Non-Goals
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-060
  - JM-BIBLE-061
related_documents:
  - JM-BIBLE-JDL-README
implementation_status: partial
professional_validation: not_required
normative: true
---

# JDL Design Goals and Non-Goals

## Goals

1. Give every JDL field a single authoritative definition (type, unit, default, required/optional/derived status) shared by frontend, backend, and specification.
2. Make Canonical JSON round-trippable: parse, canonicalize, hash, re-serialize without loss.
3. Keep structural validation and semantic/business-rule validation as two separately testable layers (see [`075-validation-pipeline.md`](075-validation-pipeline.md)).
4. Make geometry generation from a JDL Canonical Document fully deterministic (JDL-GOV-010).
5. Make every diagnostic a stable, namespaced code, not a free-text string alone (see [`080-errors-warnings-and-diagnostics.md`](080-errors-warnings-and-diagnostics.md)).
6. Define an explicit, additive path for future ring styles, stone shapes, setting types, and export formats without breaking `schemaVersion: "0.1.0"` documents (see [`082-extension-and-capability-model.md`](082-extension-and-capability-model.md)).
7. Keep the stone reference formally distinct from production metal at the language level, not only in geometry code (see LAW-006 and [`064-canonical-document-model.md`](064-canonical-document-model.md)).
8. Make units unambiguous: millimeters for length everywhere, with angular tolerance's unit (radians) explicitly documented rather than assumed (see [`071-units-and-numeric-model.md`](071-units-and-numeric-model.md)).
9. Give every example document (valid or invalid) a documented, single, correct reason for its validity status (see [`jdl-example-index.md`](../appendices/jdl-example-index.md)).
10. Make conformance testable in layers (JDL-READER, JDL-VALIDATOR, JDL-COMPILER, JDL-EXPORTER, JDL-FULL-V1) so a future non-JewelMind implementation has a target to test against (see [`085-conformance-and-test-vectors.md`](085-conformance-and-test-vectors.md)).
11. Document every open language decision explicitly rather than resolving it by implicit default (see [`086-open-jdl-questions.md`](086-open-jdl-questions.md)).
12. Keep JDL specification files (`specs/jdl/v1/`) mechanically checkable against the running implementation, not just prose (see `backend/tests/test_jdl_schema_examples.py`).

## Non-goals

1. **No executable code inside a JDL document** — no expressions, scripts, macros, or functions, in any representation, present or future.
2. **No arbitrary external network references** — a JDL document cannot point at a remote resource for the compiler to fetch at generation time.
3. **Not automatically certifying manufacturability** — passing every JDL validation layer never means a qualified jewelry professional has reviewed the result (see [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md) and LAW-010).
4. **No new ring style, stone shape, or setting type introduced by this Sprint** — JDL v1 formalizes exactly the current solitaire/round/prong surface; extension is a documented *mechanism*, not new content.
5. **No new geometry feature or component.**
6. **No AI-driven geometry generation, now or as a JDL-level capability** — see LAW-003.
7. **No authentication, payments, subscriptions, or multi-user collaboration model** introduced via JDL fields.
8. **No production textual-DSL parser in this milestone** — `specs/jdl/v1/jdl.ebnf` is grammar only.
9. **No production YAML parser in this milestone** — [`066-yaml-serialization-contract.md`](066-yaml-serialization-contract.md) is a contract for a future implementer, not running code.
10. **No silent unit conversion** — a document is always interpreted in millimeters; JDL never guesses or converts from another unit system.
11. **No hidden defaults invented for this Sprint** — every default value documented in this section is the literal Pydantic/TypeScript default already in the codebase, never a new number chosen to make the specification look complete.
12. **No refactor of working application code to make the specification match more cleanly** — discrepancies are documented (see [`084-current-implementation-mapping.md`](084-current-implementation-mapping.md) and `SPRINT-3-VALIDATION-REPORT.md`), not silently patched over except for the narrow, explicitly-flagged exceptions allowed by the Sprint 3 brief.
