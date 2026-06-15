# gokilimanjarotreks.com (Astro rebuild)

The Astro rebuild of the live HTML site. This is the **staging repo** —
connect it to a fresh Cloudflare project, test on a `*.workers.dev` URL,
then point the domain at it when verified.

## What's inside

```
src/
├── data/
│   ├── site.ts         ← single source for phone, email, address, social
│   └── nav.ts          ← single source for nav and footer link structure
├── layouts/
│   └── BaseLayout.astro ← <head>, header, footer, scripts, JSON-LD wrap
├── components/
│   ├── Nav.astro        ← desktop + mobile + Plan Your Trip dropdown
│   └── Footer.astro
├── styles/
│   └── global.css       ← all CSS that used to be inline on 35 HTML pages
└── pages/
    ├── *.astro          ← 22 top-level pages
    ├── blog/            ← 16 blog posts (14 migrated + 2 new safari)
    ├── safaris/         ← 11 new safari itineraries + index
    └── corporate-climbs.astro ← new B2B page
```

51 pages built in ~6 seconds.

## Local dev

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # outputs to ./dist/
npm run preview      # serves ./dist/ to confirm the prod build works
```

## Cloudflare deploy (one-time, the staging cutover)

1. Cloudflare dashboard → Workers & Pages → **Create application** → **Pages** → **Connect to Git**
2. Pick this repo (`cwasylishen/gokilimanjarotreks-astro`)
3. **Build settings:**
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Root directory: (leave empty)
4. Save and deploy
5. CF gives you a `gokilimanjarotreks-astro.pages.dev` URL → test there

Once everything looks right, point `gokilimanjarotreks.com` at this new project
(Custom domains tab) and the old `gokilimanjarotreks-com` project can be
archived.

## Why this exists

The live site grew to 35 HTML files with the `<style>`, header, footer,
and nav duplicated on every single one. Updating the nav meant editing
35 files. Astro fixes that: edit `src/data/nav.ts` once, every page
rerenders.
