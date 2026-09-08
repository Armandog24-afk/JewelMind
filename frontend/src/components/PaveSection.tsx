import type {
  MicrosettingSpec,
  PaveDefinition,
  PaveSpec,
} from '@shared/types/jewelry-definition'
import { useProjectStore } from '../store/useProjectStore'
import { FormSection } from './FormSection'
import { NumericField } from './NumericField'
import { SelectField } from './SelectField'

/**
 * Pavé & microsetting controls (Sprint 26).
 *
 * EXPOSES ONLY WHAT THE BACKEND BUILDS. Every option list below is a literal
 * mirror of the backend's own `Literal` members, which are exactly the values
 * with a real builder: a reserved host (`SETTING_SURFACE`, `BAND_INNER`, …) or
 * a reserved retention strategy (`SHARED_PRONG`, `CHANNEL`, …) is absent from
 * the type and therefore cannot appear here. The panel does not carry its own
 * list of "coming soon" options, because an option a user can pick and the
 * product cannot build is worse than an absent one (STUDIO-GOV-011).
 *
 * NO THRESHOLD LIVES HERE. The `min`/`max` on each field are the SCHEMA's own
 * bounds, mirrored so a slider cannot leave the representable range; they are
 * advisory, and the backend's `validate_definition()` verdict always wins
 * (STUDIO-GOV-001/002). Whether a pitch is *settable* is a professional
 * question the panel never answers — `JM-PAVE-005` states on every field that
 * a qualified professional must review it, and that finding is rendered by the
 * existing validation list rather than restated here.
 *
 * EVERY EDIT IS A DESIGN EDIT. All of them route through the store's
 * `setPave`/`updatePave`, which go through `withUpdatedDefinition()` — so an
 * existing model is marked stale and the last-good preview is preserved,
 * exactly as for any other geometry-driving parameter (STUDIO-GOV-004/006).
 */

/** The default field a user gets when switching the pavé on.
 *
 * A single row on the shank at a pitch inside the schema's range, with shared
 * beads and no recess. Chosen to be the least surprising thing that builds:
 * not a recommendation, and every value is immediately editable.
 */
function defaultPave(): PaveDefinition {
  return {
    paveId: 'pave',
    enabled: true,
    kind: 'PAVE',
    spec: {
      kind: 'PAVE',
      angularSpanDeg: 90,
      startAngleDeg: 0,
      axialSpanMm: null,
      pitchMm: 1,
      rowPitchMm: null,
      rowCount: 1,
      pattern: 'GRID',
      rowOffsetFraction: 0.5,
      termination: 'CENTERED',
      symmetry: 'SYMMETRIC',
    },
    host: 'BAND_OUTER',
    stoneRef: 'primary',
    stoneScale: 0.1,
    stoneOrientationDeg: 0,
    gem: null,
    retention: {
      strategy: 'SHARED_BEAD',
      beadRadiusMm: 0.18,
      beadEmbedMm: 0.06,
      prongHeightMm: 0.35,
    },
    seat: { mode: 'NONE', clearanceMm: 0.02 },
    containment: 'CLIP',
    explicitPlacements: [],
    label: null,
  }
}

/** A `MICROSETTING` spec carrying over what the two kinds share.
 *
 * Switching kind changes WHICH QUESTION the field answers — an area at a
 * density, or a stated structure — so the spec is rebuilt rather than merged.
 * The shared lattice axes (pattern, offset, termination, symmetry) are carried
 * across, because those mean the same thing in both.
 */
function toMicrosetting(spec: PaveSpec | MicrosettingSpec): MicrosettingSpec {
  return {
    kind: 'MICROSETTING',
    columnCount: 12,
    rowCount: spec.rowCount,
    stoneSpacingMm: spec.kind === 'PAVE' ? spec.pitchMm : spec.stoneSpacingMm,
    rowSpacingMm: null,
    startAngleDeg: spec.startAngleDeg,
    axialOffsetMm: 0,
    pattern: spec.pattern,
    rowOffsetFraction: spec.rowOffsetFraction,
    termination: spec.termination,
    symmetry: spec.symmetry,
  }
}

function toPaveSpec(spec: PaveSpec | MicrosettingSpec): PaveSpec {
  return {
    kind: 'PAVE',
    angularSpanDeg: 90,
    startAngleDeg: spec.startAngleDeg,
    axialSpanMm: null,
    pitchMm: spec.kind === 'MICROSETTING' ? spec.stoneSpacingMm : spec.pitchMm,
    rowPitchMm: null,
    rowCount: spec.rowCount,
    pattern: spec.pattern,
    rowOffsetFraction: spec.rowOffsetFraction,
    termination: spec.termination,
    symmetry: spec.symmetry,
  }
}

