"""Generate the Food (Altitude Menu) and Hygiene guide pages as Astro pages
from the GKT docx sources, styled like the existing guide pages.

Run from the astro repo root:  python scripts/build_guide_pages.py
"""
import re, html, zipfile
from pathlib import Path

SRC = Path('C:/Users/cwasy/Downloads/GKT')
OUT = Path('src/pages')
BASE = 'https://gokilimanjarotreks.com'


def parse_blocks(path, major, sub):
    """Return ordered blocks: ('h2'|'h3'|'p'|'ul'|'table', payload).
    major/sub are the docx pStyle names that map to page h2 / h3."""
    xml = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8', 'ignore')
    # Split into top-level paragraphs and tables in document order.
    tokens = re.findall(r'<w:tbl>.*?</w:tbl>|<w:p\b.*?</w:p>', xml, re.S)
    blocks, ul = [], []

    def flush_ul():
        nonlocal ul
        if ul:
            blocks.append(('ul', ul)); ul = []

    def textof(frag):
        t = ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', frag, re.S))
        for a, b in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&apos;', "'"), ('&quot;', '"')]:
            t = t.replace(a, b)
        return re.sub(r'\s+', ' ', t).strip()

    def xmlish(s):
        return bool(re.search(r'w:(tcPr|tblPr|pStyle|gridCol|tcMar|tcBorders|trPr)', s))

    for tok in tokens:
        if tok.startswith('<w:tbl'):
            flush_ul()
            rows = []
            for tr in re.findall(r'<w:tr\b.*?</w:tr>', tok, re.S):
                cells = [textof(tc) for tc in re.findall(r'<w:tc\b.*?</w:tc>', tr, re.S)]
                if any(c for c in cells):
                    rows.append(cells)
            # Skip tables whose cells are literal XML text (the food doc's
            # "markdown table" artifact) — handled separately as a clean table.
            if rows and not any(xmlish(c) for r in rows for c in r):
                blocks.append(('table', rows))
            continue
        style = re.search(r'w:pStyle w:val="([^"]+)"', tok)
        sname = style.group(1) if style else 'Normal'
        txt = textof(tok)
        if not txt:
            continue
        if sname == major:
            flush_ul(); blocks.append(('h2', txt))
        elif sname == sub:
            flush_ul(); blocks.append(('h3', txt))
        elif sname in ('Heading3',):
            flush_ul(); blocks.append(('h3', txt))
        elif sname.startswith('ListBullet') or sname.startswith('ListParagraph'):
            ul.append(txt)
        elif xmlish(txt):
            continue  # drop literal-XML paragraphs (markdown-table artifact)
        else:
            flush_ul(); blocks.append(('p', txt))
    flush_ul()
    return blocks


def esc(s):
    return html.escape(s, quote=False)


def fmt_p(text):
    """Bold a leading 'Label: rest' lead-in, common in these docs."""
    m = re.match(r'^([A-Z][^:]{2,55}):\s+(.+)$', text)
    if m:
        return f'<p><strong>{esc(m.group(1))}:</strong> {esc(m.group(2))}</p>'
    return f'<p>{esc(text)}</p>'


def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


