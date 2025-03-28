import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import tailwind from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwind()
  ],
  build: {
    // Change output directory to avoid permission issues
    outDir: '/var/www/platepal',
    emptyOutDir: true,
    // Ensure JSON files are processed
    assetsInlineLimit: 0,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
    extensions: ['.js', '.json', '.vue']
  },
  // Explicitly tell Vite to process JSON files
  assetsInclude: ['**/*.json'],
})
