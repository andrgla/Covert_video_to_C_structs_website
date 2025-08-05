import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // This proxy tells Vite to forward API requests to your Python backend
    proxy: {
      '/upload': 'http://127.0.0.1:5000',
      '/api': 'http://127.0.0.1:5000',
    }
  }
})