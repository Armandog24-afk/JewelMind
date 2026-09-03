# Stone Arrangement Engine v1 — machine-readable specification

Which stones participate in a design, and where they sit. A different question
from *what a stone is* ([`specs/stone/v2/`](../../stone/v2/README.md)), *what it
is made of* ([`specs/gem/v1/`](../../gem/v1/README.md)), and *how metal holds
it* ([`specs/setting/v1/`](../../setting/v1/README.md)).

Narrative half: [`docs/bible/24-arrangement/`](../../../docs/bible/24-arrangement/README.md).

## Status: PARTIAL, precisely

The declarative layer, its validation, its deterministic resolution and its
compilation boundary all execute. **Multi-stone geometry does not.** An
eight-stone halo resolves to eight real positions and produces one stone solid;
the other seven instances are reported `NOT_GENERATED`, each with a reason.

Nothing here may be read as multi-stone geometry support. See
[`execution-boundary.md`](../../../docs/bible/24-arrangement/execution-boundary.md).

## What this is not

- **Not a geometry engine.** Resolution produces numbers. No schema field holds
  a kernel object.
- **Not a constraint solver.** Every pattern is a closed-form generator,
  evaluated directly in a fixed order. A solver's output would depend on
  iteration order and starting values.
- **Not a jewelry-rule layer.** No spacing, clearance, stone-count or proportion
  rule exists. Each would need sourced professional evidence this project does
  not have.
- **Not category-specific.** No schema here mentions a ring.

## Files

| File | Contents |
| --- | --- |
| `arrangement-definition.schema.json` | The declarative arrangement: instances, groups, patterns, relations. |
| `stone-instance-def.schema.json` | One occurrence of a stone. |
| `instance-placement.schema.json` | Where an occurrence sits, and how that was expressed. |
| `instance-transform.schema.json` | Translation plus one vertical-axis rotation, in mm and degrees. |
| `instance-overrides.schema.json` | The closed set of per-instance deviations. |
| `arrangement-group.schema.json` | A named set that moves and is edited together. |
| `arrangement-pattern.schema.json` | LINEAR / RADIAL / MIRROR, plus what it applies to. |
| `arrangement-relation.schema.json` | A declared relationship between instances or groups. |
| `resolved-arrangement.schema.json` | The resolved contract every downstream consumer reads. |
| `resolved-instance.schema.json` | One instance's explicit placement and generation status. |
| `arrangement-registry.json` | Capabilities and the component-naming contract, from live code. |
| `examples/*.json` | Real arrangements, and the compiled resolution each one produces. |
| `test-vectors/*.json` | Behaviour recorded by running the real implementation. |

Every artifact was produced by running the real code, and
`backend/tests/test_arrangement_schemas.py` re-derives each one on every test
run — so a drift between this directory and the implementation fails the suite.

## Three independent capability axes

| Axis | Question |
| --- | --- |
| `representable` | can the model express it, and does it round-trip through JDL? |
| `resolvable` | does the resolver turn it into explicit numbers? |
| `generatable` | does the geometry pipeline build a solid for it? |

A capability may be representable and resolvable while remaining ungeneratable.
Today exactly one capability is `generatable`. Reporting the others as
"supported" would be a misstatement, so the registry keeps the axes apart.

## Identity is by ID, never by position

Reordering `instances`, `groups`, `patterns` or `relations` must not change the
fingerprint — ids are the authoritative identity and array order is a
serialization artifact. `test-vectors/normalization-vectors.json` records that
equality.

Generated pattern members get **derived** ids (`halo.0`, `halo.1`, …), so
re-resolving the same pattern produces the same ids. A random identifier would
break determinism and make a stored resolution impossible to compare with a
fresh one.

## Three separate identities

| Identity | Covers |
| --- | --- |
| `definitionHash` | the whole JDL document |
| `geometryHash` | the document minus provably non-geometry fields — the arrangement IS included |
| `arrangementFingerprint` | the arrangement's own content plus the resolver version |

The same arrangement reused in two rings has one fingerprint and two definition
hashes. `test-vectors/fingerprint-vectors.json` records the fingerprints.

## Component naming

The primary instance keeps the historical component name `stone_reference`
exactly, which is why every Golden baseline, exporter, inspection check and
frontend consumer is unaffected. An additional instance is
`stone_reference.<instanceId>`, and `backend/jewelmind/geometry/roles.py`
recognizes that prefix — so such a component is classified as a stone reference
and stays excluded from production exports by default (LAW-006), rather than
falling through to the `production_metal` default and being fused into metal.
`test-vectors/component-naming-vectors.json` records the classification.

## Forge rules

Six rules, all structural or referential:

| Rule | Checks | Severity |
| --- | --- | --- |
| `JM-ARRANGE-001` | instance ids are unique | error |
| `JM-ARRANGE-002` | every group/instance reference resolves | error |
| `JM-ARRANGE-003` | the referenced stone specification exists | warning (the design still generates) |
| `JM-ARRANGE-004` | the arrangement resolves, via the real resolver | error |
| `JM-ARRANGE-005` | at most one instance claims CENTER | warning |
| `JM-ARRANGE-006` | the multi-stone execution boundary | information |

`test-vectors/invalid-arrangement-vectors.json` records which LAYER refuses each
malformed case — a schema rejection means the document is malformed, a resolver
rejection means it is well-formed and inconsistent, and conflating them would
misreport where the mistake is.
