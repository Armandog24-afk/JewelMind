import type {
  HeadArchitecture,
  ProngStyle,
  SeatMode,
  SettingModeId,
  SettingModeParameters,
  SettingModeSpec,
  SettingType,
} from '@shared/types/jewelry-definition'
import { useProjectStore } from '../store/useProjectStore'
import { FormSection } from './FormSection'
import { NumericField } from './NumericField'
import { SelectField } from './SelectField'

/**
 * Extended Setting Modes controls (Sprint 27).
 *
 * WHAT THIS SECTION IS FOR. `setting.type` (in the Setting section above)
 * chooses the FAMILY; this section chooses the VARIANT within it, the head
 * architecture, whether metal is relieved, and the parameters the chosen
 * variant actually reads. Three axes are present at once — primary, head and
 * seat — because they are not alternatives: a bezel on a martini with relief is
 * one setting with three choices.
 *
 * IT ALSO CLOSES A PRE-EXISTING GAP. Sprint 23 added `prongStyle`,
 * `headArchitecture` and `seatMode` to the schema and gave them real builders,
 * and no Studio control was ever added for any of them — so a capability the
 * backend genuinely had was unreachable from the workspace. Those controls are
 * here now, beside the Sprint 27 ones, which is why the mode registry can
 * honestly record `studio: CURRENT` for them.
 *
 * EXPOSES ONLY WHAT THE BACKEND BUILDS. Every option list is a literal mirror
 * of the backend's own `Literal` members, which are exactly the values with a
 * real builder: a reserved mode (`HEAD_TRELLIS`, `HEAD_AZURE`,
 * `CHANNEL_SHARED_WALL`, `TENSION_COMPRESSION_MODELLED`, …) is absent from the
 * type and therefore cannot appear here. This panel carries no "coming soon"
 * list, because an option a user can pick and the product cannot build is worse
 * than an absent one (STUDIO-GOV-011).
 *
 * ONLY THE PARAMETERS THE MODE READS ARE SHOWN. That mirrors the backend's own
 * `MODE_PARAMETER_FIELDS`, and it is why a channel's wall height is not offered
 * for a flush collar. A value the mode ignores is not hidden from the document —
 * it stays there and `JM-SETTING-009` reports it as having no effect — it is
 * simply not offered as though it did something.
 *
 * NO THRESHOLD LIVES HERE. Every `min`/`max` is the SCHEMA's own bound,
 * mirrored so a control cannot leave the representable range; it is advisory,
 * and the backend's `validate_definition()` verdict always wins
 * (STUDIO-GOV-001/002). Whether a wall is thick enough is a professional
 * question this panel never answers.
 *
 * EVERY EDIT IS A DESIGN EDIT, routed through `updateSetting` and therefore
 * through `withUpdatedDefinition()`, so an existing model is marked stale and
 * the last-good preview is preserved (STUDIO-GOV-004/006).
 */

/** The parameters a mode gets when it is switched on with no values.
 *
 * MIRRORS the backend's `default_mode_parameters()` exactly. One definition of
 * "turn this mode on" is what stops a spoken instruction and a UI toggle
 * producing different designs from the same request — the discipline Sprint 26
 * established for the pavé's own default field.
 */
function defaultParameters(): SettingModeParameters {
  return {
    openingCount: 2,
    openingSweepDeg: 40,
    openingStartAngleDeg: 90,
    collarWidthMm: 1,
    rimHeightMm: 0.4,
    gripAxisDeg: 0,
    padWidthMm: 2,
    padThicknessMm: 1.6,
    padDepthMm: 0.6,
    gripHeightMm: 1.2,
    axisDeg: 0,
    spanMm: null,
    innerWidthMm: null,
    wallThicknessMm: 0.7,
    wallHeightMm: 0.8,
    barCount: 2,
    barSpacingMm: null,
    barHeightMm: 0.8,
    barLengthMm: null,
    termination: 'OPEN',
    symmetry: 'SYMMETRIC',
    offsetXMm: 0,
    offsetYMm: 0,
    offsetZMm: 0,
  }
}

function defaultMode(modeId: SettingModeId): SettingModeSpec {
  return {
    modeId,
    enabled: true,
    stoneRef: 'primary',
    arrangementInstanceIds: [],
    host: 'HEAD',
    parameters: defaultParameters(),
    label: null,
  }
}

