# Go Kilimanjaro Treks — Design & UX Review
**Date:** 2026-08-13 · **Scope:** src/ (pages, layouts, components, styles), public/, astro.config.mjs, live site (gokilimanjarotreks.com)
**Constraint honored:** every recommendation is visual, typographic, copy, accessibility, or performance only. No form, script, URL, or navigation behavior changes.

## Verdict: 28 / 40

| Dimension | Score /10 | Summary |
|---|---|---|
| Craft | 7 | Strong foundations (self-hosted fonts, focus-visible styles, semantic sections) undercut by ~600 inline `style=` attributes, an inert reveal animation, and text-letter social icons |
| Hierarchy | 8 | Clear Persuade-mode flow on home and Kilimanjaro pages: hero → proof → routes → trust → FAQ → CTA. Emoji icons and inline-styled sub-blocks dilute otherwise disciplined section rhythm |
| Cohesion | 6 | global.css carries duplicated `:root` blocks and repeated rule definitions; page-level one-off inline styles drift from the token system; six pages share the same hero photo |
| Accessibility | 7 | Good bones (aria-expanded on toggles, aria-hidden decorative images, visible focus rings) with fixable gaps: menu-role misuse, popup focus behavior, low-contrast footer links |

The site is a competent, warm, conversion-focused build with a real identity (navy/gold/amber, Cormorant + DM Sans, Nelson-first storytelling). What separates it from a top-tier operator site is finish: consolidation of styles, an icon system, image performance, and photographic variety — exactly what the incoming Nelson photo batch enables.

---

## Findings (ordered by impact)

### 1. Hero and route images ship as heavy JPEGs while WebP versions already exist — performance
- `src/pages/index.astro:19-31` — the `<picture>` element serves `hero-uhuru.jpg` (180 KB) and JPEG srcset variants, yet `public/images/hero-uhuru.webp` (98 KB, −46%) and `hero-uhuru-mobile.webp`/`hero-uhuru-tablet.webp` sit unused in `public/images/`.
- Same pattern across `route-*.jpg`, `page-hero-*.jpg`, and `dest-*.jpg` on `kilimanjaro.astro:161,222,274,327,379,437`, `index.astro:123-183`. The gallery already pairs every `.jpg` with a `.webp` (`public/images/gallery/`) — the pattern exists, it just is not wired into `<picture>`/`<source type="image/webp">` on the main pages.
- Adding a WebP `<source>` is markup-only; URLs, alts, and layout are untouched. This is the single largest LCP win available.

### 2. Gallery thumbnails load full-resolution originals — performance
- `src/pages/gallery.astro:56-59` — each grid card's `<img>` uses the same `/images/gallery/${p.slug}` file that the lightbox opens. `public/images/` totals 111 MB; the grid downloads multi-hundred-KB originals to render ~400 px thumbnails.
- Fix without touching behavior: generate resized thumbnail files (e.g. `-thumb.webp`) and point only the grid `<img src>` at them; the anchor `href` (lightbox target) keeps the original. Filtering and lightbox scripts are untouched.

### 3. ~600 inline `style=` attributes across pages — cohesion/craft
- `grep -c 'style=' src/pages/*.astro` → 599. Worst offenders: `index.astro` (video section rows 286-305, safari teaser cards 461-480, best-time box 265-272), `kilimanjaro.astro` (comparison table cells, route images at lines 161-437).
- Consequences: token drift (hard-coded `#fbbf24`, `rgba(255,255,255,.6)` duplicating `--gold`/`--muted`), inconsistent spacing between siblings, and heavier HTML. Consolidate into classes in `global.css` with identical computed styles — a pure refactor, zero visual or functional change, that makes every later polish pass cheap.

### 4. The scroll-reveal animation is inert — craft (dead pattern)
- `src/styles/global.css:141-142` defines `.reveal{transition:opacity .35s ease,transform .35s ease}` and `.reveal.visible{opacity:1;transform:none}`, but no rule ever sets the initial hidden state (`opacity:0; transform:translateY(...)`).
- `src/layouts/BaseLayout.astro:167-181` runs a scroll sweep adding `.visible`, so the JS executes on every page for no visible effect. Two clean resolutions, both visual-only: (a) add the initial state gated behind `@media(prefers-reduced-motion:no-preference)` so the reveal actually plays, or (b) delete the `.reveal` CSS rules and classes as dead weight. (a) is recommended — the site's calm 350 ms ease matches the brand.

### 5. Footer social icons are literal text letters — craft/brand
- `src/components/Footer.astro` (social-links block): Facebook renders as the letter "f", Instagram as "in" — which reads as **LinkedIn** — and WhatsApp as the 💬 emoji. Contact rows use 📞/✉️ emoji.
- The WhatsApp float directly above them uses a proper SVG. Swap the three social anchors' contents for inline SVG glyphs (same `href`, same `aria-label`); swap the emoji in contact rows for small SVGs or drop them. Pure markup-inside-anchor change.

### 6. Emoji as a card icon system — cohesion
- `src/pages/index.astro:86-98` (feature list: 🧭 👥 ❤️ 📋) and `index.astro:210-225` (why-us: 🎯 🪖 🤝 ✂️ — scissors for "Fully Tailored Packages" reads as literal scissors). Meanwhile the video section (`index.astro:288-301`) and charity pages use consistent SVG icons.
- Emoji render differently per OS and clash with the serif/gold identity. Replace with the site's existing SVG icon style (stroke or gold-fill). Same grid, same copy.

