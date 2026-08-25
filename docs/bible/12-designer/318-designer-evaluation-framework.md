---
id: JM-BIBLE-318
title: Designer Evaluation Framework
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-317
related_documents:
  - JM-BIBLE-319
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Evaluation Framework

## The 9 metrics

1. **`FIELD_EXTRACTION_ACCURACY`** — did the correct JDL field/value get proposed for a request that specifies one.
2. **`ENUM_NORMALIZATION_ACCURACY`** — did a synonym (e.g. "oro giallo") correctly map to its canonical enum value.
3. **`UNSUPPORTED_FEATURE_RECALL`** — was a genuinely unsupported concept (halo, pavé, trilogy, ...) actually caught and reported, not silently missed.
4. **`HALLUCINATED_FIELD_RATE`** — how often a field or enum value reaches the candidate JDL that the schema does not actually support.
5. **`CLARIFICATION_PRECISION`** — was a clarification only raised for genuine ambiguity, not for something that had one clear answer.
6. **`PRESERVATION_OF_UNSPECIFIED_FIELDS`** — on a `MODIFY`, did every field the request didn't touch survive unchanged into the candidate.
7. **`VALID_JDL_RATE`** — what fraction of candidates pass `JewelryDefinition.model_validate()` rather than becoming `INVALID`.
8. **`FORGE_PASS_RATE`** — what fraction of valid candidates also pass Forge without errors.
9. **`USER_CORRECTION_RATE`** (future, needs real usage data) — how often a user edits or rejects a proposal after review, which requires real production usage telemetry that does not exist yet (see [`316-designer-observability.md`](316-designer-observability.md)).

## The 62-case corpus as a first deterministic proxy

`backend/tests/test_designer_corpus.py`'s corpus (see [`designer-test-case-catalog.md`](../appendices/designer-test-case-catalog.md)) is not a formal evaluation harness scoring these nine metrics numerically, but its 11 categories already exercise several of them directly as pass/fail assertions: `EXACT_SUPPORTED`/`SUPPORTED_SYNONYM`/`MULTI_FIELD` cases assert metric 1 and 2 by construction; `UNSUPPORTED`/`PARTIALLY_SUPPORTED` cases assert metric 3; `AMBIGUOUS` cases assert metric 5; `MODIFY_EXISTING` cases assert metric 6; `INVALID_NUMERIC` cases assert a controlled failure path relevant to metric 7. Every corpus case, by running through `_apply_patch()` and `validate_definition()`, also implicitly checks metrics 7 and 8 for that input.

## `HALLUCINATED_FIELD_RATE` is provably zero — the single most critical metric

Unlike the other eight, this metric is not merely measured favorably by the corpus — it is structurally impossible to violate against any input, corpus or otherwise. `capability.py::is_known_field()` and `normalizer.normalize_enum_token()` gate every field and enum value a candidate JDL patch can ever contain (DESIGNER-GOV-004); a value that fails either gate becomes a `DESIGNER_CAPABILITY_MISMATCH` diagnostic or an `UnsupportedFeature`, never a patched field. This means `HALLUCINATED_FIELD_RATE` is zero not because the 62 test cases happen not to trigger a hallucination, but because the architecture makes a hallucinated field unable to reach the candidate JDL regardless of what a provider (real or fake) returns — including a hypothetical future live model behaving unpredictably. This is why it is called out as the single most critical metric in this framework: every other metric measures how *good* Designer's interpretation is, but this one measures whether Designer can ever be *unsafe*, and the answer current architecture guarantees is no.

See [`319-designer-test-corpus.md`](319-designer-test-corpus.md) for the corpus itself, and [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md) for `USER_CORRECTION_RATE`'s dependency on real usage data that doesn't exist yet.
