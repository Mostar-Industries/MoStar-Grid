import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 5173, // Aligned with builder-status.ps1 script
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000', // Proxy to local Python API
          changeOrigin: true,
          secure: false,
        },
        '/ws': {
          target: 'ws://127.0.0.1:8000', // WebSocket proxy
          ws: true,
        },
      },
    },
    plugins: [react()],
});
