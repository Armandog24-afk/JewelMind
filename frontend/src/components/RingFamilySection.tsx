import type {
  JewelryStyle,
  RingFamilyParams,
  RingFamilySpec,
  RingFamilyVariantId,
} from '@shared/types/jewelry-definition'
import { useProjectStore } from '../store/useProjectStore'
import { FormSection } from './FormSection'
import { NumericField } from './NumericField'
import { SelectField } from './SelectField'

/**
 * Ring Family controls (Sprint 28).
 *
 * WHAT THIS SECTION IS FOR, and why it comes first among the design controls. A
 * ring family is the design's own STRUCTURE: which family it belongs to, which
 * variant of it, and the parameters that variant reads. Everything below it —
 * the band, the stone, the setting — is either read by the family or modulated
 * by it, so choosing the family first is choosing what the rest of the form
 * means.
 *
 * A FAMILY IS A RELATION, NOT A PRESET, and the interface has to make that
 * visible or the system reads as a catalogue. Two things do it:
 *
 * - Changing the family or the variant does NOT overwrite the band, the stone or
 *   the head. It changes what the family DERIVES from them, so `ring.size` and
 *   `stone.diameter` keep driving the geometry and the variant modulates the
 *   result. A user who set a basket height keeps it; an elevated variant scales
 *   it.
 * - Only the parameters the chosen variant READS are shown, mirroring the
 *   backend's own `parameters_read_by()`. A value the variant ignores is not
 *   hidden from the document — it stays there and `JM-RINGFAM-003` reports it as
 *   having no effect — it is simply not offered as though it did something.
 *
 * EXPOSES ONLY WHAT THE BACKEND BUILDS. Every option list is a literal mirror of
 * the backend's own `Literal` members, which are exactly the variants with a
 * real derivation: a reserved family (`plain_band`, `channel_set_band`) or
 * variant (`SOLITAIRE_TRELLIS`, `SIGNET_ENGRAVED`) is absent from the type and
 * therefore cannot appear here. `eternity`, `cluster` and `toi_et_moi` were
 * reserved until Sprint 29 built them, and they appear here now for exactly
 * that reason. This panel carries no "coming soon" list, because an
 * option a user can pick and the product cannot build is worse than an absent
 * one (STUDIO-GOV-011).
 *
 * NO THRESHOLD LIVES HERE. Every `min`/`max` is the SCHEMA's own bound, mirrored
 * so a control cannot leave the representable range; it is advisory, and the
 * backend's `validate_definition()` verdict always wins (STUDIO-GOV-001/002).
 *
 * EVERY EDIT IS A DESIGN EDIT, routed through the store so an existing model is
 * marked stale and the last-good preview is preserved (STUDIO-GOV-004/006).
 */

/** Mirrors the backend's `default_params()` exactly.
 *
 * One definition of "pick this family" is what stops a spoken instruction and a
 * UI selection producing different designs from the same request — the
 * discipline `default_pave_field()` and `default_mode_parameters()` both
 * established.
 */
function defaultParams(): RingFamilyParams {
  return {
    headHeightFactor: 1.0,
    shoulderSpanDeg: 50,
    shoulderTopWidthFactor: 0.85,
    shoulderTopThicknessFactor: 0.85,
    splitSeparationMm: 1.2,
    splitJoinSpanDeg: 200,
    bypassSeparationMm: 1.0,
    bypassOverlapDeg: 60,
    signetTableLengthMm: 11,
    signetTableWidthMm: 9,
    signetTableHeightMm: 2,
    sideStoneScale: 0.55,
    sideSpacingMm: 5,
    sideGraduationFactor: 0.8,
    haloStoneCount: 16,
    haloRadiusFactor: 1.05,
    haloStoneScale: 0.22,
    paveShoulders: false,
    paveSpanDeg: 90,
    paveStoneScale: 0.1,
    eternityPitchMm: 1.6,
    eternityStoneCount: 12,
    eternityStoneSpacingMm: 1.6,
    eternityStoneScale: 0.18,
    eternityStartAngleDeg: 0,
    eternityRetention: 'BEAD',
    clusterStoneCount: 8,
    clusterStoneScale: 0.4,
    clusterRadiusMm: 4,
    toiEtMoiSecondScale: 1.0,
    toiEtMoiSeparationMm: 5,
    toiEtMoiOrientationDeg: 30,
    symmetry: 'SYMMETRIC',
  }
}

