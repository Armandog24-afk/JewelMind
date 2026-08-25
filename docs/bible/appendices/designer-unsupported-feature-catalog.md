---
id: JM-BIBLE-A59
title: "Appendix: Designer Unsupported Feature Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGNER-README
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-301
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Designer Unsupported Feature Catalog

The real `KNOWN_UNSUPPORTED_CONCEPTS` dict from `backend/jewelmind/designer/capability.py` — a deterministic backstop for unsupported-feature detection, independent of whether a provider itself flags the request (DESIGNER-GOV-008, DESIGNER-GOV-012).

| Concept key | Reason (verbatim from `capability.py`) |
|---|---|
| `oval` | Only round stones are currently supported (stone.shape). |
| `emerald_cut` | Only round stones are currently supported (stone.shape). |
| `princess_cut` | Only round stones are currently supported (stone.shape). |
| `pear` | Only round stones are currently supported (stone.shape). |
| `marquise` | Only round stones are currently supported (stone.shape). |
| `cushion` | Only round stones are currently supported (stone.shape). |
| `halo` | Halo settings are not currently supported; only a single prong setting exists. |
| `pave` | Pave bands are not currently supported. |
| `pavé` | Pave bands are not currently supported. |
| `trilogy` | Only a single-stone solitaire is currently supported. |
| `three_stone` | Only a single-stone solitaire is currently supported. |
| `multi_stone` | Only a single-stone solitaire is currently supported. |
| `bezel` | Only a prong setting is currently supported (setting.type). |
| `tension` | Only a prong setting is currently supported (setting.type). |
| `channel` | Only a prong setting is currently supported (setting.type). |
| `necklace` | Only rings are currently supported (jewelry.category). |
| `bracelet` | Only rings are currently supported (jewelry.category). |
| `earring` | Only rings are currently supported (jewelry.category). |
| `pendant` | Only rings are currently supported (jewelry.category). |

This dict is consulted from `service.py::_build_proposal()` only as a fallback message lookup when an enum-field value fails `normalizer.normalize_enum_token()` (i.e. `stone.shape`, `setting.type`, `jewelry.category` style values submitted as a `proposedCanonicalValues` entry rather than a `detectedUnsupportedFeatures` entry); if the concept key isn't present, the code falls back to a generic `"'{value}' is not a supported value for {path}."` message.

## Which corpus `UNSUPPORTED`-category cases exercise it

All 6 `UNSUPPORTED` cases in `backend/tests/test_designer_corpus.py` exercise unsupported-feature detection via the provider-reported `detectedUnsupportedFeatures` path (not the `KNOWN_UNSUPPORTED_CONCEPTS` fallback-message path), since the corpus cases model a well-behaved provider that already flags the unsupported concept explicitly rather than misrouting it through `proposedCanonicalValues`:

| Corpus case ID | Request text | Unsupported feature(s) |
|---|---|---|
| `unsup-01` | "Fammi un halo con diamante ovale." | `halo`, `oval diamond` |
| `unsup-02` | "Use an oval stone with a halo." | `halo`, `oval stone` |
| `unsup-03` | "A trilogy ring with three stones." | `trilogy` |
| `unsup-04` | "Un anello con fascia pavé." | `pave band` |
| `unsup-05` | "A bezel-set emerald cut stone." | `bezel setting`, `emerald cut` |
| `unsup-06` | "Fammi una collana." | `collana (necklace)` |

The `KNOWN_UNSUPPORTED_CONCEPTS` fallback-message path itself is exercised directly by `backend/tests/test_designer.py::TestUnsupportedFeature::test_unsupported_stone_shape_value_is_caught_deterministically`, which submits `stone.shape = "oval"` as a `proposedCanonicalValues` entry (not a `detectedUnsupportedFeatures` entry) and asserts the dict's `oval` reason is surfaced and `candidateJDL.stone.shape` stays at the schema default (`round`), never silently smuggled through.
