---
id: JM-BIBLE-A35
title: "Appendix: Foundry MIME Type Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-190
related_documents:
  - JM-BIBLE-197
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Foundry MIME Type Catalog

Every value below is a fixed literal in `backend/jewelmind/api/routes.py`, confirmed by direct inspection — none is derived from file content.

| Artifact | Extension | `media_type` sent | IANA-registered? |
|---|---|---|---|
| STEP | `.step` | `application/step` | Not an IANA-registered type; a widely-used community convention (the formally registered type is `model/step`, not yet adopted here) |
| STL | `.stl` | `model/stl` | Yes — registered |
| JSON | `.json` | `application/json` | Yes — registered |
| Technical specification | `.md` | `text/markdown` | Yes — registered |
| Preview mesh | `.stl` | `model/stl` | Yes — same as production STL |

## Known, low-priority naming inconsistency

`application/step` is not the IANA-registered media type for STEP files (`model/step` is). This has never caused an observed interoperability problem — browsers and download managers key off the `Content-Disposition` filename and extension far more than the `Content-Type` header for a file download — but is recorded here for completeness rather than silently left unexamined. See [`09-foundry/218-foundry-gap-analysis.md`](../09-foundry/218-foundry-gap-analysis.md) for whether this is worth changing (not currently listed as a gap, since it has never caused a real failure).
