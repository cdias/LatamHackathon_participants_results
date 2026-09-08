import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// VITE_API_BASE define o backend em produção (EC2). Em dev, proxy para :8000.
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
