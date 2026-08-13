# Update changelog — 2026-08-13

Execution log for `update-plan-2026-08-13.md`. Local commits only, no deploy.

## Phase 1 — Performance
- Added `scripts/optimize-images.mjs` (sharp, already in the dependency tree via Astro). Generated missing `.webp` variants for `route-*`, `page-hero-*`, `dest-*`, `daytrip-*`, `nelson*`, `testimonials-bg`, `hero*` (the plan said these webp files existed; they did not, only the hero and gallery had pairs, so they were generated).
- Recompressed every original above 250 KB to max 1600 px wide JPEG q80 and refreshed its webp pair. `public/images` went from 111 MB to 81 MB (gallery originals were the bulk).
- Generated 600 px gallery thumbnails (`*-thumb.webp` + `*-thumb.jpg`); grid `<img>`/`<source>` now use thumbs, lightbox `href` keeps originals. Verified all 85 slugs have all 4 variants.
- Added `scripts/wire-webp.mjs` codemod: wrapped 158 `<img src="/images/*.jpg">` in `<picture>` with a webp `<source>` (only where the webp file exists and the img was not already in a picture).
- index.astro hero: fixed relative `srcset` paths to root-absolute and added webp sources for mobile/tablet/desktop; fixed relative `poster` path on the video.
- Verified: build passes (70 pages), form actions and all `<a href>` values byte-identical to baseline, all 144 referenced webp paths exist on disk.
- Note: impeccable hook flagged gallery `#lb-img` empty `src`; intentional, populated by the lightbox script (review item 15).
