import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

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
  integrations: [
    sitemap({
      // The build uses format:'file' so Astro emits about.html, etc., and the
      // sitemap would list .html URLs. Cloudflare serves (and canonicalises) the
      // clean URL, so rewrite every entry to the clean form to match the
      // <link rel="canonical"> tags exactly.
      serialize(item) {
        item.url = item.url
          .replace(/index\.html$/, '')
          .replace(/\.html$/, '');
        return item;
      },
    }),
  ],
});