export function PaveSection() {
  const pave = useProjectStore((s) => s.currentDefinition.pave)
  const setPave = useProjectStore((s) => s.setPave)
  const updatePave = useProjectStore((s) => s.updatePave)

  const patchSpec = (patch: Partial<PaveSpec> | Partial<MicrosettingSpec>) => {
    if (pave === null) return
    updatePave({ spec: { ...pave.spec, ...patch } as PaveDefinition['spec'] })
  }

  return (
    <FormSection title="Pavé & microsetting">
      <div className="form-field form-field--wide">
        <label htmlFor="pave-present">Pavé</label>
        <select
          id="pave-present"
          value={pave === null ? 'off' : 'on'}
          onChange={(event) =>
            setPave(event.target.value === 'on' ? defaultPave() : null)
          }
        >
          <option value="off">None</option>
          <option value="on">Configured</option>
        </select>
      </div>

      {pave !== null && (
        <>
          {/* Enabled is a THIRD state, distinct from having no pavé: it keeps
              the parameters and builds nothing, so a field can be switched off
              without losing how it was configured. */}
          <SelectField
            id="pave-enabled"
            label="Build stones"
            value={pave.enabled ? 'yes' : 'no'}
            options={[
              { value: 'yes', label: 'Yes' },
              { value: 'no', label: 'No (keep settings)' },
            ]}
            onChange={(value) => updatePave({ enabled: value === 'yes' })}
          />

          <SelectField
            id="pave-kind"
            label="Field type"
            value={pave.kind}
            options={[
              { value: 'PAVE', label: 'Pavé (area & density)' },
              { value: 'MICROSETTING', label: 'Microsetting (rows & columns)' },
            ]}
            onChange={(value) =>
              updatePave(
                value === 'MICROSETTING'
                  ? { kind: 'MICROSETTING', spec: toMicrosetting(pave.spec) }
                  : { kind: 'PAVE', spec: toPaveSpec(pave.spec) },
              )
            }
          />

          <SelectField
            id="pave-host"
            label="Surface"
            value={pave.host}
            options={[
              { value: 'BAND_OUTER', label: 'Band (shank)' },
              { value: 'HEAD_PLANE', label: 'Head (gallery rim)' },
            ]}
            onChange={(value) =>
              updatePave({ host: value as PaveDefinition['host'] })
            }
          />

          <SelectField
            id="pave-pattern"
            label="Pattern"
            value={pave.spec.pattern}
            options={[
              { value: 'GRID', label: 'Grid' },
              { value: 'STAGGERED', label: 'Staggered' },
              { value: 'ROW_OFFSET', label: 'Row offset' },
              { value: 'RADIAL', label: 'Radial' },
              { value: 'EXPLICIT', label: 'Explicit placements' },
            ]}
            onChange={(value) =>
              patchSpec({ pattern: value as PaveSpec['pattern'] })
            }
          />

          {pave.spec.kind === 'PAVE' ? (
            <>
              <NumericField
                id="pave-span"
                label="Coverage"
                value={pave.spec.angularSpanDeg}
                onChange={(angularSpanDeg) => patchSpec({ angularSpanDeg })}
                min={0.1}
                max={360}
                step={5}
                unit="°"
              />
              <NumericField
                id="pave-pitch"
                label="Stone pitch"
                value={pave.spec.pitchMm}
                onChange={(pitchMm) => patchSpec({ pitchMm })}
                min={0.05}
                max={50}
                step={0.05}
                unit="mm"
              />
            </>
          ) : (
            <>
              <NumericField
                id="pave-columns"
                label="Stones per row"
                value={pave.spec.columnCount}
                onChange={(columnCount) => patchSpec({ columnCount })}
                min={1}
                max={60}
                step={1}
              />
              <NumericField
                id="pave-spacing"
                label="Stone spacing"
                value={pave.spec.stoneSpacingMm}
                onChange={(stoneSpacingMm) => patchSpec({ stoneSpacingMm })}
                min={0.05}
                max={50}
                step={0.05}
                unit="mm"
              />
            </>
          )}

          <NumericField
            id="pave-rows"
            label="Rows"
            value={pave.spec.rowCount}
            onChange={(rowCount) => patchSpec({ rowCount })}
            min={1}
            max={12}
            step={1}
          />

          <NumericField
            id="pave-stone-scale"
            label="Stone size"
            value={pave.stoneScale}
            onChange={(stoneScale) => updatePave({ stoneScale })}
            min={0.001}
            max={10}
            step={0.01}
            unit="×"
          />

          <SelectField
            id="pave-retention"
            label="Retention"
            value={pave.retention.strategy}
            options={[
              { value: 'SHARED_BEAD', label: 'Shared beads' },
              { value: 'BEAD', label: 'Beads' },
              { value: 'MICRO_PRONG', label: 'Micro prongs' },
              { value: 'NONE', label: 'None (stones only)' },
            ]}
            onChange={(value) =>
              updatePave({
                retention: {
                  ...pave.retention,
                  strategy: value as PaveDefinition['retention']['strategy'],
                },
              })
            }
          />

          {pave.retention.strategy !== 'NONE' && (
            <NumericField
              id="pave-bead-radius"
              label="Retention size"
              value={pave.retention.beadRadiusMm}
              onChange={(beadRadiusMm) =>
                updatePave({ retention: { ...pave.retention, beadRadiusMm } })
              }
              min={0.01}
              max={5}
              step={0.01}
              unit="mm"
            />
          )}

          <SelectField
            id="pave-recess"
            label="Recess host metal"
            value={pave.seat.mode}
            options={[
              { value: 'NONE', label: 'No' },
              { value: 'REFERENCE_RECESS', label: 'Yes (reference recess)' },
            ]}
            onChange={(value) =>
              updatePave({
                seat: { ...pave.seat, mode: value as PaveDefinition['seat']['mode'] },
              })
            }
          />

          <SelectField
            id="pave-containment"
            label="Beyond the surface"
            value={pave.containment}
            options={[
              { value: 'CLIP', label: 'End the field at the edge' },
              { value: 'REJECT', label: 'Refuse the field' },
            ]}
            onChange={(value) =>
              updatePave({
                containment: value as PaveDefinition['containment'],
              })
            }
          />

          {pave.spec.pattern === 'EXPLICIT' && pave.explicitPlacements.length === 0 && (
            <p className="form-note form-note--warning">
              Explicit placement is selected and no placements are defined, so
              this field cannot be built. Placements are set through the API in
              this release.
            </p>
          )}

          <p className="form-note">
            No pavé dimension, spacing or retention size in JewelMind is
            professionally validated. A qualified jewelry professional must
            review this field before production.
          </p>
        </>
      )}
    </FormSection>
  )
}
