---
id: JM-BIBLE-199
title: JSON Export Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-079
related_documents:
  - JM-BIBLE-065
implementation_status: current
professional_validation: not_required
normative: true
---

# JSON Export Contract

## Contract, exactly

`export_json(definition) -> str`, in `backend/jewelmind/exporters/json_exporter.py`:

```python
def export_json(definition: JewelryDefinition) -> str:
    data = definition.model_dump(mode="json")
    return json.dumps(data, indent=2, sort_keys=True) + "\n"
```

- **Source**: the `JewelryDefinition` itself — this is the only Foundry artifact classified as `DESIGN_DEFINITION_ARTIFACT` (see [`192-artifact-domain-model.md`](192-artifact-domain-model.md)) rather than a geometry export.
- **Component inclusion**: not applicable in the geometric sense — every field of the definition, including `stone.diameter`/`stone.depth`, is present as design metadata. There is no metal solid in this artifact, so LAW-006 (never fuse the stone into metal) simply does not apply; there is nothing to fuse.
- **Determinism**: fully deterministic — `sort_keys=True` guarantees identical byte output for an identical definition, on any platform, every time. Unlike STEP (see [`197-step-export-contract.md`](197-step-export-contract.md)), no wall-clock or kernel-instance data is ever embedded.
- **Relationship to canonicalization**: this is *not* the same thing as Canonical JSON serialization used for `definitionHash` (see [`05-jdl/065-canonical-json-serialization.md`](../05-jdl/065-canonical-json-serialization.md)) — that canonicalization exists to produce a stable hash input; this export exists to produce a human/tool-readable file. Both happen to use `sort_keys=True`, but for different reasons, and this document does not claim they use an identical algorithm beyond that one shared property.

## Why JSON is the highest-fidelity Foundry artifact

Of the four current artifact types, JSON is the only one that is fully re-loadable as an equivalent `JewelryDefinition` — re-parsing the exported JSON and validating it against the schema reproduces the original definition exactly, confirmed by `backend/tests/test_api.py::test_export_json_matches_original_definition`. STEP and STL are one-way, lossy derivatives of the geometry Atlas built from this same definition; JSON is the design intent itself, serialized.

## Never a placeholder

`export_json()` always calls `definition.model_dump(mode="json")` on the real, already-validated `JewelryDefinition` object — there is no code path that returns a cached, stale, or hand-written sample document instead.
