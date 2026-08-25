---
id: JM-BIBLE-314
title: Prompt Injection and Untrusted Input
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-313
related_documents:
  - JM-BIBLE-315
implementation_status: current
professional_validation: not_required
normative: true
---

# Prompt Injection and Untrusted Input

## A denylist is not complete protection — and this document says so plainly

`_INJECTION_MARKERS` (see [`313-designer-security-model.md`](313-designer-security-model.md)) is a fixed set of lowercase substring matches. It catches the phrasings it lists and nothing else by construction: a rephrased, translated, or obfuscated injection attempt that doesn't contain one of those exact substrings passes the screen untouched. `normalizer.py`'s own comment is explicit about this: "a coarse, explicit denylist, not a claim of complete prompt-injection immunity." No document in this Sprint claims otherwise, and none should — a denylist that overclaims its coverage would be a worse security posture than an honest, narrow one.

## Why the architecture stays safe regardless

The denylist is one layer, not the only layer. Even in the hypothetical worst case — a real `AnthropicDesignerProvider` call, and a successful injection that got the model to attempt something outside its intended role — the structural pipeline downstream is unaffected, for a concrete reason: `capability.py`'s deterministic checks apply to a provider's output exactly the same way they apply to any other input, with no special trust extended to values that happen to have originated from an LLM response.

Concretely: suppose an injected instruction convinced a live model to emit `proposedCanonicalValues=[{"field": "material.metal", "value": "unobtainium"}]` or `{"field": "stone.setting_style", "value": "diamond_pave_halo"}` — a field or enum value outside what JewelMind actually supports. `_build_proposal()` still runs `capability.is_known_field()` on the field path and `normalizer.normalize_enum_token()` on the value, exactly as it does for a completely ordinary, non-adversarial request (see [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md), [`303-field-provenance-model.md`](303-field-provenance-model.md)). An unrecognized field becomes a `DESIGNER_CAPABILITY_MISMATCH` diagnostic and is dropped from the patch; an unrecognized enum value becomes an `UnsupportedFeature`. Neither can reach `JewelryDefinition.model_validate()`, because `_apply_patch()` only ever receives values that already survived that gating (DESIGNER-GOV-004).

## The real limit of this guarantee

This structural safety net protects the *shape* of the resulting design — it cannot smuggle an unsupported field or enum value into a candidate JDL. It does not protect against a successful injection causing a *supported* field to be set to a *misleading but structurally valid* value (e.g. talking the model into reporting an unusually large `stone.diameter` as if the user asked for it). That risk is bounded by the same review-before-apply discipline every proposal already goes through — see [`310-user-review-and-acceptance.md`](310-user-review-and-acceptance.md) — not by capability-awareness, which has nothing to say about a value's plausibility, only its shape.

## Why a stronger defense isn't simply added now

A more sophisticated defense — semantic classification of injection intent, a second LLM call to screen the first, rate-limiting by suspicious-pattern frequency — is plausible future work, but each option trades away something this Sprint's `_INJECTION_MARKERS` approach preserves: determinism, zero added latency, zero added provider cost, and zero additional external dependency. Upgrading the screen is a deliberate trade-off decision, not a free improvement, and belongs behind the same RFC discipline as any other major Designer capability change.

See [`313-designer-security-model.md`](313-designer-security-model.md) for the concrete screening mechanism, and [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md) for whether a stronger injection defense is worth a future RFC.
