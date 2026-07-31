---
id: JM-BIBLE-000
title: Bible Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-README
  - JM-BIBLE-004
implementation_status: current
---

# Bible Governance

## Purpose

The Technical Bible exists to prevent three specific failure modes that
are common in fast-moving prototypes:

1. **Drift** — the code changes, but nothing describing *why* it works
   this way is updated, so the reasoning is lost.
2. **Wishful documentation** — a document describes what the team wants
   to be true, or what is planned, in the same tone as what is actually
   implemented, so a reader cannot tell the difference.
3. **Silent architectural change** — a significant decision (a data
   format, a validation boundary, a deployment shape) changes without
   anyone recording that it changed or why.

Every rule below exists to close one of those three gaps.

## What is a source of truth

Each Bible document declares `source_of_truth: true` or `false` in its
front matter.

- `true` means: if this document and the running code disagree, that is a
  **bug or a documentation defect**, and it must be resolved — not
  ignored. Most Bible documents are `true`.
- `false` is reserved for documents that are explicitly aspirational by
  design (e.g. a vision document) — their content is *never* meant to
  match the current code, and that mismatch is not a defect.

`docs/*.md` (the pre-existing technical reference set — architecture,
API, validation rules, geometry conventions, domain model, development
guide, known limitations) remains the source of truth for the
implementation-level detail it already covers. The Bible does not
duplicate that detail; where a Bible document needs it, it links to the
relevant `docs/*.md` file instead of restating it. See
[`appendices/documentation-index.md`](../appendices/documentation-index.md).

## Document statuses

| Status | Meaning |
|---|---|
| `draft` | Written, not yet reviewed against the running code by anyone other than its author. |
| `accepted` | Reviewed and confirmed accurate as of `last_updated`. Safe to rely on. |
| `deprecated` | Superseded by another document (linked in `related_documents`) or no longer describes the current system. Kept for history, not for current guidance. |

A document created in this Sprint-1 pass starts as `accepted` only when
its content was directly checked against the repository (code, tests, or
CI configuration) while writing it. Documents that describe judgment
calls without a directly-checkable artifact (e.g. `002-vision-and-mission.md`)
are `accepted` as an honest statement of current intent, not as a factual
claim.

## Versioning rules

- A document's `version` follows `MAJOR.MINOR.PATCH`.
- **PATCH**: wording fixes, broken links, typos. No meaning changes.
- **MINOR**: added detail, new rows in a table, clarified scope — the
  document's conclusions do not change.
- **MAJOR**: the document's conclusion changes (a decision is reversed, a
  scope boundary moves, a status changes from `planned` to `current`).
  A MAJOR bump on an ADR requires either a new ADR that supersedes it, or
  an explicit "Status: superseded" edit with a link to the replacement.

## How to update a document

1. Read the document you intend to change and its `related_documents`.
2. Make the change.
3. Bump `version` per the rule above and update `last_updated`.
4. If the change affects `implementation_status` anywhere (a feature
   moved from `planned` to `current`, for example), update
   [`00-foundation/005-current-product-status.md`](005-current-product-status.md)
   and [`appendices/implementation-inventory.md`](../appendices/implementation-inventory.md)
   in the same change.
5. If the change contradicts an existing accepted ADR, do not silently
   edit around it — write a new ADR (see below).

## When an ADR is required

Write a new ADR in [`03-decisions/`](../03-decisions/) before — not after —
any change that:

- introduces a new CAD engine, geometry library, or removes CadQuery;
- changes the canonical `JewelryDefinition` schema in a way that is not
  purely additive;
- moves validation authority away from the backend, or duplicates a
  business rule directly into UI code;
- changes what is exported by default (e.g. starts including the stone
  reference in a default export);
- changes the coordinate system or unit convention;
- changes which party (frontend/backend) is authoritative for a decision
  currently owned by one side;
- violates any law in
  [`004-jewelmind-constitution.md`](004-jewelmind-constitution.md).

An ADR is not required for routine bug fixes, dependency bumps, new tests,
or additive validation rules that follow the existing pattern in
`docs/validation-rules.md`.

## When an RFC will be required (future)

This repository does not yet have multiple maintainers or external
contributors, so a formal RFC (Request for Comments) process is not in
place. **Future rule, not yet active:** once JewelMind has more than one
active maintainer or accepts external contributions, any change that
would require an ADR under the rule above must first be proposed as an
RFC document (a numbered `RFC-XXX.md`, structure to be defined when this
becomes necessary) and reach explicit agreement before the ADR is written
and the change is implemented.

## Rules against undocumented architecture changes

- No pull request (or equivalent change) that triggers one of the "ADR
  required" conditions above may be merged without the ADR present in the
  same change.
- A change that silently does one of those things without an ADR is
  itself a defect in the change, not just in the documentation, and
  should be flagged for correction rather than accepted as-is.

## Rules for future AI coding agents

See the "TECHNICAL BIBLE RULES" section added to the root `CLAUDE.md` for
the operational checklist. In summary: read this file and
[`004-jewelmind-constitution.md`](004-jewelmind-constitution.md) before
architectural work; identify which law and which ADRs are relevant; update
implementation-status documents in the same change as the code; never
mark `planned` as `current`; write an ADR before violating an accepted
one; report contradictions rather than silently resolving them in the
code's favor.

## How CURRENT, PARTIAL, PLANNED, and VISION must be used

Every capability discussed anywhere in the Bible must be classified as
exactly one of:

| Label | Meaning | Evidence required |
|---|---|---|
| `current` | Implemented, working, covered by at least one test or directly observable in the running app. | A file path and/or a test name. |
| `partial` | Some implementation exists but it is incomplete, has a known gap, or only covers part of the described behavior. | A file path plus a specific description of what is missing. |
| `planned` | Not implemented. There is a concrete intention to build it as a near-term next step. | None required, but it must not be described using present-tense "the system does X" language. |
| `vision` | Not implemented. Describes the long-term direction, not a near-term commitment. | None required; must be visually/textually distinguished from `planned` (see `002-vision-and-mission.md`). |

`implementation_status` in a document's front matter describes the
**document's overall subject**. Within a document that mixes current and
planned material (e.g. `013-functional-requirements.md`), each individual
requirement or row must carry its own status — the front matter field
alone is not sufficient for mixed-status documents.

## How contradictions between code and documentation must be handled

**Fundamental rule: when documentation and implementation disagree, the
disagreement must be explicitly reported and resolved. Never silently
change the meaning of the product.**

Concretely:

1. If you find code that does something a `source_of_truth: true`
   document says it doesn't (or vice versa), do not silently edit the
   document to match the code, and do not silently change the code to
   match the document.
2. Determine which one is *intended* to be correct. If that is not
   obvious from context (git history, tests, related ADRs), say so
   explicitly rather than guessing.
3. Fix the wrong side, and only the wrong side — a documentation fix
   should be a documentation-only change; a code fix should not be
   bundled with an unrelated documentation rewrite.
4. If the contradiction reveals a deliberate-but-undocumented decision,
   write the missing ADR instead of just fixing the text.
