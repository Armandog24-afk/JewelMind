import type {
  BandProfile,
  ManufacturingMethod,
  MetalType,
  SettingType,
  StoneReferenceProfile,
  StoneShape,
} from '@shared/types/jewelry-definition'
import { useProjectStore } from '../store/useProjectStore'
import { FormSection } from './FormSection'
import { NumericField } from './NumericField'
import { SelectField } from './SelectField'

const BAND_PROFILE_OPTIONS: Array<{ value: BandProfile; label: string }> = [
  { value: 'comfort_fit', label: 'Comfort fit' },
  { value: 'flat', label: 'Flat' },
]

const METAL_OPTIONS: Array<{ value: MetalType; label: string }> = [
  { value: 'yellow_gold_18k', label: 'Yellow gold 18k' },
  { value: 'white_gold_18k', label: 'White gold 18k' },
  { value: 'rose_gold_18k', label: 'Rose gold 18k' },
  { value: 'platinum', label: 'Platinum' },
  { value: 'silver', label: 'Silver' },
]

const MANUFACTURING_OPTIONS: Array<{ value: ManufacturingMethod; label: string }> = [
  { value: 'lost_wax_casting', label: 'Lost-wax casting' },
  { value: 'direct_resin_printing', label: 'Direct resin printing' },
]

// Mirrors `jewelmind/stone/capability.py::native_shapes()` — every shape with a
// real generator (Sprint 20). Kept in sync by hand, same discipline as every
// other option list in this file. Update this list in the same change as the
// backend capability registry.
//
// The `custom` and `imported` pseudo-shapes are deliberately ABSENT: they are
// not cuts a user picks, they are consequences of choosing a different stone
// source, and offering them here would invite a stone with no outline behind it.
const STONE_SHAPE_OPTIONS: Array<{ value: StoneShape; label: string }> = [
  { value: 'round', label: 'Round' },
  { value: 'oval', label: 'Oval' },
  { value: 'pear', label: 'Pear' },
  { value: 'emerald', label: 'Emerald' },
  { value: 'cushion', label: 'Cushion' },
  { value: 'princess', label: 'Princess' },
  { value: 'marquise', label: 'Marquise' },
  { value: 'heart', label: 'Heart' },
  { value: 'radiant', label: 'Radiant' },
  { value: 'asscher', label: 'Asscher' },
  { value: 'trillion', label: 'Trillion' },
  { value: 'baguette', label: 'Baguette' },
  { value: 'tapered_baguette', label: 'Tapered baguette' },
  { value: 'triangle', label: 'Triangle' },
  { value: 'trapezoid', label: 'Trapezoid' },
  { value: 'lozenge', label: 'Lozenge' },
  { value: 'hexagon', label: 'Hexagon' },
  { value: 'kite', label: 'Kite' },
  { value: 'shield', label: 'Shield' },
  { value: 'half_moon', label: 'Half moon' },
  { value: 'pearl', label: 'Pearl (sphere)' },
]

// Shapes whose single horizontal size is a diameter rather than a length/width
// pair. Mirrors `_ROUND_LIKE_SHAPES` in the backend schema.
const ROUND_LIKE_SHAPES: StoneShape[] = ['round', 'pearl']

// Shapes that require an explicit narrow-end width. Mirrors `_TAPERED_SHAPES`.
// The taper is a real dimension the user supplies, never a default ratio.
const TAPERED_SHAPES: StoneShape[] = ['tapered_baguette', 'trapezoid']

// Which 3D reference profile each shape supports. Mirrors the
// `supportedProfiles` field of the backend shape registry. Profile is a second,
// independent axis: this is why there is no `OVAL_CABOCHON` shape.
const SHAPE_PROFILE_OPTIONS: Partial<
  Record<StoneShape, Array<{ value: StoneReferenceProfile; label: string }>>
> = {
  round: [
    { value: 'FACETED_REFERENCE', label: 'Faceted' },
    { value: 'CABOCHON_REFERENCE', label: 'Cabochon' },
  ],
  oval: [
    { value: 'FACETED_REFERENCE', label: 'Faceted' },
    { value: 'CABOCHON_REFERENCE', label: 'Cabochon' },
  ],
  heart: [
    { value: 'FACETED_REFERENCE', label: 'Faceted' },
    { value: 'CABOCHON_REFERENCE', label: 'Cabochon' },
  ],
  half_moon: [
    { value: 'FACETED_REFERENCE', label: 'Faceted' },
    { value: 'CABOCHON_REFERENCE', label: 'Cabochon' },
  ],
}

// Mirrors `setting/capability.py::SETTING_CAPABILITIES`'s generatable
// families (Sprint 19) — kept in sync by hand, same discipline as every
// other option list here. Reserved families (channel, flush, bar, tension,
// bead, pave, custom) have no generator and must NOT appear.
const SETTING_TYPE_OPTIONS: Array<{ value: SettingType; label: string }> = [
  { value: 'prong', label: 'Prong' },
  { value: 'bezel', label: 'Bezel' },
]

