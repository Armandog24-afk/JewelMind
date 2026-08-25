---
id: JM-BIBLE-301
title: Unsupported Request Handling
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-300
related_documents:
  - JM-BIBLE-302
implementation_status: current
professional_validation: not_required
normative: true
---

# Unsupported Request Handling

## `UnsupportedFeature`'s 7 fields

`designer/schemas.py::UnsupportedFeature` is the structured way Designer names a gap rather than pretending one doesn't exist (DESIGNER-GOV-005):

| Field | Purpose |
|---|---|
| `feature` | The concept the user asked for, verbatim or normalized token (e.g. `"halo"`) |
| `sourceText` | The fragment of the request that named it |
| `reason` | Human-readable explanation of what's missing |
| `currentCapability` | The real supported alternative set for that field, when one exists (e.g. every currently-supported stone shape) |
| `futureRoadmapReference` | Optional pointer to a planned capability; never populated with a promise Designer's own code can't verify |
| `blocking` | Always `True` in current code — every `UnsupportedFeature` `_build_proposal()` constructs sets it, whether from `capability.KNOWN_UNSUPPORTED_CONCEPTS` or a provider-reported `RawUnsupportedFeature` |
| `suggestedSupportedAlternative` | The nearest real, currently-buildable alternative, when one is known |

## `KNOWN_UNSUPPORTED_CONCEPTS`

`capability.py::KNOWN_UNSUPPORTED_CONCEPTS` is a deterministic backstop, independent of whether a provider itself flags a concept as unsupported. Its real keys today: `oval`, `emerald_cut`, `princess_cut`, `pear`, `marquise`, `cushion` (all stone shapes beyond `round`), `halo`, `pave`/`pavé`, `trilogy`/`three_stone`/`multi_stone` (beyond a single-stone solitaire), `bezel`/`tension`/`channel` (beyond `prong` setting), and `necklace`/`bracelet`/`earring`/`pendant` (beyond `ring` category). Every value here maps to a plain-language reason, never a fabricated manufacturing rule (DESIGNER-GOV-008).

This dict is deliberately not schema-derived the way `current_capabilities()` is — it names concepts the schema has no member for at all, so there is nothing to introspect.

## `PARTIALLY_SUPPORTED` vs `UNSUPPORTED`

`service.py::_resolve_status()` distinguishes the two by whether *anything* survived alongside the gap:

- **`UNSUPPORTED`** — `unsupported_features` is non-empty and `proposed_fields` is empty. Nothing in the request could be turned into a real value; there is no partial design to offer.
- **`PARTIALLY_SUPPORTED`** — `unsupported_features` is non-empty but at least one `proposed_field` was also produced. The candidate JDL still reflects the supported portion of the request; the unsupported portion is reported alongside it, not silently dropped.

Both statuses can carry a real `candidateJDL` (unless `_apply_patch` itself fails, which is `INVALID`, a separate status). Neither status ever substitutes a nearby supported value for the unsupported one without saying so — that would violate DESIGNER-GOV-012.

See [`300-clarification-policy.md`](300-clarification-policy.md) for why an unsupported feature never becomes a `ClarificationQuestion` instead, and [`302-confidence-model.md`](302-confidence-model.md) for how the fields that *do* survive are scored.
