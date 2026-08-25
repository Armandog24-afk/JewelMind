---
id: JM-BIBLE-330
title: Intent Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-331
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Governance

## INTENT-GOV-001 through INTENT-GOV-018

| ID | Rule |
|---|---|
| **INTENT-GOV-001** | Subjective language must never silently become numeric geometry. No code path in `backend/jewelmind/design_intent/` writes to a JDL dotted path; `IntentStatement.relatedJDLPaths` is always empty in v1 (verified by `test_designer_intent_integration.py::TestNoArbitraryNumericMapping`). |
| **INTENT-GOV-002** | Every intent statement must identify its target. `IntentStatement.target` is a required (non-optional) field in `design_intent/schemas.py`; `resolver.py` never constructs one without a real, normalized `IntentTarget`. |
| **INTENT-GOV-003** | Every intent statement must have provenance. `IntentStatement.provenance` is required; `service.py`'s pipeline always sets it to `AI_NORMALIZED` for a provider-sourced statement. |
| **INTENT-GOV-004** | Intent and JDL must remain separate models. `DesignIntent` (`design_intent/schemas.py`) and `JewelryDefinition` (`domain/schema.py`) share no fields; on the frontend, `useDesignIntentStore` and `useProjectStore` are two independent Zustand stores with no cross-dependency in either direction except a one-way `resetProject() -> clearIntent()` call. |
| **INTENT-GOV-005** | Unresolved intent must be preservable. `DesignIntent.unresolvedDescriptors` exists precisely for this — a descriptor JewelMind can't classify is kept verbatim, never discarded (see [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md)). |
| **INTENT-GOV-006** | Unsupported intent must not be silently discarded. An unrecognized target, concept, or descriptor value becomes an entry in `unresolvedDescriptors` with an `INTENT_UNKNOWN_DESCRIPTOR` diagnostic — never dropped without a trace. |
| **INTENT-GOV-007** | Conflicting intent must be explicit. `conflicts.py::detect_conflicts()` is real, runs on every request, and every resulting `IntentConflict` is both returned in `DesignIntent.conflicts` and rendered in the Studio review UI's "Conflicting intent" section. |
| **INTENT-GOV-008** | Intent strength must not be confused with geometric magnitude. `IntentStrength` (`OPTIONAL/PREFERRED/IMPORTANT/REQUIRED`) never influences a numeric value anywhere in the codebase — it exists purely as review-priority metadata. |
| **INTENT-GOV-009** | AI interpretation remains non-authoritative. Every `IntentStatement.provenance` a provider produces is `AI_NORMALIZED`, never a status implying authority; the real JDL/Forge gate for technical fields is entirely untouched by intent statements. |
| **INTENT-GOV-010** | Only deterministic approved mappings may automatically influence JDL. See [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md) — zero such mappings exist in v1, by design. |
| **INTENT-GOV-011** | Professional manufacturing rules do not belong in the intent model. No file under `design_intent/` references a manufacturing tolerance, density, or Forge-style threshold. |
| **INTENT-GOV-012** | Intent vocabulary must be versioned. `DesignIntent.version` (currently `"1.0.0"`) and `specs/design-intent/v1/vocabulary.json`'s own `version` field both exist for this; a future vocabulary change is a new version, never a silent edit. |
| **INTENT-GOV-013** | Language-specific synonyms must resolve to language-neutral canonical concepts. `vocabulary.py`'s synonym tables map both Italian and English words to the same canonical value (e.g. `"delicato"`/`"delicate"` both → `DELICATE`) — verified by the corpus's `MULTILINGUAL` category. |
| **INTENT-GOV-014** | Aesthetic concepts must not claim universal human meaning. Every concept category and value in `vocabulary.py`/`333-intent-vocabulary.md` is documented as a JewelMind software taxonomy, not a claimed universal truth about aesthetics — see [`051-professional-boundary`](../04-jewelry-domain/058-professional-validation-register.md)-style framing repeated in this Sprint's own governance. |
| **INTENT-GOV-015** | Intent resolution must remain reviewable. Every statement is rendered in Studio's "Design intent" review section before it is ever stored via `applyIntent()`; nothing is applied automatically. |
| **INTENT-GOV-016** | User-explicit technical values override subjective interpretations. A field present in `proposedFields` (Designer's technical channel) is never overridden by a same-named aesthetic statement — the two channels are structurally disjoint (`design_intent` never writes to `candidateJDL`). |
| **INTENT-GOV-017** | Existing JDL values must not be overwritten merely because an aesthetic descriptor is present. Confirmed by `TestNoArbitraryNumericMapping.test_bolder_never_increases_band_width_stone_diameter_or_prong_diameter` — a pure aesthetic MODIFY request leaves every existing JDL field byte-identical. |
| **INTENT-GOV-018** | Future intent-to-geometry profiles must have provenance and versioning. `IntentProfile` (`design_intent/schemas.py`) already requires `provenance`, `version`, and `professionalReview` fields even though no profile is registered yet — see [`355-intent-profile-model.md`](355-intent-profile-model.md). |

## When an ADR is required

Registering the first deterministic intent-to-JDL mapping (a real `IntentProfile` with a non-empty `jdlMapping`), letting Design Intent write directly to `candidateJDL`, or any change that violates INTENT-GOV-001 through 018 without superseding this document first.

## When an RFC is required

A new major semantic intent family beyond the 6 current concept categories, multi-turn intent negotiation, or a professionally-validated aesthetic profile library; see [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md).
