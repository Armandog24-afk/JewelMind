---
id: JM-BIBLE-108
title: Rule Versioning
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-092
related_documents:
  - JM-BIBLE-081
implementation_status: current
professional_validation: not_required
normative: true
---

# Rule Versioning

## Independent from every other version axis

Rule version is tracked separately from: JDL schema version (`0.1.0`), product/package version (backend `0.1.0`, frontend `0.0.0` — see [`05-jdl/081-schema-versioning-and-migrations.md`](../05-jdl/081-schema-versioning-and-migrations.md)), compiler version, and geometry generator version (`GENERATOR_VERSION = "0.1.0"`). **Every rule in `current-rule-registry.json` is currently `version: "1.0.0"`, coincidentally distinct from all of the above** — this is the first time a rule-specific version number has existed in this codebase; it did not exist before this Sprint because rules had no independent versioning concept, only implicit "whatever `engine.py` currently does."

## PATCH / MINOR / MAJOR

| Level | Definition | Example |
|---|---|---|
| PATCH | Message wording only, or a documentation/provenance-notes correction that changes no behavior | Rewording `JM-BAND-001`'s message text without changing its 1.5mm threshold |
| MINOR | An additional, non-breaking applicability condition, or a newly-added `suggestedValue` that wasn't there before | Restricting `JM-MANUFACTURING-001` to also check a new resin-specific field, without changing its existing 0.8mm threshold or its effect on already-passing documents |
| MAJOR | A changed threshold, severity, or blocking behavior — or a changed meaning of what the rule checks | Changing `JM-BAND-001`'s 1.5mm floor to 1.2mm; changing its severity from `error` to `warning`; changing `JM-PRONG-001`'s valid set from `{4, 6}` to `{4, 6, 8}` |

## Professional validation is version-scoped

A professional validation record (per [`103-professional-validation-lifecycle.md`](103-professional-validation-lifecycle.md)) applies to one exact `ruleVersion`. A MAJOR change to a validated rule invalidates that record; the rule reverts to its pre-validation confidence level until re-reviewed, unless the original reviewer explicitly extends acceptance to the new version.

## Current state

Since no rule has ever been versioned independently before this Sprint, every rule starts at `1.0.0` with an empty `deprecatedVersions` list — there is no version history to report yet.
