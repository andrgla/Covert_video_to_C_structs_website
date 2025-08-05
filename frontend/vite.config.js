import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // This proxy tells Vite to forward API requests to your Python backend
    proxy: {
      // For the main file upload
      '/upload': 'http://127.0.0.1:5000',
      
      // For all API calls (like listing videos and the new preview)
      '/api': 'http://127.0.0.1:5000',
      
      // For serving the generated video files
      '/video': 'http://127.0.0.1:5000',
    }
  }
})