def render_body(blocks, intro_skip=0):
    """Render blocks to HTML; auto-build a TOC from h2 sections."""
    # assign ids to h2s
    h2s = [(i, b[1]) for i, b in enumerate(blocks) if b[0] == 'h2']
    ids = {}
    for i, t in h2s:
        ids[i] = slugify(t)
    out = []
    # TOC
    if len(h2s) >= 3:
        out.append('<div class="toc reveal"><h3>In This Guide</h3><ol>')
        for _, t in h2s:
            out.append(f'<li><a href="#{slugify(t)}">{esc(t)}</a></li>')
        out.append('</ol></div>')
    num = 0
    for i, (kind, payload) in enumerate(blocks):
        if kind == 'h2':
            num += 1
            out.append(f'<h2 id="{ids[i]}"><span class="num">{num}.</span> {esc(payload)}</h2>')
        elif kind == 'h3':
            out.append(f'<h3>{esc(payload)}</h3>')
        elif kind == 'p':
            out.append(fmt_p(payload))
        elif kind == 'ul':
            out.append('<ul>' + ''.join(f'<li>{esc(li)}</li>' for li in payload) + '</ul>')
        elif kind == 'table':
            rows = payload
            t = ['<div class="table-wrap"><table class="compare-table"><thead><tr>']
            t += [f'<th>{esc(c)}</th>' for c in rows[0]]
            t.append('</tr></thead><tbody>')
            for r in rows[1:]:
                t.append('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in r) + '</tr>')
            t.append('</tbody></table></div>')
            out.append(''.join(t))
    return '\n      '.join(out)


def page(cfg, blocks):
    body = render_body(blocks)
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": cfg['crumb'], "item": f"{BASE}/{cfg['slug']}"}]}
    article = {"@context": "https://schema.org", "@type": "Article", "headline": cfg['h1plain'],
               "description": cfg['desc'], "url": f"{BASE}/{cfg['slug']}", "image": f"{BASE}{cfg['ogImage']}",
               "author": {"@type": "Person", "name": "Nelson Mushi", "url": f"{BASE}/about"},
               "publisher": {"@id": f"{BASE}/#organization"},
               "datePublished": "2026-06-17", "dateModified": "2026-06-17"}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "url": f"{BASE}/{cfg['slug']}",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                          for q, a in cfg['faq']]}
    import json
    schemas = json.dumps([crumb, article, faq], ensure_ascii=False)

    dl = ''
    if cfg.get('pdf'):
        dl = f'''
      <div class="callout"><strong>Free PDF:</strong> Prefer to read offline? <a href="{cfg['pdf']}" download>Download the {cfg['pdfLabel']} (PDF)</a>, the same guide our climbers get at the pre-trek briefing.</div>'''

    faq_html = '\n      '.join(
        f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in cfg['faq'])

    return f'''---
import BaseLayout from '../layouts/BaseLayout.astro';
const schemas = {schemas};
---

<BaseLayout
  title="{esc(cfg['title'])}"
  description="{esc(cfg['desc'])}"
  ogImage="{BASE}{cfg['ogImage']}"
  ogImageAlt="{esc(cfg['ogAlt'])}"
  schemas={{schemas}}
>
  <main>
<section class="page-hero">
  <img src="{cfg['ogImage']}" alt="" aria-hidden="true" loading="eager" fetchpriority="high" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 40%;z-index:0;opacity:0.55">
  <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(100deg,rgba(2,6,14,0.88) 0%,rgba(2,6,14,0.82) 40%,rgba(2,6,14,0.55) 65%,rgba(2,6,14,0.15) 100%);z-index:1"></div>
  <div class="container">
    <span class="page-hero-eyebrow">{esc(cfg['eyebrow'])}</span>
    <h1>{cfg['h1']}</h1>
    <p>{esc(cfg['lead'])}</p>
    <div class="hero-ctas">
      <a href="/contact" class="btn-primary">Plan My Climb &#x2192;</a>
      <a href="https://wa.me/255677917500" class="btn-ghost" target="_blank" rel="noopener">&#x1F4AC; WhatsApp Nelson</a>
    </div>
  </div>
</section>

<section class="section-white">
  <div class="container">
    <div style="max-width:840px;margin:0 auto" class="reveal prose-section">{dl}
      {body}

      <h2 id="faq"><span class="num">{cfg['faqnum']}.</span> Frequently Asked Questions</h2>
      {faq_html}
    </div>
  </div>
</section>

<section class="cta-section">
  <div class="container">
    <div class="cta-inner reveal">
      <h2>{cfg['ctaTitle']}</h2>
      <p>{esc(cfg['ctaText'])}</p>
      <div class="cta-actions">
        <a href="/contact" class="btn-primary" style="font-size:1.05rem;padding:18px 40px">Plan My Climb &#x2192;</a>
        <a href="https://wa.me/255677917500" class="btn-wa-lg" target="_blank" rel="noopener">&#x1F4AC; WhatsApp Now</a>
      </div>
    </div>
  </div>
</section>
</main>
</BaseLayout>
'''


