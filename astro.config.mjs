import { defineConfig } from 'astro/config';

// Static site build that targets Cloudflare Workers Static Assets.
// Output goes to ./dist/ which the parent repo's wrangler config will deploy.
export default defineConfig({
  site: 'https://gokilimanjarotreks.com',
  output: 'static',
  trailingSlash: 'ignore',
  build: {
    format: 'file',
    inlineStylesheets: 'auto',
  },
  compressHTML: true,
  prefetch: {
    prefetchAll: false,
    defaultStrategy: 'hover',
  },
});
