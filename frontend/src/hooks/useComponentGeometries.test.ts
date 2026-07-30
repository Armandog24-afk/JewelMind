import { renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { PreviewComponentEntry } from '../api/types'
import { useComponentGeometries } from './useComponentGeometries'

function makeMinimalBinaryStl(): ArrayBuffer {
  // 80-byte header + uint32 triangle count (1) + one 50-byte triangle record
  // (12 floats: normal + 3 vertices, then a 2-byte attribute count).
  const buffer = new ArrayBuffer(80 + 4 + 50)
  const view = new DataView(buffer)
  view.setUint32(80, 1, true)
  const base = 84
  for (let i = 0; i < 12; i++) {
    view.setFloat32(base + i * 4, i === 3 ? 1 : 0, true) // trivial non-degenerate-ish triangle
  }
  return buffer
}

function makeEntry(url: string): PreviewComponentEntry {
  return {
    vertexCount: 3,
    triangleCount: 1,
    volumeMm3: 1,
    boundingBox: { xmin: 0, xmax: 1, ymin: 0, ymax: 1, zmin: 0, zmax: 1 },
    warnings: [],
    url,
  }
}

describe('useComponentGeometries', () => {
  let fetchMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns empty geometries and is not loading when there is nothing to load', () => {
    const { result } = renderHook(() => useComponentGeometries(null))
    expect(result.current.geometries).toEqual({})
    expect(result.current.isLoading).toBe(false)
    expect(result.current.hasError).toBe(false)
  })

  it('loads geometries for every component with a url', async () => {
    fetchMock.mockImplementation(
      async () =>
        new Response(makeMinimalBinaryStl(), { status: 200 }) as unknown as Response,
    )

    const components = { band: makeEntry('/preview/band'), stone_reference: makeEntry('/preview/stone') }
    const { result } = renderHook(() => useComponentGeometries(components))

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(Object.keys(result.current.geometries).sort()).toEqual(['band', 'stone_reference'])
    expect(result.current.hasError).toBe(false)
  })

  it('skips components whose url is null', async () => {
    fetchMock.mockImplementation(
      async () =>
        new Response(makeMinimalBinaryStl(), { status: 200 }) as unknown as Response,
    )
    const components = { band: makeEntry('/preview/band'), prongs: makeEntry(null as unknown as string) }
    components.prongs.url = null
    const { result } = renderHook(() => useComponentGeometries(components))

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(Object.keys(result.current.geometries)).toEqual(['band'])
  })

  it('reports an error and keeps the previous geometries when a reload fails', async () => {
    fetchMock.mockImplementationOnce(
      async () =>
        new Response(makeMinimalBinaryStl(), { status: 200 }) as unknown as Response,
    )
    const first = { band: makeEntry('/preview/band-v1') }
    const { result, rerender } = renderHook(
      ({ components }) => useComponentGeometries(components),
      { initialProps: { components: first } },
    )
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    const firstGeometry = result.current.geometries['band']
    expect(firstGeometry).toBeDefined()

    fetchMock.mockImplementation(async () => new Response(null, { status: 500 }) as unknown as Response)
    const second = { band: makeEntry('/preview/band-v2') }
    rerender({ components: second })

    await waitFor(() => expect(result.current.hasError).toBe(true))
    // the last successful geometry must still be there, untouched
    expect(result.current.geometries['band']).toBe(firstGeometry)
  })

  it('disposes the previous geometry once a new successful set replaces it', async () => {
    fetchMock.mockImplementation(
      async () =>
        new Response(makeMinimalBinaryStl(), { status: 200 }) as unknown as Response,
    )
    const first = { band: makeEntry('/preview/band-v1') }
    const { result, rerender } = renderHook(
      ({ components }) => useComponentGeometries(components),
      { initialProps: { components: first } },
    )
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    const firstGeometry = result.current.geometries['band']
    const disposeSpy = vi.spyOn(firstGeometry!, 'dispose')

    const second = { band: makeEntry('/preview/band-v2') }
    rerender({ components: second })

    await waitFor(() => expect(result.current.geometries['band']).not.toBe(firstGeometry))
    expect(disposeSpy).toHaveBeenCalledTimes(1)
  })

  it('aborts the in-flight fetch when superseded before it resolves', async () => {
    const capturedSignals: AbortSignal[] = []
    fetchMock.mockImplementation(async (_url: string, init?: RequestInit) => {
      if (init?.signal) capturedSignals.push(init.signal)
      // never resolves within the test's lifetime on purpose
      return new Promise<Response>(() => {})
    })

    const first = { band: makeEntry('/preview/band-v1') }
    const { rerender, unmount } = renderHook(
      ({ components }) => useComponentGeometries(components),
      { initialProps: { components: first } },
    )

    await waitFor(() => expect(capturedSignals.length).toBe(1))
    const firstSignal = capturedSignals[0]!
    expect(firstSignal.aborted).toBe(false)

    const second = { band: makeEntry('/preview/band-v2') }
    rerender({ components: second })

    // the first (superseded) request's signal must now be aborted, even
    // though a brand-new request for the new props has since started
    expect(firstSignal.aborted).toBe(true)
    unmount()
  })

  it('disposes all held geometries on unmount', async () => {
    fetchMock.mockImplementation(
      async () =>
        new Response(makeMinimalBinaryStl(), { status: 200 }) as unknown as Response,
    )
    const components = { band: makeEntry('/preview/band') }
    const { result, unmount } = renderHook(() => useComponentGeometries(components))
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    const geometry = result.current.geometries['band']!
    const disposeSpy = vi.spyOn(geometry, 'dispose')

    unmount()
    expect(disposeSpy).toHaveBeenCalledTimes(1)
  })
})