const FAMILY_OPTIONS: ReadonlyArray<{ value: JewelryStyle; label: string }> = [
  { value: 'solitaire', label: 'Solitaire' },
  { value: 'three_stone', label: 'Three stone / trilogy' },
  { value: 'halo', label: 'Halo' },
  { value: 'split_shank', label: 'Split shank' },
  { value: 'bypass', label: 'Bypass' },
  { value: 'signet', label: 'Signet' },
  { value: 'eternity', label: 'Eternity band' },
  { value: 'cluster', label: 'Cluster' },
  { value: 'toi_et_moi', label: 'Toi et moi' },
]

/**
 * The variants each family offers, and the default one FIRST.
 *
 * The first entry is what a document with no `ringFamily` resolves to, so
 * choosing it is equivalent to declaring no variant — which is why selecting it
 * clears the block rather than storing a variant that means "the default".
 */
const FAMILY_VARIANTS: Readonly<
  Record<JewelryStyle, ReadonlyArray<{ value: RingFamilyVariantId; label: string }>>
> = {
  solitaire: [
    { value: 'SOLITAIRE_CLASSIC', label: 'Classic' },
    { value: 'SOLITAIRE_CATHEDRAL', label: 'Cathedral (shoulder arches)' },
    { value: 'SOLITAIRE_LOW_PROFILE', label: 'Low profile' },
    { value: 'SOLITAIRE_ELEVATED', label: 'Elevated' },
  ],
  three_stone: [
    { value: 'THREE_STONE_SYMMETRIC', label: 'Symmetric sides' },
    { value: 'THREE_STONE_GRADUATED', label: 'Graduated sides' },
  ],
  halo: [
    { value: 'HALO_SINGLE', label: 'Single halo' },
    { value: 'HALO_DOUBLE', label: 'Double halo' },
    { value: 'HALO_HIDDEN', label: 'Hidden halo' },
  ],
  split_shank: [
    { value: 'SPLIT_SHANK_PARALLEL', label: 'Parallel rails' },
    { value: 'SPLIT_SHANK_TAPERED', label: 'Tapered rails' },
  ],
  bypass: [{ value: 'BYPASS_CROSSOVER', label: 'Crossover' }],
  signet: [{ value: 'SIGNET_FLAT_TABLE', label: 'Flat table' }],
  eternity: [
    { value: 'ETERNITY_FULL', label: 'Full — stones all the way round' },
    { value: 'ETERNITY_HALF', label: 'Half — a set region and a plain region' },
  ],
  cluster: [{ value: 'CLUSTER_ROUND', label: 'Round cluster' }],
  toi_et_moi: [{ value: 'TOI_ET_MOI_BYPASS', label: 'Two stones' }],
}

/**
 * Which parameters each variant READS. Mirrors the backend's
 * `resolve.py::parameters_read_by()`.
 *
 * `headHeightFactor` and the three pavé fields are read by EVERY variant —
 * every family has a head, and any family may compose a pavé onto its
 * shoulders — so they are not listed per variant.
 */
