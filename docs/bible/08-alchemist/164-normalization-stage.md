---
id: JM-BIBLE-164
title: Normalization Stage
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-163
related_documents:
  - JM-BIBLE-065
implementation_status: current
professional_validation: not_required
normative: true
---

# Normalization Stage

## What normalization may do

Expand accepted defaults; normalize enum representations (moot today — no case-insensitive or alternate-spelling enum acceptance exists, every enum is exact-match); canonicalize field order (happens at hashing time, not at normalization time — see [`05-jdl/065-canonical-json-serialization.md`](../05-jdl/065-canonical-json-serialization.md)); validate finite numbers (`allow_inf_nan=False`); normalize supported unit representation (moot — only millimeters ever exists, no conversion occurs); create stable internal structures (the `JewelryDefinition` instance itself); calculate derived non-domain metadata when explicitly defined (none currently calculated at this stage — all derivation happens later, inside geometry builders).

## What normalization must NOT do, and confirmed does not do

| Prohibition | Confirmed by |
|---|---|
| Change design intent | `JewelryDefinition.model_validate()` never mutates a provided value — only fills omitted ones |
| Change geometry-driving values | Same — see `normalization-vectors.json`'s `explicit-default-values-are-unchanged` vector |
| Silently fix invalid jewelry parameters | Confirmed by `normalization-vectors.json`'s `normalization-does-not-fix-invalid-values` vector: `band.width: -2.4` passes through unchanged and is only later caught by Forge |
| Apply professional heuristics | No heuristic code exists at this stage — Pydantic performs pure type/default-filling only |
| Infer missing jewelry components | Every field has a fixed, documented default (Sprint 3); nothing is inferred from context |

## Mapping to current canonicalization behavior

Normalization (this document) and canonicalization ([`05-jdl/065-canonical-json-serialization.md`](../05-jdl/065-canonical-json-serialization.md)) are two different steps that happen to both be trivial today: normalization is `JewelryDefinition.model_validate()` (parse + default-fill); canonicalization is `canonical_json()` (serialize deterministically for hashing). The first produces a Python object; the second produces a string from that object. Sprint 3 already fully specifies the second; this document is the first Bible treatment of the first, framed at the compiler-stage level.

## Current implementation

There is no function named `normalize()` anywhere in this codebase — `JewelryDefinition.model_validate()` (a Pydantic library method, not custom JewelMind code) is the entire normalization stage today.
