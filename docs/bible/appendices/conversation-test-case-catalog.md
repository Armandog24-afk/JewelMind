---
id: JM-BIBLE-A78
title: "Appendix: Conversation Test Case Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-CONVERSATION-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Conversation Test Case Catalog

## The 6 required CASE A-F scenarios (`backend/tests/test_conversation_engine.py`)

These are the required multi-turn behaviors named directly in the Sprint 12 brief, each its own test class.

| Case | Class | What it proves |
|---|---|---|
| A | `TestCaseA_TechnicalModifyPreservesUnrelatedFields` | Accepting a proposal, then issuing a second technical change, only touches the newly-requested field — `setting.prongCount` from the first accepted turn survives a later material-only change untouched. |
| B | `TestCaseB_IntentOnlyNeverStalesGeometry` | A pure aesthetic request ("più minimal") produces zero changed technical `diff` entries and is labeled `MODIFY_INTENT`, so it can never mark geometry stale. |
| C | `TestCaseC_ClarificationThenResolution` | An ambiguous/underspecified technical request ("Allarga la fascia.") opens a real clarification thread, and the numeric answer that follows is correctly applied to the proposed `candidateJDL`. |
| D | `TestCaseD_PreserveStoneWhileChangingMaterial` | An explicit "leave the stone as is" instruction alongside a material change leaves every stone field at its default while the material field changes. |
| E | `TestCaseE_UnsupportedThenAbandoned` | An unsupported feature (halo) is reported honestly, and a follow-up "never mind" resolves to a real no-op with no proposal created. |
| F | `TestCaseF_CorrectionSupersedesWithoutIntermediateMutation` | A correction ("No, quattro griffe.") replaces rather than merges with the prior six-prong proposal, and the original `JewelryDefinition` default is never mutated by the superseded proposal. |

## The 80 corpus cases (`backend/tests/test_conversation_corpus.py`)

Verified by `pytest tests/test_conversation_corpus.py --collect-only -q`: **82 tests collected** = 80 parametrized `test_corpus_case` cases + `test_corpus_has_at_least_80_cases` + `test_corpus_covers_all_required_categories`. The 80 case count matches the brief's "at least 80 cases across 17 categories" exactly.