const PRONG_COUNT_OPTIONS = [
  { value: '4', label: '4 prongs' },
  { value: '6', label: '6 prongs' },
]

/**
 * Design parameters vs. advanced/technical parameters — see
 * docs/bible/11-studio/255-design-editing-contract.md and
 * 256-parameter-editor-model.md for which fields ended up in which
 * group and why (in short: a field moves to Advanced only when a more
 * commonly-understood equivalent already exists in the Design group,
 * e.g. ring size vs. exact inner diameter, or when it controls preview
 * rendering rather than the design itself).
 */
export function ConfigurationPanel() {
  const definition = useProjectStore((s) => s.currentDefinition)
  const updateProject = useProjectStore((s) => s.updateProject)
  const updateRing = useProjectStore((s) => s.updateRing)
  const updateBand = useProjectStore((s) => s.updateBand)
  const updateStone = useProjectStore((s) => s.updateStone)
  const updateSetting = useProjectStore((s) => s.updateSetting)
  const updateMaterial = useProjectStore((s) => s.updateMaterial)
  const updateManufacturing = useProjectStore((s) => s.updateManufacturing)
  const updatePreview = useProjectStore((s) => s.updatePreview)

  return (
    <div>
      <FormSection title="Project">
        <div className="form-field form-field--wide">
          <label htmlFor="project-name">Name</label>
          <input
            id="project-name"
            type="text"
            value={definition.project.name}
            onChange={(e) => updateProject({ name: e.target.value })}
          />
        </div>
      </FormSection>

      <FormSection title="Ring">
        <NumericField
          id="ring-size"
          label="EU size"
          value={definition.ring.size}
          onChange={(size) => updateRing({ size })}
          step={0.5}
          min={1}
          max={49.9}
        />
      </FormSection>

      <FormSection title="Band">
        <NumericField
          id="band-width"
          label="Width"
          unit="mm"
          value={definition.band.width}
          onChange={(width) => updateBand({ width })}
          step={0.1}
          min={0.1}
          max={20}
        />
        <NumericField
          id="band-thickness"
          label="Thickness"
          unit="mm"
          value={definition.band.thickness}
          onChange={(thickness) => updateBand({ thickness })}
          step={0.1}
          min={0.1}
          max={10}
        />
        <SelectField
          id="band-profile"
          label="Profile"
          value={definition.band.profile}
          options={BAND_PROFILE_OPTIONS}
          onChange={(value) => updateBand({ profile: value as BandProfile })}
          wide
        />
      </FormSection>

      <FormSection title="Stone">
        <SelectField
          id="stone-shape"
          label="Shape"
          value={definition.stone.shape}
          options={STONE_SHAPE_OPTIONS}
          onChange={(value) => {
            const shape = value as StoneShape
            // Carry compatible dimensions across a shape change and clear the
            // ones the new shape cannot use, so switching never leaves a
            // half-populated stone the backend would reject. A profile the new
            // shape does not support falls back to its first supported one.
            const profiles = SHAPE_PROFILE_OPTIONS[shape]
            const profile: StoneReferenceProfile =
              shape === 'pearl'
                ? 'SPHERICAL_REFERENCE'
                : profiles?.some((option) => option.value === definition.stone.profile)
                  ? definition.stone.profile
                  : 'FACETED_REFERENCE'

            if (ROUND_LIKE_SHAPES.includes(shape)) {
              updateStone({
                shape,
                profile,
                diameter: definition.stone.diameter ?? 6.5,
                length: null,
                width: null,
                narrowWidth: null,
              })
            } else {
              const width = definition.stone.width ?? 6.0
              updateStone({
                shape,
                profile,
                length: definition.stone.length ?? 8.0,
                width,
                // A tapered shape needs a real narrow width; seed it from the
                // wide width so the field starts valid, and let the user set it.
                narrowWidth: TAPERED_SHAPES.includes(shape)
                  ? (definition.stone.narrowWidth ?? Number((width * 0.6).toFixed(2)))
                  : null,
              })
            }
          }}
          wide
        />
        {SHAPE_PROFILE_OPTIONS[definition.stone.shape] && (
          <SelectField
            id="stone-profile"
            label="Profile"
            value={definition.stone.profile}
            options={SHAPE_PROFILE_OPTIONS[definition.stone.shape] ?? []}
            onChange={(value) => updateStone({ profile: value as StoneReferenceProfile })}
            wide
          />
        )}
        {ROUND_LIKE_SHAPES.includes(definition.stone.shape) ? (
          <NumericField
            id="stone-diameter"
            label="Diameter"
            unit="mm"
            value={definition.stone.diameter ?? 6.5}
            onChange={(diameter) => updateStone({ diameter })}
            step={0.1}
            min={0.5}
            max={20}
          />
        ) : (
          <>
            <NumericField
              id="stone-length"
              label="Length"
              unit="mm"
              value={definition.stone.length ?? 8.0}
              onChange={(length) => updateStone({ length })}
              step={0.1}
              min={0.5}
              max={20}
            />
            <NumericField
              id="stone-width"
              label={TAPERED_SHAPES.includes(definition.stone.shape) ? 'Wide-end width' : 'Width'}
              unit="mm"
              value={definition.stone.width ?? 6.0}
              onChange={(width) => updateStone({ width })}
              step={0.1}
              min={0.5}
              max={20}
            />
            {TAPERED_SHAPES.includes(definition.stone.shape) && (
              <NumericField
                id="stone-narrow-width"
                label="Narrow-end width"
                unit="mm"
                value={definition.stone.narrowWidth ?? 3.6}
                onChange={(narrowWidth) => updateStone({ narrowWidth })}
                step={0.1}
                min={0.5}
                max={20}
              />
            )}
          </>
        )}
      </FormSection>

      <FormSection title="Setting">
        <SelectField
          id="setting-type"
          label="Type"
          value={definition.setting.type}
          options={SETTING_TYPE_OPTIONS}
          onChange={(value) => updateSetting({ type: value as SettingType })}
          wide
        />
        {definition.setting.type === 'prong' ? (
          <SelectField
            id="prong-count"
            label="Prong count"
            value={String(definition.setting.prongCount)}
            options={PRONG_COUNT_OPTIONS}
            onChange={(value) => updateSetting({ prongCount: Number(value) })}
          />
        ) : (
          <>
            <NumericField
              id="bezel-wall-thickness"
              label="Wall thickness"
              unit="mm"
              value={definition.setting.bezelWallThickness}
              onChange={(bezelWallThickness) => updateSetting({ bezelWallThickness })}
              step={0.1}
              min={0.1}
              max={5}
            />
            <NumericField
              id="bezel-wall-height"
              label="Wall height"
              unit="mm"
              value={definition.setting.bezelWallHeight}
              onChange={(bezelWallHeight) => updateSetting({ bezelWallHeight })}
              step={0.1}
              min={0.1}
              max={10}
            />
          </>
        )}
      </FormSection>

      <FormSection title="Material">
        <SelectField
          id="metal"
          label="Metal"
          value={definition.material.metal}
          options={METAL_OPTIONS}
          onChange={(value) => updateMaterial({ metal: value as MetalType })}
          wide
        />
      </FormSection>

      <FormSection title="Manufacturing">
        <SelectField
          id="manufacturing-method"
          label="Method"
          value={definition.manufacturing.method}
          options={MANUFACTURING_OPTIONS}
          onChange={(value) => updateManufacturing({ method: value as ManufacturingMethod })}
          wide
        />
      </FormSection>

      <details className="advanced-parameters">
        <summary>Advanced / technical parameters</summary>
        <p className="advanced-parameters__hint">
          These control exact dimensions and preview quality directly. Most designs only need the parameters
          above.
        </p>

        <FormSection title="Ring — exact diameter">
          <NumericField
            id="ring-inner-diameter"
            label="Inner diameter"
            unit="mm"
            value={definition.ring.innerDiameter}
            onChange={(innerDiameter) => updateRing({ innerDiameter })}
            step={0.1}
            min={10.1}
            max={29.9}
          />
        </FormSection>

        <FormSection title="Stone — depth">
          <NumericField
            id="stone-depth"
            label="Depth"
            unit="mm"
            value={definition.stone.depth}
            onChange={(depth) => updateStone({ depth })}
            step={0.1}
            min={0.1}
            max={20}
          />
          {definition.stone.shape !== 'round' && (
            <NumericField
              id="stone-orientation"
              label="Orientation"
              unit="deg"
              value={definition.stone.orientation}
              onChange={(orientation) => updateStone({ orientation })}
              step={1}
              min={0}
              max={359}
            />
          )}
        </FormSection>

        <FormSection title="Setting — dimensions">
          <NumericField
            id="prong-diameter"
            label="Prong diameter"
            unit="mm"
            value={definition.setting.prongDiameter}
            onChange={(prongDiameter) => updateSetting({ prongDiameter })}
            step={0.05}
            min={0.1}
            max={5}
          />
          <NumericField
            id="prong-height"
            label="Prong height"
            unit="mm"
            value={definition.setting.prongHeight}
            onChange={(prongHeight) => updateSetting({ prongHeight })}
            step={0.1}
            min={0.1}
            max={15}
          />
          <NumericField
            id="basket-height"
            label="Basket height"
            unit="mm"
            value={definition.setting.basketHeight}
            onChange={(basketHeight) => updateSetting({ basketHeight })}
            step={0.1}
            min={0.1}
            max={15}
          />
        </FormSection>

        <FormSection title="Preview tessellation">
          <NumericField
            id="preview-mesh-tolerance"
            label="Mesh tolerance"
            unit="mm"
            value={definition.preview.meshTolerance}
            onChange={(meshTolerance) => updatePreview({ meshTolerance })}
            step={0.01}
            min={0.01}
            max={2}
          />
          <NumericField
            id="preview-angular-tolerance"
            label="Angular tolerance"
            unit="rad"
            value={definition.preview.angularTolerance}
            onChange={(angularTolerance) => updatePreview({ angularTolerance })}
            step={0.01}
            min={0.01}
            max={1}
          />
        </FormSection>
      </details>
    </div>
  )
}
