import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    mainFields: [], 
  },
  build: {
    commonjsOptions: {
      transformMixedEsModules: true,
    },
  },
  // Recharts sorunu için özel yama
  optimizeDeps: {
    include: ['recharts'],
  },
})