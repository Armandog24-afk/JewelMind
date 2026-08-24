---
id: JM-BIBLE-109
title: Rule Registry
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-092
  - JM-BIBLE-108
related_documents:
  - JM-BIBLE-A14
implementation_status: current
professional_validation: not_required
normative: true
---

# Rule Registry

The normative registry shape is `specs/forge/v1/rule-registry.schema.json`; the actual populated registry is `specs/forge/v1/current-rule-registry.json` — **21 rules, generated exclusively from real code inspection, none invented.**

## Fields per entry

`ruleId`, `currentVersion`, `active`, `lifecycleState`, `classification`, `stage`, `applicability` (jewelry categories/styles/materials/manufacturing methods), `professionalValidationStatus`, `source` (repository-relative code location), `dependencies`, `tests`, `deprecatedVersions`.

## How this registry is kept honest

`backend/tests/test_forge_registry.py` validates `current-rule-registry.json` against `rule-registry.schema.json` on every test run, and separately cross-checks the severity of every `JM-*` entry against a live run of `validate_definition()`. This means a future change to `engine.py` that silently changes a rule's severity without updating the registry will fail CI, not just go undetected in documentation.

## Registry vs. full rule definitions

The registry stores a *summary* per rule (enough to classify, locate, and test it); the *full* `ForgeRule` shape (condition text, message template, provenance detail, applicability lists) lives only in the two worked examples under `specs/forge/v1/examples/valid/` for this Sprint. Populating a full `ForgeRule` JSON file for all 21 rules was judged out of scope for this milestone (a mechanical, low-risk follow-up, not an architectural decision) — recorded as a gap in `SPRINT-4-VALIDATION-REPORT.md` rather than rushed.

## Registry statistics (from `current-rule-registry.json`, Sprint 4)

| Metric | Value |
|---|---|
| Total rules | 21 |
| Active | 21 |
| Deprecated | 0 |
| `lifecycleState: ACCEPTED` | 21 |
| `professionalValidationStatus: validated` | 0 |
| `professionalValidationStatus: preliminary` | 16 |
| `professionalValidationStatus: not_required` | 5 |
