---
id: JM-BIBLE-347
title: Intent Compatibility Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-346
related_documents:
  - JM-BIBLE-348
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Compatibility Model

## Two different claims that must never be conflated

**Technical validity** is what Forge decides: does a `JewelryDefinition` pass every applicable `Forge` rule (see [`../06-forge/README.md`](../06-forge/README.md))? It is computed by `validate_definition()` and reported in `DesignerProposal.validation`/`forgeEvaluation`, entirely independent of Design Intent.

**Intent compatibility** is a different, currently-unimplemented question: does a `JewelryDefinition`'s actual geometry match what the user's aesthetic language asked for? Nothing in the current codebase answers this question. A design can pass every Forge rule while carrying aesthetic statements that remain purely `PRESERVED` — never checked against, confirmed by, or reconciled with the geometry that was actually generated.

## A design can be technically valid and aesthetically unresolved at the same time

This is not a hypothetical edge case — it is the *normal* state for any design that includes an aesthetic descriptor in v1. A request for "a very delicate solitaire in platinum with a 1.8mm band" produces a `JewelryDefinition` that Forge validates purely on its numeric/structural merits (band width, prong count, metal, etc.). The `VISUAL_WEIGHT: DELICATE` statement sits alongside that validated definition with `resolutionStatus: PRESERVED` — nobody, and no code, has confirmed that a 1.8mm platinum band actually *reads* as delicate. Forge's verdict and the intent statement's status are two independent, unconnected facts about the same proposal.

## Why this must be visible to the user, not hidden

Because compatibility is never automatically checked, hiding the distinction would let a user believe their aesthetic request was "handled" simply because the proposal was technically valid and applied without error. The real mechanism that prevents this is the Studio review UI's per-statement resolution label — `RESOLUTION_LABEL` in `frontend/src/components/DesignerPanel.tsx` renders `PRESERVED` as **"Preserved — not yet technically resolved"** and `CONFLICTING` as **"Conflicting — needs your attention"**, next to every statement, every time a proposal is reviewed. This label is the honest, load-bearing signal that a passed Forge validation says nothing about whether the aesthetic request was actually satisfied.

## What would be required to change this

Closing this gap would mean building a real deterministic (or reviewed) mapping from an intent statement to a measurable geometric property, and a way to check the generated geometry against it — exactly the territory [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md) and [`355-intent-profile-model.md`](355-intent-profile-model.md) describe and exactly what `IntentProfile` is shaped for. None of that exists yet; `IntentProfile.jdlMapping` is empty everywhere in the current codebase, so there is no registered mapping to check compatibility against even in principle.

## Where Forge and Design Intent stay separate

Per [`330-intent-governance.md`](330-intent-governance.md), INTENT-GOV-011, no file under `design_intent/` references a manufacturing tolerance, density, or Forge-style threshold, and no Forge rule reads a `DesignIntent` field. The two systems evaluate genuinely different things — one a jewelry-domain/manufacturing fact about the geometry, the other a preserved subjective claim about how the geometry should feel — and this doc exists specifically so that difference is never accidentally blurred in review UI copy, documentation, or future code.