const VARIANT_PARAMS: Readonly<Record<RingFamilyVariantId, readonly string[]>> = {
  SOLITAIRE_CLASSIC: [],
  SOLITAIRE_CATHEDRAL: ['shoulder'],
  SOLITAIRE_LOW_PROFILE: [],
  SOLITAIRE_ELEVATED: ['shoulder'],
  THREE_STONE_SYMMETRIC: ['side'],
  THREE_STONE_GRADUATED: ['side', 'graduation'],
  HALO_SINGLE: ['halo'],
  HALO_DOUBLE: ['halo'],
  HALO_HIDDEN: ['halo'],
  SPLIT_SHANK_PARALLEL: ['split', 'shoulder'],
  SPLIT_SHANK_TAPERED: ['split', 'shoulder'],
  BYPASS_CROSSOVER: ['bypass'],
  SIGNET_FLAT_TABLE: ['signet'],
  ETERNITY_FULL: ['eternityFull'],
  ETERNITY_HALF: ['eternityHalf'],
  CLUSTER_ROUND: ['cluster'],
  TOI_ET_MOI_BYPASS: ['toiEtMoi'],
}

/** Variants whose capability status the backend records as PARTIAL, with what
 * is missing. Mirrored so the interface never presents one as complete. */
const PARTIAL_NOTE: Partial<Record<RingFamilyVariantId, string>> = {
  HALO_SINGLE:
    'Halo stones are real geometry. No metal is generated to hold them — a boundary recorded since Sprint 25, unchanged here.',
  HALO_DOUBLE:
    'Halo stones are real geometry. No metal is generated to hold them — a boundary recorded since Sprint 25, unchanged here.',
  HALO_HIDDEN:
    'Halo stones are real geometry. No metal is generated to hold them — a boundary recorded since Sprint 25, unchanged here.',
  SIGNET_FLAT_TABLE:
    'The body and its table are real geometry. The table is flat and rectangular: no engraving, relief or texture exists anywhere in JewelMind yet.',
  CLUSTER_ROUND:
    'The surrounding stones are real geometry. No metal is generated to hold them — only the centre stone is held. A boundary recorded since Sprint 24, unchanged here.',
  TOI_ET_MOI_BYPASS:
    'Both stones are real geometry with independent sizes. The second stone is not held by metal, and the two cannot have different cuts: both are occurrences of this design’s one stone.',
}

