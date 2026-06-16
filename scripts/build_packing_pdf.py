"""Build the Kilimanjaro Packing List PDF lead magnet using ReportLab.
Designed in Go Kilimanjaro Treks brand colors. Saved to /downloads/kilimanjaro-packing-list.pdf"""
import os, io, sys
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, FrameBreak, NextPageTemplate
)
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as RLImage
from reportlab.lib.utils import ImageReader

# Photos (relative to astro repo root, where this script is run from)
COVER_IMG = 'public/images/page-hero-kilimanjaro.jpg'
TRAIL_IMG = 'public/images/gallery/porter-walking-toward-kibo.jpg'

# Brand
INK = HexColor('#0b1a2e')
INK2 = HexColor('#111827')
NAVY = HexColor('#1d3557')
GOLD = HexColor('#fbbf24')
AMBER = HexColor('#b45309')
AMBER_DARK = HexColor('#92400e')
CREAM = HexColor('#f9f7f4')
TEXT = HexColor('#374151')
MUTED = HexColor('#6b7280')
BORDER = HexColor('#e5e7eb')
WHITE = HexColor('#ffffff')

os.makedirs('public/downloads', exist_ok=True)
OUTPUT = 'public/downloads/kilimanjaro-packing-list.pdf'

PAGE_W, PAGE_H = LETTER
MARGIN_L = 0.7 * inch
MARGIN_R = 0.7 * inch
MARGIN_T = 0.9 * inch
MARGIN_B = 0.9 * inch
USABLE_W = PAGE_W - MARGIN_L - MARGIN_R

# ===== STYLES =====
styles = getSampleStyleSheet()

H_TITLE = ParagraphStyle('HTitle', parent=styles['Normal'], fontName='Helvetica-Bold',
                        fontSize=42, leading=46, textColor=WHITE, alignment=TA_LEFT,
                        spaceAfter=10)
H_TITLE_GOLD = ParagraphStyle('HTitleGold', parent=H_TITLE, textColor=GOLD)
H_SUB = ParagraphStyle('HSub', parent=styles['Normal'], fontName='Helvetica',
                      fontSize=12, leading=18, textColor=HexColor('#e5e7eb'),
                      alignment=TA_LEFT, spaceAfter=14)
H_EYEBROW = ParagraphStyle('Eyebrow', parent=styles['Normal'], fontName='Helvetica-Bold',
                          fontSize=8.5, leading=12, textColor=GOLD,
                          alignment=TA_LEFT, spaceAfter=10)

H1 = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold',
                   fontSize=22, leading=26, textColor=INK,
                   alignment=TA_LEFT, spaceBefore=8, spaceAfter=8)
H2 = ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica-Bold',
                   fontSize=14, leading=18, textColor=AMBER,
                   alignment=TA_LEFT, spaceBefore=18, spaceAfter=8)
BODY = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica',
                     fontSize=10.5, leading=15.5, textColor=TEXT,
                     alignment=TA_LEFT, spaceAfter=8)
BODY_BOLD = ParagraphStyle('BodyBold', parent=BODY, fontName='Helvetica-Bold')
ITEM = ParagraphStyle('Item', parent=styles['Normal'], fontName='Helvetica',
                     fontSize=10.5, leading=16, textColor=TEXT, leftIndent=18,
                     bulletIndent=4, alignment=TA_LEFT, spaceAfter=2)
ITEM_BOLD = ParagraphStyle('ItemBold', parent=ITEM, fontName='Helvetica-Bold', textColor=INK2)
NOTE = ParagraphStyle('Note', parent=styles['Normal'], fontName='Helvetica-Oblique',
                     fontSize=9.5, leading=13.5, textColor=MUTED, alignment=TA_LEFT,
                     spaceAfter=4)
CTA = ParagraphStyle('CTA', parent=styles['Normal'], fontName='Helvetica-Bold',
                    fontSize=11, leading=15, textColor=WHITE, alignment=TA_CENTER)

