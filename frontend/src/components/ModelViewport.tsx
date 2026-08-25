import { Environment, OrbitControls, PerspectiveCamera, ContactShadows } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { RoomEnvironment } from 'three-stdlib'
import { triggerBrowserDownload } from '../api/client'
import { useProjectStore } from '../store/useProjectStore'
import { isComponentVisible, useVisionStore } from '../store/useVisionStore'
import { useComponentGeometries } from '../hooks/useComponentGeometries'
import { BACKGROUND_COLOR, resolveComponentMaterial } from '../vision/materials'
import { computeCameraPreset, computeFitPose, computeGroundY } from '../vision/camera'
import type { BoundingBoxMm } from '../vision/camera'
import type { CameraPresetKey } from '../vision/types'
import { buildCaptureFilename } from '../vision/filename'
import { CAPTURE_BLOCKED_MESSAGES, captureBlockedReason } from '../vision/capture'
import { computeModelState, describeModelState } from '../studio/modelState'
import { resolveShortcutKey, shouldIgnoreShortcut } from '../studio/keyboardShortcuts'
import { hasErrors } from '@shared/validation/engine'
import { ComponentMesh } from './ComponentMesh'
import { ComponentVisibilityPanel } from './ComponentVisibilityPanel'
import { ErrorBanner } from './ErrorBanner'
import { LoadingOverlay } from './LoadingOverlay'
import { PresentationPanel } from './PresentationPanel'
import { ViewModeSwitch } from './ViewModeSwitch'
import { ViewportToolbar } from './ViewportToolbar'

const CAPTURE_WIDTH = 1920
const CAPTURE_HEIGHT = 1080

