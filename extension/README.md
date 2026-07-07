# Kilimanjaro New Tab: Daily Summit & Focus Climb

Chrome (Manifest V3) new-tab extension for Go Kilimanjaro Treks. Bundled
original photography, live Moshi weather, Swahili word of the day, and a
pomodoro "Climb Mode" that ascends the Machame Route session by session.

No servers, no accounts, no tracking. Only network call: open-meteo weather.

## Files

- `manifest.json` — MV3, new-tab override, `storage` permission only
- `newtab.html/css/js` — the page; works in a plain browser too (localStorage fallback)
- `daily.js` + `photos/` + `icons/` — GENERATED, do not hand-edit
- Regenerate assets + the store zip: `python scripts/build_extension_assets.py`
  (run from the repo root; zip lands at `gokilimanjarotreks-newtab.zip`)

## Test locally

chrome://extensions → enable Developer mode → "Load unpacked" → select this
`extension/` folder → open a new tab.

## Publish checklist (Clinton)

1. **Developer account**: https://chrome.google.com/webstore/devconsole —
   sign in (use the client's Google account if Nelson should own it),
   pay the one-time $5 registration fee.
2. **New item** → upload `gokilimanjarotreks-newtab.zip`.
3. **Store listing**:
   - Category: Productivity → Tools (or Lifestyle → Well-being)
   - Language: English
   - Description: use the copy below.
   - Screenshots (1280x800): open the new tab locally, screenshot 3-5 states
     (daily photo, Climb Mode open, summit certificate).
   - Small promo tile 440x280 (crop a photo + logo).
4. **Privacy tab**: single purpose = "Replaces the new tab with Kilimanjaro
   photography, Moshi weather, and a focus timer." Permission justification:
   `storage` = "Saves the user's climb progress and settings locally."
   Data usage: "This item does not collect user data." Remote code: none.
5. **Verified publisher badge**: in the dev console, associate the publisher
   with gokilimanjarotreks.com (the domain must be verified in Google Search
   Console, which it already is).
6. Submit for review (typically 1-3 days).
7. When live: paste the store URL into `STORE_URL` in
   `src/pages/new-tab.astro` and push, so the landing page's install buttons
   go live.

## Store listing copy

**Name:** Kilimanjaro New Tab: Daily Summit & Focus Climb

**Summary (132 chars max):**
Original Kilimanjaro & Serengeti photography, live Moshi weather, a Swahili
word a day, and a focus timer that climbs to Uhuru Peak.

**Description:**
Open a tab, see the summit.

Every new tab brings one of 24 original photographs from real Kilimanjaro
climbs and Serengeti safaris: sunrise over Mawenzi, glacier walls above the
clouds, lions in the Ngorongoro Crater, elephants at last light. No stock
photos. These were shot on the mountain by Go Kilimanjaro Treks, a guiding
team based in Moshi, Tanzania.

WHAT YOU GET
- A new original photo each day (plus a shuffle button)
- Live time and weather in Moshi, the town where every climb begins
- A Swahili word or Kilimanjaro fact every day
- Climb Mode: a focus timer that turns deep work into an expedition. Every
  completed 25 or 50 minute session moves you up the Machame Route, camp by
  camp, to Uhuru Peak at 5,895 m. Summit and download your certificate.

PRIVATE BY DESIGN
No account. No ads. No analytics. No data collection. Photos are bundled in
the extension, progress stays in your browser, and the only network request
is a weather check from the free open-meteo service.

Made by the team at gokilimanjarotreks.com. If the daily view gets you
dreaming, the real mountain is waiting.

## Distribution plan (where installs actually come from)

- Banner/link on gokilimanjarotreks.com (landing page: /new-tab)
- Blog post announcing it
- Reddit r/Kilimanjaro, r/hiking, r/chrome_extensions (genuine, not spammy)
- Kilimanjaro/trekking Facebook groups Nelson is in
- Nelson's past climbers via the newsletter/WhatsApp: "take the mountain home"
- Pitch to hiking newsletters and "beautiful new tab" roundups
