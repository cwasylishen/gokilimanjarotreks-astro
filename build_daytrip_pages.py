"""Generate a detail page for every day trip from the hub card content, and
rewrite the hub so each card links out to its detail page (dedupes the inline
<details> accordion). Single source of truth = the cards on daytrips.astro.

Run from the astro repo root:  python build_daytrip_pages.py
"""
import json
import re
from pathlib import Path

HUB = Path("src/pages/daytrips.astro")
OUT = Path("src/pages/daytrips")
BASE = "https://gokilimanjarotreks.com"

# card id on the hub  ->  detail-page slug (existing slugs preserved)
SLUGS = {
    "tarangire-safari-tour": "tarangire",
    "materuni-waterfall-and-coffee-farm-tour": "materuni-waterfall-coffee",
    "arusha-safari": "arusha-national-park",
    "ol-doinyo-lengai": "ol-doinyo-lengai",
    "kilimanjaro-helicopter-tour": "kilimanjaro-helicopter-tour",
    "lake-chala": "lake-chala",
    "ndarakwai-ranch": "ndarakwai-ranch",
    "chemka-hot-springs": "chemka-hot-springs",
    "mount-kilimanjaro-day-hikes": "kilimanjaro-day-hike",
    "horseback-riding": "horseback-riding",
    "arusha-shopping-tour": "arusha-shopping-tour",
}

# Short SEO title + meta description per slug (kept tight, keyword-front-loaded)
META = {
    "tarangire": ("Tarangire Safari Day Trip", "A full-day game drive in Tarangire National Park from Arusha, famous for its giant elephant herds and ancient baobab trees."),
    "materuni-waterfall-coffee": ("Materuni Waterfall & Coffee Tour", "A day trip from Moshi to the 80-metre Materuni Waterfall and a hands-on Chagga coffee experience on the lower slopes of Kilimanjaro."),
    "arusha-national-park": ("Arusha National Park Day Trip", "A day safari in Arusha National Park: walking safari with a ranger, the Momella Lakes, Ngurdoto Crater, and views of Meru and Kilimanjaro."),
    "ol-doinyo-lengai": ("Ol Doinyo Lengai Volcano Trek", "A demanding night climb of Ol Doinyo Lengai, the Maasai 'Mountain of God' and the world's only active carbonatite volcano, above Lake Natron."),
    "kilimanjaro-helicopter-tour": ("Kilimanjaro Helicopter Tour", "A scenic helicopter flight over Mount Kilimanjaro's summit, glaciers and craters, with hotel transfers from Arusha. See the Roof of Africa from the air."),
    "lake-chala": ("Lake Chala Day Trip", "A day trip to Lake Chala, a spring-fed volcanic crater lake on the Tanzania and Kenya border, for hiking, birdwatching and quiet swimming."),
    "ndarakwai-ranch": ("Ndarakwai Ranch Day Trip", "A walking safari on the private 11,000-acre Ndarakwai conservation ranch on the western slopes of Kilimanjaro, supporting Maasai community conservation."),
    "chemka-hot-springs": ("Chemka Hot Springs Day Trip", "A relaxing day trip to Chemka (Kikuletwa) Hot Springs, warm turquoise pools under ancient fig trees, perfect after a safari or Kilimanjaro climb."),
    "kilimanjaro-day-hike": ("Kilimanjaro Day Hike to Mandara", "A one-day hike through Kilimanjaro's rainforest from Marangu Gate up to the Mandara Huts and Maundi Crater, no multi-day trek required."),
    "horseback-riding": ("Horseback Safari Near Arusha", "A horseback riding day trip on a wildlife estate near Arusha, riding quietly alongside zebra and antelope under Mount Meru. All levels welcome."),
    "arusha-shopping-tour": ("Arusha Shopping & Market Tour", "A guided day tour of Arusha's markets, craft co-ops and art galleries with a local expert, for authentic Tanzanian souvenirs and Tanzanite."),
}