export function RingFamilySection() {
  const style = useProjectStore((s) => s.currentDefinition.jewelry.style)
  const ringFamily = useProjectStore((s) => s.currentDefinition.ringFamily)
  const updateJewelry = useProjectStore((s) => s.updateJewelry)
  const setRingFamily = useProjectStore((s) => s.setRingFamily)

  const variants = FAMILY_VARIANTS[style]
  const defaultVariant: RingFamilyVariantId =
    variants[0]?.value ?? 'SOLITAIRE_CLASSIC'
  const activeVariant: RingFamilyVariantId =
    ringFamily !== null && ringFamily.enabled ? ringFamily.variant : defaultVariant
  const params = ringFamily?.params ?? defaultParams()
  const reads = VARIANT_PARAMS[activeVariant]

  const patchParams = (patch: Partial<RingFamilyParams>) => {
    const base: RingFamilySpec =
      ringFamily ?? {
        variant: activeVariant,
        enabled: true,
        params: defaultParams(),
        label: null,
      }
    setRingFamily({ ...base, params: { ...base.params, ...patch } })
  }

  const selectFamily = (next: JewelryStyle) => {
    // Changing the FAMILY clears the variant block, because a variant belongs
    // to exactly one family and carrying one across would be refused by
    // `JM-RINGFAM-001`. Nothing else in the document is touched: the band, the
    // stone and the head keep their values and the new family derives from
    // them, which is what makes this a relation rather than a preset.
    updateJewelry({ style: next })
    setRingFamily(null)
  }

  const selectVariant = (next: RingFamilyVariantId) => {
    // Choosing the family's DEFAULT variant clears the block rather than
    // storing a variant that means "the default": a document with no
    // `ringFamily` is the pre-Sprint-28 state, and keeping the two
    // distinguishable makes "no variant declared" a real answer.
    if (next === defaultVariant) {
      setRingFamily(null)
      return
    }
    const base: RingFamilySpec =
      ringFamily ?? {
        variant: next,
        enabled: true,
        params: defaultParams(),
        label: null,
      }
    setRingFamily({ ...base, variant: next, enabled: true })
  }

  return (
    <FormSection title="Ring family">
      <SelectField
        id="ring-family"
        label="Family"
        value={style}
        options={FAMILY_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
        onChange={(value) => selectFamily(value as JewelryStyle)}
        wide
      />

      {variants.length > 1 && (
        <SelectField
          id="ring-family-variant"
          label="Variant"
          value={activeVariant}
          options={variants.map((v) => ({ value: v.value, label: v.label }))}
          onChange={(value) => selectVariant(value as RingFamilyVariantId)}
          wide
        />
      )}

      {/* Read by every variant: every family has a head. */}
      <NumericField
        id="ring-family-head-height"
        label="Head height"
        value={params.headHeightFactor}
        onChange={(headHeightFactor) => patchParams({ headHeightFactor })}
        min={0.06}
        max={5}
        step={0.05}
        unit="×"
      />

      {reads.includes('shoulder') && (
        <>
          <NumericField
            id="ring-family-shoulder-span"
            label="Shoulder reach"
            value={params.shoulderSpanDeg}
            onChange={(shoulderSpanDeg) => patchParams({ shoulderSpanDeg })}
            min={2}
            max={170}
            step={5}
            unit="°"
          />
          <NumericField
            id="ring-family-shoulder-width"
            label="Shoulder narrowing"
            value={params.shoulderTopWidthFactor}
            onChange={(shoulderTopWidthFactor) =>
              patchParams({ shoulderTopWidthFactor })
            }
            min={0.06}
            max={1}
            step={0.05}
            unit="×"
          />
        </>
      )}

      {reads.includes('split') && (
        <>
          <NumericField
            id="ring-family-split-separation"
            label="Rail separation"
            value={params.splitSeparationMm}
            onChange={(splitSeparationMm) => patchParams({ splitSeparationMm })}
            min={0.05}
            max={20}
            step={0.1}
            unit="mm"
          />
          <NumericField
            id="ring-family-split-join"
            label="Joined span"
            value={params.splitJoinSpanDeg}
            onChange={(splitJoinSpanDeg) => patchParams({ splitJoinSpanDeg })}
            min={15}
            max={350}
            step={10}
            unit="°"
          />
        </>
      )}

      {reads.includes('bypass') && (
        <>
          <NumericField
            id="ring-family-bypass-separation"
            label="Crossing separation"
            value={params.bypassSeparationMm}
            onChange={(bypassSeparationMm) => patchParams({ bypassSeparationMm })}
            min={0.05}
            max={20}
            step={0.1}
            unit="mm"
          />
          <NumericField
            id="ring-family-bypass-overlap"
            label="Crossing span"
            value={params.bypassOverlapDeg}
            onChange={(bypassOverlapDeg) => patchParams({ bypassOverlapDeg })}
            min={6}
            max={180}
            step={5}
            unit="°"
          />
        </>
      )}

      {reads.includes('side') && (
        <>
          <NumericField
            id="ring-family-side-spacing"
            label="Side stone spacing"
            value={params.sideSpacingMm}
            onChange={(sideSpacingMm) => patchParams({ sideSpacingMm })}
            min={0.05}
            max={40}
            step={0.5}
            unit="mm"
          />
          <NumericField
            id="ring-family-side-scale"
            label="Side stone size"
            value={params.sideStoneScale}
            onChange={(sideStoneScale) => patchParams({ sideStoneScale })}
            min={0.02}
            max={10}
            step={0.05}
            unit="×"
          />
        </>
      )}

      {reads.includes('graduation') && (
        <NumericField
          id="ring-family-side-graduation"
          label="Graduation"
          value={params.sideGraduationFactor}
          onChange={(sideGraduationFactor) => patchParams({ sideGraduationFactor })}
          min={0.06}
          max={0.95}
          step={0.05}
          unit="×"
        />
      )}

      {reads.includes('halo') && (
        <>
          <NumericField
            id="ring-family-halo-count"
            label="Halo stones"
            value={params.haloStoneCount}
            onChange={(haloStoneCount) => patchParams({ haloStoneCount })}
            min={3}
            max={96}
            step={1}
          />
          {/* A RELATION, not a millimetre value: the radius is the centre
              stone's own half width times this factor, so the halo follows the
              stone when the stone changes. */}
          <NumericField
            id="ring-family-halo-radius"
            label="Halo radius"
            value={params.haloRadiusFactor}
            onChange={(haloRadiusFactor) => patchParams({ haloRadiusFactor })}
            min={0.2}
            max={10}
            step={0.05}
            unit="× stone"
          />
          <NumericField
            id="ring-family-halo-scale"
            label="Halo stone size"
            value={params.haloStoneScale}
            onChange={(haloStoneScale) => patchParams({ haloStoneScale })}
            min={0.02}
            max={10}
            step={0.02}
            unit="×"
          />
        </>
      )}

      {reads.includes('signet') && (
        <>
          <NumericField
            id="ring-family-signet-length"
            label="Table length"
            value={params.signetTableLengthMm}
            onChange={(signetTableLengthMm) => patchParams({ signetTableLengthMm })}
            min={0.2}
            max={60}
            step={0.5}
            unit="mm"
          />
          <NumericField
            id="ring-family-signet-width"
            label="Table width"
            value={params.signetTableWidthMm}
            onChange={(signetTableWidthMm) => patchParams({ signetTableWidthMm })}
            min={0.2}
            max={60}
            step={0.5}
            unit="mm"
          />
          <NumericField
            id="ring-family-signet-height"
            label="Table height"
            value={params.signetTableHeightMm}
            onChange={(signetTableHeightMm) => patchParams({ signetTableHeightMm })}
            min={0.2}
            max={30}
            step={0.2}
            unit="mm"
          />
        </>
      )}

      {reads.includes('eternityFull') && (
        <>
          {/* A PITCH, not a count: the stone count follows from the band's own
              circumference, so a larger finger carries more stones. */}
          <NumericField
            id="ring-family-eternity-pitch"
            label="Stone pitch"
            value={params.eternityPitchMm}
            onChange={(eternityPitchMm) => patchParams({ eternityPitchMm })}
            min={0.1}
            max={50}
            step={0.1}
            unit="mm"
          />
        </>
      )}

      {reads.includes('eternityHalf') && (
        <>
          <NumericField
            id="ring-family-eternity-count"
            label="Set stones"
            value={params.eternityStoneCount}
            onChange={(eternityStoneCount) => patchParams({ eternityStoneCount })}
            min={1}
            max={200}
            step={1}
          />
          <NumericField
            id="ring-family-eternity-spacing"
            label="Stone spacing"
            value={params.eternityStoneSpacingMm}
            onChange={(eternityStoneSpacingMm) =>
              patchParams({ eternityStoneSpacingMm })
            }
            min={0.1}
            max={50}
            step={0.1}
            unit="mm"
          />
          <NumericField
            id="ring-family-eternity-start"
            label="Set region starts at"
            value={params.eternityStartAngleDeg}
            onChange={(eternityStartAngleDeg) =>
              patchParams({ eternityStartAngleDeg })
            }
            min={-360}
            max={360}
            step={15}
            unit="°"
          />
        </>
      )}

      {(reads.includes('eternityFull') || reads.includes('eternityHalf')) && (
        <>
          <NumericField
            id="ring-family-eternity-scale"
            label="Set stone size"
            value={params.eternityStoneScale}
            onChange={(eternityStoneScale) => patchParams({ eternityStoneScale })}
            min={0.01}
            max={10}
            step={0.02}
            unit="× stone"
          />
          <SelectField
            id="ring-family-eternity-retention"
            label="Held by"
            value={params.eternityRetention}
            options={[
              { value: 'BEAD', label: 'Beads' },
              { value: 'SHARED_BEAD', label: 'Shared beads' },
              { value: 'MICRO_PRONG', label: 'Micro prongs' },
              { value: 'NONE', label: 'Nothing — stone layout only' },
            ]}
            onChange={(value) =>
              patchParams({ eternityRetention: value as RingFamilyParams['eternityRetention'] })
            }
            wide
          />
        </>
      )}

      {reads.includes('cluster') && (
        <>
          <NumericField
            id="ring-family-cluster-count"
            label="Surrounding stones"
            value={params.clusterStoneCount}
            onChange={(clusterStoneCount) => patchParams({ clusterStoneCount })}
            min={1}
            max={24}
            step={1}
          />
          <NumericField
            id="ring-family-cluster-radius"
            label="Cluster radius"
            value={params.clusterRadiusMm}
            onChange={(clusterRadiusMm) => patchParams({ clusterRadiusMm })}
            min={0.1}
            max={40}
            step={0.5}
            unit="mm"
          />
          <NumericField
            id="ring-family-cluster-scale"
            label="Surrounding stone size"
            value={params.clusterStoneScale}
            onChange={(clusterStoneScale) => patchParams({ clusterStoneScale })}
            min={0.02}
            max={10}
            step={0.05}
            unit="× stone"
          />
        </>
      )}

      {reads.includes('toiEtMoi') && (
        <>
          {/* RELATIVE, and deliberately allowed at and above 1.0: a toi-et-moi's
              two stones are frequently equal and frequently not, and neither is
              the "correct" one. */}
          <NumericField
            id="ring-family-toi-scale"
            label="Second stone size"
            value={params.toiEtMoiSecondScale}
            onChange={(toiEtMoiSecondScale) => patchParams({ toiEtMoiSecondScale })}
            min={0.02}
            max={10}
            step={0.05}
            unit="× first"
          />
          <NumericField
            id="ring-family-toi-separation"
            label="Stone separation"
            value={params.toiEtMoiSeparationMm}
            onChange={(toiEtMoiSeparationMm) => patchParams({ toiEtMoiSeparationMm })}
            min={0.1}
            max={40}
            step={0.5}
            unit="mm"
          />
          <NumericField
            id="ring-family-toi-orientation"
            label="Pair angle"
            value={params.toiEtMoiOrientationDeg}
            onChange={(toiEtMoiOrientationDeg) =>
              patchParams({ toiEtMoiOrientationDeg })
            }
            min={-180}
            max={180}
            step={15}
            unit="°"
          />
        </>
      )}

      {/* Composition, offered on every family: the Pavé Engine does all of it,
          and the family only names the region and the density. */}
      <SelectField
        id="ring-family-pave-shoulders"
        label="Pavé shoulders"
        value={params.paveShoulders ? 'yes' : 'no'}
        options={[
          { value: 'no', label: 'None' },
          { value: 'yes', label: 'Pavé the shoulders' },
        ]}
        onChange={(value) => patchParams({ paveShoulders: value === 'yes' })}
        wide
      />

      {params.paveShoulders && (
        <NumericField
          id="ring-family-pave-span"
          label="Pavé coverage"
          value={params.paveSpanDeg}
          onChange={(paveSpanDeg) => patchParams({ paveSpanDeg })}
          min={2}
          max={360}
          step={5}
          unit="°"
        />
      )}

      {PARTIAL_NOTE[activeVariant] !== undefined && (
        <p className="form-note form-note--warning">
          {PARTIAL_NOTE[activeVariant]}
        </p>
      )}

      <p className="form-note">
        A ring family is a relation, not a preset: the ring size, the band and
        the stone still drive the geometry, and the variant modulates what they
        produce. No ring dimension in JewelMind is professionally validated — a
        qualified jewelry professional must review this design before
        production.
      </p>
    </FormSection>
  )
}
