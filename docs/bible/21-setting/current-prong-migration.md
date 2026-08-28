---
id: JM-BIBLE-590
title: Current Prong Migration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
  - JM-BIBLE-081
related_documents:
  - JM-BIBLE-585
  - JM-BIBLE-592
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Prong Migration

## The responsibility audit

Brief section 22 required classifying existing head behaviour before moving anything, and warned specifically against sweeping every basket/head function into Setting.

| Behaviour | Classification | Moved? | Reasoning |
|---|---|---|---|
| Prong solids, count, diameter, height | **SETTING** | Yes → `setting/prong.py` | Purely a stone/metal interaction. Knows nothing about rings. |
| Prong placement | **SETTING** | Yes → `setting/placement.py` | Derived from stone geometry alone. |
| Bezel wall | **SETTING** | New | Derived from the stone outline. |
| Attachment plane Z, embed depth | **RING_HEAD** | No | Computed from band geometry (`band_top_z`). Passed *in* via `SettingAttachmentInterface`. |
| `basket_support` geometry | **PARTIAL — RING_HEAD today** | No | See below. |
| Stone girdle Z placement | **STONE + RING_HEAD** | No | The stone builder computes `band_top_z + basketHeight`; Setting reads the result as a fact. |
| Metal fusion | **RING_HEAD** | No | The assembly decides what to fuse; it reads `productionComponents` rather than hardcoding names. |
| Component roles, connectivity, inspection | **SHARED_ATLAS** | No | Pre-existing infrastructure, extended for `bezel`. |

## The basket boundary

`basket_support` is genuinely ambiguous, and brief section 23 explicitly permits saying so rather than forcing a split.

It is simultaneously:

- a **setting support structure** — it holds the stone at the correct height, and its radius is derived from the prong placement radius; and
- a **ring attachment structure** — it physically bridges the band to the head, and its base is embedded into the band.

Current status: **PARTIAL, RING_HEAD-owned.** It stays in `geometry/components/basket.py`, is built by the assembly, and continues to use `geometry/constants.py::prong_center_radius()`.

Forcing a split today would mean either duplicating the radius computation (inviting drift) or moving band-dependent geometry into a category-neutral package (violating SETTING-GOV-001). Neither is an improvement. The **TARGET** is that a future setting-support concept lives in Setting while ring-specific attachment stays in the RingHead — likely alongside Sprint 23's advanced heads.

One real consequence is guarded: because the basket still calls `prong_center_radius()` while the Setting System computes the same radius independently, `test_radial_placement_matches_the_legacy_prong_center_radius_helper` asserts the two agree to `rel=1e-12` so they cannot silently diverge.

## The JDL change: MINOR, additive

`domain/schema.py::SettingSpec` changed in two ways:

- `type` gained the `bezel` enum member.
- `bezelWallThickness` and `bezelWallHeight` were added, both with defaults.

Per [`../05-jdl/081-schema-versioning-and-migrations.md`](../05-jdl/081-schema-versioning-and-migrations.md)'s MINOR definition — *"an additive, backward-compatible change: a new optional field with a default, a new enum member appended to an existing list"* — both qualify exactly. `schemaVersion` stays `"0.1.0"`.

Crucially, **prong fields are not required for a bezel and bezel fields are not required for a prong.** Every field keeps a default, so neither family's fields are mandatory for the other; they are simply unread. `test_setting.py::test_prong_fields_are_not_required_for_a_bezel` and `test_a_pre_sprint19_document_without_bezel_fields_still_validates` pin both directions.

The discriminated model lives one layer in (`ProngSettingDefinition` / `BezelSettingDefinition`), with `geometry/setting_adapter.py` as the compatibility adapter — the arrangement brief section 30 permits.

## The `definitionHash` drift, third occurrence

The two additive fields changed `definition_hash()` for every document once regenerated:

| Example | Before | After |
|---|---|---|
| `default-solitaire.json` | `e1d6dc2f2390875d` | `8def81bd12b97d38` |
| `four-prong-solitaire.json` | `76cd86b9ac469105` | `32c53d931bce713c` |
| `flat-band-solitaire.json` | `613e1b7451247e6f` | `e14e38d7d9d7fd71` |
| `direct-resin-printing-solitaire.json` | `276ac91816f0fd6a` | `b16cb081b5a415dc` |

(plus the three `examples/invalid/` documents.)

This is the **third consecutive sprint** with this finding, for the identical mechanism: `canonical_json()` serialises every field including newly-added defaults, so any additive schema change alters the hash of every existing document once re-validated. It is **not** a violation of Migration Requirement 4 — that rule concerns migrating an already-stored document, whereas this is normalization-time default-filling on a freshly re-validated one.

It is recorded as a standing structural tension in [`../appendices/jdl-version-compatibility-matrix.md`](../appendices/jdl-version-compatibility-matrix.md) rather than re-argued each sprint. Verified again that `compare_snapshot()` never reads `definitionHash`, so Golden regression detection is unaffected.

Regenerated by running real code (never hand-typed): the JDL hash and canonicalization vectors, Alchemist normalization and capability vectors, Atlas metadata vectors, both geometry-inspection examples, the Designer example, and the Conversation example.

## What was removed, and what was deliberately kept

**Removed** — because it had become factually false:

- `bezel` from `designer/capability.py::KNOWN_UNSUPPORTED_CONCEPTS`, which claimed *"Only a prong setting is currently supported."* Leaving it would have made Designer actively misreport a real capability. (`tension`/`channel` remain, and `flush`/`bar` were added, since those are genuinely unimplemented.)

**Deliberately kept:**

- `geometry/components/prongs.py` as a thin adapter, preserving the pre-Sprint-19 import path so no caller had to change. It rebuilds the stone to derive the setting's stone facts; the assembly path avoids that duplicate build by calling the Setting System directly with the stone it already made.
- `prong_center_radius()` in `geometry/constants.py`, still used by the basket.
- The `prongs` compound as a single component (see [`prong-setting-contract.md`](prong-setting-contract.md) for why splitting it was rejected).
- The fuse order (band, basket, then setting), which is what keeps a prong model's fused solid byte-identical.

## Verified backward compatibility

- `combined_metal_volume_mm3 == 341.44334316909976` — exact equality.
- Prong volume `== 29.650351464580467` — exact equality.
- All 12 round-stone Golden cases (`SOL-001`–`SOL-012`): **zero** baseline updates.

The six non-round Golden cases *did* change, intentionally — see [`setting-golden-strategy.md`](setting-golden-strategy.md).
