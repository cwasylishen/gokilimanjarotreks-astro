# Go Kilimanjaro Treks — Update Plan
**Date:** 2026-08-13 · Companion to `impeccable-review-2026-08-13.md`
**Hard rule for every phase:** no functionality changes. Forms, scripts, navigation targets, and page URLs stay byte-for-byte in behavior. Everything below is markup, CSS, image files, and copy.

## Phase 1 — Performance (highest ROI, lowest risk)
1. Wire existing WebP files into `<picture>` sources: hero on `src/pages/index.astro:19-31` (also fix the relative `srcset`/`poster` paths to root-absolute), then `route-*.jpg` blocks on `index.astro` and `kilimanjaro.astro`, and the shared `page-hero-*` images on all interior pages. No new URLs required — the `.webp` files already exist in `public/images/`.
2. Generate thumbnail variants for the gallery grid (`public/images/gallery/*-thumb.webp`, ~600 px wide) and point only the grid `<img src>` in `src/pages/gallery.astro:59` at them; lightbox `href` keeps the originals. Cuts the gallery page weight by an order of magnitude.
3. Audit `public/images` (111 MB): recompress any original above ~250 KB that is displayed smaller than 1600 px.

## Phase 2 — CSS consolidation (invisible refactor)
1. Merge the two `:root` blocks in `src/styles/global.css` (lines 10 and 183) into one, keeping `--forest`.
2. Dedupe repeated rules, keeping the currently-winning declaration: `.page-hero p` (45/184/401), `.cta-section` (112/217), `.reveal` (141/774), `.callout` (250/373), `.dest-faq summary` (274/386), `.section-title` (57/404).
3. Move the ~600 inline `style=` attributes into named utility/section classes with identical computed values, starting with `index.astro` (video section, safari teaser, best-time box) and `kilimanjaro.astro` (route images, table cells). Verify with a before/after screenshot diff per page.

## Phase 3 — Craft & cohesion
1. Replace text-letter/emoji social icons in `src/components/Footer.astro` with inline SVGs (Facebook, Instagram, WhatsApp) — same anchors, hrefs, aria-labels. Swap 📞/✉️ in contact rows for small SVGs.
2. Replace emoji card icons on `index.astro:86-98` and `210-225` with the site's existing SVG icon style (gold stroke/fill). Priority: ✂️ on "Fully Tailored Packages".
3. Retire the gold side-tab `border-left` card pattern (`index.astro:464-476`, `kilimanjaro.astro:408,566`; harmonize `cred-item`, `week-card`, callouts in `global.css`) into a quieter treatment: hairline border + gold text accent.
4. Activate the reveal animation: add `.reveal{opacity:0;transform:translateY(14px)}` inside `@media(prefers-reduced-motion:no-preference)` so the existing sweep script (already shipping in `BaseLayout.astro`) produces its intended effect — or delete the classes if a static feel is preferred.

## Phase 4 — Accessibility
1. Remove `role="menu"`/`role="menuitem"` from the Plan Your Trip dropdown in `src/components/Nav.astro` (keep `aria-haspopup`/`aria-expanded`; handlers untouched).
2. Raise footer fine-print link contrast from `.35`/`.4` alpha to ≈`.62` (`Footer.astro`, `global.css:132`); check `.testi-meta` at `.5`.
3. Popup markup-only fixes on `index.astro`: `aria-live="polite"` on `#pkmd-success` and `#pkmd-error`, clearer close-button label. (A focus trap would alter script behavior — deferred until functionality changes are permitted.)
4. Confirm the gallery lightbox script sets `alt` on `#lb-img` from the caption; if not, that one-line addition is within the a11y remit.

## Phase 5 — Copy polish (with Nelson's sign-off)
1. `index.astro:419` FAQ: recast the nested "pole pole (slowly, slowly)" parenthetical.
2. `index.astro:70` "100% Safety Record": verify with Nelson and either anchor it in a checkable fact or soften to "Safety-First, Every Climb".
3. Consider a more ownable hero line than "Conquer Kilimanjaro." — the brand's strength is Nelson's local, humble authority. Keep if he prefers the current line.

## Phase 6 — Photo placement map (incoming Nelson batch)
Each subject below has ready-made slots; drop-in replacements keep existing dimensions, `loading`, and alt patterns (write new alts describing the actual scene).

| Incoming photo subject | Placement |
|---|---|
| **Marangu route** (trail, huts, forest) | Replace stock-feeling `route-marangu.jpg` used at `index.astro:147` and `kilimanjaro.astro:274`; add best frame to gallery (Routes category); one shot as a fresh hero for `compare-routes.astro:15` (currently the shared Kilimanjaro hero) |
| **Rongai route** (northern approach, savanna views) | Replace `route-rongai.jpg` at `index.astro:159` and `kilimanjaro.astro:327`; gallery (Routes); candidate hero for `choose-operator.astro:15` to break the shared-hero repetition |
| **Mawenzi peak** | Gallery hero-tier addition; supporting image inside the "What Summit Night Looks Like" section (`kilimanjaro.astro:545`); strong candidate for a distinct `about.astro:15` or `safety.astro:15` page hero; already echoed in `new-tab.astro` — a fresh Mawenzi frame keeps that surface alive |
| **Crater lake at Mawenzi Turn Hut (4,330 m)** | The Rongai route detail section on `kilimanjaro.astro` (Mawenzi Turn Hut is a Rongai landmark — a photo no template competitor has); gallery with the altitude in the caption; consider a figure in `travel-guide.astro` acclimatization content |
| **Kibo Hut saddle views** | Marangu route detail (`kilimanjaro.astro:243-294` — Kibo Hut is the Marangu summit base); `kosovo-camp.astro` (currently leans on `kibo-scree-approach.jpg`); fresh hero for `hygiene.astro:15` or `safety.astro:15`; gallery (Summit category) |
| **Tulivu retreat, Moshi (pool / briefing point)** | The "Pre-Trek Briefing in Moshi or Arusha" section (`kilimanjaro.astro:506`) — currently text-heavy, this photo makes the promise tangible; contact page sidebar or hero (`contact.astro`) to ground "based in Moshi"; `travel-guide.astro` accommodation section; about page "life off the mountain" slot |

Sequencing note: run Phase 6 alongside Phase 1 so every new photo lands as an optimized JPEG+WebP pair (match the existing `public/images/gallery/` convention) with mobile/tablet crops for any hero use.

## Verification per phase
Before/after screenshot comparison at 390 px and 1440 px on: home, kilimanjaro, contact, gallery, one blog post. Confirm live output with `curl` (status, HTML size, canonical) after each deploy. No phase ships if any form submit, nav target, or script behavior differs.