/**
 * The variants each family offers, and the default one.
 *
 * The FIRST entry of each list is the family's default variant, which is what a
 * document with no mode block resolves to — so choosing it is equivalent to
 * declaring no mode, and every existing design keeps its geometry.
 */
const FAMILY_MODES: Readonly<
  Record<SettingType, ReadonlyArray<{ value: SettingModeId; label: string }>>
> = {
  prong: [
    { value: 'PRONG_ROUND', label: 'Round prong' },
    { value: 'PRONG_TAPERED', label: 'Tapered prong' },
    { value: 'PRONG_CLAW', label: 'Claw prong' },
    { value: 'PRONG_V', label: 'V prong' },
  ],
  bezel: [
    { value: 'BEZEL_FULL', label: 'Full bezel' },
    { value: 'BEZEL_PARTIAL', label: 'Partial bezel (openings)' },
  ],
  channel: [{ value: 'CHANNEL_LINEAR', label: 'Linear channel' }],
  bar: [{ value: 'BAR_TRANSVERSE', label: 'Transverse bars' }],
  flush: [{ value: 'FLUSH_GYPSY', label: 'Flush / gypsy' }],
  tension: [{ value: 'TENSION_OPPOSED', label: 'Opposed supports' }],
}

const HEAD_ARCHITECTURE_OPTIONS: ReadonlyArray<{
  value: HeadArchitecture
  label: string
}> = [
  { value: 'BASKET', label: 'Basket' },
  { value: 'PEG_HEAD', label: 'Peg head' },
  { value: 'MARTINI', label: 'Martini' },
  { value: 'TULIP', label: 'Tulip' },
  { value: 'OPEN_GALLERY', label: 'Open gallery' },
]

const PRONG_STYLE_OPTIONS: ReadonlyArray<{ value: ProngStyle; label: string }> = [
  { value: 'ROUND_PRONG', label: 'Round' },
  { value: 'TAPERED_PRONG', label: 'Tapered' },
  { value: 'CLAW_PRONG', label: 'Claw' },
  { value: 'V_PRONG', label: 'V' },
]

const SEAT_MODE_OPTIONS: ReadonlyArray<{ value: SeatMode; label: string }> = [
  { value: 'NONE', label: 'No relief' },
  { value: 'REFERENCE_SEAT', label: 'Reference relief' },
]