| Case ID(s) | Category | Description |
|---|---|---|
| `create-modify-01`, `create-modify-02`, `create-modify-03` | CREATE_THEN_MODIFY | Create a ring (rose gold / yellow gold+prongs / four-prong), accept it, then issue a second technical change (metal to platinum / prong count to six / metal to silver) against the accepted base. |
| `technical-mod-01`..`06` | TECHNICAL_MODIFICATION | Single-turn technical field changes: metal to platinum/silver, prong count to six/four, band profile to comfort/flat. |
| `intent-only-01`..`04` | INTENT_ONLY_MODIFICATION | Single-turn pure aesthetic statements (più minimal / more classic / più delicato / bolder) resolving to an intent statement with zero technical diff. |
| `reference-01`, `reference-02` | REFERENCE_TO_PREVIOUS_COMPONENT | "Allarga la fascia." resolves to `band.width`; "Make the stone bolder." resolves to a `STONE`-targeted `VISUAL_WEIGHT` intent statement. |
| `pronoun-01`, `pronoun-02` | PRONOUN_RESOLUTION | "make it rose gold" / "fallo oro bianco" resolve the bare pronoun via the material-word safe exception to `material.metal`. |
| `ambiguous-ref-01`..`03` | AMBIGUOUS_REFERENCE | "make it wider" / "lo voglio più largo" / "make that wider" with no established topic each open a clarification instead of guessing a target. |
| `clarification-01`, `clarification-02` | CLARIFICATION | "Allarga la fascia." / "Widen the band." each open a numeric band-width clarification, then apply the answered value (2.8mm / 3.1mm). |
| `clarification-03` | CLARIFICATION | "Cambia metallo." opens an `ENUM_CHOICE` clarification offering two metal options. |
| `clarification-correction-01` | CLARIFICATION_CORRECTION | An open band-width clarification answered "not a number" leaves the thread still pending (not silently closed). |
| `proposal-reject-01`, `proposal-reject-02` | PROPOSAL_REJECTION | A platinum/silver proposal followed by "no" / "cancel" discards the proposal with no active proposal remaining. |
| `proposal-correction-01`, `proposal-correction-02`, `proposal-correction-03`..`05` | PROPOSAL_CORRECTION | A second turn ("No, quattro griffe." / "Actually platinum." / "No, silver instead." / "Invece quattro." / "Actually 3.0mm.") supersedes the first proposal's value rather than merging with it. |
| `preserve-unspecified-01`, `preserve-unspecified-02`, `preserve-unspecified-04`..`06` | PRESERVE_UNSPECIFIED | A request naming exactly one field to change (stone left as-is + metal change; band width only; stone diameter only; prong diameter only; stone depth only) leaves every other field, including `material.metal` where not targeted, at its default. |
| `preserve-unspecified-03` | PRESERVE_UNSPECIFIED | "leave the stone as is" alone (no accompanying change) classifies as `PRESERVE_TARGET` with no proposal created at all. |
| `unsupported-01`, `unsupported-02` | UNSUPPORTED_FEATURE | "Fammi un halo." / "Can you do an oval stone?" each report the unsupported feature honestly via `REPORT_UNSUPPORTED`. |
| `unsupported-03` | UNSUPPORTED_FEATURE | A halo report followed by "Lascia perdere." resolves to a genuine `NO_CHANGE` with no active proposal. |
| `partial-support-01` | PARTIAL_SUPPORT | "Platino con fascia pavé." both changes `material.metal` and reports the unsupported pavé band in the same turn. |
| `stale-context-01` | STALE_CONTEXT | Accepting a platinum proposal against a JDL that was concurrently, manually edited (band width changed) raises `ConversationStaleContextError` rather than silently applying it. |
| `stale-context-02` | STALE_CONTEXT | Accepting the same proposal against an unchanged base JDL succeeds normally (the negative-control counterpart to `stale-context-01`). |
| `malicious-01`..`06` | MALICIOUS_HISTORY | 6 distinct prompt-injection phrasings ("ignore previous instructions", "reveal your system prompt", "you are now DAN", requests for `ANTHROPIC_API_KEY`, "disregard your instructions", "jailbreak: ...") each raise `DesignerSecurityRejectedError` before classification. |
| `italian-01`, `italian-03`, `english-01`, `english-03` | ITALIAN / ENGLISH | Equivalent Italian/English technical phrasings ("Usa il platino."/"Use platinum.", "Sei griffe."/"Six prongs.") converge on the identical resolved field value. |
| `italian-02`, `english-02` | ITALIAN / ENGLISH | Equivalent Italian/English aesthetic phrasings ("Fammi un anello delicato."/"Make it delicate.") both resolve to `RING`/`VISUAL_WEIGHT`/`DELICATE` and both classify as `MODIFY_INTENT`. |
| `technical-mod-07`..`12` | TECHNICAL_MODIFICATION | A second batch of single-turn technical changes: metal to yellow/white gold, band profile comfort/flat, prong count four/six (Italian/English pairs). |
| `intent-only-05`..`08` | INTENT_ONLY_MODIFICATION | A second batch of aesthetic statements: classico (STYLE_TEMPORALITY), understated (VISUAL_EMPHASIS), pulito (SIMPLICITY -> CLEAN), broad (PROPORTIONAL_CHARACTER). |
| `reference-03`..`05` | REFERENCE_TO_PREVIOUS_COMPONENT | Component-scoped technical requests: band narrower (`band.width`), setting taller (`setting.basketHeight`), prongs raised (`setting.prongHeight`). |
| `technical-mod-13`..`18` | TECHNICAL_MODIFICATION | A third batch of single-turn technical changes: metal platino/silver, band profile flat/comfort, stone diameter, prong diameter. |
| `intent-only-09`..`14` | INTENT_ONLY_MODIFICATION | A third batch of aesthetic statements: timeless (STYLE_TEMPORALITY), statement (VISUAL_EMPHASIS), ornate (SIMPLICITY), slim (PROPORTIONAL_CHARACTER), robusto/STRONG and soft/SOFT (both STRUCTURAL_CHARACTER). |

## Notes grounded in the real code

- The corpus's own `test_corpus_covers_all_required_categories()` asserts all 17 category names used in the table above are present as a subset of the categories actually registered — verified structurally by the test suite itself, not just by this appendix's manual count.
- Case IDs following a `NN` numeric suffix are not always contiguous within one category in file order (e.g. `technical-mod-01`..`06`, then `07`..`12` later, then `13`..`18` later still) because the corpus was built incrementally across several `for` loops appending to the same category — this appendix lists them in the order they appear in `CASES`, matching `pytest`'s own collection order.