# ===== PAGE TEMPLATES =====
def draw_cover_bg(canv, doc):
    """Dark navy hero with gold accent stripe at the bottom"""
    canv.saveState()
    # Full bleed dark background (fallback if the image fails to load)
    canv.setFillColor(INK)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Full-bleed hero photo, scaled to cover the page (centre-cropped)
    try:
        ir = ImageReader(COVER_IMG)
        iw, ih = ir.getSize()
        scale = max(PAGE_W / iw, PAGE_H / ih)
        w, h = iw * scale, ih * scale
        canv.drawImage(ir, (PAGE_W - w) / 2, (PAGE_H - h) / 2, w, h, mask='auto')
    except Exception:
        pass
    # Dark wash for legibility: light over the peak up top, heavier over the
    # lower half where the white title text sits.
    canv.setFillColor(INK)
    canv.setFillAlpha(0.32)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.setFillAlpha(0.62)
    canv.rect(0, 0, PAGE_W, PAGE_H * 0.55, fill=1, stroke=0)
    canv.setFillAlpha(1)
    # Bottom amber stripe
    canv.setFillColor(AMBER)
    canv.rect(0, 0.45 * inch, PAGE_W, 0.08 * inch, fill=1, stroke=0)
    canv.setFillColor(GOLD)
    canv.rect(0, 0.53 * inch, PAGE_W, 0.03 * inch, fill=1, stroke=0)
    # Logo area top right
    canv.setFillColor(GOLD)
    canv.setFont('Helvetica-Bold', 10)
    canv.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 0.6 * inch, 'GO KILIMANJARO TREKS')
    canv.setFillColor(HexColor('#cbd5e1'))
    canv.setFont('Helvetica', 8.5)
    canv.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 0.78 * inch, 'Moshi, Tanzania')
    # Footer URL
    canv.setFillColor(WHITE)
    canv.setFont('Helvetica-Bold', 9.5)
    canv.drawCentredString(PAGE_W / 2, 0.22 * inch, 'gokilimanjarotreks.com')
    canv.restoreState()

def draw_content_bg(canv, doc):
    """Light cream background with brand header strip and footer"""
    canv.saveState()
    # Header navy bar
    canv.setFillColor(INK)
    canv.rect(0, PAGE_H - 0.6 * inch, PAGE_W, 0.6 * inch, fill=1, stroke=0)
    canv.setFillColor(GOLD)
    canv.rect(0, PAGE_H - 0.62 * inch, PAGE_W, 0.02 * inch, fill=1, stroke=0)
    canv.setFillColor(WHITE)
    canv.setFont('Helvetica-Bold', 9.5)
    canv.drawString(MARGIN_L, PAGE_H - 0.42 * inch, 'GO KILIMANJARO TREKS')
    canv.setFillColor(GOLD)
    canv.setFont('Helvetica', 9.5)
    canv.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 0.42 * inch, 'KILIMANJARO PACKING LIST')
    # Footer
    canv.setFillColor(INK)
    canv.rect(0, 0, PAGE_W, 0.45 * inch, fill=1, stroke=0)
    canv.setFillColor(GOLD)
    canv.rect(0, 0.45 * inch, PAGE_W, 0.02 * inch, fill=1, stroke=0)
    canv.setFillColor(WHITE)
    canv.setFont('Helvetica', 9)
    canv.drawString(MARGIN_L, 0.18 * inch, 'gokilimanjarotreks.com  |  +255 677 917 500  |  info@gokilimanjarotreks.com')
    canv.setFillColor(GOLD)
    canv.drawRightString(PAGE_W - MARGIN_R, 0.18 * inch, f'Page {doc.page}')
    canv.restoreState()

# Build doc
doc = BaseDocTemplate(OUTPUT, pagesize=LETTER,
                     leftMargin=MARGIN_L, rightMargin=MARGIN_R,
                     topMargin=0.95 * inch, bottomMargin=0.85 * inch,
                     title='Kilimanjaro Packing List | Go Kilimanjaro Treks',
                     author='Nelson Mushi, Go Kilimanjaro Treks',
                     subject='Complete packing list for Mount Kilimanjaro climbs',
                     keywords='Kilimanjaro, packing list, climbing gear, Tanzania')

frame_cover = Frame(0.9 * inch, 1.1 * inch, PAGE_W - 1.8 * inch, PAGE_H - 2.2 * inch,
                   leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                   showBoundary=0, id='cover')
frame_content = Frame(MARGIN_L, MARGIN_B, USABLE_W, PAGE_H - MARGIN_T - MARGIN_B,
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                     showBoundary=0, id='content')

doc.addPageTemplates([
    PageTemplate(id='Cover', frames=[frame_cover], onPage=draw_cover_bg),
    PageTemplate(id='Content', frames=[frame_content], onPage=draw_content_bg)
])

# ===== CONTENT =====
story = []

# COVER PAGE
story.append(Spacer(1, 2.4 * inch))
story.append(Paragraph('THE COMPLETE GUIDE', H_EYEBROW))
story.append(Paragraph('Kilimanjaro', H_TITLE))
story.append(Paragraph('<i>Packing List.</i>', H_TITLE_GOLD))
story.append(Spacer(1, 16))
story.append(Paragraph(
    'Everything you need on the mountain, by category and climate zone. From Nelson Mushi, '
    'a senior guide with 22 years on Kilimanjaro and over 270 personal summits to Uhuru Peak.',
    H_SUB))
