import { useProjectStore } from '../store/useProjectStore'

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="model-info__row">
      <span className="model-info__label">{label}</span>
      <span className="model-info__value">{value}</span>
    </div>
  )
}

export function ModelInformation() {
  const generatedModel = useProjectStore((s) => s.generatedModel)

  if (!generatedModel) {
    return <p className="empty-state">No model generated yet.</p>
  }

  const bbox = generatedModel.metadata.boundingBoxMm
  const prongs = generatedModel.metadata.prongs

  return (
    <div className="model-info">
      <Row label="Model ID" value={generatedModel.modelId} />
      <Row label="Definition hash" value={generatedModel.definitionHash} />
      <Row label="Generator version" value={generatedModel.metadata.generatorVersion} />
      <Row label="Generated at" value={generatedModel.generatedAt} />
      <Row
        label="Generation time"
        value={`${generatedModel.metadata.generationDurationSeconds.toFixed(3)} s`}
      />
      <Row label="Requested / generated prongs" value={`${prongs.requestedCount} / ${prongs.generatedCount}`} />
      <Row
        label="Combined metal volume"
        value={`${generatedModel.metadata.combinedMetalVolumeMm3.toFixed(2)} mm³`}
      />
      {Object.entries(generatedModel.metadata.componentVolumesMm3).map(([name, volume]) => (
        <Row key={name} label={`${name} volume`} value={`${volume.toFixed(2)} mm³`} />
      ))}
      <Row
        label="Bounding box (mm)"
        value={`X ${bbox['xmin']?.toFixed(1)}…${bbox['xmax']?.toFixed(1)}, Y ${bbox['ymin']?.toFixed(1)}…${bbox['ymax']?.toFixed(1)}, Z ${bbox['zmin']?.toFixed(1)}…${bbox['zmax']?.toFixed(1)}`}
      />
      {generatedModel.warnings.length > 0 ? (
        <div>
          <p className="model-info__label">Warnings</p>
          <ul>
            {generatedModel.warnings.map((warning, i) => (
              <li key={i}>{warning}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  )
}
