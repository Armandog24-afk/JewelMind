---
id: JM-BIBLE-448
title: Validation Security and Privacy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-413
  - JM-BIBLE-414
  - JM-BIBLE-446
implementation_status: current
professional_validation: not_required
normative: false
---

# Validation Security and Privacy

This document states, plainly and only from verified code, what the
Professional Validation Framework does and does not do with data that
could be sensitive: a designer's unpublished design, exported CAD
geometry, a reviewer's identity, and any confidential manufacturing
information a review touches.

## No email, phone, or postal address field exists anywhere in this framework

`backend/jewelmind/professional_validation/schemas.py` was searched
directly for `email`, `phone`, and `address` — none of the three appears
anywhere in the file. `ReviewerQualification` (the one model that
describes a person) carries `reviewerId`, `role`, `yearsOfExperience`,
`professionalFocus`, `processes`, `materials`, `softwareExperience`,
`relevantPortfolioOrEvidence`, `geographicPractice`,
`qualificationNotes`, and `verificationStatus` — an identifying string
(`reviewerId`) and free-text professional context, never a structured
contact-detail field. There is no schema anywhere in this codebase asking
a reviewer for a way to be contacted.

## What is genuinely sensitive here, named explicitly

- **Unpublished designs.** A `JewelryDefinition` a user has not chosen to
  share publicly is exactly what a review package's `design.json` and
  `technical-specification.md` contain in full.
- **Exported CAD files.** `model.step`/`model.stl` are complete,
  real geometry — not a preview-quality approximation — and could
  reveal proprietary design details if the package reached an
  unintended recipient.
- **Review attachments and observations.** A future real
  `ReviewObservation`/photo/video evidence attachment could describe
  confidential manufacturing feedback (e.g. a named supplier's casting
  defect) — the schema (`ValidationEvidence.fileOrReference`) allows for
  this, though no such attachment mechanism is implemented yet (see
  [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md)).
- **Confidential manufacturing information.** A `ValidationScope`'s
  `geographicOrWorkshopConstraints` field could, in a real filled-in
  record, name a specific workshop or supplier relationship.

## The workflow is local and single-process

Review package generation runs entirely inside the same FastAPI backend
process that serves every other JewelMind endpoint — there is no separate
service, queue, or worker process for this feature.
`build_review_package()` reads only in-memory `ModelService` state and
files already on the local filesystem (`specs/forge/v1/current-rule-
registry.json`); it makes no outbound network call of any kind.

## No server-side database, no reviewer directory

The active professional-validation registry is one JSON file on disk
(`specs/professional-validation/v1/current-validation-registry.json`),
loaded fresh on every read by `registry.py::load_active_registry()` — no
SQL/NoSQL database, no reviewer-account table, and no persistent reviewer
directory exists anywhere in this codebase. `cli.py`'s own module
docstring says this directly: *"existence of a real reviewer profile is
not checked here — this tool has no reviewer database to check against
... this [is] an explicit, deliberate v1 scope limit."* A `reviewerId` is
therefore an unverified, self-declared string end to end; there is
nowhere in the system that could leak a reviewer roster, because no such
roster is ever stored.

## No automatic publication

`backend/jewelmind/professional_validation/` and
`backend/jewelmind/api/routes.py` were searched for `publish`/`public` in
any form related to this framework: no match. The one route this
framework adds, `POST /api/professional-validation/review-package`,
returns a file to the caller who requested it — nothing in this codebase
posts a review package, a validation record, or any derived summary
anywhere else automatically. Whether a completed review ever becomes
customer-visible is a question this Sprint does not answer; see open
question 7 in
[`452-open-professional-validation-questions.md`](452-open-professional-validation-questions.md).

## The ZIP is generated on demand and deleted immediately after the response

`review_package_route` (`api/routes.py`) returns the generated ZIP via:

```python
return FileResponse(
    zip_path,
    media_type="application/zip",
    filename=filename,
    headers={"X-Content-SHA256": checksum, "X-Package-Id": manifest.packageId},
    background=BackgroundTask(_delete_file, zip_path),
)
```

This is the identical `BackgroundTask(_delete_file, ...)` pattern every
other Foundry export endpoint (STEP, STL) already uses — Starlette runs
`_delete_file(zip_path)` only after the HTTP response has been fully sent
to the client, so the temporary ZIP exists on the server's local
filesystem only for the duration of one request/response cycle, never as
a standing artifact a second, unrelated request could retrieve. The two
intermediate export files (`model.step`/`model.stl` written by Foundry's
exporters before being read into the ZIP) are separately deleted inside
`build_review_package()`'s own `finally` block — see
[`446-review-package-generation.md`](446-review-package-generation.md).

## No internal server path is exposed to the caller

The `Content-Disposition`/`filename` the client receives is built from
`sanitize_filename(record.definition.project.name, ...)` — a sanitized,
user-facing project name — never the real `tempfile.mkstemp()`-generated
absolute path (FOUNDRY-GOV-011, restated at this endpoint).

## What this document does not claim

This is not a claim that JewelMind has undergone a formal security audit,
that transport-layer protections (TLS, auth) are configured for any
particular deployment, or that a future reviewer-facing portal (not
built) would inherit these same properties automatically. It is a
statement of what the current, local, single-process code path actually
does, verified against the real files named above.

## Cross-references

- [`446-review-package-generation.md`](446-review-package-generation.md) — the generation control flow this document's cleanup claims are based on.
- [`413-reviewer-role-model.md`](413-reviewer-role-model.md), [`414-reviewer-qualification-model.md`](414-reviewer-qualification-model.md) — the full `ReviewerQualification` shape.
- [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md) — no attachment storage, no signed record, no reviewer portal, tracked as real gaps.
