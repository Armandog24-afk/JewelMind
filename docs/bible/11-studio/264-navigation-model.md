---
id: JM-BIBLE-264
title: Navigation Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-252
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Navigation Model

## One primary workspace, confirmed unchanged

JewelMind has exactly one route/screen — `App.tsx` renders the single workspace directly, with no router, no dashboard, and no account menu. This Sprint did not introduce navigation infrastructure of any kind, per its own explicit instruction to avoid a dashboard, marketplace, analytics pages, or collaboration pages at this stage.

## What "navigation" means today

Within the single workspace, the only navigation-like interactions are the `Technical`/`Presentation` view-mode tabs (Vision, Sprint 8) and the `Validation`/`Outputs`/`Specification`/`JSON`/`Model info` right-panel tabs (Studio, this Sprint's `Outputs` addition) — both are in-page tab switches, not page navigations, and neither changes the browser URL.

## Deliberately not built this Sprint

A project dashboard, a multi-project switcher, and any settings/account surface — all recorded as PLANNED in [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md), consistent with CLAUDE.md's explicit out-of-scope list (no accounts, no cloud projects, no collaboration).
