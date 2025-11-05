import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    // Load .env files from the project root
    const env = loadEnv(mode, process.cwd(), '');
    return {
      server: {
        port: 5173, // Aligned with builder-status.ps1 script
        proxy: {
          '/api': {
            target: 'http://127.0.0.1:8000', // Proxy to local Python API
            changeOrigin: true,
            secure: false,
          },
        },
      },
      plugins: [react()],
      define: {
        // Expose API key to the frontend, preferring API_KEY but falling back
        'process.env.API_KEY': JSON.stringify(env.API_KEY || env.GEMINI_API_KEY),
      },
    };
});
