---
id: JM-BIBLE-A36
title: "Appendix: Foundry Component Inclusion Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-195
related_documents:
  - JM-BIBLE-196
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Foundry Component Inclusion Matrix

Restates [`09-foundry/195-component-inclusion-policy.md`](../09-foundry/195-component-inclusion-policy.md)'s matrix as a standalone reference table, kept in sync with `specs/foundry/v1/test-vectors/component-inclusion-vectors.json`.

| Component | STEP | STL | JSON | Technical specification | Preview mesh |
|---|---|---|---|---|---|
| `band` | included_by_default | included_by_default | not_applicable_metadata_only | included_by_default | included_by_default |
| `prongs` | included_by_default | included_by_default | not_applicable_metadata_only | included_by_default | included_by_default |
| `basket_support` | included_by_default | included_by_default | not_applicable_metadata_only | included_by_default | included_by_default |
| `stone_reference` | excluded_by_default_optional | excluded_by_default_optional | not_applicable_metadata_only | included_by_default_dimensions_only | included_by_default |

Real exported component sets, confirmed by running the exporters: `STEP_default = STL_default = [band, prongs, basket_support]`; `STEP_with_stone = STL_with_stone = [band, prongs, basket_support, stone_reference]`.
