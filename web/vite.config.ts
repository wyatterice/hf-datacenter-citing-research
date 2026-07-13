import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// The production build is served from a GitHub Pages project subpath
// (https://<owner>.github.io/hf-datacenter-citing-research/), so built assets
// and the scores.json fetch must resolve under that prefix. Dev and the
// Playwright suite keep the root base so local URLs stay at /.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/hf-datacenter-citing-research/' : '/',
  plugins: [react()],
}))