story.append(Spacer(1, 0.4 * inch))
story.append(Paragraph('NINE CATEGORIES  |  WHAT TO RENT  |  WHAT NOT TO BRING',
                      ParagraphStyle('TagLine', parent=H_EYEBROW, textColor=HexColor('#cbd5e1'), fontSize=8)))

story.append(NextPageTemplate('Content'))
story.append(PageBreak())

# INTRO
story.append(Paragraph('Before You Pack', H1))
story.append(Paragraph(
    'Kilimanjaro takes you through five distinct climate zones in a single week, from '
    'tropical rainforest at the base to arctic conditions on the summit. Your kit needs '
    'to handle all of them.',
    BODY))
story.append(Paragraph(
    'This list reflects what we recommend to every Go Kilimanjaro Treks climber based on '
    'over two decades on the mountain. Build the list, lay everything out at home, then '
    'pack twice: once for the climb (in your duffel that porters will carry) and once for '
    'your daypack (what you carry yourself each day).',
    BODY))

# Callout box: Duffel weight
duffel_data = [[Paragraph(
    '<b>Duffel weight limit:</b> 15 kg (33 lb) per climber. Porters are limited by Tanzania '
    'National Park regulation and porter welfare standards. If you bring more, the overflow '
    'has to come out of your duffel at the gate.',
    ParagraphStyle('Callout', parent=BODY, textColor=AMBER_DARK, fontSize=10, leading=14))]]
duffel_t = Table(duffel_data, colWidths=[USABLE_W], rowHeights=None)
duffel_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), HexColor('#fef3c7')),
    ('LEFTPADDING', (0,0), (-1,-1), 16),
    ('RIGHTPADDING', (0,0), (-1,-1), 16),
    ('TOPPADDING', (0,0), (-1,-1), 14),
    ('BOTTOMPADDING', (0,0), (-1,-1), 14),
    ('LINEABOVE', (0,0), (-1,0), 0, BORDER),
    ('LINEBEFORE', (0,0), (0,-1), 3, AMBER),
    ('ROUNDEDCORNERS', [8, 8, 8, 8]),
]))
story.append(Spacer(1, 6))
story.append(duffel_t)
story.append(Spacer(1, 14))

# Trail photo: a porter carrying the duffel toward Kibo (ties to the weight rule)
try:
    _ir = ImageReader(TRAIL_IMG)
    _iw, _ih = _ir.getSize()
    _h = 2.4 * inch
    _w = _h * (_iw / _ih)
    if _w > USABLE_W:
        _w = USABLE_W
        _h = _w * (_ih / _iw)
    _photo = RLImage(TRAIL_IMG, width=_w, height=_h)
    _photo.hAlign = 'CENTER'
    CAPTION = ParagraphStyle('Caption', parent=BODY, fontSize=8.5, leading=12,
                             textColor=MUTED, alignment=TA_CENTER, spaceBefore=6, spaceAfter=2)
    story.append(_photo)
    story.append(Paragraph('Your porters carry the duffel to camp each day. Pack to the 15 kg limit, and lay it all out at home first.', CAPTION))
    story.append(Spacer(1, 16))
except Exception:
    pass

# ===== CATEGORY DEFINITIONS =====
def section(title, items, note=None):
    out = [Paragraph(title, H2)]
    for item in items:
        if isinstance(item, tuple):
            label, desc = item
            out.append(Paragraph(f'<b>{label}.</b>  {desc}', ITEM, bulletText='☐'))
        else:
            out.append(Paragraph(item, ITEM, bulletText='☐'))
    if note:
        out.append(Spacer(1, 4))
        out.append(Paragraph(note, NOTE))
    out.append(Spacer(1, 6))
    return KeepTogether(out)

# REQUIRED DOCUMENTS
story.append(section('1. Required Documents', [
    ('Passport', 'Valid 6+ months past entry, with 2 blank pages.'),
    ('Tanzania e-Visa printed', 'Or visa on arrival cash USD 50 (USD 100 for US citizens).'),
    ('Vaccination certificate', 'Yellow fever required if arriving from an endemic country.'),
    ('Travel insurance proof', 'Must cover trekking to 6,000 m and helicopter evacuation.'),
    ('Printed flight itinerary', 'Plus a backup digital copy.'),
    ('Two passport photos', 'Useful for unexpected permit renewals.'),
]))

