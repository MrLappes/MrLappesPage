import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import tailwind from '@tailwindcss/vite'
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwind(),
    VueI18nPlugin({
      include: resolve(__dirname, './src/locales/**/*.json'),
    }),
  ],
  build: {
    outDir: '/var/www/platepal',
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
    extensions: ['.js', '.json', '.vue']
  },
  json: {
    stringify: false
  },
  css: {
    devSourcemap: true,
  },
  assetsInclude: ['**/*.json', '**/*.mp4', '**/*.svg', '**/*.png'],
  server: {
    hmr: true,
    proxy: {
      '/sm-api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sm-api/, '/api')
      },
      '/sm-ws': {
        target: 'ws://127.0.0.1:8001',
        ws: true,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sm-ws/, '/ws')
      }
    }
  }
})
