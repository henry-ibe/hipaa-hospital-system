import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/hipaa-hospital-system/',  // GitHub Pages needs this!
  server: {
    port: 3001,
    host: '0.0.0.0',
    strictPort: true
  }
})