# CLOTHING
story.append(section('2. Clothing: The Layered System', [
    ('Base layers', 'Merino wool or synthetic, top and bottom. Never cotton. 2 sets.'),
    ('Mid-layer fleece', 'Heavy fleece for cool moorland evenings and early summit night.'),
    ('Heavy insulation', 'Down or synthetic puffy jacket rated to -15 C minimum.'),
    ('Hardshell jacket', 'Waterproof and windproof, with hood. Pit zips help.'),
    ('Hardshell pants', 'Waterproof, side-zip preferred for putting on over boots.'),
    ('Hiking pants', '2 pairs, quick-dry. Convertible to shorts is optional.'),
    ('Hiking shirts', '3 long-sleeve and 1 short-sleeve, synthetic or merino.'),
    ('Underwear', '5-6 pairs, synthetic or merino. Avoid cotton.'),
], note='Layers go on and off through five climate zones. The system matters more than any single item.'))

# EXTREMITIES
story.append(section('3. Head, Hands, Feet', [
    ('Wool beanie', 'For evenings and summit night.'),
    ('Balaclava or buff', 'Covers face on summit night, can cover neck the rest of the time.'),
    ('Sun hat', 'Wide-brim or cap with neck protection.'),
    ('Sunglasses', 'Category 4 UV protection (high altitude UV is brutal).'),
    ('Liner gloves', 'Thin merino or synthetic, worn under outer gloves.'),
    ('Heavy insulated outer gloves', 'Rated to -20 C. Frostbite kills summit attempts.'),
    ('Hand warmers', '4-6 pairs for summit night.'),
    ('Hiking boots', 'Insulated, waterproof, already broken in. No new boots.'),
    ('Wool hiking socks', '4-5 pairs, heavy weight.'),
    ('Sock liners', '4-5 pairs, thin synthetic to wick moisture.'),
    ('Camp shoes', 'Lightweight sandals or trainers for around camp.'),
    ('Gaiters', 'Keep scree and snow out of boots on summit night.'),
]))

# SLEEPING
story.append(section('4. Sleeping System', [
    ('Sleeping bag', 'Rated to -10 C minimum. Rentable in Moshi if you do not own one.'),
    ('Sleeping pad', 'Inflatable, R-value 3+. Tent floor gets cold.'),
    ('Liner', 'Silk or synthetic. Adds 5 C of warmth and keeps the bag clean.'),
    ('Compression sack', 'Reduces sleeping bag volume in the duffel.'),
]))

# DAYPACK
story.append(section('5. Daypack (30-40 L)', [
    ('Daypack', '30-40 L with hip belt, sternum strap, and rain cover.'),
    ('Hydration bladder', '3 L capacity with insulated hose for cold days.'),
    ('Wide-mouth bottles', '2 x Nalgene 1 L. Wide-mouth bottles do not freeze shut.'),
    ('Camera', 'Plus 2-3 spare batteries (cold drains them fast).'),
    ('Headlamp', 'Plus spare batteries. Used every summit night.'),
    ('Trekking poles', 'Reduce knee load on descent significantly.'),
    ('Personal first aid kit', 'Blister care, ibuprofen, personal medications.'),
    ('Snacks', 'Energy bars, gels, nuts, dried fruit. Bring what you like.'),
    ('Toilet paper', 'In a ziploc, plus hand sanitiser.'),
    ('Pee bottle (optional)', 'Wide-mouth Nalgene. Cold-night option.'),
]))

# SUMMIT NIGHT SPECIFICS
story.append(section('6. Summit Night Extras', [
    ('Extra hand warmers', '6+ pairs, opened just before leaving camp.'),
    ('Heated insoles (optional)', 'Worth it for cold-feet climbers.'),
    ('Insulated bottle covers', 'Or wrap bottles in wool socks.'),
    ('Energy gels', '4-6 portions for the 6-8 hour push.'),
    ('Sunscreen and lip balm', 'Apply before leaving. The dawn at altitude is intense.'),
], note='Summit night starts around 11 PM and reaches Uhuru at sunrise. Plan extremity protection first.'))

# TOILETRIES
story.append(section('7. Toiletries and Personal', [
    ('Toothbrush and toothpaste', 'Travel size.'),
    ('Biodegradable wet wipes', 'No showers on the mountain.'),
    ('Sunscreen SPF50', 'Mineral preferred, reef-safe at coast if extending.'),
    ('Lip balm SPF30', 'Critical at altitude.'),
    ('Quick-dry travel towel', 'For face washing at camp.'),
    ('Personal medications', 'Sealed and labelled. Discuss Diamox with your doctor.'),
    ('Earplugs and eye mask', 'Tents are not soundproof.'),
    ('Insect repellent', 'For lower forest zones and Moshi.'),
]))

