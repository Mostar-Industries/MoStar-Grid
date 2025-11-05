/**
 * Environment Configuration
 * 
 * Dev:  Uses Vite proxy (/api, /ws)
 * Prod: Uses public backend URLs from env vars
 */

export const API_BASE =
  (import.meta.env.VITE_API_URL as string | undefined) || '/api'; // dev uses Vite proxy

export const WS_BASE =
  (import.meta.env.VITE_WS_URL as string | undefined) || '/ws';   // dev uses Vite WS proxy

export const isProd = import.meta.env.PROD;

export const isDev = import.meta.env.DEV;

// For debugging
if (isDev) {
  console.log('[env] API_BASE:', API_BASE);
  console.log('[env] WS_BASE:', WS_BASE);
  console.log('[env] Mode:', import.meta.env.MODE);
}
