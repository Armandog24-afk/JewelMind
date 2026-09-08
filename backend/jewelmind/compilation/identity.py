"""`compilationHash`: the identity of a COMPILATION, not of a design.

TWO QUESTIONS, TWO IDENTITIES, and conflating them is the gap this module
closes (ALCHEMIST-GOV-010):

    definitionHash   "is this the same design?"
    compilationHash  "would compiling this design today produce the same
                      output as compiling it before?"

`definitionHash` is UNCHANGED and still means exactly what it meant —
`utils/hashing.py::definition_hash()`, the canonical JSON of the document. This
module adds an identifier beside it; it replaces nothing.

WHY THE DISTINCTION IS NOT ACADEMIC. A compiler upgrade, a Forge rule-set
change or a CadQuery/OpenCascade upgrade can all change the geometry produced
for an *unchanged* document. With `definitionHash` as the sole cache key, a
cached result could be served across such a change — reporting geometry that
today's code would no longer produce. In an in-memory cache that cleared on
every restart the risk stayed theoretical; the moment anything durable appears
it becomes a real defect, which is why this is closed BEFORE persistence rather
than with it.

DELIBERATELY PURE AND KERNEL-FREE. This module takes plain strings and returns
a string. It reads no version, imports no kernel and touches no filesystem, so
it is deterministic by construction and usable from any layer.

NOT A NEW HASHING CONVENTION. SHA-256 truncated to 16 hex characters, exactly
`definition_hash()`'s own scheme — the formula prescribed by
`docs/bible/08-alchemist/175-definition-hash-vs-compilation-hash.md`.
"""

from __future__ import annotations

import hashlib

from pydantic import BaseModel, ConfigDict, Field

#: Length of the truncated hex digest. The same 16 characters
#: `utils/hashing.py::definition_hash()` uses; stated once here rather than
#: repeated as a literal.
HASH_LENGTH = 16

#: Separator between fingerprint components.
#:
#: A character that cannot appear in any version string, so
#: `("1.0", "0|1")` and `("1.0|0", "1")` can never collide into one input.
#: Prescribed by 175's own formula.
_SEPARATOR = "|"

#: Placeholder for a component this environment cannot report.
#:
#: A STABLE STRING rather than an omission: dropping an absent component would
#: shorten the input and let an environment that cannot read its OCP build
#: produce the same hash as one that reports a build literally named for the
#: missing value. `None` is a fact about the environment, and it is recorded as
#: one.
ABSENT = "absent"


class CompilationFingerprint(BaseModel):
    """The output-affecting versions of one compilation environment.

    EVERY FIELD IS READ FROM A REAL RUNNING VERSION by
    `environment.py::current_fingerprint()` — never invented, never defaulted
    to a plausible value.

    WHICH COMPONENTS, AND WHY EXACTLY THESE. The set is prescribed by
    `175-definition-hash-vs-compilation-hash.md` (compiler, geometry generator,
    Forge rule-set) and extended with the kernel by
    `174-determinism-and-version-fingerprint.md`, which states that a
    `compilationHash` including a kernel version "would let two different kernel
    builds carry two different hashes for the same design intent — arguably
    more honest than today's `definitionHash`". Sprint 5's CI run had already
    proved two OCCT builds produce different volumes for one design, so the
    kernel is not a speculative component: it is the one empirically shown to
    matter.

    TWO THINGS ARE DELIBERATELY ABSENT, and their absence is the substantive
    design decision here:

    - **`jdlSchemaVersion`** — already inside `definitionHash`, because
      `schemaVersion` is a field of the document. Including it again would add
      no distinguishing power and would suggest the two identities overlap
      more than they do.
    - **`inspectionVersion`** — Geometry Inspection is READ-ONLY by contract
      (INSPECT-GOV-013): it measures geometry and never produces it. Including
      it would invalidate every cached solid whenever a measurement changed,
      discarding correct geometry for a reason that cannot affect geometry.

    `frozen=True` because a fingerprint describes an environment at a moment;
    mutating one would let a computed hash drift from the thing it identifies.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    #: The `jewelmind` package version — the Alchemist/compiler orchestration.
    compilerVersion: str = Field(min_length=1, max_length=64)

    #: `geometry/constants.py::GENERATOR_VERSION` — the Atlas builders.
    geometryGeneratorVersion: str = Field(min_length=1, max_length=64)

    #: The aggregate Forge rule-set version, from the live registry.
    forgeRuleSetVersion: str = Field(min_length=1, max_length=64)

    #: The installed CadQuery version.
    kernelVersion: str = Field(min_length=1, max_length=64)

    #: The installed OpenCascade (OCP) build, or `None` where it cannot be
    #: read. Carried separately from `kernelVersion` because
    #: `174-determinism-and-version-fingerprint.md` lists them as two distinct
    #: fields: one CadQuery release can be built against more than one OCCT.
    ocpVersion: str | None = Field(default=None, max_length=64)

    def components(self) -> tuple[str, ...]:
        """The fingerprint as an ORDERED tuple of strings.

        Order is fixed by this method and by nothing else — never by dict
        iteration, `model_dump()` ordering or field-definition order read at
        runtime. A hash whose input order could shift is not an identity.
        """

        return (
            self.compilerVersion,
            self.geometryGeneratorVersion,
            self.forgeRuleSetVersion,
            self.kernelVersion,
            self.ocpVersion if self.ocpVersion is not None else ABSENT,
        )


def compilation_hash(
    definition_hash_value: str, fingerprint: CompilationFingerprint
) -> str:
    """The identity of compiling THIS design in THIS environment.

    Deterministic by construction: the only inputs are the caller's
    `definitionHash` and the fingerprint's own ordered components. No
    timestamp, no UUID, no process id, no memory address, no environment
    variable and no iteration-order dependency participates.

    `definitionHash` comes first, so a reader can see at a glance that the
    design's own identity is the base and the environment qualifies it.
    """

    payload = _SEPARATOR.join((definition_hash_value, *fingerprint.components()))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:HASH_LENGTH]
