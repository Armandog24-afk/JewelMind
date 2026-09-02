---
id: JM-BIBLE-616
title: "Stone v2 Capability Model"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-613
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone v2 Capability Model

`backend/jewelmind/stone/capability.py` is the **single source of truth** for
what the Stone System can actually do. Everything else mirrors it:

```
capability.py  ──►  specs/stone/v2/shape-registry-v2.json      (generated)
               ──►  specs/stone/v2/stone-source-registry.json  (generated)
               ──►  specs/stone/v2/setting-compatibility-v2.json (generated)
               ──►  specs/capabilities/jewelmind-capabilities.json (generated)
               ──►  setting/capability.py's shape split         (derived)
               ──►  designer/capability.py's unsupported list   (derived)
               ──►  designer/normalizer.py's identity aliases   (derived)
```

Nothing in that list is hand-maintained. Sprint 20 removed three hand-copies
that had already drifted:

1. Setting's shape lists still held only the seven Stone v1 shapes, so a bezel
   over a custom outline was refused as unsupported.
2. Designer's `KNOWN_UNSUPPORTED_CONCEPTS` still listed heart, radiant, asscher,
   trillion, baguette and cabochon as unsupported.
3. Designer's synonym table lacked the underscored canonical IDs, so
   `tapered_baguette` and `half_moon` were reported unsupported.

Each was a *misreport of a real capability* — the same failure Sprint 18 had to
correct for its six shapes. Deriving instead of copying is what stops a fourth
occurrence.

## The three independent axes

```
generationSupported          does real CAD come out?
prong/bezelCompatibility     can a setting grip it?
professionalValidationStatus did a qualified human review it?
```

They are independent, and `pearl` is the clearest proof: it generates a real
sphere (`true`), no setting will hold it (`UNSUPPORTED`), and no one has
reviewed it (`NOT_REVIEWED`).

Every entry in the registry is `NOT_REVIEWED`. The active
professional-validation registry holds **zero** records
(STONEV2-GOV-007, PROVAL-GOV-006).

## Status vocabulary

| Status | Requires |
|---|---|
| `CURRENT` | a real generator AND real tests AND a Golden case |
| `PARTIAL` | some of the capability is real; the note says which part is not |
| `PLANNED` | no implementation. Never advertised as working |
| `BLOCKED` | cannot be implemented now; the note says what blocks it |
| `OUT_OF_SCOPE` | deliberately excluded |

## The Capability Coverage Guard

`specs/capabilities/jewelmind-capabilities.json` grew from 101 to **137**
entries: 56 `CURRENT`, 69 `PLANNED`, 2 `PARTIAL`, 7 `BLOCKED`,
3 `OUT_OF_SCOPE`.

The 49 stone entries span six domains — `stone_shape`, `stone_source`,
`stone_profile`, `stone_import_format`, `stone_outline`, `stone_anchor` — and
are all generated from the live registries.

`backend/tests/test_capability_coverage.py` (18 tests) checks the guard against
the live code, including:

- every `CURRENT` shape must be in the live registry and have a generator;
- every `PLANNED` shape must NOT be a JDL enum member;
- every `BLOCKED` entry must explain what blocks it;
- the Stone v1 and v2 registries must agree on the facts they both state.

That last test is new, and it exists because two registries describing the same
seven shapes is a drift hazard. The Sprint 18 registry remains as a frozen
record of Stone v1 with its own field shape; what must never diverge is which
shapes exist and whether each generates.

## What is honestly `PARTIAL`

**`IMPORTED_CAD`** — B-Rep and mesh import, unit normalization, inspection and
Vision work. Setting compatibility is decided per asset from real geometry
rather than granted, and outline projection does not exist.

**`imported` (the pseudo-shape)** — same reason.

## What is honestly `PLANNED`

| Capability | Why |
|---|---|
| `STONE_SCAN` | No scan-specific processing exists. A converted scan is importable today through `IMPORTED_CAD` |
| `IMPORTED_OUTLINE_PROJECTION` | Deriving a girdle outline from imported geometry is not implemented |
| `CUSTOM_OUTLINE_CURVE_SEGMENTS` | Only ordered points are accepted; curve segments and SVG import do not exist |
| `ANCHOR_DRIVEN_PRONG_PLACEMENT` | Setting places prongs from the outline support function, not from named anchors |
| 5 reserved shapes | `briolette`, `rose_cut`, `old_mine`, `star`, `cross` — each with a real recorded reason |
| Near-round / drop / button pearls | No non-spherical pearl body exists |

## What is `BLOCKED`

The seven unsupported import formats — `.obj`, `.gltf`, `.glb`, `.iges`,
`.igs`, `.3dm` — each with the real reason the installed build cannot read it.
`.3dm` is additionally blocked by policy: JewelMind never requires Rhino.

## Frontend mirrors are hand-maintained, deliberately

`ConfigurationPanel.tsx`'s `STONE_SHAPE_OPTIONS` and `SHAPE_PROFILE_OPTIONS`
are hand-kept, like every other option list in that file. The frontend has no
runtime access to the Python registry, and generating TypeScript from it would
add a build step this project does not have.

The mitigation is that the lists are small, documented as mirrors, and required
to change in the same commit as the backend registry. `custom` and `imported`
are deliberately absent from the shape dropdown: they are consequences of
choosing a different source, not cuts a user picks.

## Cross-references

- [`stone-setting-compatibility-v2.md`](stone-setting-compatibility-v2.md)
- [`code-mapping-and-gaps.md`](code-mapping-and-gaps.md)
- [`../15-professional-validation/410-validation-governance.md`](../15-professional-validation/410-validation-governance.md)
