/**
 * Frontend-only filename sanitizer for Vision image captures. Conceptually
 * mirrors backend/jewelmind/exporters/filenames.py::sanitize_filename() but
 * is its own small utility — the frontend never has (and must never need)
 * a server round-trip just to name a client-side PNG download. See
 * docs/bible/10-vision/238-image-capture-contract.md.
 */

const UNSAFE_CHARS = /[^A-Za-z0-9._-]+/g
const MAX_LENGTH = 120
const DEFAULT_NAME = 'jewelmind-render'

export function sanitizeForFilename(name: string, fallback: string = DEFAULT_NAME): string {
  const collapsed = name.trim().replace(UNSAFE_CHARS, '_').replace(/^[._-]+|[._-]+$/g, '')
  const safe = collapsed.length > 0 ? collapsed : fallback
  return safe.slice(0, MAX_LENGTH)
}

/** `timestamp` is injected by the caller (e.g. `Date.now()`) rather than
 * computed inside this pure function, keeping it trivially testable. */
export function buildCaptureFilename(projectName: string, viewMode: string, timestamp: number): string {
  const safeProject = sanitizeForFilename(projectName, 'ring')
  const iso = new Date(timestamp).toISOString().replace(/[:.]/g, '-')
  return `jewelmind-${safeProject}-${viewMode}-${iso}.png`
}