# DUFFEL
story.append(section('8. Duffel and Storage', [
    ('Duffel bag', '90-100 L, soft-sided, with carry handles.'),
    ('Dry bags', '3-4 various sizes, to organise inside the duffel.'),
    ('Heavy ziploc bags', '5-6 to compartmentalise small items.'),
    ('Padlock', 'Optional, for the duffel zip.'),
], note='Duffel max weight 15 kg. Pack with this in mind.'))

# RENTING
story.append(section('9. Renting in Moshi', [
    ('Sleeping bag rental', 'USD 30-40 for the climb. Cleaned between climbers.'),
    ('Down jacket rental', 'USD 25-35 for the climb.'),
    ('Hardshell pants rental', 'USD 15-20 for the climb.'),
    ('Trekking pole rental', 'USD 10-15 for the climb.'),
    ('Gaiters rental', 'USD 10 for the climb.'),
    ('Full rental kit', 'Approximately USD 100-150 for the full climb.'),
], note='Coordinate rentals at the pre-trek briefing the day before heading to the gate.'))

# DO NOT BRING
story.append(Paragraph('What NOT to Bring', H1))
story.append(Spacer(1, 4))
not_data = [
    ['Item', 'Why Not'],
    ['Cotton clothing', 'Becomes dangerous at altitude when wet. No insulation when soaked.'],
    ['Brand new boots', 'Blisters end summit attempts. Break boots in 6+ weeks before.'],
    ['Drones', 'Customs impounds drones without 4 separate permits.'],
    ['Plastic bags', 'Banned in Tanzania since 2019. Confiscated at airport.'],
    ['Alcohol', 'No benefit at altitude. Severely dehydrates. Skip until descent.'],
    ['Bluetooth speakers', 'No, just no. Respect the mountain and other climbers.'],
    ['Heavy luxuries', 'Every kilogram a porter carries is a kilogram of effort.'],
]
nt = Table(not_data, colWidths=[1.6 * inch, USABLE_W - 1.6 * inch])
nt.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), INK),
    ('TEXTCOLOR', (0, 0), (-1, 0), GOLD),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    ('TEXTCOLOR', (0, 1), (0, -1), INK2),
    ('TEXTCOLOR', (1, 1), (1, -1), TEXT),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
    ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ('LINEBELOW', (0, 0), (-1, 0), 0, INK),
    ('LINEBELOW', (0, 1), (-1, -1), 0.5, BORDER),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, CREAM]),
]))
story.append(nt)
story.append(Spacer(1, 18))

# CTA / outro
story.append(Paragraph('Ready to Climb?', H1))
story.append(Paragraph(
    'Nelson personally responds to every booking enquiry within 24 hours. Send your dates, '
    'preferred route, and any questions about gear or fitness, and you will hear back from '
    'a senior guide with two decades on the mountain.',
    BODY))

cta_data = [[
    Paragraph('<b>Web</b><br/>gokilimanjarotreks.com', ParagraphStyle('CTACell', parent=BODY, textColor=WHITE, alignment=TA_CENTER, leading=14)),
    Paragraph('<b>Email</b><br/>info@gokilimanjarotreks.com', ParagraphStyle('CTACell', parent=BODY, textColor=WHITE, alignment=TA_CENTER, leading=14)),
    Paragraph('<b>WhatsApp</b><br/>+255 677 917 500', ParagraphStyle('CTACell', parent=BODY, textColor=WHITE, alignment=TA_CENTER, leading=14)),
]]
ct = Table(cta_data, colWidths=[USABLE_W / 3] * 3)
ct.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), INK),
    ('TOPPADDING', (0, 0), (-1, -1), 16),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LINEABOVE', (0, 0), (-1, 0), 2, GOLD),
    ('LINEBELOW', (0, -1), (-1, -1), 2, GOLD),
]))
story.append(Spacer(1, 8))
story.append(ct)

story.append(Spacer(1, 18))
story.append(Paragraph(
    'Nelson Mushi  |  Senior Guide  |  Go Kilimanjaro Treks  |  Moshi, Tanzania',
    ParagraphStyle('Sign', parent=BODY, alignment=TA_CENTER, textColor=MUTED, fontSize=9.5)))

doc.build(story)
print(f'PDF generated: {OUTPUT}')
print(f'Size: {os.path.getsize(OUTPUT) / 1024:.1f} KB')
