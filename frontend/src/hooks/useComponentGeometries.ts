import { useEffect, useState } from 'react'
import type * as THREE from 'three'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { resolveApiUrl } from '../api/client'
import type { PreviewComponentEntry } from '../api/types'

/**
 * Fetches and parses every component's STL preview mesh directly (fetch +
 * STLLoader.parse), rather than one useLoader()/Suspense call per mesh.
 * Each component genuinely is an independent backend-generated solid, so
 * this loads all of them in parallel and exposes plain BufferGeometry
 * objects the viewport can render as soon as they resolve.
 */
export function useComponentGeometries(
  previewComponents: Record<string, PreviewComponentEntry> | null,
): Record<string, THREE.BufferGeometry> {
  const [geometries, setGeometries] = useState<Record<string, THREE.BufferGeometry>>({})

  useEffect(() => {
    if (!previewComponents) {
      setGeometries({})
      return
    }

    let cancelled = false
    const loader = new STLLoader()
    const entries = Object.entries(previewComponents).filter(
      (pair): pair is [string, PreviewComponentEntry & { url: string }] => pair[1].url !== null,
    )

    Promise.all(
      entries.map(async ([name, entry]) => {
        const response = await fetch(resolveApiUrl(entry.url))
        const buffer = await response.arrayBuffer()
        const geometry = loader.parse(buffer)
        return [name, geometry] as const
      }),
    )
      .then((pairs) => {
        if (!cancelled) setGeometries(Object.fromEntries(pairs))
      })
      .catch(() => {
        if (!cancelled) setGeometries({})
      })

    return () => {
      cancelled = true
    }
  }, [previewComponents])

  return geometries
}
