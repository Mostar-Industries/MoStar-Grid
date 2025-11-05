import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
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
});
