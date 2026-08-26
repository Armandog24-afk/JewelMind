"""Professional Validation Framework v1.

This package never performs professional validation itself — it is the
infrastructure that lets a real, identifiable jewelry professional's
review be captured as structured, versioned, auditable evidence. See
docs/bible/15-professional-validation/README.md and
370-conversation-governance.md's sibling, 410-validation-governance.md.

Nothing in this package may:
  - invent a reviewer, a qualification, or a piece of evidence;
  - treat a passing automated test as professional validation
    (PROVAL-GOV-006);
  - treat AI/LLM output as professional validation (PROVAL-GOV-007);
  - let a template or example `ValidationRecord` count toward the active
    validation registry (`registry.py` enforces this structurally: the
    active registry file and the example fixtures live in separate
    locations, and `registry.py` additionally rejects any loaded record
    with `isTemplate=True`).

As of this Sprint, the active registry
(`specs/professional-validation/v1/current-validation-registry.json`)
contains zero records, because no real professional review has occurred.
"""
