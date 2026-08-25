---
id: JM-BIBLE-A69
title: "Appendix: Intent Diagnostic Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-358
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Diagnostic Catalog

The 9 verbatim `INTENT_*` codes from `backend/jewelmind/design_intent/diagnostics.py`. Unlike Designer's diagnostic model, none of these ever fails the HTTP request — an unresolved or conflicting intent is a normal, expected outcome, always returned in a 200 `DesignerProposal.designIntent.diagnostics`, never a backend error (`diagnostics.py`'s own module docstring). Verified by grepping every `D.INTENT_*` reference in `backend/jewelmind/design_intent/resolver.py` — only 4 of the 9 codes are currently emitted.

| Code | Severity | Currently emitted? | Real trigger condition |
|---|---|---|---|
| `INTENT_UNKNOWN_DESCRIPTOR` | `info` | Yes | `resolver.py::_resolve_statements` — either the raw `target` doesn't normalize, the raw `concept` isn't one of the 6 known categories, or the raw `value` isn't a recognized descriptor for that category |
| `INTENT_AMBIGUOUS_DESCRIPTOR` | n/a (declared, unused) | No | Reserved for future use — v1 has no code path that distinguishes "recognized but ambiguous" from "unrecognized"; a genuinely ambiguous word (e.g. Italian "importante") is deliberately excluded from every synonym table and falls through the same `INTENT_UNKNOWN_DESCRIPTOR` path as any other unrecognized word |
| `INTENT_CONFLICT` | `warning` | Yes | `resolver.py::build_design_intent` — emitted once per `IntentConflict` returned by `conflicts.py::detect_conflicts()` |
| `INTENT_UNSUPPORTED_TARGET` | n/a (declared, unused) | No | Reserved for future use — v1 has no notion of a target that is recognized but structurally unsupported for a given concept; an unresolvable target is instead folded into the generic `INTENT_UNKNOWN_DESCRIPTOR` path |
| `INTENT_NO_DETERMINISTIC_RESOLUTION` | n/a (declared, unused) | No | Reserved for future use — meaningful only once a resolution-attempt step exists; since v1 never attempts deterministic resolution (zero `IntentProfile`s registered), this code cannot yet fire |
| `INTENT_PROFILE_UNAVAILABLE` | n/a (declared, unused) | No | Reserved for future use — meaningful only once profile-based resolution is requested against a `profileId` that isn't registered; no caller can request a profile in v1 |
| `INTENT_RESOLUTION_REQUIRES_CONFIRMATION` | n/a (declared, unused) | No | Reserved for future use — would fire when a proposed resolution needs explicit user confirmation before touching JDL (per **INTENT-GOV-015**); no such resolution step exists yet |
| `INTENT_INVALID_RELATION` | `info` | Yes | `resolver.py::_resolve_relations` — the raw `subject`, `predicate`, or `object` fails to normalize |
| `INTENT_PRESERVED_UNRESOLVED` | `info` | Yes | `resolver.py::build_design_intent` — emitted once per entry in the final `unresolved` list (covers both unresolved statements/relations and provider-reported `unresolvedDescriptors` passed straight through) |

## Notes grounded in the real code

- The 5 unemitted codes are honestly "reserved for future use," not a gap to silently paper over — each corresponds to a resolution-model concept (`IntentProfile`, deterministic mapping, user-confirmation flow) that is modeled in `schemas.py` but not wired into any live code path in v1, consistent with `docs/bible/13-design-intent/349-deterministic-resolution-policy.md`'s deliberate "zero automatic mappings" stance.
- `severity` for the 4 emitted codes always matches the value passed at the real construction site in `resolver.py` — `info` for extraction/preservation bookkeeping, `warning` for a detected conflict. No code path in v1 constructs an `IntentDiagnostic` with `severity="error"`.