# Ngorongoro is not one of the 11 hub cards but already has a page; rebuild it on
# the same template from its own cleaned content so it is consistent and linked.
NGORONGORO = {
    "slug": "ngorongoro",
    "id": None,
    "name": "Ngorongoro Crater Day Trip",
    "price": "$620",
    "image": "/images/gallery/ngorongoro-lion-crater-walls.jpg",
    "imageAlt": "Lion on the Ngorongoro Crater floor",
    "tags": ["Ngorongoro", "Day Trip"],
    "description": "Spend a full day inside the Ngorongoro Crater, the largest unbroken volcanic caldera on Earth and home to the densest concentration of large wildlife in Africa. Descend the crater wall into a self-contained world of grassland, swamp, forest and soda lake, where the Big Five can be seen in a single day.",
    "highlights": [
        "Descend more than 600 metres into the floor of an intact volcanic caldera.",
        "One of the best places in Tanzania to see the Big Five, including the rare black rhino, in a single day.",
        "Flamingos, crowned cranes and ostriches around the soda lake at Lake Magadi.",
    ],
    "itinerary": [
        "Early morning: Drive from Arusha up to the Ngorongoro Conservation Area and the crater rim.",
        "Mid morning: Descend the steep access road onto the crater floor and begin the game drive across grasslands, swamps and forest.",
        "Midday: Picnic lunch at a scenic site on the crater floor, surrounded by wildlife.",
        "Afternoon: Continue the game drive, looking for lion, elephant, buffalo, hyena, hippo and black rhino, then ascend the crater wall.",
        "Late afternoon: Drive back to Arusha.",
    ],
    "included": "Ngorongoro Conservation Area fees, crater service fee, professional English-speaking safari guide, private 4x4 safari vehicle with pop-up roof, picnic lunch, bottled drinking water, government taxes and VAT.",
    "notIncluded": "International flights, travel insurance, personal expenses, alcoholic and soft drinks, tips and gratuities, items of a personal nature.",
}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_cards(html: str) -> list[dict]:
    cards = []
    for m in re.finditer(r'<article class="dest-card reveal" id="([^"]+)">(.*?)</article>', html, re.S):
        cid, body = m.group(1), m.group(2)
        if cid not in SLUGS:
            continue
        price = clean(re.search(r'<span class="trip-price">([^<]+)</span>', body).group(1))
        price = price.replace("Per person", "").replace("From", "").strip()
        img = re.search(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', body)
        name = clean(re.search(r'<h3 class="dest-name">(.*?)</h3>', body, re.S).group(1))
        desc = clean(re.search(r'<p class="dest-desc">(.*?)</p>', body, re.S).group(1))
        tags = [clean(t) for t in re.findall(r'<span class="dest-tag">([^<]+)</span>', body)]
        highlights = [clean(li) for li in re.findall(r'<h4>Highlights</h4>\s*<ul>(.*?)</ul>', body, re.S)[0:1] for li in re.findall(r'<li>(.*?)</li>', li, re.S)]
        itinerary = [clean(li) for li in re.findall(r'<h4>Itinerary</h4>\s*<ol>(.*?)</ol>', body, re.S)[0:1] for li in re.findall(r'<li>(.*?)</li>', li, re.S)]
        included = clean(re.search(r'<h4>What is Included</h4><p>(.*?)</p>', body, re.S).group(1))
        not_inc = clean(re.search(r'<h4>What is Not Included</h4><p>(.*?)</p>', body, re.S).group(1))
        cards.append({
            "slug": SLUGS[cid], "id": cid, "name": name, "price": price,
            "image": img.group(1), "imageAlt": img.group(2), "tags": tags,
            "description": desc, "highlights": highlights, "itinerary": itinerary,
            "included": included, "notIncluded": not_inc,
        })
    return cards


def render(trip: dict, siblings: list[dict]) -> str:
    slug = trip["slug"]
    title, meta_desc = META.get(slug, (trip["name"], trip["description"][:155]))
    url = f"{BASE}/daytrips/{slug}"
    price_num = re.sub(r"[^0-9.]", "", trip["price"]) or None

    trip_ld = {
        "@context": "https://schema.org", "@type": "TouristTrip",
        "name": trip["name"], "description": meta_desc,
        "provider": {"@id": f"{BASE}/#organization"},
        "touristType": "Day-trip traveller", "url": url, "duration": "P1D",
    }
    if price_num:
        trip_ld["offers"] = {
            "@type": "Offer", "price": price_num, "priceCurrency": "USD",
            "url": url, "availability": "https://schema.org/InStock",
            "description": "Starting price per person",
        }
    crumb_ld = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Day Trips", "item": f"{BASE}/daytrips"},
            {"@type": "ListItem", "position": 3, "name": trip["name"], "item": url},
        ],
    }
    schemas = json.dumps([trip_ld, crumb_ld], ensure_ascii=False)

    hl = "\n".join(f'<li style="font-size:1rem;color:var(--text);line-height:1.7;margin-bottom:8px">{h}</li>' for h in trip["highlights"])
    it = "\n".join(f'<li style="font-size:1rem;color:var(--text);line-height:1.7;margin-bottom:10px">{s}</li>' for s in trip["itinerary"])
    sib = "\n".join(f'<a href="/daytrips/{s["slug"]}" style="display:inline-block;padding:8px 16px;border:1.5px solid var(--border);border-radius:999px;font-size:.9rem;color:var(--ink-2);text-decoration:none;font-weight:600">{s["name"]}</a>' for s in siblings if s["slug"] != slug)
    p = 'style="font-size:1rem;color:var(--text);line-height:1.78;margin-bottom:14px"'

    return f"""---
import BaseLayout from '../../layouts/BaseLayout.astro';
const schemas = {schemas};
---

<BaseLayout
  title="{title} | Go Kilimanjaro Treks"
  description="{meta_desc}"
  ogImage="{BASE}{trip['image']}"
  ogImageAlt="{trip['imageAlt']}"
  schemas={{schemas}}
>

<section class="page-hero">
  <img src="{trip['image']}" alt="" aria-hidden="true" loading="eager" fetchpriority="high" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 40%;z-index:0;opacity:0.55" />
  <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(100deg,rgba(2,6,14,0.88) 0%,rgba(2,6,14,0.82) 40%,rgba(2,6,14,0.55) 65%,rgba(2,6,14,0.15) 100%);z-index:1"></div>
  <div class="container">
    <span class="page-hero-eyebrow">Tanzania Day Trip</span>
    <h1>{trip['name']}</h1>
    <p>{trip['description']}</p>
    <div class="hero-ctas">
      <a href="/contact" class="btn-primary">Request a Quote &#x2192;</a>
      <a href="https://wa.me/255677917500" class="btn-ghost" target="_blank" rel="noopener">&#x1F4AC; WhatsApp Nelson</a>
    </div>
  </div>
</section>

<section class="section-white">
  <div class="container" style="max-width:820px">
    <p style="font-size:1.15rem;color:var(--amber-cta);font-weight:700;margin:30px 0 18px">From {trip['price']} per person</p>

    <h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--amber-cta);margin:32px 0 12px">Highlights</h2>
    <ul style="padding-left:22px;margin-bottom:8px">
{hl}
    </ul>

    <h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--amber-cta);margin:32px 0 12px">A Day on This Trip</h2>
    <ol style="padding-left:22px;margin-bottom:8px">
{it}
    </ol>

    <h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--amber-cta);margin:32px 0 12px">What is Included</h2>
    <p {p}>{trip['included']}</p>

    <h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--amber-cta);margin:32px 0 12px">What is Not Included</h2>
    <p {p}>{trip['notIncluded']}</p>
    <p style="font-size:.92rem;color:var(--muted);line-height:1.7;margin-top:18px">Every day trip is private and fully customisable. Prices vary with group size and season, so message Nelson for an exact quote for your dates.</p>
  </div>
</section>

<section class="section-tinted">
  <div class="container" style="max-width:900px;text-align:center">
    <h2 style="font-family:var(--font-display);font-size:clamp(1.5rem,3vw,2rem);font-weight:700;color:var(--ink-2);margin-bottom:8px">More Tanzania Day Trips</h2>
    <p style="color:var(--muted);margin-bottom:22px">Pair this with another single-day adventure from Moshi or Arusha.</p>
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center">
{sib}
    </div>
    <p style="margin-top:24px"><a href="/daytrips" style="color:var(--amber-cta);font-weight:600">See all day trips &#x2192;</a></p>
  </div>
</section>

<section class="cta-section">
  <div class="container">
    <h2>Ready to <em>Book This Day Trip</em>?</h2>
    <p>Talk to Nelson about your dates and the rest of your time in Tanzania. He responds personally within 24 hours.</p>
    <div class="cta-actions">
      <a href="/contact" class="btn-primary" style="font-size:1.05rem;padding:18px 40px">Request a Quote &#x2192;</a>
      <a href="https://wa.me/255677917500" class="btn-wa" style="font-size:1rem" target="_blank" rel="noopener">&#x1F4AC; WhatsApp Now</a>
    </div>
  </div>
</section>

</BaseLayout>
"""