FOOD = {
    'slug': 'food-on-the-mountain',
    'crumb': 'Food on the Mountain',
    'title': 'Food on Kilimanjaro: The Altitude Menu | Go Kilimanjaro Treks',
    'desc': 'What you eat on a Go Kilimanjaro Treks climb: fresh-cooked meals, a Day 4 resupply, high-altitude nutrition, and full vegetarian, vegan, gluten-free, halal and allergy accommodations.',
    'ogImage': '/images/gallery/barranco-camp-tent.jpg',
    'ogAlt': 'A tent at Barranco Camp on Mount Kilimanjaro where fresh meals are served',
    'eyebrow': 'On the Mountain',
    'h1': 'Food on <em>Kilimanjaro.</em>',
    'h1plain': 'Food on Kilimanjaro: The Altitude Menu',
    'lead': 'Fresh-cooked, nutritionally balanced meals all the way to the summit, with a Day 4 fresh resupply and full support for every diet. Climbing is hard enough; your food should never be the reason you turn back.',
    'pdf': '/downloads/kilimanjaro-altitude-menu.pdf',
    'pdfLabel': 'Altitude Menu',
    'faqnum': 0,  # filled after
    'faq': [
        ('Is the food on Kilimanjaro fresh or dehydrated?', 'Every meal is cooked fresh on the mountain by our mountain chefs. We do not rely on dehydrated rations. A fresh resupply of beef, chicken, fish and vegetables is brought to Karanga Camp on Day 4, before the most demanding days of the climb.'),
        ('Can you cater to vegetarian, vegan or gluten-free diets?', 'Yes. We accommodate vegetarian, vegan, gluten-free and coeliac, dairy-free, low-carb and ketogenic, diabetic, allergy-specific, halal and kosher-style diets. Tell us your requirements at the time of booking so our procurement team can source the right ingredients in advance.'),
        ('How much will I eat at altitude?', 'Trekkers burn roughly 4,000 to 5,000 calories a day on Kilimanjaro. Our menus are built around complex carbohydrates (55 to 65 percent of intake), with protein for muscle repair and healthy fats for sustained energy. We also serve unlimited boiled, filtered water and encourage four to five litres a day.'),
        ('Should I bring my own snacks?', 'Yes, we recommend it. Altitude suppresses appetite, so a personal supply of your favourite energy bars, trail mix, electrolyte powders and comfort snacks is invaluable for morale and energy, especially if you have a restrictive diet.'),
    ],
    'ctaTitle': 'Fuelled for the <em>Summit.</em>',
    'ctaText': "Tell Nelson your dietary needs when you enquire and we'll build your mountain menu around them. Personal reply within 24 hours.",
    'major': 'Heading2', 'sub': 'Heading3',
    'src': 'GoKilimanjaroTreks__The_Ultimate_Altitude_Menu.doc.docx',
}

