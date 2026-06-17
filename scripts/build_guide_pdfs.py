"""Build branded PDF versions of the Food (Altitude Menu) and Hygiene guides,
matching the packing-list PDF style. Run from the astro repo root:
    python scripts/build_guide_pdfs.py
"""
import os, sys, re
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, Table, TableStyle, KeepTogether,
                                NextPageTemplate, ListFlowable, ListItem)
from reportlab.lib.utils import ImageReader

sys.path.insert(0, os.path.dirname(__file__))
from build_guide_pages import parse_blocks, MEAL_TABLE, FOOD, HYGIENE  # noqa

INK = HexColor('#0b1a2e'); NAVY = HexColor('#1d3557'); GOLD = HexColor('#fbbf24')
AMBER = HexColor('#b45309'); TEXT = HexColor('#374151'); MUTED = HexColor('#6b7280')
BORDER = HexColor('#e5e7eb'); WHITE = HexColor('#ffffff'); CREAM = HexColor('#f9f7f4')

PAGE_W, PAGE_H = LETTER
ML = MR = 0.75 * inch
USABLE_W = PAGE_W - ML - MR

styles = getSampleStyleSheet()
H_TITLE = ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=40, leading=44, textColor=WHITE)
H_TITLE_G = ParagraphStyle('tg', parent=H_TITLE, textColor=GOLD)
H_SUB = ParagraphStyle('s', fontName='Helvetica', fontSize=12, leading=18, textColor=HexColor('#e5e7eb'))
H_EYE = ParagraphStyle('e', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=GOLD)
H2 = ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=INK, spaceBefore=18, spaceAfter=8)
H3 = ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=AMBER, spaceBefore=12, spaceAfter=4)
BODY = ParagraphStyle('b', fontName='Helvetica', fontSize=10, leading=15, textColor=TEXT, spaceAfter=7)
BULLET = ParagraphStyle('bu', parent=BODY, leftIndent=14, spaceAfter=3)
CELL = ParagraphStyle('c', fontName='Helvetica', fontSize=8.5, leading=12, textColor=TEXT)
CELLH = ParagraphStyle('ch', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=WHITE)


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def bold_leadin(text):
    m = re.match(r'^([A-Z][^:]{2,55}):\s+(.+)$', text)
    if m:
        return f'<b>{esc(m.group(1))}:</b> {esc(m.group(2))}'
    return esc(text)


