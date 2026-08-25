import type { BandProfile, ManufacturingMethod, MetalType } from '@shared/types/jewelry-definition'
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
        <NumericField
          id="stone-diameter"
          label="Diameter"
          unit="mm"
          value={definition.stone.diameter}
          onChange={(diameter) => updateStone({ diameter })}
          step={0.1}
          min={0.5}
          max={20}
        />
      </FormSection>

      <FormSection title="Setting">
        <SelectField
          id="prong-count"
          label="Prong count"
          value={String(definition.setting.prongCount)}
          options={PRONG_COUNT_OPTIONS}
          onChange={(value) => updateSetting({ prongCount: Number(value) })}
        />
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