HYGIENE = {
    'slug': 'hygiene',
    'crumb': 'Hygiene on the Mountain',
    'title': 'Hygiene & Cleanliness on Kilimanjaro | Go Kilimanjaro Treks',
    'desc': 'How Go Kilimanjaro Treks keeps climbers healthy: private toilets, hand-washing stations, hot shower service, safe drinking water, camp cleanliness, and a dedicated hygiene team.',
    'ogImage': '/images/page-hero-kilimanjaro.jpg',
    'ogAlt': 'Mount Kilimanjaro, where Go Kilimanjaro Treks maintains strict camp hygiene standards',
    'eyebrow': 'Health on the Mountain',
    'h1': 'Hygiene on <em>Kilimanjaro.</em>',
    'h1plain': 'Hygiene and Cleanliness on Kilimanjaro',
    'lead': 'Most illness on the mountain is preventable. Here is how we keep camp clean and climbers healthy: private toilets, hand-washing stations, a hot shower service, safe water, and a dedicated hygiene team.',
    'pdf': '/downloads/kilimanjaro-hygiene-guide.pdf',
    'pdfLabel': 'Hygiene Guide',
    'faqnum': 0,
    'faq': [
        ('What are the toilet facilities like on Kilimanjaro?', 'We provide private, portable chemical toilets in dedicated privacy tents, at a strict ratio of one toilet for every three trekkers. Our Toilet Helpers clean and sanitise them with eco-friendly disinfectant several times a day and restock paper and sanitiser continuously.'),
        ('Can I shower on Kilimanjaro?', 'Yes. We offer a hot shower service: warm water is heated and provided in a private shower tent so you can wash properly during the trek. Between showers, daily washing with warm water, biodegradable soap and wet wipes keeps you clean and comfortable.'),
        ('Is the drinking water safe?', 'Yes. All drinking water is collected from mountain streams, then boiled, filtered and purified before it reaches you. We provide unlimited safe water and encourage four to five litres a day for hydration and acclimatisation.'),
        ('How do you prevent illness spreading in camp?', 'Rigorous hand hygiene is the core of it: wash or sanitise after the toilet, before every meal, and after coughing or handling gear. Combined with sanitised toilets, safe water, strict kitchen and dishwashing standards and proper waste management, this prevents the gastrointestinal and respiratory illnesses that most often end a climb.'),
    ],
    'ctaTitle': 'Climb Clean, Climb <em>Healthy.</em>',
    'ctaText': 'Staying healthy is staying on the mountain. Ask Nelson anything about our hygiene setup, or start planning your climb. Personal reply within 24 hours.',
    'major': 'Heading1', 'sub': 'Heading2',
    'src': 'Go_Kilimanjaro_Treks_Hygiene_Guide_Final.docx',
}


MEAL_TABLE = ('table', [
    ['Meal', 'Typical Offerings', 'Nutritional Focus'],
    ['Breakfast', 'Oatmeal or millet porridge; eggs (scrambled, fried, or omelets); sausages or bacon; toast with peanut butter, jam, and honey; fresh tropical fruit; tea, coffee, and hot chocolate.', 'High carbohydrate loading for morning energy, combined with protein for satiety.'],
    ['Lunch', 'Hearty vegetable or chicken soup; sandwiches or wraps; falafel or roasted chicken portions; pasta or potato salad; hard-boiled eggs; fresh fruit and juice.', 'Balanced macronutrients to replenish energy mid-hike without causing sluggishness.'],
    ['Afternoon Tea', 'Salted popcorn; roasted peanuts; assorted biscuits; hot tea, coffee, and hot chocolate.', 'Quick carbohydrate replenishment and sodium intake on arriving at camp.'],
    ['Dinner', 'Thick soups (pumpkin, leek, or vegetable); mains such as tilapia, spaghetti bolognese, chicken stew, or beef paella; sides of rice, potatoes, or pasta; fresh vegetables; desserts like apple pancakes or fruit salad.', 'Complex carbohydrates to restore glycogen overnight, paired with protein for muscle recovery.'],
])


def build(cfg):
    blocks = parse_blocks(SRC / cfg['src'], cfg['major'], cfg['sub'])
    # Food: inject the clean meal table after the "standard menu" intro paragraph.
    if cfg['slug'] == 'food-on-the-mountain':
        for i, b in enumerate(blocks):
            if b[0] == 'p' and 'standard menu is designed' in b[1]:
                blocks.insert(i + 1, MEAL_TABLE)
                break
    # drop a leading h2/h3 that merely repeats the document title/subtitle
    while blocks and blocks[0][0] in ('h2', 'h3') and (
            'HYGIENE' in blocks[0][1].upper() or 'ALTITUDE MENU' in blocks[0][1].upper()
            or 'Essential Cleanliness' in blocks[0][1]):
        blocks.pop(0)
    # faqnum = number of h2 sections + 1
    cfg['faqnum'] = sum(1 for b in blocks if b[0] == 'h2') + 1
    (OUT / f"{cfg['slug']}.astro").write_text(page(cfg, blocks), encoding='utf-8')
    print(f"wrote {cfg['slug']}.astro  ({len(blocks)} blocks, {cfg['faqnum'] - 1} sections)")


if __name__ == '__main__':
    build(FOOD)
    build(HYGIENE)
