---
id: JM-BIBLE-209
title: CAD Interoperability Philosophy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-190
related_documents:
  - JM-BIBLE-210
  - JM-BIBLE-211
implementation_status: current
professional_validation: not_required
normative: true
---

# CAD Interoperability Philosophy

## Three honest levels, never conflated

| Level | Meaning | What it takes to claim |
|---|---|---|
| `EXPORT_SUPPORTED` | JewelMind can produce a file in this format | The exporter exists and is exercised by tests — true for STEP and STL today |
| `IMPORT_TESTED` | A specific external application version was actually launched and opened a real JewelMind-exported file | A recorded test run, with the application name and version noted — not an assumption based on the format being "standard" |
| `WORKFLOW_VALIDATED` | A full round-trip (JewelMind export → external tool → a meaningful downstream action, e.g. successful casting-file preparation) was actually performed and observed | The strongest claim; restates FOUNDRY-GOV-014 — never claimed without a recorded end-to-end test |

## Why this three-level split exists

CLAUDE.md is explicit: JewelMind must never require Rhino, MatrixGold, JewelCAD, or any other paid/interactive CAD application to run. That constraint means this Sprint cannot purchase or install any of those applications to perform a real `IMPORT_TESTED` or `WORKFLOW_VALIDATED` check — see [`210-step-interoperability-boundaries.md`](210-step-interoperability-boundaries.md) for exactly which applications remain `EXPORT_SUPPORTED`-only (never tested) as a direct consequence.

## What IS tested this Sprint, and at which level

The only real `IMPORT_TESTED`-equivalent check performed this Sprint is `cadquery.importers.importStep()` re-importing JewelMind's own STEP output — this proves the file is well-formed STEP, but CadQuery is not an independent third-party CAD application; it is the same library that wrote the file. This is documented as a self-consistency check, not an external interoperability test, and is never described as `IMPORT_TESTED` against a genuinely separate application.

## The governing rule, restated plainly

**Do not call an external CAD workflow "validated" unless actual testing exists.** A format being widely supported in the industry (STEP, STL) is a reasonable basis for *expecting* `IMPORT_TESTED` to succeed in a specific application — it is never a substitute for actually running that test and recording the result.
