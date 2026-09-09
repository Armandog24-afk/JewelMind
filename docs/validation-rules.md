# Validation rules

Validation is deterministic and runs in two places:

- **Backend (authoritative):** `backend/jewelmind/validation/engine.py`. Runs
  on every `POST /api/models/validate` and `POST /api/models/generate` call,
  and again defensively before every export. Its verdict always wins.
- **Frontend (mirror):** `shared/validation/engine.ts`. Gives the user
  instant feedback while typing, without a network round trip. Kept in sync
  with the backend rule-by-rule; if the two ever disagree, trust the
  backend response (surfaced automatically — see below).

A `ValidationResult` looks like:

```json
{
  "ruleId": "JM-BAND-002",
  "severity": "error | warning | information",
  "message": "Human-readable message",
  "parameter": "band.thickness",
  "suggestedValue": 1.6
}
```

`error` results block generation and export. `warning` and `information`
results are shown but never block anything.

## Rule reference

| Rule ID | Parameter(s) | Condition | Severity |
|---|---|---|---|
| `JM-RING-001` | `ring.innerDiameter` | Must be strictly between 10 mm and 30 mm. | error |
| `JM-RING-002` | `ring.size` | Must be strictly between 1 and 50. | error |
| `JM-RING-003` | `ring.innerDiameter` | EU size and inner diameter are converted via `size = (π × diameter) − 40` (see `docs/domain-model.md` and `sizing.py`) and compared; a discrepancy over 0.15 mm is `information`, over 0.5 mm is `warning`. Neither field is ever rewritten automatically. | information / warning |
| `JM-BAND-001` | `band.width` | Below 1.5 mm. | error |
| `JM-BAND-002` | `band.thickness` | Below 1.4 mm is an error; 1.4–1.6 mm (exclusive) is a warning. | error / warning |
| `JM-BAND-003` | `band.width` | Above 12 mm. | warning |
| `JM-STONE-001` | `stone.diameter` | Must be between 2 mm and 15 mm. | error |
| `JM-STONE-002` | `stone.depth` | Must be greater than 0.5 mm and less than `stone.diameter`. | error |
| `JM-PRONG-001` | `setting.prongCount` | Must be exactly 4 or 6. | error |
| `JM-PRONG-002` | `setting.prongDiameter` | Below 0.8 mm is an error; 0.8–1.0 mm (exclusive) is a warning. | error / warning |
| `JM-PRONG-003` | `setting.prongCount` | `stone.diameter` > 8 mm with 4 prongs. | warning |
| `JM-PRONG-004` | `setting.prongHeight` | Must be greater than `setting.basketHeight`. | error |
| `JM-SETTING-001` | `setting.basketHeight` | Must be positive. | error |
| `JM-SETTING-002` | `setting.basketHeight` | Above 8 mm. | warning |
| `JM-GEM-001` | `stone.gem.gemId` | The referenced gem registry entry does not exist. A **warning**, not an error: a design referencing a removed entry must still load and still generate. | warning |
| `JM-GEM-002` | `stone.gem.origin` | The declared origin is not in the registry entry's `applicableOrigins` (e.g. a cubic zirconia declared `NATURAL`). Refused rather than corrected — resolving it would mean deciding whether the user meant the material or the origin. | error |
| `JM-GEM-003` | `stone.gem.customName` | `custom` requires a material name, and only `custom` may have one. Also enforced structurally by `JdlGemIdentity`, so the second branch fires only for an identity built in Python. | error |
| `JM-GEM-004` | `stone.gem.visualProfileId` | The visual profile override does not resolve; a neutral fallback appearance is used. Affects how the stone is drawn, never what it is. | warning |
| `JM-GEM-005` | `stone.gem.treatments` | A duplicate treatment record is a warning; the same treatment recorded as both `PRESENT` and `NOT_PRESENT` is an error. | warning / error |
| `JM-GEM-006` | `stone.gem.gemId` | The entry is deprecated but still resolvable. | warning |
| `JM-SETTING-005` | `setting.pegDiameter`, `setting.pegHeight` | A `PEG_HEAD` requires both, and the peg must be positive and shorter than `setting.basketHeight`. No default is applied: an invented peg size would be a construction choice the user never made. | error |
| `JM-SETTING-006` | `setting.prongStyle`, `setting.pegDiameter`, `setting.pegHeight` | A field the chosen family or architecture does not read. `information`, not a warning: the design is valid and only the value is inert. | information |
| `JM-SETTING-008` | `setting.mode.modeId` | The declared setting mode belongs to a different family than `setting.type` selects, or is a HEAD/RETENTION mode declared on the PRIMARY axis. Refused rather than resolved by precedence: two authorities over one setting have no determinate resolution. | error |
| `JM-SETTING-009` | `setting.mode.parameters.*` | The resolved mode does not read a parameter the document set, or the mode is disabled so the family's default variant is used. The value is kept in the document and has no effect — reported rather than silently dropped. | information |
| `JM-SETTING-010` | `setting.seatMode` | A flush setting was requested without seat relief. The recess is half a flush setting's geometry: without it the collar occupies the stone's whole volume. A GEOMETRIC precondition, not a professional requirement. | error |
| `JM-SETTING-011` | `setting.mode.parameters.rimHeightMm` / `padDepthMm` | A collar rim taller than the whole stone buries it; two opposing supports reaching further inward than the stone's half-extent meet through its middle. Both are ARITHMETIC. Necessary conditions on the document's own requested dimensions — the exact check runs against the real measured solid at generation time. | error |
| `JM-SETTING-012` | `setting.type` | The setting mode requires review by a qualified jewelry professional. Emitted for a tension setting, whose structural behaviour JewelMind does not model at all. **Not a verdict**: it says a professional must look, never that one has. | warning |
| `JM-SETTING-013` | `setting.type` | The resolved setting mode's capability status is PARTIAL rather than CURRENT, with what is missing. Reported so a caller never has to read the capability registry to learn that a mode it just used is incomplete. | information |
| `JM-SETTING-007` | `setting.seatMode` | Seat relief cuts the stone volume out of the metal, which needs the stone to parse as a solid; an imported asset may be a mesh. Whether it does is only knowable after import, hence a warning. | warning |
| `JM-FAMILY-001` | `family` | The design declares both a family and an explicit arrangement. A family compiles into an arrangement, so only one may be present — two authorities over one set of placements has no determinate resolution. | error |
| `JM-FAMILY-002` | `family.members` | A member's role is not accepted by this family, or a required role has the wrong number of members (e.g. two centres in a three-stone design). | error |
| `JM-FAMILY-003` | `family` | The family cannot be compiled into an arrangement. Evaluated by running the REAL compiler, so Forge can never disagree with what generation does. | error |
| `JM-FAMILY-004` | `family.members` | A member references a stone specification other than `primary`, or requests a setting the design does not use. A **warning**: the design is valid and only that member is affected. | warning |
| `JM-FAMILY-005` | `family` | The family builds stone geometry for every member, but a setting is generated only for the primary stone. Not a fault in the design. | information |
| `JM-HALO-001` | `halo.centerMemberId` | The halo names a centre this design's placement does not contain. Refused rather than re-anchored on the design origin — a halo around the wrong stone is worse than one that fails loudly. | error |
| `JM-HALO-002` | `halo` | The halo cannot be composed onto this design's placement. Evaluated by running the REAL compiler, so Forge can never disagree with what generation does. | error |
| `JM-HALO-003` | `halo.centerMemberId` | This family/halo combination is not supported — e.g. a halo naming a centre in a toi-et-moi, which has no CENTER member. Reported with the real reason rather than only refused. | error |
| `JM-HALO-004` | `halo.rings` | A ring references a stone specification other than `primary`, or requests a setting the design does not use. A **warning**: the design is valid and only those stones are affected. | warning |
| `JM-HALO-005` | `halo` | The halo builds stone geometry for every halo stone, but no metal is generated to hold them. Not a fault in the design. | information |
| `JM-PAVE-001` | `pave.host` | The requested host surface has no resolver. Refused rather than approximated onto another surface. | error |
| `JM-PAVE-002` | `pave` | The field cannot be compiled against this design's real host surface. Evaluated by running the REAL compiler, so Forge can never disagree with what generation does. | error |
| `JM-PAVE-003` | `pave.spec` | Lattice cells fell outside the host surface's declared extent and were clipped. A **warning**: a clipped field is a real, buildable design. | warning |
| `JM-PAVE-004` | `pave.stoneRef` | The field references a stone specification other than `primary`. A **warning**: only that field produces no geometry. | warning |
| `JM-PAVE-005` | `pave` | What the field builds and does not build, plus the requirement that a qualified jewelry professional review it before production. Not a fault. | information |
| `JM-PAVE-006` | `pave.stoneScale` | The stones are wider than the pitch between their centres, so they overlap as a matter of arithmetic. A GEOMETRIC inconsistency, **not** a manufacturing threshold: JewelMind states no minimum pavé spacing. | warning |
| `JM-ARRANGE-001` | `arrangement.instances` | Two stone instances declare the same id. Ids are the authoritative identity, so a duplicate makes every reference to it ambiguous. | error |
| `JM-ARRANGE-002` | `arrangement.instances`, `arrangement.patterns` | A placement or pattern names a group or instance that is not declared. | error |
| `JM-ARRANGE-003` | `arrangement.instances` | An instance references a stone specification other than `primary`, which no current document declares. A **warning**: the design is structurally valid and still generates, and only that instance produces no geometry. | warning |
| `JM-ARRANGE-004` | `arrangement` | The arrangement cannot be resolved. Evaluated by running the REAL resolver, so Forge can never disagree with what generation does. | error |
| `JM-ARRANGE-005` | `arrangement.instances` | More than one instance claims the `CENTER` role, which is ambiguous about which stone the single-stone pipeline builds. The lowest id is used. | warning |
| `JM-ARRANGE-006` | `arrangement.instances` | The arrangement resolves more than one instance. Multi-stone geometry is not implemented, so one stone is built and the rest are reported as placements only. Not a fault in the design. | information |
| `JM-MANUFACTURING-001` | `band.thickness`, `band.width` | For `manufacturing.method = direct_resin_printing`, either dimension below 0.8 mm. (`setting.prongDiameter` is excluded here — `JM-PRONG-002` already errors below 0.8 mm regardless of manufacturing method.) | warning |
| `JM-GEOMETRY-001` | `band.thickness`, `band.width` | Defense-in-depth: rejects any combination that would produce a non-positive outer band dimension (e.g. zero/negative thickness or width), independent of the rules above. | error |

## Why the EU size ↔ diameter conversion is isolated

`ring.size` and `ring.innerDiameter` are both user-editable and can
legitimately disagree (different sizing conventions, a ring resized after
casting, deliberately loose/tight fit). JewelMind never silently overwrites
one from the other. The conversion itself lives in one place —
`backend/jewelmind/validation/sizing.py` and its TypeScript mirror
`shared/validation/sizing.ts` — so the convention is documented once and
reused by both the rule engine and (if needed later) any future UI helper
that suggests a consistent pair of values.

## Adding a new rule

1. Add a `JM-XXX-NNN` constant to `backend/jewelmind/validation/rules.py`
   and its mirror in `shared/validation/rules.ts`.
2. Implement the check in `backend/jewelmind/validation/engine.py`.
3. Mirror it in `shared/validation/engine.ts`.
4. Add a backend test in `backend/tests/test_validation.py` for every
   severity branch.
5. Update the table above.
