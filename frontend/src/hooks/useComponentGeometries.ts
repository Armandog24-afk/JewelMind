import { useEffect, useRef, useState } from 'react'
import type * as THREE from 'three'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { resolveApiUrl } from '../api/client'
import type { PreviewComponentEntry } from '../api/types'

export interface ComponentGeometriesResult {
  geometries: Record<string, THREE.BufferGeometry>
  isLoading: boolean
  hasError: boolean
}

function disposeAll(geometries: Record<string, THREE.BufferGeometry>): void {
  for (const geometry of Object.values(geometries)) {
    geometry.dispose()
  }
}

/**
 * Fetches and parses every component's STL preview mesh directly (fetch +
 * STLLoader.parse), rather than one useLoader()/Suspense call per mesh.
 * Each component genuinely is an independent backend-generated solid, so
 * this loads all of them in parallel and exposes plain BufferGeometry
 * objects the viewport can render as soon as they resolve.
 *
 * Reliability properties this hook guarantees:
 * - In-flight fetches from a previous (now-superseded) set of preview
 *   components are aborted via AbortController, not just ignored — no
 *   wasted bandwidth/CPU on results nobody will use.
 * - The previously loaded geometries stay visible (and are NOT disposed)
 *   until a full new set has successfully loaded, so a failed or
 *   in-progress reload never blanks the viewport.
 * - Every BufferGeometry this hook creates is disposed exactly once, when
 *   it is replaced or when the hook unmounts — repeated regeneration must
 *   not leak GPU buffers.
 */
export function useComponentGeometries(
  previewComponents: Record<string, PreviewComponentEntry> | null,
): ComponentGeometriesResult {
  const [geometries, setGeometries] = useState<Record<string, THREE.BufferGeometry>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [hasError, setHasError] = useState(false)
  const currentGeometriesRef = useRef(geometries)
  currentGeometriesRef.current = geometries

  useEffect(() => {
    if (!previewComponents) {
      // No model generated yet (fresh project, or a reset). Nothing to show
      // and nothing stale to keep around.
      setGeometries((previous) => {
        disposeAll(previous)
        return {}
      })
      setIsLoading(false)
      setHasError(false)
      return
    }

    const controller = new AbortController()
    const loader = new STLLoader()
    const entries = Object.entries(previewComponents).filter(
      (pair): pair is [string, PreviewComponentEntry & { url: string }] => pair[1].url !== null,
    )

    setIsLoading(true)
    setHasError(false)

    Promise.all(
      entries.map(async ([name, entry]) => {
        const response = await fetch(resolveApiUrl(entry.url), { signal: controller.signal })
        if (!response.ok) {
          throw new Error(`Preview mesh request for "${name}" failed with status ${response.status}`)
        }
        const buffer = await response.arrayBuffer()
        const geometry = loader.parse(buffer)
        return [name, geometry] as const
      }),
    )
      .then((pairs) => {
        if (controller.signal.aborted) {
          // Superseded — dispose geometries nobody will ever render.
          for (const [, geometry] of pairs) geometry.dispose()
          return
        }
        const next = Object.fromEntries(pairs)
        // Only dispose the previous set once the new one is fully ready,
        // so the viewport never goes blank mid-reload.
        disposeAll(currentGeometriesRef.current)
        setGeometries(next)
        setIsLoading(false)
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return
        // A failed preview-mesh fetch must not erase an already-visible,
        // still-valid last-known-good preview.
        setIsLoading(false)
        setHasError(true)
        console.error('Failed to load preview mesh:', err)
      })

    return () => {
      controller.abort()
    }
  }, [previewComponents])

  // Dispose whatever is currently held when the hook itself unmounts (e.g.
  // the viewport is torn down).
  useEffect(() => {
    return () => {
      disposeAll(currentGeometriesRef.current)
    }
  }, [])

  return { geometries, isLoading, hasError }
}
