---
id: JM-BIBLE-295
title: Designer To JDL Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-294
related_documents:
  - JM-BIBLE-296
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer → JDL Contract

## The 19 fields, and only these 19

`backend/jewelmind/designer/capability.py::KNOWN_JDL_FIELD_PATHS`:

```
project.name, ring.size, ring.innerDiameter, ring.sizeSystem,
band.width, band.thickness, band.profile,
stone.diameter, stone.depth, stone.shape,
setting.prongCount, setting.prongDiameter, setting.prongHeight,
setting.basketHeight, setting.type,
material.metal, manufacturing.method,
jewelry.category, jewelry.style
```

This frozenset is the entire contract between Designer and JDL. A dotted path the provider names that isn't in this set never reaches a candidate JDL, regardless of how confidently or repeatedly the provider names it — this is DESIGNER-GOV-004's mechanism, verified by `test_designer.py::TestUnsupportedFeature::test_unknown_field_from_provider_is_rejected_not_smuggled_into_jdl`.

## What happens to an unknown field

`service.py::_build_proposal()`:

```python
if not capability.is_known_field(path):
    diagnostics.append(DesignerDiagnostic(
        code=DESIGNER_CAPABILITY_MISMATCH,
        severity="warning",
        message=f"'{path}' is not a JDL field JewelMind recognizes; ignored.",
        field=path,
    ))
    continue
```

It becomes exactly one `DesignerDiagnostic` with code `DESIGNER_CAPABILITY_MISMATCH`, and processing moves on to the next proposed value. It is never appended to the patch dict, never reaches `_apply_patch()`, and never appears in `proposedFields`. There is no "best effort" partial acceptance of an unknown path.

## Why this list is a frozen constant, not schema introspection

Unlike the enum capability sets in [`296-capability-awareness.md`](296-capability-awareness.md), `KNOWN_JDL_FIELD_PATHS` is a hand-maintained frozenset, not derived by walking `JewelryDefinition`'s fields at runtime. This is a deliberate, narrower surface: `JewelryDefinition` has other fields (e.g. `manufacturing.notes`, metadata-only fields) that Designer is not meant to ever propose, even though they exist in the schema. Adding a field to this set is itself a capability change and must be reviewed alongside a schema change, per [`../05-jdl/README.md`](../05-jdl/README.md)'s own schema-change discipline.

## The one path with no schema `Literal`

`setting.prongCount` is in this list but is not an enum field the way the others are — see [`296-capability-awareness.md`](296-capability-awareness.md) for the full explanation of why its allowed values come from a Forge rule, not a `Literal`.

## Candidate JDL is always built by JewelMind's own code

`_apply_patch()` merges the accepted patch dict onto a `model_dump()` of the base definition and re-validates through `JewelryDefinition.model_validate()` — the same strict Pydantic entry point every other code path uses. A provider never constructs or returns a `JewelryDefinition`-shaped object itself; it can only ever return the flatter `RawDesignerResponse` shape described in [`305-structured-output-contract.md`](305-structured-output-contract.md).

See [`296-capability-awareness.md`](296-capability-awareness.md) for how the allowed *values* within each of these 19 paths are determined.
