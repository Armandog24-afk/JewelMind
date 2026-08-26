# Jewelry Architecture v1 — machine-readable specifications

The platform-level half of [`docs/bible/18-ring-architecture/`](../../../docs/bible/18-ring-architecture/README.md). Ring is one jewelry category, never JewelMind's architectural root (JEWELRY-ARCH-GOV-001).

## Authority

This directory is authoritative for **category identity and capability metadata** — it never defines geometry, JDL fields, or validation rules; those remain owned by `specs/jdl/v1/`, `specs/forge/v1/`, and `specs/ring/v2/` respectively. `category-registry.json` mirrors the real Python registry at `backend/jewelmind/jewelry_category/registry.py` — regenerated from it, never hand-edited to add a capability the code doesn't have.

## Schemas

| File | Describes |
|---|---|
| `jewelry-category.schema.json` | A recognized category identity value (the fixed 6-value vocabulary). |
| `category-capability.schema.json` | The real capability declaration for one category. |
| `category-contract.schema.json` | The checklist a future category is expected to satisfy before moving from `planned` to `current`. |

## Category registry

`category-registry.json` — 6 entries, generated from `backend/jewelmind/jewelry_category/registry.py::CATEGORY_CAPABILITIES`. Only `ring` has `status: "current"` and `generationSupported: true`.
