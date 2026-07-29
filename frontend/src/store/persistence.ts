import type { JewelryDefinition } from '@shared/types/jewelry-definition'

const STORAGE_KEY = 'jewelmind:project-definition:v1'

export function loadDefinition(): JewelryDefinition | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as JewelryDefinition
  } catch {
    return null
  }
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
