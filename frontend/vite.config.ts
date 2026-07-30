/// <reference types="vitest/config" />
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const projectRoot = fileURLToPath(new URL('.', import.meta.url))
const sharedRoot = fileURLToPath(new URL('../shared', import.meta.url))

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': sharedRoot,
    },
  },
  server: {
    port: 3000,
    host: true,
    fs: {
      // Vite's dev server otherwise refuses to serve files outside its
      // detected project root. Locally that root auto-expands to the git
      // repository root (so ../shared already works), but inside the
      // Docker image there is no .git and no shared package.json
      // workspace, so /shared (a sibling of /app, see frontend/Dockerfile)
      // must be explicitly allow-listed here in both environments.
      allow: [projectRoot, sharedRoot],
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
})
