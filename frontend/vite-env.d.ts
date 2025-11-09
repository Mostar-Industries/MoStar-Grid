/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_NEO4J_URI: string
  readonly VITE_NEO4J_USER: string
  readonly VITE_NEO4J_PASSWORD: string
  readonly VITE_NEO4J_DATABASE: string
  readonly VITE_GEMINI_API_KEY: string
  readonly VITE_GOOGLE_MAPS_API_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
