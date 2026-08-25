---
id: JM-BIBLE-A58
title: "Appendix: Designer Clarification Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGNER-README
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-299
  - JM-BIBLE-300
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Designer Clarification Catalog

## The 3 `AmbiguityLevel` values and the real code path that produces each

| `AmbiguityLevel` | Producing code path |
|---|---|
| `HIGH_IMPACT_AMBIGUITY` | (a) `service.py::_build_proposal()`'s bare-metal-term branch, when `normalizer.normalize_enum_token()` returns `is_ambiguous=True` (e.g. "gold"/"oro"); (b) a provider-reported `RawAmbiguity` whose `field` is `capability.is_known_field(...) == True`; (c) a provider-reported `RawClarification` that carries at least one `options` entry |
| `UNSUPPORTED_AMBIGUITY` | (a) a provider-reported `RawAmbiguity` whose `field` is **not** a known JDL field (`capability.is_known_field(...) == False`); (b) a provider-reported `RawClarification` with an empty `options` list |
| `LOW_IMPACT_AMBIGUITY` | Defined in `schemas.py` but not constructed anywhere in `service.py` today — no current code path distinguishes a "low impact" ambiguity from a high-impact one; every ambiguity the pipeline currently produces is either `HIGH_IMPACT_AMBIGUITY` or `UNSUPPORTED_AMBIGUITY` |

## Real example clarification cases, from `backend/tests/test_designer_corpus.py`'s `AMBIGUOUS` category (5 cases)

| Corpus case ID | Request text | What triggers the clarification |
|---|---|---|
| `ambig-01` | "Fammi un anello d'oro." | Provider extracts `material.metal = "gold"`; `AMBIGUOUS_METAL_TERMS` in `normalizer.py` recognizes bare "gold"/"oro" as ambiguous and refuses to guess a canonical metal |
| `ambig-02` | "I want a gold ring." | Same bare-"gold" path as `ambig-01`, English phrasing |
| `ambig-03` | "un anello d'oro con sei griffe" | Same bare-"oro" ambiguity, alongside an unrelated, successfully-normalized `setting.prongCount = "sei"` (6) — the proposal still surfaces both the clarification and the extracted prong count |
| `ambig-04` | "metal: gold or maybe rose?" | Provider directly reports a `RawAmbiguity(field="material.metal", candidateValues=["yellow_gold_18k", "rose_gold_18k"])`; asserted `proposalStatus == "NEEDS_CLARIFICATION"` |
| `ambig-05` | "band profile, not sure which" | Provider reports a `RawAmbiguity(field="band.profile", candidateValues=["comfort_fit", "flat"])` |

`backend/tests/test_designer.py::TestAmbiguity::test_bare_gold_triggers_clarification_not_a_guess` additionally asserts the exact clarification question shape for the bare-"gold" case: `question.field == "material.metal"` and `question.options` equal to the full 5-value metal capability set (`{"yellow_gold_18k", "white_gold_18k", "rose_gold_18k", "platinum", "silver"}`) — i.e. the clarification always offers every currently-supported option, never a narrowed guess.

## Provider-authored clarification (not derived from ambiguity detection)

A provider may also submit a `RawClarification` directly (`clarificationCandidates`), which `service.py` turns into a `ClarificationQuestion` verbatim (question text, `field`, `options`) — see `TestClarification::test_provider_clarification_candidate_becomes_a_question` in `backend/tests/test_designer.py`. This is a second, independent source of `ClarificationQuestion`s alongside the ambiguity-detection path above.
