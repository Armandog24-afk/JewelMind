---
id: JM-BIBLE-355
title: Intent Profile Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-354
related_documents:
  - JM-BIBLE-356
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Profile Model

## The shape, in full

`IntentProfile` (`design_intent/schemas.py`) is a complete Pydantic model describing a future, versioned, deterministic intent-to-JDL mapping:

| Field | Type | Meaning |
|---|---|---|
| `profileId` | `str` | Stable identifier, never renamed or reused once published (mirrors FORGE-GOV-001's rule for rule ids). |
| `version` | `str` | Independent version for this profile, so a later change is a new version, never a silent edit. |
| `supportedDomain` | `str` | What kind of jewelry/statement space this profile applies to. |
| `resolvedIntent` | `list[str]` | Which intent statement/target/concept combinations this profile knows how to resolve. |
| `jdlMapping` | `dict[str, float \| str]` | The actual deterministic field-path -> value mapping. Always `{}` in v1. |
| `provenance` | `str` | Who defined this profile and on what basis — required, no default. |
| `professionalReview` | `Literal["not_required","preliminary","required","validated"]` | Defaults to `"not_required"`; never implicit for a real profile. |
| `deterministicMapping` | `bool` | Defaults to `True` — a profile that cannot guarantee determinism should not exist under this model at all. |
| `applicableCapabilityVersion` | `str` | Defaults to `"0.1.0"` — ties the profile to a specific compiler-capability generation. |

## Zero profiles registered in v1

No `IntentProfile` instance is constructed, loaded, or referenced anywhere in `backend/jewelmind/design_intent/`. `resolver.py::build_design_intent()` always sets `DesignIntent.profile = None` (`resolver.py:211`). This is intentional, not incomplete — it is the direct consequence of [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md): no mapping in this codebase currently satisfies all seven conditions that policy requires, so none is registered, per this Sprint's own instruction not to invent mappings to make the feature look more powerful than it safely is.

## An illustrative future example — not implemented

A hypothetical `DELICATE_SOLITAIRE_PROFILE` illustrates what a *later* sprint's profile might look like: `supportedDomain` scoped to solitaire rings, `resolvedIntent` covering `(RING, VISUAL_WEIGHT, DELICATE)` and a small number of closely related statements, `jdlMapping` containing a small number of specific field-path -> value pairs (e.g. a narrower band width band, a smaller basket), `provenance` naming the jewelry professional or documented source who defined the specific numeric choices, and `professionalReview` set to `"required"` or `"validated"` rather than left at the default. No such profile exists in the codebase today; this paragraph is illustration only, per this document's own governing policy, not a roadmap commitment.

## What registering the first profile would require

Per [`330-intent-governance.md`](330-intent-governance.md), registering the first `IntentProfile` with a non-empty `jdlMapping` is one of exactly two changes that require an ADR before shipping (the other being letting Design Intent write directly to `candidateJDL` outside the profile mechanism). It would also require, in the same change: an update to [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md) recording that a mapping now satisfies its seven conditions, a `professionalValidationStatus`-equivalent record analogous to Forge's own provenance model (`../06-forge/094-rule-provenance-model.md`), and new resolution-status coverage in [`348-intent-resolution-model.md`](348-intent-resolution-model.md) (the currently-unused `DETERMINISTICALLY_RESOLVED`/`PROFILE_RESOLVED` statuses would finally be produced).

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-010, INTENT-GOV-018.
- [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md) — the seven conditions a profile's mapping must satisfy.
- [`348-intent-resolution-model.md`](348-intent-resolution-model.md) — the resolution statuses a profile would finally activate.
- `../06-forge/094-rule-provenance-model.md` — the provenance discipline this model deliberately parallels.
