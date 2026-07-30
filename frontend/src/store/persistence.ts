import { isValidJewelryDefinition, type JewelryDefinition } from '@shared/types/jewelry-definition'

const STORAGE_KEY = 'jewelmind:project-definition:v1'

/**
 * Loads the saved definition, or null if there is none — or if it's
 * corrupted, obsolete, or otherwise not a valid JewelryDefinition. Callers
 * must fall back to the default definition in that case (see
 * useProjectStore.ts); this function never throws and never returns a
 * value that failed the structural check.
 */
export function loadDefinition(): JewelryDefinition | null {
  let raw: string | null
  try {
    raw = window.localStorage.getItem(STORAGE_KEY)
  } catch {
    // localStorage can be unavailable entirely (private browsing, disabled
    // storage) — treat exactly like "nothing saved".
    return null
  }
  if (!raw) return null

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    // Corrupted JSON must never crash the app.
    return null
  }

  if (!isValidJewelryDefinition(parsed)) {
    // Obsolete schema version or structurally invalid data — reject rather
    // than risk feeding a malformed object into the rest of the app.
    return null
  }

  return parsed
}

export function saveDefinition(definition: JewelryDefinition): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(definition))
  } catch {
    // localStorage can be unavailable (private browsing, quota) — persistence
    // is a convenience, not a correctness requirement, so fail silently.
  }
}

export function clearDefinition(): void {
  try {
    window.localStorage.removeItem(STORAGE_KEY)
  } catch {
    // see saveDefinition
  }
}