def make_pdf(cfg, cover_img):
    out = cfg['out']
    os.makedirs('public/downloads', exist_ok=True)

    def cover_bg(canv, doc):
        canv.saveState()
        canv.setFillColor(INK); canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        try:
            ir = ImageReader(cover_img); iw, ih = ir.getSize()
            s = max(PAGE_W / iw, PAGE_H / ih); w, h = iw * s, ih * s
            canv.drawImage(ir, (PAGE_W - w) / 2, (PAGE_H - h) / 2, w, h, mask='auto')
        except Exception:
            pass
        canv.setFillColor(INK); canv.setFillAlpha(0.34); canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canv.setFillAlpha(0.64); canv.rect(0, 0, PAGE_W, PAGE_H * 0.55, fill=1, stroke=0); canv.setFillAlpha(1)
        canv.setFillColor(AMBER); canv.rect(0, 0.45 * inch, PAGE_W, 0.08 * inch, fill=1, stroke=0)
        canv.setFillColor(GOLD); canv.rect(0, 0.53 * inch, PAGE_W, 0.03 * inch, fill=1, stroke=0)
        canv.setFillColor(GOLD); canv.setFont('Helvetica-Bold', 10)
        canv.drawRightString(PAGE_W - MR, PAGE_H - 0.6 * inch, 'GO KILIMANJARO TREKS')
        canv.setFillColor(HexColor('#cbd5e1')); canv.setFont('Helvetica', 8.5)
        canv.drawRightString(PAGE_W - MR, PAGE_H - 0.78 * inch, 'Moshi, Tanzania')
        canv.setFillColor(WHITE); canv.setFont('Helvetica-Bold', 9.5)
        canv.drawCentredString(PAGE_W / 2, 0.22 * inch, 'gokilimanjarotreks.com')
        canv.restoreState()

    def content_bg(canv, doc):
        canv.saveState()
        canv.setFillColor(INK); canv.rect(0, PAGE_H - 0.6 * inch, PAGE_W, 0.6 * inch, fill=1, stroke=0)
        canv.setFillColor(GOLD); canv.rect(0, PAGE_H - 0.62 * inch, PAGE_W, 0.02 * inch, fill=1, stroke=0)
        canv.setFillColor(WHITE); canv.setFont('Helvetica-Bold', 9.5)
        canv.drawString(ML, PAGE_H - 0.42 * inch, 'GO KILIMANJARO TREKS')
        canv.setFillColor(GOLD); canv.setFont('Helvetica', 9.5)
        canv.drawRightString(PAGE_W - MR, PAGE_H - 0.42 * inch, cfg['runhead'])
        canv.setFillColor(INK); canv.rect(0, 0, PAGE_W, 0.45 * inch, fill=1, stroke=0)
        canv.setFillColor(GOLD); canv.rect(0, 0.45 * inch, PAGE_W, 0.02 * inch, fill=1, stroke=0)
        canv.setFillColor(WHITE); canv.setFont('Helvetica', 9)
        canv.drawString(ML, 0.18 * inch, 'gokilimanjarotreks.com  |  +255 677 917 500  |  info@gokilimanjarotreks.com')
        canv.setFillColor(GOLD); canv.drawRightString(PAGE_W - MR, 0.18 * inch, f'Page {doc.page}')
        canv.restoreState()

    doc = BaseDocTemplate(out, pagesize=LETTER, leftMargin=ML, rightMargin=MR,
                          topMargin=0.95 * inch, bottomMargin=0.8 * inch,
                          title=cfg['title'], author='Nelson Mushi, Go Kilimanjaro Treks')
    fc = Frame(0.9 * inch, 1.1 * inch, PAGE_W - 1.8 * inch, PAGE_H - 2.2 * inch, id='c',
               leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    fb = Frame(ML, 0.7 * inch, USABLE_W, PAGE_H - 0.95 * inch - 0.7 * inch, id='b',
               leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='Cover', frames=[fc], onPage=cover_bg),
                          PageTemplate(id='Content', frames=[fb], onPage=content_bg)])

    story = [Spacer(1, 2.3 * inch), Paragraph('THE COMPLETE GUIDE', H_EYE),
             Paragraph(cfg['t1'], H_TITLE), Paragraph(cfg['t2'], H_TITLE_G), Spacer(1, 14),
             Paragraph(cfg['sub'], H_SUB), Spacer(1, 0.35 * inch),
             Paragraph(cfg['tag'], ParagraphStyle('tl', parent=H_EYE, textColor=HexColor('#cbd5e1'), fontSize=8)),
             NextPageTemplate('Content'), PageBreak()]

    blocks = parse_blocks(FOOD['srcpath'] if cfg['key'] == 'food' else HYGIENE['srcpath'],
                          cfg['major'], cfg['subhead'])
    if cfg['key'] == 'food':
        for i, b in enumerate(blocks):
            if b[0] == 'p' and 'standard menu is designed' in b[1]:
                blocks.insert(i + 1, MEAL_TABLE); break
    while blocks and blocks[0][0] in ('h2', 'h3') and (
            'HYGIENE' in blocks[0][1].upper() or 'ALTITUDE MENU' in blocks[0][1].upper()
            or 'Essential Cleanliness' in blocks[0][1]):
        blocks.pop(0)

    pending_bullets = []

    def flush_bullets():
        if pending_bullets:
            items = [ListItem(Paragraph(esc(b), BULLET), leftIndent=14, value=None) for b in pending_bullets]
            story.append(ListFlowable(items, bulletType='bullet', start='square',
                                      bulletColor=AMBER, bulletFontSize=6, leftIndent=12))
            story.append(Spacer(1, 6))
            pending_bullets.clear()

    for kind, payload in blocks:
        if kind == 'ul':
            pending_bullets.extend(payload); continue
        flush_bullets()
        if kind == 'h2':
            story.append(Paragraph(esc(payload), H2))
        elif kind == 'h3':
            story.append(Paragraph(esc(payload), H3))
        elif kind == 'p':
            story.append(Paragraph(bold_leadin(payload), BODY))
        elif kind == 'table':
            data = [[Paragraph(esc(c), CELLH if r == 0 else CELL) for c in row] for r, row in enumerate(payload)]
            ncol = len(payload[0])
            col_w = [USABLE_W * 0.16] + [USABLE_W * 0.84 / (ncol - 1)] * (ncol - 1) if ncol > 1 else [USABLE_W]
            t = Table(data, colWidths=col_w, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), INK),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, CREAM]),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ]))
            story.append(Spacer(1, 4)); story.append(t); story.append(Spacer(1, 10))
    flush_bullets()

    # closing block
    story.append(Spacer(1, 10))
    story.append(Paragraph('Ready to Climb?', H2))
    story.append(Paragraph(
        'Nelson responds personally to every enquiry within 24 hours. Send your dates and any '
        'questions to <b>info@gokilimanjarotreks.com</b>, call <b>+255 677 917 500</b>, or message on WhatsApp.', BODY))

    doc.build(story)
    print(f"wrote {out} ({os.path.getsize(out)//1024} KB)")


FOOD['srcpath'] = FOOD and __import__('pathlib').Path('C:/Users/cwasy/Downloads/GKT') / FOOD['src']
HYGIENE['srcpath'] = __import__('pathlib').Path('C:/Users/cwasy/Downloads/GKT') / HYGIENE['src']

CFG_FOOD = dict(key='food', out='public/downloads/kilimanjaro-altitude-menu.pdf',
                title='Kilimanjaro Altitude Menu | Go Kilimanjaro Treks', runhead='ALTITUDE MENU',
                t1='Altitude', t2='Menu.', major='Heading2', subhead='Heading3',
                tag='FRESH MEALS  |  DAY 4 RESUPPLY  |  EVERY DIET CATERED FOR',
                sub='What you eat on a Go Kilimanjaro Treks climb: fresh-cooked, balanced meals all the way to the summit, with full support for every diet. From Nelson Mushi and our mountain chefs.')
CFG_HYG = dict(key='hygiene', out='public/downloads/kilimanjaro-hygiene-guide.pdf',
               title='Kilimanjaro Hygiene Guide | Go Kilimanjaro Treks', runhead='HYGIENE GUIDE',
               t1='Hygiene', t2='Guide.', major='Heading1', subhead='Heading2',
               tag='TOILETS  |  HAND HYGIENE  |  HOT SHOWERS  |  SAFE WATER',
               sub='How Go Kilimanjaro Treks keeps climbers healthy on the mountain: private toilets, hand-washing, hot showers, safe water and a dedicated hygiene team.')

if __name__ == '__main__':
    make_pdf(CFG_FOOD, 'public/images/gallery/barranco-camp-tent.jpg')
    make_pdf(CFG_HYG, 'public/images/page-hero-kilimanjaro.jpg')
