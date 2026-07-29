import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { useProjectStore } from '../store/useProjectStore'
import { useComponentGeometries } from '../hooks/useComponentGeometries'
import { ComponentMesh } from './ComponentMesh'
import { ComponentVisibilityPanel } from './ComponentVisibilityPanel'
import { ErrorBanner } from './ErrorBanner'
import { LoadingOverlay } from './LoadingOverlay'
import { ViewportToolbar } from './ViewportToolbar'

const METAL_COLORS: Record<string, string> = {
  yellow_gold_18k: '#d4af37',
  white_gold_18k: '#e7e7ea',
  rose_gold_18k: '#e3b7a4',
  platinum: '#e5e4e2',
  silver: '#c8c8ce',
}

const STONE_COLOR = '#bfe3ff'

const DEFAULT_CAMERA_POSITION: [number, number, number] = [30, 22, 30]

export function ModelViewport() {
  const definition = useProjectStore((s) => s.currentDefinition)
  const lastSuccessfulPreview = useProjectStore((s) => s.lastSuccessfulPreview)
  const generationStatus = useProjectStore((s) => s.generationStatus)
  const generationError = useProjectStore((s) => s.generationError)
  const isStale = useProjectStore((s) => s.isStale)

  const [visible, setVisible] = useState<Record<string, boolean>>({
    band: true,
    stone_reference: true,
    prongs: true,
    basket_support: true,
  })
  const [showGrid, setShowGrid] = useState(true)
  const [showAxes, setShowAxes] = useState(false)

  interface ControlsHandle {
    target: THREE.Vector3
    update: () => void
  }
  const controlsRef = useRef<ControlsHandle | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)

  const metalColor = METAL_COLORS[definition.material.metal] ?? METAL_COLORS['yellow_gold_18k']!

  const componentNames = useMemo(
    () => (lastSuccessfulPreview ? Object.keys(lastSuccessfulPreview.previewComponents) : []),
    [lastSuccessfulPreview],
  )

  const geometries = useComponentGeometries(lastSuccessfulPreview?.previewComponents ?? null)

  function resetCamera() {
    const camera = cameraRef.current
    const controls = controlsRef.current
    if (!camera || !controls) return
    camera.position.set(...DEFAULT_CAMERA_POSITION)
    controls.target.set(0, 0, 0)
    controls.update()
  }

  function fitToView() {
    const camera = cameraRef.current
    const controls = controlsRef.current
    if (!camera || !controls || !lastSuccessfulPreview) {
      resetCamera()
      return
    }
    const bbox = lastSuccessfulPreview.metadata.boundingBoxMm
    const min = new THREE.Vector3(bbox['xmin'], bbox['ymin'], bbox['zmin'])
    const max = new THREE.Vector3(bbox['xmax'], bbox['ymax'], bbox['zmax'])
    const center3d = min.clone().add(max).multiplyScalar(0.5)
    // account for the -90deg X rotation applied to the model group below
    const center = new THREE.Vector3(center3d.x, center3d.z, -center3d.y)
    const size = Math.max(max.clone().sub(min).length(), 5)
    const distance = size * 1.6
    const direction = new THREE.Vector3(1, 0.8, 1).normalize()
    camera.position.copy(center.clone().add(direction.multiplyScalar(distance)))
    controls.target.copy(center)
    controls.update()
  }

  const showEmptyState = !lastSuccessfulPreview && generationStatus !== 'generating'

  return (
    <div className="viewport">
      <ViewportToolbar
        onResetCamera={resetCamera}
        onFitToView={fitToView}
        showGrid={showGrid}
        onToggleGrid={() => setShowGrid((v) => !v)}
        showAxes={showAxes}
        onToggleAxes={() => setShowAxes((v) => !v)}
      />
      <ComponentVisibilityPanel
        componentNames={componentNames}
        visible={visible}
        onToggle={(name) => setVisible((v) => ({ ...v, [name]: !(v[name] ?? true) }))}
      />

      <div className="viewport__canvas-wrap">
        <Canvas>
          <PerspectiveCamera
            makeDefault
            ref={cameraRef}
            position={DEFAULT_CAMERA_POSITION}
            fov={45}
            near={0.1}
            far={2000}
          />
          <OrbitControls ref={controlsRef as never} makeDefault enableDamping />
          <ambientLight intensity={0.65} />
          <directionalLight position={[25, 35, 15]} intensity={1.1} />
          <directionalLight position={[-20, 10, -15]} intensity={0.35} />

          {showGrid ? <gridHelper args={[60, 30, '#3c434c', '#262b31']} /> : null}
          {showAxes ? <axesHelper args={[20]} /> : null}

          <group rotation={[-Math.PI / 2, 0, 0]}>
            {Object.entries(geometries).map(([name, geometry]) => {
              if (!(visible[name] ?? true)) return null
              const isStone = name === 'stone_reference'
              return (
                <ComponentMesh
                  key={name}
                  geometry={geometry}
                  color={isStone ? STONE_COLOR : metalColor}
                  opacity={isStone ? 0.55 : 1}
                  metalness={isStone ? 0.1 : 0.7}
                  roughness={isStone ? 0.05 : 0.3}
                />
              )
            })}
          </group>
        </Canvas>
      </div>

      {generationStatus === 'generating' ? <LoadingOverlay /> : null}
      {generationStatus === 'error' && generationError ? <ErrorBanner message={generationError} /> : null}
      {isStale ? <div className="stale-banner">Parameters changed — regenerate model.</div> : null}
      {showEmptyState ? (
        <p className="empty-state" style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          Configure your ring and press Generate model to see a preview.
        </p>
      ) : null}
    </div>
  )
}