export function SettingModeSection() {
  const setting = useProjectStore((s) => s.currentDefinition.setting)
  const updateSetting = useProjectStore((s) => s.updateSetting)

  const variants = FAMILY_MODES[setting.type]
  // Every family has at least one variant by construction; the fallback keeps
  // the type honest under `noUncheckedIndexedAccess` rather than asserting.
  const defaultVariant: SettingModeId = variants[0]?.value ?? 'PRONG_ROUND'
  const activeMode: SettingModeId =
    setting.mode !== null && setting.mode.enabled
      ? setting.mode.modeId
      : defaultVariant
  const parameters = setting.mode?.parameters ?? defaultParameters()

  const patchParameters = (patch: Partial<SettingModeParameters>) => {
    const base = setting.mode ?? defaultMode(activeMode)
    updateSetting({
      mode: { ...base, parameters: { ...base.parameters, ...patch } },
    })
  }

  const selectMode = (modeId: SettingModeId) => {
    // Choosing the family's DEFAULT variant clears the block rather than
    // storing a mode that means "the default": a document with no mode is the
    // pre-Sprint-27 state, and keeping the two distinguishable is what makes
    // "no mode declared" a real answer rather than a hidden one.
    if (modeId === defaultVariant) {
      updateSetting({ mode: null })
      return
    }
    const base = setting.mode ?? defaultMode(modeId)
    updateSetting({ mode: { ...base, modeId } })
  }

  return (
    <FormSection title="Setting mode">
      {variants.length > 1 && (
        <SelectField
          id="setting-mode"
          label="Variant"
          value={activeMode}
          options={variants.map((v) => ({ value: v.value, label: v.label }))}
          onChange={(value) => selectMode(value as SettingModeId)}
          wide
        />
      )}

      {setting.type === 'prong' && (
        <>
          <SelectField
            id="prong-style"
            label="Prong body"
            value={setting.prongStyle}
            options={PRONG_STYLE_OPTIONS.map((o) => ({
              value: o.value,
              label: o.label,
            }))}
            onChange={(value) =>
              updateSetting({ prongStyle: value as ProngStyle })
            }
          />
          {setting.prongStyle !== 'ROUND_PRONG' && (
            <NumericField
              id="prong-tip-ratio"
              label="Tip ratio"
              value={setting.prongTipRatio}
              onChange={(prongTipRatio) => updateSetting({ prongTipRatio })}
              min={0.06}
              max={1}
              step={0.05}
              unit="×"
            />
          )}
        </>
      )}

      {activeMode === 'BEZEL_PARTIAL' && (
        <>
          <NumericField
            id="bezel-opening-count"
            label="Openings"
            value={parameters.openingCount}
            onChange={(openingCount) => patchParameters({ openingCount })}
            min={1}
            max={24}
            step={1}
          />
          <NumericField
            id="bezel-opening-sweep"
            label="Opening width"
            value={parameters.openingSweepDeg}
            onChange={(openingSweepDeg) => patchParameters({ openingSweepDeg })}
            min={1}
            max={180}
            step={5}
            unit="°"
          />
        </>
      )}

      {(setting.type === 'channel' || setting.type === 'bar') && (
        <NumericField
          id="setting-mode-axis"
          label="Run direction"
          value={parameters.axisDeg}
          onChange={(axisDeg) => patchParameters({ axisDeg })}
          min={-360}
          max={360}
          step={15}
          unit="°"
        />
      )}

      {setting.type === 'channel' && (
        <>
          <NumericField
            id="channel-wall-thickness"
            label="Wall thickness"
            value={parameters.wallThicknessMm}
            onChange={(wallThicknessMm) => patchParameters({ wallThicknessMm })}
            min={0.05}
            max={20}
            step={0.05}
            unit="mm"
          />
          <NumericField
            id="channel-wall-height"
            label="Wall height"
            value={parameters.wallHeightMm}
            onChange={(wallHeightMm) => patchParameters({ wallHeightMm })}
            min={0.05}
            max={50}
            step={0.05}
            unit="mm"
          />
          <SelectField
            id="channel-termination"
            label="Ends"
            value={parameters.termination}
            options={[
              { value: 'OPEN', label: 'Open' },
              { value: 'CLOSED_ENDS', label: 'Closed' },
            ]}
            onChange={(value) =>
              patchParameters({
                termination: value as SettingModeParameters['termination'],
              })
            }
          />
        </>
      )}

      {setting.type === 'bar' && (
        <>
          <NumericField
            id="bar-count"
            label="Bars"
            value={parameters.barCount}
            onChange={(barCount) => patchParameters({ barCount })}
            min={1}
            max={40}
            step={1}
          />
          <NumericField
            id="bar-width"
            label="Bar thickness"
            value={parameters.wallThicknessMm}
            onChange={(wallThicknessMm) => patchParameters({ wallThicknessMm })}
            min={0.05}
            max={20}
            step={0.05}
            unit="mm"
          />
          <NumericField
            id="bar-height"
            label="Bar height"
            value={parameters.barHeightMm}
            onChange={(barHeightMm) => patchParameters({ barHeightMm })}
            min={0.05}
            max={50}
            step={0.05}
            unit="mm"
          />
        </>
      )}

      {(setting.type === 'channel' || setting.type === 'bar') && (
        <SelectField
          id="setting-mode-symmetry"
          label="Run placement"
          value={parameters.symmetry}
          options={[
            { value: 'SYMMETRIC', label: 'Centred on the stone' },
            { value: 'ASYMMETRIC', label: 'Starting at the stone' },
          ]}
          onChange={(value) =>
            patchParameters({
              symmetry: value as SettingModeParameters['symmetry'],
            })
          }
        />
      )}

      {setting.type === 'flush' && (
        <>
          <NumericField
            id="flush-collar-width"
            label="Collar width"
            value={parameters.collarWidthMm}
            onChange={(collarWidthMm) => patchParameters({ collarWidthMm })}
            min={0.05}
            max={20}
            step={0.05}
            unit="mm"
          />
          <NumericField
            id="flush-rim-height"
            label="Rim above girdle"
            value={parameters.rimHeightMm}
            onChange={(rimHeightMm) => patchParameters({ rimHeightMm })}
            min={0.05}
            max={20}
            step={0.05}
            unit="mm"
          />
        </>
      )}

      {setting.type === 'tension' && (
        <>
          <NumericField
            id="tension-grip-axis"
            label="Grip direction"
            value={parameters.gripAxisDeg}
            onChange={(gripAxisDeg) => patchParameters({ gripAxisDeg })}
            min={-360}
            max={360}
            step={15}
            unit="°"
          />
          <NumericField
            id="tension-pad-width"
            label="Support width"
            value={parameters.padWidthMm}
            onChange={(padWidthMm) => patchParameters({ padWidthMm })}
            min={0.05}
            max={50}
            step={0.1}
            unit="mm"
          />
          <NumericField
            id="tension-pad-thickness"
            label="Support thickness"
            value={parameters.padThicknessMm}
            onChange={(padThicknessMm) => patchParameters({ padThicknessMm })}
            min={0.05}
            max={50}
            step={0.1}
            unit="mm"
          />
          <NumericField
            id="tension-grip-height"
            label="Support height"
            value={parameters.gripHeightMm}
            onChange={(gripHeightMm) => patchParameters({ gripHeightMm })}
            min={0.05}
            max={50}
            step={0.1}
            unit="mm"
          />
        </>
      )}

      <SelectField
        id="head-architecture"
        label="Head"
        value={setting.headArchitecture}
        options={HEAD_ARCHITECTURE_OPTIONS.map((o) => ({
          value: o.value,
          label: o.label,
        }))}
        onChange={(value) =>
          updateSetting({ headArchitecture: value as HeadArchitecture })
        }
        wide
      />

      {setting.headArchitecture === 'PEG_HEAD' && (
        <>
          {/* Deliberately NOT defaulted to a number by the panel either: an
              invented peg size would be a construction choice the user never
              made, which is why the backend refuses rather than guessing
              (JM-SETTING-005). */}
          <NumericField
            id="peg-diameter"
            label="Peg diameter"
            value={setting.pegDiameter ?? 1}
            onChange={(pegDiameter) => updateSetting({ pegDiameter })}
            min={0.05}
            max={20}
            step={0.1}
            unit="mm"
          />
          <NumericField
            id="peg-height"
            label="Peg height"
            value={setting.pegHeight ?? 1.5}
            onChange={(pegHeight) => updateSetting({ pegHeight })}
            min={0.05}
            max={50}
            step={0.1}
            unit="mm"
          />
        </>
      )}

      {(setting.headArchitecture === 'MARTINI' ||
        setting.headArchitecture === 'TULIP') && (
        <NumericField
          id="head-base-ratio"
          label="Base ratio"
          value={setting.headBaseRatio}
          onChange={(headBaseRatio) => updateSetting({ headBaseRatio })}
          min={0.06}
          max={1}
          step={0.05}
          unit="×"
        />
      )}

      {setting.headArchitecture === 'OPEN_GALLERY' && (
        <>
          <NumericField
            id="gallery-window-count"
            label="Windows"
            value={setting.galleryWindowCount}
            onChange={(galleryWindowCount) =>
              updateSetting({ galleryWindowCount })
            }
            min={1}
            max={24}
            step={1}
          />
          <NumericField
            id="gallery-window-sweep"
            label="Window width"
            value={setting.galleryWindowSweep}
            onChange={(galleryWindowSweep) =>
              updateSetting({ galleryWindowSweep })
            }
            min={1}
            max={180}
            step={5}
            unit="°"
          />
          <NumericField
            id="gallery-window-height"
            label="Window height"
            value={setting.galleryWindowHeightFraction}
            onChange={(galleryWindowHeightFraction) =>
              updateSetting({ galleryWindowHeightFraction })
            }
            min={0.05}
            max={0.95}
            step={0.05}
            unit="×"
          />
        </>
      )}

      <SelectField
        id="seat-mode"
        label="Relieve metal for the stone"
        value={setting.seatMode}
        options={SEAT_MODE_OPTIONS.map((o) => ({
          value: o.value,
          label: o.label,
        }))}
        onChange={(value) => updateSetting({ seatMode: value as SeatMode })}
        wide
      />

      {setting.type === 'flush' && setting.seatMode === 'NONE' && (
        <p className="form-note form-note--warning">
          A flush setting needs the metal relieved for the stone. Without it the
          collar fills the space the stone occupies, so nothing can be built.
        </p>
      )}

      {setting.type === 'tension' && (
        <p className="form-note form-note--warning">
          JewelMind builds the two opposing supports as real geometry and does
          not model how a tension setting holds a stone — no force, no
          spring-back, no retention behaviour. A qualified jewelry professional
          must review this design before production.
        </p>
      )}

      <p className="form-note">
        No setting dimension in JewelMind is professionally validated. A
        qualified jewelry professional must review this design before
        production.
      </p>
    </FormSection>
  )
}
