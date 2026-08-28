---
id: JM-BIBLE-584
title: Setting Attachment Interface
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-581
  - JM-BIBLE-528
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Attachment Interface

## The contract

`SettingAttachmentInterface` (`setting/models.py`) is the generic, category-neutral handoff between a Setting and whatever structure incorporates it:

| Field | Meaning |
|---|---|
| `attachmentPlaneZMm` | Z of the plane the setting attaches down onto. For a ring this is the top of the band — but the Setting does not know that. |
| `embedMm` | How far setting geometry sinks past the attachment plane so a boolean union yields genuine 3D overlap rather than a zero-volume tangent touch. A kernel/boolean-robustness value, never a jewelry threshold. |
| `supportHeightMm` | Vertical distance from the attachment plane up to the stone's girdle plane — how much support structure sits between them. |

Three fields, all numbers, all supplied **by** the category integration. That is the whole interface.

## Why so small

The temptation was to model attachment richly — an attachment region, a contact surface, a list of connection anchors, an expected overlap volume. Brief section 21 lists exactly those as *potential* concepts.

They were not implemented, because nothing consumes them yet. The current integration needs precisely three numbers to place a prong or a bezel correctly, and a Setting that received an attachment *region* would have no code path that read it. Adding unread fields would have been speculative configuration presented as capability — the thing SETTING-GOV-005 and the Capability Coverage Guard exist to prevent.

Richer attachment concepts are a real future need (a cathedral head, a pendant bail, an earring post all attach differently), and the interface is the right place for them. They belong to the sprint that has a consumer.

## Who supplies it

`geometry/setting_adapter.py::setting_attachment_interface()`:

```python
interface = shank_connection_interface(definition)   # Ring-side, Sprint 17
return SettingAttachmentInterface(
    attachmentPlaneZMm=interface.topZMm,
    embedMm=interface.embedMm,
    supportHeightMm=definition.setting.basketHeight,
)
```

Note the chain: Sprint 17 built `ShankConnectionInterface` for the Shank → RingHead handoff, and this Sprint reuses its `topZMm`/`embedMm` as the Setting's attachment plane. So the ring's own head geometry is computed once and handed to the Setting, rather than the Setting re-deriving it — which is the difference between an interface and a shared assumption.

Because the adapter lives outside `jewelmind/setting/`, the Setting core never imports `shank_connection_interface` or `JewelryDefinition`. `test_setting_system_no_ring_dependency.py` asserts both.

## How a Setting uses it

Both families consume it the same way — build downward from the plane they were handed:

```python
base_z = attachment.attachmentPlaneZMm - attachment.embedMm   # prong
height = prong.prongHeightMm + attachment.embedMm
```

The bezel does not use `attachmentPlaneZMm` directly at all: its wall is centred on the stone's girdle plane, and connectivity to the ring is achieved because the basket support already spans from the band top up to that girdle plane, so the wall overlaps its top. Verified rather than assumed — `test_setting.py::TestSettingConnectivity` asserts the production connectivity graph is fully connected and that the metal fuses to a single solid for both families.

`test_setting.py::TestSettingAttachmentInterface::test_attachment_plane_is_independent_of_the_setting_family` asserts prong and bezel receive an identical interface, which is what makes the contract genuinely generic rather than incidentally shared.

## The future consumers

The interface is deliberately named for structures, not for rings:

| Consumer | Status |
|---|---|
| `RingHead` (`assemblies/solitaire.py`) | **CURRENT** — the only implemented integration. |
| `PendantBody` | PLANNED. A pendant attaches a setting to a bail rather than a shank; the same three numbers describe it. |
| `EarringBody` | PLANNED. Same shape of contract. |

None of the planned consumers is registered anywhere as working, and no category other than `ring` is `generationSupported` (Sprint 16's registry).

## What must never happen

- A Setting computing its own attachment plane from a band, shank, or ring-size field (SETTING-GOV-001/014).
- A Setting branching on which category is attaching it.
- Category-specific attachment logic moving *into* `jewelmind/setting/` — that belongs in the adapter or the category's own head module.

## Cross-references

- [`../19-shank/550-head-connection-interface.md`](../19-shank/550-head-connection-interface.md) — the Shank → RingHead interface whose values this one reuses.
- [`../18-ring-architecture/528-head-contract.md`](../18-ring-architecture/528-head-contract.md) — the Ring-side head contract.
- [`current-prong-migration.md`](current-prong-migration.md) — the SETTING / RING_HEAD responsibility audit.
