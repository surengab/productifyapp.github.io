#!/usr/bin/env python3
"""Rebuild the six printable PDFs: python3 _scripts/build_printables.py.

Requires reportlab and pypdf for authoring only; the deployed site is static.
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfgen import canvas
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets' / 'printables'
INK = colors.HexColor('#202536')
MUTED = colors.HexColor('#535B6B')
LINE = colors.HexColor('#A4ACB9')
PALE = colors.HexColor('#F1F3F8')
BLUE = colors.HexColor('#4059BE')
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def text(c, x, y, value, size=10, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    c.drawString(x, y, value)


def rule(c, x, y, width):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(x, y, x + width, y)


def header(c, width, height, title, subtitle, size_label):
    text(c, 36, height - 35, 'PRODUCTIFY  /  MAKE ROOM FOR ONE HABIT', 9, True, BLUE)
    text(c, 36, height - 72, title, 29, True)
    text(c, 36, height - 94, subtitle, 10, color=MUTED)
    text(c, width - 100, 27, size_label, 8, color=MUTED)
    text(c, 36, 27, 'productifyapp.org/guides/habit-tracker-printable/', 8, color=MUTED)
    c.linkURL('https://productifyapp.org/guides/habit-tracker-printable/', (36, 23, 250, 37), relative=0)


def grid(c, top, widths, labels, rows, row_height, header_height):
    left, total = 36, sum(widths)
    bottom = top - header_height - rows * row_height
    c.setFillColor(PALE)
    c.rect(left, top - header_height, total, header_height, stroke=0, fill=1)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.rect(left, bottom, total, top - bottom, stroke=1, fill=0)
    x = left
    for i, cell_width in enumerate(widths):
        if i:
            c.line(x, bottom, x, top)
        if i == 0:
            text(c, x + 10, top - header_height / 2 - 3, labels[i], 10, True)
        else:
            c.setFont('Helvetica-Bold', 8 if len(labels) > 8 else 10)
            c.setFillColor(INK)
            c.drawCentredString(x + cell_width / 2, top - header_height / 2 - 3, labels[i])
        x += cell_width
    for n in range(rows):
        y = top - header_height - n * row_height
        c.line(left, y, left + total, y)
    return bottom


def monthly(c, width, height, size_label):
    header(c, width, height, 'Monthly habit tracker', 'One mark per day. A small routine is enough.', size_label + ' / landscape')
    text(c, 36, height - 126, 'MONTH / YEAR', 8, True, MUTED)
    rule(c, 120, height - 129, 180)
    text(c, 338, height - 126, 'MY FOCUS THIS MONTH', 8, True, MUTED)
    rule(c, 469, height - 129, width - 505)
    available = width - 72
    widths = [160] + [(available - 160) / 31] * 31
    bottom = grid(c, height - 150, widths, ['HABIT + TARGET'] + [str(day) for day in range(1, 32)], 8, 29, 27)
    text(c, 36, bottom - 20, 'KEY  Tick = completed    Dash = not scheduled    Blank = missed or not logged', 9, color=MUTED)
    text(c, 36, bottom - 36, 'Cross out dates that are not in this month. Decide the schedule before tracking.', 9, color=MUTED)
    text(c, 36, bottom - 65, 'WHAT WORKED?', 8, True)
    text(c, width / 2 + 12, bottom - 65, 'ONE CHANGE FOR NEXT MONTH', 8, True)
    rule(c, 36, bottom - 87, width / 2 - 60)
    rule(c, width / 2 + 12, bottom - 87, width / 2 - 48)


def weekly(c, width, height, size_label, start):
    days = DAYS if start == 'monday' else DAYS[-1:] + DAYS[:-1]
    header(c, width, height, 'Weekly habit tracker', f'{start.title()} start. Choose when each habit is due before you begin.', size_label + ' / portrait')
    text(c, 36, height - 132, 'WEEK OF', 8, True, MUTED)
    rule(c, 92, height - 135, 160)
    text(c, 36, height - 159, 'MY FIRST HABIT', 8, True, MUTED)
    rule(c, 132, height - 162, width - 168)
    available = width - 72
    widths = [176] + [(available - 176) / 7] * 7
    bottom = grid(c, height - 185, widths, ['HABIT + TARGET'] + days, 5, 55, 32)
    text(c, 36, bottom - 24, 'KEY  Tick = completed    Dash = not scheduled', 9, color=MUTED)
    text(c, 36, bottom - 40, 'Blank = missed or not logged. You can also write an amount, such as minutes.', 9, color=MUTED)
    text(c, 36, bottom - 73, 'REVIEW THE PLANNED DAYS', 9, True)
    text(c, 36, bottom - 91, 'What fitted your week? What got in the way?', 10, color=MUTED)
    rule(c, 36, bottom - 115, width - 72)
    text(c, 36, bottom - 143, 'ONE SMALL CHANGE FOR NEXT WEEK', 9, True)
    rule(c, 36, bottom - 170, width - 72)


def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    generated = []
    for size_name, size in [('a4', A4), ('letter', letter)]:
        for layout in ['monthly', 'weekly-monday', 'weekly-sunday']:
            pagesize = landscape(size) if layout == 'monthly' else size
            path = OUTPUT / f'habit-tracker-{layout}-{size_name}.pdf'
            c = canvas.Canvas(str(path), pagesize=pagesize, pageCompression=1, invariant=1)
            c.setTitle(f'Productify {layout.replace("-", " ")} habit tracker - {size_name.upper()}')
            c.setAuthor('Productify')
            c.setSubject('Free printable habit tracker for personal use')
            if layout == 'monthly':
                monthly(c, *pagesize, size_name.upper())
            else:
                weekly(c, *pagesize, size_name.upper(), layout.split('-')[1])
            c.showPage()
            c.save()
            # Check the file users will actually download, including page dimensions.
            pdf = PdfReader(path)
            assert len(pdf.pages) == 1
            page = pdf.pages[0]
            assert abs(float(page.mediabox.width) - pagesize[0]) < 0.1
            assert abs(float(page.mediabox.height) - pagesize[1]) < 0.1
            content = page.extract_text()
            assert 'habit tracker' in content and 'productifyapp.org/guides/habit-tracker-printable/' in content
            assert [a.get_object()['/A']['/URI'] for a in page.get('/Annots', [])] == [
                'https://productifyapp.org/guides/habit-tracker-printable/'
            ]
            if layout == 'monthly':
                assert all(str(day) in content.splitlines() for day in range(1, 32))
            else:
                ordered = DAYS if layout.endswith('monday') else DAYS[-1:] + DAYS[:-1]
                positions = [content.index(day) for day in ordered]
                assert positions == sorted(positions)
            generated.append(path.name)
    assert len(generated) == 6
    print('Built and checked six one-page PDFs:', ', '.join(generated))


if __name__ == '__main__':
    build()
