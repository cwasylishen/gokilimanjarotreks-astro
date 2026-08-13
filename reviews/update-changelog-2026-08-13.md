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

## Phase 2 — CSS consolidation
- Merged the four `:root` blocks in `global.css` into one (kept `--forest` and `--gold-dk`).
- Deduped repeated rules keeping the cascade winner: `.page-hero p` (1 def left, the .9-alpha/text-shadow winner), `.cta-section` (merged winner properties incl. `position:relative;overflow:hidden`, restored the sole `.cta-section h2`/`h2 em` rules that lived in a deleted block), `.reveal`, `.callout`, `.dest-faq summary`, `.section-title`.
- Extracted the named inline-style hotspots into classes with identical computed values: index video feature rows (`.vf-*`), safari teaser (`.safari-list`, `.combo-panel`, `.combo-card`, `.combo-title/.combo-sub`), best-time box (`.best-time-box`, `.bt-*`); kilimanjaro route detail images (`.route-img`) and the summit-night table (`.snt` family). Remaining inline styles (index 28, kilimanjaro 150 of the original ~600 sitewide) left for a later pass; partial by design.
- Verified: build passes, form actions identical, only diff vs baseline href set is the hashed CSS filename.

## Phase 3 — Craft & cohesion
- Footer: replaced the "f" / "in" / 💬 social anchors with inline SVG glyphs (Facebook, Instagram, WhatsApp); same hrefs, aria-labels, targets. Contact rows 📞/✉️ swapped for small stroke SVGs.
- index.astro: replaced the 8 emoji card icons (feature list 🧭👥❤️📋, why-us 🎯🪖🤝✂️) with inline SVGs in the site's existing icon style (amber stroke on light, gold stroke on dark). The scissors on "Fully Tailored Packages" is now a sliders/adjust icon.
- Retired the gold side-tab `border-left` pattern into hairline borders with matching accent tint: `.cred-item`, `.week-card`, `.callout` (+ blue/red/green variants), `.combo-card`, and the two inline instances on kilimanjaro.astro (flagship callout, summit-night safety box).
- Activated the reveal animation: `html.js .reveal{opacity:0;transform:translateY(14px)}` gated behind `@media(prefers-reduced-motion:no-preference)`; the `js` class is added by the existing reveal script itself, so no-JS users always see content. One added line in BaseLayout (allowed as the intended-behavior fix).
- Verified: build passes, form actions identical, non-hashed hrefs identical.

## Phase 4 — Accessibility
- Nav.astro: removed `role="menu"`/`role="menuitem"` from the Plan Your Trip dropdown; kept `aria-haspopup`/`aria-expanded` and all handlers.
- Contrast: footer fine-print links `.35` -> `.62` alpha, `.footer-bottom p` `.4` -> `.62`, `.testi-meta` `.5`/`.55` -> `.62`.
- Packing-list popup: `aria-live="polite"` on `#pkmd-success` and `#pkmd-error`; close button label is now "Close packing list offer". Focus trap deferred (would change script behavior).
- Gallery lightbox: confirmed the script already sets `lbImg.alt = p.caption` on open; no change needed.
- Verified: build passes, form actions and non-hashed hrefs identical, `role="menu"` gone from output.

## Phase 5 — Copy polish
- FAQ (page copy + FAQ JSON-LD kept in sync): nested parenthetical recast to `(pole pole, Swahili for "slowly, slowly")`. JSON-LD re-validated after the change.
- "100% Safety Record" softened to "Safety / First, Every Climb" on index, partners, and charity-climbs stat bands; about page Nelson stat "Safety Record: 100% Safe" -> "Approach: Safety First". Nelson was not reachable in this run, so the plan's soft fallback was used; if he can anchor a checkable fact (for example zero client evacuations), swap it back in.
- Hero line "Conquer Kilimanjaro." kept unchanged per the plan (owner's preference pending).
- Verified: build passes, no em dashes or AI-tell phrases in touched pages, form actions and non-hashed hrefs identical.

## Phase 6 — Photo placement (SKIPPED)
- Pending: Nelson's photo batch has not arrived. The placement map in the update plan is untouched and still current.

## Not done / notes
- Screenshot before/after diffs and live-site curl checks were not run (no deploy in this task; local build verification only).
- ~430 inline style attributes remain outside the named hotspots; candidates for a later invisible refactor pass.