### 7. Gold side-tab accent borders on cards — visual tell
- `src/pages/index.astro:464,468,472,476` (combo-trip cards), `src/pages/kilimanjaro.astro:408,566` — `border-left:3-4px solid var(--gold)` tab cards, a generic template pattern flagged by mechanical scan. Replace with a quieter treatment (hairline full border + gold text accent, or a small gold marker glyph) to keep the section feeling designed rather than generated. `cred-item`/`week-card`/`callout` in `global.css:190,396,250` share the pattern; harmonize once.

### 8. One hero photograph carries six different pages — hierarchy/brand
- `page-hero-kilimanjaro.jpg` is the hero for `about.astro:15`, `safety.astro:15`, `compare-routes.astro:15`, `choose-operator.astro:15`, `hygiene.astro:15`, and `kilimanjaro.astro:16`. A returning visitor sees the same image everywhere; page identity blurs.
- The incoming Nelson batch solves this directly — see the photo placement map in the update plan.

### 9. Duplicated and conflicting rules in global.css — cohesion
- `src/styles/global.css:10` vs `:183` — `:root` is declared twice; the second drops `--forest`, and any future edit to one block silently diverges from the other.
- Repeated definitions: `.page-hero p` (lines 45, 184, 401 — three different `max-width`s: 620/620/580), `.cta-section` (112, 217), `.reveal` (141, 774), `.callout` (250, 373), `.dest-faq summary` (274, 386), `.section-title` (57 vs 404 with different clamp). Later declarations win unpredictably per page order. Dedupe to one source of truth; computed output stays identical if the surviving rule matches what currently wins.

### 10. Navigation dropdown misuses `role="menu"` — accessibility
- `src/components/Nav.astro` — the "Plan Your Trip" dropdown wraps plain links in `role="menu"`/`role="menuitem"`. ARIA menus imply arrow-key navigation the widget does not implement, so screen readers announce a broken menu. Removing the two role attributes (keeping `aria-haspopup`/`aria-expanded` on the button) makes it an honest disclosure of links — attribute-only change, all click handlers untouched.

### 11. Packing-list popup: focus and announcement gaps — accessibility
- `src/pages/index.astro:508-547, 563-571` — the dialog sets `aria-modal="true"` and steals focus to the name input on open (including the unprompted 25-second open), but there is no focus containment and the success state (`pkmd-success`) is not announced. Markup-only improvements: `aria-live="polite"` on the success block and the error box (`pkmd-error`), and a more honest label than `aria-label="Close"` alone on ✕ ("Close packing list offer"). Full focus-trap logic would touch script behavior, so it is noted as out of scope under the current constraint.

### 12. Low-contrast fine print — accessibility
- `src/components/Footer.astro` — privacy/credits/attribution links at `rgba(255,255,255,.35)` on `#060e1c` fall well below WCAG AA (≈2.1:1); `footer-bottom p` at `.4` alpha similar (`global.css:132`). Raise to ≈`.62` alpha; visual weight barely changes, compliance is met. Also check `.testi-meta` (`global.css:216`, `.5` alpha on dark).

### 13. Copy polish opportunities (no claims added)
- `index.astro:419` — "pole pole (slowly, slowly)" sits inside another parenthetical; recast as: pacing the climb *pole pole* — "slowly, slowly" in Swahili.
- `index.astro:70` — "100% Safety Record" is a strong absolute next to verifiable stats; consider "Safety-First Record" or anchor it ("zero client evacuations" only if true — verify with Nelson before changing).
- `index.astro:49` — "Conquer Kilimanjaro." is category-generic and slightly at odds with the humble, safety-first voice everywhere else; "Climb Kilimanjaro with the man who grew up on it" territory is more ownable. Copy-level only; keep if Nelson prefers it.
- `contact.astro` autoresponse and form copy are excellent — personal, concrete, honest. Keep.

### 14. Fragile relative asset paths on the home page — craft
- `src/pages/index.astro:20-21` (`srcset="images/hero-uhuru-mobile.jpg"`) and `:312` (`poster="images/hero-uhuru.jpg"`) are relative, unlike every other page's root-absolute `/images/...`. They work today only because home lives at `/`. Normalize to leading-slash paths — byte-level output change only at the root URL, zero behavior change.

### 15. Minor
- `gallery.astro:86` — lightbox `<img id="lb-img" src="" alt="">`: flagged by mechanical scan; it is populated by script (verified), so not broken, but confirm the script also sets `alt` from the caption so the lightbox is not a silent image for screen readers.
- `BaseLayout.astro:55-56` preloads only 2 of 6 fonts — correct choice; consider adding the 700-weight DM Sans if CTAs paint late (measure first).
- Header is 100 px tall with an 88 px logo (`global.css:20-23`); generous, and `nav-mobile` is pinned to `top:100px` (`:35`) — if header height is ever tuned, both must move together (note, not a defect).
- Live checks: home 200/61 KB HTML, clean-URL canonicals match sitemap rewrite in `astro.config.mjs` — build output is healthy.

## Strengths worth protecting
- Self-hosted subset fonts with `font-display:swap` and preload (`global.css:4-9`, `BaseLayout.astro:55-56`).
- Real, specific proof everywhere: named testimonials, route-by-route success bars, transparent "From $" pricing on `kilimanjaro.astro`.
- Decorative hero images correctly `alt="" aria-hidden="true"`; FAQ buttons manage `aria-expanded`; strong gold `:focus-visible` ring (`global.css:39`).
- The Moshi live time/weather widget (`index.astro:34-46`) is a genuinely distinctive touch — keep it.
