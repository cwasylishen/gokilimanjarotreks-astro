"""Build the Chrome extension's bundled assets from the site gallery:
- 24 curated landscape photos resized to 1920w -> extension/photos/NN.jpg
- extension/daily.js (photo manifest with real captions + facts/Swahili pool)
- icons 16/32/48/128 (navy tile, gold mountain, snow cap)
- extension zip for Web Store upload

Run from the astro repo root:  python scripts/build_extension_assets.py
"""
import io, json, re, pathlib, zipfile
from PIL import Image, ImageDraw

ROOT = pathlib.Path('.')
GAL = ROOT / 'public/images/gallery'
EXT = ROOT / 'extension'
(EXT / 'photos').mkdir(parents=True, exist_ok=True)
(EXT / 'icons').mkdir(parents=True, exist_ok=True)

# Curated, landscape-only, best-of set: mountain + safari + culture.
PICKS = [
    'summit-sunrise-mawenzi-flare', 'summit-snow-plateau-dawn', 'uhuru-sunrise-mawenzi-flare',
    'kilimanjaro-dawn-pink-flowers', 'above-the-clouds-glacier', 'lone-tree-sunset-meru',
    'tree-bird-mount-meru-dusk', 'barranco-camp-tent', 'mount-meru-ash-cone',
    'barranco-wall-scramble-close',
    'serengeti-lion-portrait', 'serengeti-lion-pair', 'serengeti-elephant-herd',
    'wildebeest-zebra-graze-foothills', 'serengeti-zebra-mother-foal', 'safari-27-0924-003',
    'safari-27-1457-016', 'safari-27-1602-019', 'safari-27-0934-004', 'safari-28-1331-039',
    'safari-27-0812-000', 'safari-28-1218-038',
    'maasai-cultural-welcome', 'maasai-women-traditional-dress',
]

# Captions come from the gallery page's PHOTOS const (single source of truth).
gal_src = (ROOT / 'src/pages/gallery.astro').read_text(encoding='utf-8')
m = re.search(r'const PHOTOS = (\[.*?\]);', gal_src)
captions = {e['slug'].replace('.jpg', ''): e['caption'] for e in json.loads(m.group(1))}

photos = []
for i, slug in enumerate(PICKS):
    src = GAL / f'{slug}.jpg'
    im = Image.open(src).convert('RGB')
    w, h = im.size
    if w > 1920:
        im = im.resize((1920, round(h * 1920 / w)), Image.LANCZOS)
    out = EXT / 'photos' / f'{i:02d}.jpg'
    im.save(out, 'JPEG', quality=80, optimize=True, progressive=True)
    photos.append({'file': f'photos/{i:02d}.jpg', 'caption': captions.get(slug, 'Mount Kilimanjaro, Tanzania')})
    print(f'  {out.name}  {out.stat().st_size // 1024} KB  {slug}')

FACTS = [
    {"sw": "Pole pole", "en": "Slowly, slowly. The two words that get climbers to the summit."},
    {"sw": "Uhuru", "en": "Freedom. Uhuru Peak, 5,895 m, is the highest point in Africa."},
    {"sw": "Twende", "en": "Let's go."},
    {"sw": "Asante sana", "en": "Thank you very much."},
    {"sw": "Karibu", "en": "Welcome. You will hear it everywhere in Tanzania."},
    {"sw": "Jambo", "en": "Hello."},
    {"sw": "Safari njema", "en": "Have a good journey."},
    {"sw": "Mlima", "en": "Mountain."},
    {"sw": "Kilele", "en": "Summit."},
    {"sw": "Theluji", "en": "Snow. Yes, there is snow on the equator."},
    {"sw": "Simba", "en": "Lion."},
    {"sw": "Tembo", "en": "Elephant."},
    {"sw": "Twiga", "en": "Giraffe, Tanzania's national animal."},
    {"sw": "Chui", "en": "Leopard."},
    {"sw": "Kifaru", "en": "Rhinoceros."},
    {"sw": "Nyati", "en": "Buffalo. That completes the Big Five."},
    {"sw": "Rafiki", "en": "Friend."},
    {"sw": "Maji", "en": "Water. Four to five litres a day on the mountain."},
    {"sw": "Jua", "en": "Sun. Equatorial UV is fierce at altitude."},
    {"sw": "Mwezi", "en": "Moon. Full-moon summit nights need no headlamp."},
    {"fact": "Kilimanjaro is the tallest free-standing mountain on Earth: 5,895 m straight off the plains."},
    {"fact": "The climb crosses five climate zones, from rainforest to arctic summit, in under a week."},
    {"fact": "Kilimanjaro has three volcanic cones: Kibo, Mawenzi, and Shira. Only Kibo could erupt again."},
    {"fact": "Hans Meyer and Ludwig Purtscheller made the first recorded summit in 1889."},
    {"fact": "In 1912 the summit held about 11 km² of glacier ice. Less than 1 km² remains today."},
    {"fact": "Roughly 35,000 to 50,000 people attempt Kilimanjaro every year. About two thirds summit."},
    {"fact": "Summit night starts around midnight so you reach Uhuru Peak at sunrise, above the clouds."},
    {"fact": "The Machame Route is nicknamed the Whiskey Route; gentler Marangu is the Coca-Cola Route."},
    {"fact": "Kosovo Camp (4,870 m) is the highest summit base camp on the mountain."},
    {"fact": "Acclimatization beats fitness on Kilimanjaro. The slow climber summits; the racer turns back."},
]

daily = 'const GKT_PHOTOS = ' + json.dumps(photos, ensure_ascii=False, indent=1) + ';\n'
daily += 'const GKT_FACTS = ' + json.dumps(FACTS, ensure_ascii=False, indent=1) + ';\n'
(EXT / 'daily.js').write_text(daily, encoding='utf-8')
print(f'daily.js: {len(photos)} photos, {len(FACTS)} facts')

# ---- Icons: navy rounded tile, gold mountain, white snow cap, sun dot ----
def icon(size):
    s = size * 4  # supersample
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = s // 5
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=(11, 26, 46, 255))
    # gold mountain
    base = s * 0.82
    d.polygon([(s * 0.10, base), (s * 0.52, s * 0.22), (s * 0.66, s * 0.46),
               (s * 0.76, s * 0.34), (s * 0.94, base)], fill=(212, 160, 90, 255))
    # snow cap on the main peak
    d.polygon([(s * 0.40, s * 0.415), (s * 0.52, s * 0.22), (s * 0.625, s * 0.40),
               (s * 0.575, s * 0.375), (s * 0.53, s * 0.43), (s * 0.465, s * 0.375)],
              fill=(255, 255, 255, 255))
    # sun
    d.ellipse([s * 0.72, s * 0.12, s * 0.86, s * 0.26], fill=(251, 191, 36, 255))
    return img.resize((size, size), Image.LANCZOS)

for size in (16, 32, 48, 128):
    icon(size).save(EXT / 'icons' / f'icon{size}.png')
print('icons written')

# ---- Zip for the Web Store (excludes README) ----
zip_path = ROOT / 'gokilimanjarotreks-newtab.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(EXT.rglob('*')):
        if p.is_file() and p.name != 'README.md':
            z.write(p, p.relative_to(EXT))
print(f'zip: {zip_path} ({zip_path.stat().st_size // 1024} KB)')
