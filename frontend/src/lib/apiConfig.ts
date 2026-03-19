// Centralised backend base-URL configuration for all API routes.
// Read once at module load so every route uses a consistent value.

export const GRID_API_BASE =
  process.env.GRID_API_BASE ??
  process.env.NEXT_PUBLIC_GRID_API_BASE ??
  "http://localhost:7001";

export const CONSCIOUSNESS_API_BASE =
  process.env.CONSCIOUSNESS_API_BASE ?? "http://localhost:8001";

export const OLLAMA_HOST =
  process.env.OLLAMA_HOST ?? "http://localhost:11434";