def rewrite_hub(html: str) -> str:
    # 1) Replace each card's <details> accordion with a link to the detail page,
    #    and repoint the trailing "Book This Trip" CTA to the detail page.
    for m in list(re.finditer(r'<article class="dest-card reveal" id="([^"]+)">', html)):
        cid = m.group(1)
        if cid not in SLUGS:
            continue
        slug = SLUGS[cid]
        # remove the details block for this card (first one after the id)
    # do replacements globally using slug map keyed by surrounding id
    def strip_details(match):
        return ""  # placeholder, handled below

    # Process card-by-card to keep ids aligned with slugs
    out = html
    for cid, slug in SLUGS.items():
        # Within this card, drop the <details>...</details>
        pat_card = re.compile(r'(<article class="dest-card reveal" id="%s">.*?)<details class="trip-details">.*?</details>\s*' % re.escape(cid), re.S)
        out = pat_card.sub(r'\1', out, count=1)
        # Repoint the card CTA to the detail page
        pat_cta = re.compile(r'(<article class="dest-card reveal" id="%s">.*?)<a href="/contact" class="dest-cta"([^>]*)>Book This Trip &#x2192;</a>' % re.escape(cid), re.S)
        out = pat_cta.sub(r'\1<a href="/daytrips/%s" class="dest-cta"\2>See full itinerary &amp; details &#x2192;</a>' % slug, out, count=1)

    # 2) Point the ItemList schema entries at the detail pages instead of #anchors
    for cid, slug in SLUGS.items():
        out = out.replace(f"{BASE}/daytrips.html#{cid}", f"{BASE}/daytrips/{slug}")
        out = out.replace(f"{BASE}/daytrips#{cid}", f"{BASE}/daytrips/{slug}")
    return out


def main():
    html = HUB.read_text(encoding="utf-8")
    cards = parse_cards(html)
    assert len(cards) == 11, f"expected 11 cards, got {len(cards)}"
    all_trips = cards + [NGORONGORO]

    for trip in all_trips:
        page = render(trip, all_trips)
        (OUT / f"{trip['slug']}.astro").write_text(page, encoding="utf-8")
        print(f"  wrote daytrips/{trip['slug']}.astro  ({trip['name']}, {trip['price']})")

    HUB.write_text(rewrite_hub(html), encoding="utf-8")
    print(f"rewrote hub: {len(cards)} cards now link to detail pages; ItemList -> detail URLs")
    print(f"generated {len(all_trips)} detail pages")


if __name__ == "__main__":
    main()