export function ModelViewport() {
  const definition = useProjectStore((s) => s.currentDefinition)
  const lastSuccessfulPreview = useProjectStore((s) => s.lastSuccessfulPreview)
  const generationStatus = useProjectStore((s) => s.generationStatus)
  const generationError = useProjectStore((s) => s.generationError)
  const isStale = useProjectStore((s) => s.isStale)
  const validationResults = useProjectStore((s) => s.validationResults)
  const generate = useProjectStore((s) => s.generate)

  const viewMode = useVisionStore((s) => s.viewMode)
  const setViewMode = useVisionStore((s) => s.setViewMode)
  const componentVisibility = useVisionStore((s) => s.componentVisibility)
  const toggleComponentVisible = useVisionStore((s) => s.toggleComponentVisible)
  const showAllComponents = useVisionStore((s) => s.showAllComponents)
  const showOnlyComponents = useVisionStore((s) => s.showOnlyComponents)
  const selectedComponent = useVisionStore((s) => s.selectedComponent)
  const selectComponent = useVisionStore((s) => s.selectComponent)
  const showGridSetting = useVisionStore((s) => s.showGrid)
  const showAxesSetting = useVisionStore((s) => s.showAxes)
  const toggleShowGrid = useVisionStore((s) => s.toggleShowGrid)
  const toggleShowAxes = useVisionStore((s) => s.toggleShowAxes)
  const captureRequestToken = useVisionStore((s) => s.captureRequestToken)

  const [isCapturing, setIsCapturing] = useState(false)

  interface ControlsHandle {
    target: THREE.Vector3
    update: () => void
  }
  const controlsRef = useRef<ControlsHandle | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)

  const backgroundColor = BACKGROUND_COLOR[viewMode]
  // Grid/axes are technical-inspection aids; Presentation mode always
  // hides them regardless of the stored toggle, per the "clean
  // background, no debug overlays by default" product requirement.
  const showGrid = viewMode === 'technical' && showGridSetting
  const showAxes = viewMode === 'technical' && showAxesSetting

  const bbox: BoundingBoxMm | null = lastSuccessfulPreview?.metadata.boundingBoxMm ?? null

  const componentEntries = useMemo(
    () => (lastSuccessfulPreview ? Object.entries(lastSuccessfulPreview.previewComponents) : []),
    [lastSuccessfulPreview],
  )
  const metalComponentNames = useMemo(
    () =>
      componentEntries
        .filter(([, entry]) => (entry.geometryRole ?? 'production_metal') === 'production_metal')
        .map(([name]) => name),
    [componentEntries],
  )
  const allComponentNames = useMemo(() => componentEntries.map(([name]) => name), [componentEntries])

  const { geometries, hasError: previewMeshError } = useComponentGeometries(
    lastSuccessfulPreview?.previewComponents ?? null,
  )

  // Hooks must run unconditionally (Rules of Hooks) even though the
  // RoomEnvironment scene is only actually used while in Presentation
  // mode below.
  const roomEnvironment = useMemo(() => RoomEnvironment(), [])
  // A referentially-stable initial position: recomputing a new array
  // every render here would fight OrbitControls, snapping the camera
  // back on every unrelated re-render (e.g. toggling a checkbox).
  const initialCameraPosition = useMemo(() => computeCameraPreset('perspective', null).position, [])

  function applyPose(pose: { position: [number, number, number]; target: [number, number, number] }) {
    const camera = cameraRef.current
    const controls = controlsRef.current
    if (!camera || !controls) return
    camera.position.set(...pose.position)
    controls.target.set(...pose.target)
    controls.update()
  }

  function handleCameraPreset(preset: CameraPresetKey) {
    applyPose(computeCameraPreset(preset, bbox))
  }

  function resetCamera() {
    applyPose(computeCameraPreset('perspective', bbox))
  }

  function fitToView() {
    applyPose(computeFitPose(bbox))
  }

  function handleCapture() {
    const gl = rendererRef.current
    const scene = sceneRef.current
    const camera = cameraRef.current
    if (!gl || !scene || !camera || captureBlockedReason(lastSuccessfulPreview !== null, isStale) !== null) return

    setIsCapturing(true)
    const previousSize = new THREE.Vector2()
    gl.getSize(previousSize)
    const previousAspect = camera.aspect
    try {
      gl.setSize(CAPTURE_WIDTH, CAPTURE_HEIGHT, false)
      camera.aspect = CAPTURE_WIDTH / CAPTURE_HEIGHT
      camera.updateProjectionMatrix()
      // Render synchronously right before reading the buffer so the
      // capture is correct without paying the cost of
      // `preserveDrawingBuffer: true` on every normal frame — see
      // docs/bible/10-vision/238-image-capture-contract.md.
      gl.render(scene, camera)
      // toBlob() snapshots the canvas's current pixels synchronously when
      // called; only PNG encoding happens in the background. It is safe
      // to resize the renderer back down in `finally` immediately after
      // this call — the snapshot has already been taken.
      gl.domElement.toBlob((blob) => {
        if (blob) {
          const filename = buildCaptureFilename(definition.project.name, 'presentation', Date.now())
          triggerBrowserDownload(blob, filename)
        }
      }, 'image/png')
    } finally {
      gl.setSize(previousSize.x, previousSize.y, false)
      camera.aspect = previousAspect
      camera.updateProjectionMatrix()
      gl.render(scene, camera)
      setIsCapturing(false)
    }
  }

  const captureBlockedReasonKey = captureBlockedReason(lastSuccessfulPreview !== null, isStale)
  const captureBlockedMessage = captureBlockedReasonKey ? CAPTURE_BLOCKED_MESSAGES[captureBlockedReasonKey] : null

  // Lets Studio's consolidated Outputs panel (outside this component
  // tree's props) trigger a capture without either side holding a
  // direct reference to the other — see useVisionStore.requestCapture().
  // handleCapture is re-created every render, so it's stashed in a ref
  // (kept fresh via its own effect) rather than listed as this effect's
  // dependency — listing it directly would re-run the capture on every
  // unrelated re-render, not just on an actual capture request.
  const handleCaptureRef = useRef(handleCapture)
  useEffect(() => {
    handleCaptureRef.current = handleCapture
  })

  const isFirstCaptureTokenRender = useRef(true)
  useEffect(() => {
    if (isFirstCaptureTokenRender.current) {
      isFirstCaptureTokenRender.current = false
      return
    }
    handleCaptureRef.current()
  }, [captureRequestToken])

  // A small, discoverable keyboard shortcut set (G/F/1-4) — see
  // docs/bible/11-studio/273-keyboard-and-input-model.md. Kept behind a
  // ref of "latest callbacks" so the actual `keydown` listener is
  // attached exactly once, never re-attached on every render.
  const latestShortcutActions = useRef({
    generate: () => void generate(),
    fitToView: () => fitToView(),
    handleCameraPreset: (preset: CameraPresetKey) => handleCameraPreset(preset),
    canGenerate: () => generationStatus !== 'generating' && !hasErrors(validationResults),
  })
  useEffect(() => {
    latestShortcutActions.current = {
      generate: () => void generate(),
      fitToView: () => fitToView(),
      handleCameraPreset: (preset) => handleCameraPreset(preset),
      canGenerate: () => generationStatus !== 'generating' && !hasErrors(validationResults),
    }
  })

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (shouldIgnoreShortcut(event.target, event.metaKey || event.ctrlKey || event.altKey)) return
      const key = resolveShortcutKey(event.key)
      if (!key) return
      const actions = latestShortcutActions.current
      switch (key) {
        case 'g':
          if (actions.canGenerate()) actions.generate()
          break
        case 'f':
          actions.fitToView()
          break
        case '1':
          actions.handleCameraPreset('front')
          break
        case '2':
          actions.handleCameraPreset('side')
          break
        case '3':
          actions.handleCameraPreset('top')
          break
        case '4':
          actions.handleCameraPreset('three_quarter')
          break
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  const showEmptyState = !lastSuccessfulPreview && generationStatus !== 'generating'
  const viewportModelState = computeModelState({
    generationStatus,
    hasLastGoodPreview: lastSuccessfulPreview !== null,
    isStale,
  })

  return (
    <div className="viewport">
      <ViewModeSwitch viewMode={viewMode} onChange={setViewMode} />
      <ViewportToolbar
        viewMode={viewMode}
        onCameraPreset={handleCameraPreset}
        onResetCamera={resetCamera}
        onFitToView={fitToView}
        showGrid={showGridSetting}
        onToggleGrid={toggleShowGrid}
        showAxes={showAxesSetting}
        onToggleAxes={toggleShowAxes}
      />
      <ComponentVisibilityPanel
        components={componentEntries.map(([name, entry]) => ({
          name,
          generationStatus: entry.generationStatus ?? 'SUCCEEDED',
        }))}
        metalComponentNames={metalComponentNames}
        visible={componentVisibility}
        onToggle={toggleComponentVisible}
        onShowAll={() => showAllComponents(allComponentNames)}
        onShowMetalOnly={() => showOnlyComponents(allComponentNames, metalComponentNames)}
        selectedComponent={selectedComponent}
        onSelect={selectComponent}
      />
      {viewMode === 'presentation' ? (
        <PresentationPanel
          metal={definition.material.metal}
          onCapture={handleCapture}
          captureDisabled={captureBlockedReasonKey !== null || isCapturing}
          captureDisabledReason={captureBlockedMessage}
          isCapturing={isCapturing}
        />
      ) : null}

      <div className="viewport__canvas-wrap">
        <Canvas
          shadows
          onCreated={({ gl, scene }) => {
            rendererRef.current = gl
            sceneRef.current = scene
          }}
        >
          <color attach="background" args={[backgroundColor]} />
          <PerspectiveCamera
            makeDefault
            ref={cameraRef}
            position={initialCameraPosition}
            fov={45}
            near={0.1}
            far={2000}
          />
          <OrbitControls ref={controlsRef as never} makeDefault enableDamping />

          {viewMode === 'presentation' ? (
            <>
              <ambientLight intensity={0.35} />
              <directionalLight position={[25, 35, 15]} intensity={1.2} castShadow />
              <directionalLight position={[-20, 12, 15]} intensity={0.45} />
              <directionalLight position={[-8, 18, -25]} intensity={0.5} color="#dce8ff" />
              <Environment resolution={256} background={false}>
                <primitive object={roomEnvironment} />
              </Environment>
              <ContactShadows
                position={[0, computeGroundY(bbox) - 0.05, 0]}
                opacity={0.55}
                scale={40}
                blur={2.4}
                far={20}
              />
            </>
          ) : (
            <>
              <ambientLight intensity={0.65} />
              <directionalLight position={[25, 35, 15]} intensity={1.1} />
              <directionalLight position={[-20, 10, -15]} intensity={0.35} />
            </>
          )}

          {showGrid ? <gridHelper args={[60, 30, '#3c434c', '#262b31']} /> : null}
          {showAxes ? <axesHelper args={[20]} /> : null}

          <group rotation={[-Math.PI / 2, 0, 0]}>
            {Object.entries(geometries).map(([name, geometry]) => {
              if (!isComponentVisible({ componentVisibility }, name)) return null
              const entry = lastSuccessfulPreview?.previewComponents[name]
              const isStone = (entry?.geometryRole ?? (name === 'stone_reference' ? 'stone_reference' : 'production_metal')) === 'stone_reference'
              const material = resolveComponentMaterial(isStone, definition.material.metal, viewMode)
              const isSelected = selectedComponent === name
              return (
                <ComponentMesh
                  key={name}
                  geometry={geometry}
                  color={material.color}
                  opacity={material.opacity}
                  metalness={material.metalness}
                  roughness={material.roughness}
                  transmission={material.transmission}
                  ior={material.ior}
                  thickness={material.thickness}
                  clearcoat={material.clearcoat}
                  envMapIntensity={material.envMapIntensity}
                  emissive={isSelected ? '#ffcc66' : '#000000'}
                  emissiveIntensity={isSelected ? 0.35 : 0}
                />
              )
            })}
          </group>
        </Canvas>
      </div>

      {generationStatus === 'generating' ? <LoadingOverlay message="Generating model…" /> : null}
      {generationStatus === 'error' && generationError ? (
        <ErrorBanner message={generationError} />
      ) : previewMeshError ? (
        <ErrorBanner message="Could not load the 3D preview mesh from the backend. Showing the last successful preview, if any." />
      ) : null}
      {viewportModelState === 'STALE' || viewportModelState === 'FAILED_WITH_LAST_GOOD' ? (
        <div className="stale-banner">{describeModelState(viewportModelState).label}</div>
      ) : null}
      {showEmptyState ? (
        <p
          className="empty-state"
          style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          Configure your ring and press Generate model to see a preview.
        </p>
      ) : null}
    </div>
  )
}
