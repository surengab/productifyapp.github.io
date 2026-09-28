#!/usr/bin/env python3
"""Rebuild the printable PDFs: python3 _scripts/build_printables.py.

Builds the monthly and weekly habit trackers, the 30-day trackers and the
year-in-pixels sheet, in A4 and US Letter. Each PDF footer links back to the
page that offers it. Requires reportlab and pypdf for authoring only; the
deployed site is static.
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


PRINTABLE_PATH = '/guides/habit-tracker-printable/'
THIRTY_DAY_PATH = '/guides/30-day-habit-tracker/'
PIXELS_PATH = '/guides/year-in-pixels/'
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
MONTH_LENGTHS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def header(c, width, height, title, subtitle, size_label, path=PRINTABLE_PATH):
    text(c, 36, height - 35, 'PRODUCTIFY  /  MAKE ROOM FOR ONE HABIT', 9, True, BLUE)
    text(c, 36, height - 72, title, 29, True)
    text(c, 36, height - 94, subtitle, 10, color=MUTED)
    text(c, width - 100, 27, size_label, 8, color=MUTED)
    label = 'productifyapp.org' + path
    text(c, 36, 27, label, 8, color=MUTED)
    link_width = c.stringWidth(label, 'Helvetica', 8)
    if path == PRINTABLE_PATH:
        link_width = 214  # the original hit area; keeps the first six PDFs byte-identical
    c.linkURL('https://productifyapp.org' + path, (36, 23, 36 + link_width, 37), relative=0)


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


def centred(c, x, y, value, size=10, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    c.drawCentredString(x, y, value)


def thirty_day_single(c, width, height, size_label):
    """One habit, thirty days, laid out as weeks so the check-ins line up."""
    header(c, width, height, '30-day habit tracker', 'One habit for thirty days. Tick each day you do it; the weekly check-ins keep it realistic.',
           size_label + ' / portrait', THIRTY_DAY_PATH)
    fields = [('MY HABIT', height - 132), ('DAILY TARGET', height - 158), ('WHY IT MATTERS TO ME', height - 184)]
    for label, y in fields:
        text(c, 36, y, label, 8, True, MUTED)
        rule(c, 160, y - 3, width - 196)
    text(c, 36, height - 210, 'START DATE', 8, True, MUTED)
    rule(c, 160, height - 213, 120)
    text(c, 300, height - 210, 'END DATE', 8, True, MUTED)
    rule(c, 360, height - 213, width - 396)

    left, top = 36, height - 236
    label_w, review_w = 58, 92
    cell = (width - 72 - label_w - review_w) / 7
    row_h = min(cell, 66)
    c.setFillColor(PALE)
    c.rect(left, top - 22, width - 72, 22, stroke=0, fill=1)
    text(c, left + 8, top - 15, 'WEEK', 8, True)
    text(c, left + label_w + cell * 7 + 8, top - 15, 'CHECK-IN', 8, True)
    y = top - 22
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for week in range(5):
        days = range(week * 7 + 1, min(week * 7 + 8, 31))
        c.setStrokeColor(LINE)
        c.rect(left, y - row_h, width - 72, row_h, stroke=1, fill=0)
        text(c, left + 8, y - row_h / 2 - 3, f'Week {week + 1}', 9, True)
        for i in range(7):
            x = left + label_w + cell * i
            c.line(x, y - row_h, x, y)
            day = week * 7 + i + 1
            if day <= 30:
                text(c, x + 5, y - 12, str(day), 8, True, MUTED)
            else:
                c.setFillColor(PALE)
                c.rect(x + 0.5, y - row_h + 0.5, cell - 1, row_h - 1, stroke=0, fill=1)
        c.line(left + label_w + cell * 7, y - row_h, left + label_w + cell * 7, y)
        prompt = 'Day 30: keep, adjust or stop?' if week == 4 else 'Easier or harder?'
        c.setFillColor(MUTED)
        c.setFont('Helvetica', 7)
        c.drawString(left + label_w + cell * 7 + 6, y - 12, prompt if week < 4 else 'Day 30 review:')
        y -= row_h
    bottom = y
    text(c, 36, bottom - 22, 'KEY  Tick = done    Dash = planned rest day    Blank = missed or not logged', 9, color=MUTED)
    text(c, 36, bottom - 38, 'A missed day is information, not a reset. Pick up again the next day.', 9, color=MUTED)
    text(c, 36, bottom - 70, 'DAYS DONE', 8, True)
    rule(c, 100, bottom - 73, 50)
    text(c, 156, bottom - 70, '/ 30', 9, color=MUTED)
    text(c, 220, bottom - 70, 'WHAT MADE IT EASIER?', 8, True)
    rule(c, 340, bottom - 73, width - 376)
    text(c, 36, bottom - 100, 'WHAT I WILL KEEP OR CHANGE AFTER DAY 30', 8, True)
    rule(c, 36, bottom - 124, width - 72)


def thirty_day_multi(c, width, height, size_label):
    """Several habits across 30 numbered days, with a total column."""
    header(c, width, height, '30-day habit tracker', 'Up to eight habits across thirty days. Start on any date and total each row at the end.',
           size_label + ' / landscape', THIRTY_DAY_PATH)
    text(c, 36, height - 126, 'START DATE', 8, True, MUTED)
    rule(c, 104, height - 129, 150)
    text(c, 290, height - 126, 'MY FOCUS FOR THESE 30 DAYS', 8, True, MUTED)
    rule(c, 446, height - 129, width - 482)
    available = width - 72
    first, total_w = 150, 40
    day_w = (available - first - total_w) / 30
    widths = [first] + [day_w] * 30 + [total_w]
    labels = ['HABIT + TARGET'] + [str(day) for day in range(1, 31)] + ['/30']
    bottom = grid(c, height - 150, widths, labels, 8, 29, 27)
    # Faint week separators after days 7, 14, 21 and 28 make weekly reviews easier to spot.
    c.setStrokeColor(BLUE)
    c.setLineWidth(1)
    for day in (7, 14, 21, 28):
        x = 36 + first + day_w * day
        c.line(x, bottom, x, height - 150)
    c.setLineWidth(0.5)
    text(c, 36, bottom - 20, 'KEY  Tick = completed    Dash = not scheduled    Blank = missed or not logged    Blue lines mark each week', 9, color=MUTED)
    text(c, 36, bottom - 36, 'Write the start date above, then count days from there. The sheet works for any 30 days, not only calendar months.', 9, color=MUTED)
    text(c, 36, bottom - 65, 'WHAT WORKED?', 8, True)
    text(c, width / 2 + 12, bottom - 65, 'ONE CHANGE FOR THE NEXT 30 DAYS', 8, True)
    rule(c, 36, bottom - 87, width / 2 - 60)
    rule(c, width / 2 + 12, bottom - 87, width / 2 - 48)


def year_in_pixels(c, width, height, size_label):
    """A 12 x 31 grid: one small square per day of the year, colored by a key."""
    header(c, width, height, 'Year in pixels', 'One square for every day of the year. Choose what to track, pick five colors, fill in a square each evening.',
           size_label + ' / portrait', PIXELS_PATH)
    text(c, 36, height - 124, 'YEAR', 8, True, MUTED)
    rule(c, 70, height - 127, 70)
    text(c, 160, height - 124, 'I AM TRACKING', 8, True, MUTED)
    rule(c, 244, height - 127, width - 280)

    legend_h = 118
    top = height - 146
    grid_bottom = 36 + legend_h
    rows = 32  # header + 31 days
    row_h = (top - grid_bottom) / rows
    day_w = 24
    cell_w = min((width - 72 - day_w) / 12, row_h * 1.9)
    grid_w = day_w + cell_w * 12
    left = (width - grid_w) / 2
    c.setFillColor(PALE)
    c.rect(left + day_w, top - row_h, cell_w * 12, row_h, stroke=0, fill=1)
    for m, name in enumerate(MONTHS):
        centred(c, left + day_w + cell_w * m + cell_w / 2, top - row_h + (row_h - 7) / 2 + 1, name, 7, True)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for d in range(1, 32):
        y = top - row_h * (d + 1)
        c.setFillColor(MUTED)
        c.setFont('Helvetica-Bold', 7)
        c.drawRightString(left + day_w - 6, y + (row_h - 7) / 2 + 1, str(d))
        for m in range(12):
            x = left + day_w + cell_w * m
            if d > MONTH_LENGTHS[m]:
                c.setFillColor(PALE)
                c.rect(x, y, cell_w, row_h, stroke=0, fill=1)
                c.setStrokeColor(LINE)
                c.line(x + 3, y + 3, x + cell_w - 3, y + row_h - 3)
            elif m == 1 and d == 29:
                c.setFillColor(LINE)
                c.circle(x + cell_w - 4, y + row_h - 4, 1.2, stroke=0, fill=1)
    # Grid lines last, so shaded cells never cover them.
    c.setStrokeColor(LINE)
    c.rect(left + day_w, top - row_h * 32, cell_w * 12, row_h * 32, stroke=1, fill=0)
    for m in range(1, 12):
        x = left + day_w + cell_w * m
        c.line(x, top - row_h * 32, x, top)
    for r in range(1, 32):
        y = top - row_h * r
        c.line(left + day_w, y, left + grid_w, y)

    ly = grid_bottom - 26
    text(c, 36, ly, 'MY COLOR KEY', 8, True)
    text(c, 130, ly, 'Color each square, then write what it means. Mood example: great, good, okay, low, hard.', 8, color=MUTED)
    swatch_w = (width - 72) / 5
    for i in range(5):
        x = 36 + swatch_w * i
        c.setStrokeColor(LINE)
        c.rect(x, ly - 30, 16, 16, stroke=1, fill=0)
        rule(c, x + 22, ly - 28, swatch_w - 34)
    text(c, 36, ly - 52, 'Habit example: done, partly done, rest day, missed, not planned. A dot marks 29 February for leap years.', 8, color=MUTED)
    text(c, 36, ly - 76, 'WHAT DID THE YEAR SHOW YOU?', 8, True)
    rule(c, 190, ly - 79, width - 226)


def check(path, pagesize, url_path, required_text):
    """Check the file users will actually download, including page dimensions."""
    pdf = PdfReader(path)
    assert len(pdf.pages) == 1
    page = pdf.pages[0]
    assert abs(float(page.mediabox.width) - pagesize[0]) < 0.1
    assert abs(float(page.mediabox.height) - pagesize[1]) < 0.1
    content = page.extract_text()
    for value in required_text + ['productifyapp.org' + url_path]:
        assert value in content, (path.name, value)
    assert [a.get_object()['/A']['/URI'] for a in page.get('/Annots', [])] == [
        'https://productifyapp.org' + url_path
    ]
    return content


def new_canvas(path, pagesize, title, subject):
    c = canvas.Canvas(str(path), pagesize=pagesize, pageCompression=1, invariant=1)
    c.setTitle(title)
    c.setAuthor('Productify')
    c.setSubject(subject)
    return c


def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    generated = []
    for size_name, size in [('a4', A4), ('letter', letter)]:
        for layout in ['monthly', 'weekly-monday', 'weekly-sunday']:
            pagesize = landscape(size) if layout == 'monthly' else size
            path = OUTPUT / f'habit-tracker-{layout}-{size_name}.pdf'
            c = new_canvas(path, pagesize, f'Productify {layout.replace("-", " ")} habit tracker - {size_name.upper()}',
                           'Free printable habit tracker for personal use')
            if layout == 'monthly':
                monthly(c, *pagesize, size_name.upper())
            else:
                weekly(c, *pagesize, size_name.upper(), layout.split('-')[1])
            c.showPage()
            c.save()
            content = check(path, pagesize, PRINTABLE_PATH, ['habit tracker'])
            if layout == 'monthly':
                assert all(str(day) in content.splitlines() for day in range(1, 32))
            else:
                ordered = DAYS if layout.endswith('monday') else DAYS[-1:] + DAYS[:-1]
                positions = [content.index(day) for day in ordered]
                assert positions == sorted(positions)
            generated.append(path.name)

        # 30-day trackers: one habit in weekly rows (portrait), or up to eight habits (landscape).
        for layout, pagesize, draw in [('single', size, thirty_day_single), ('multi', landscape(size), thirty_day_multi)]:
            path = OUTPUT / f'30-day-habit-tracker-{layout}-{size_name}.pdf'
            c = new_canvas(path, pagesize, f'Productify 30-day habit tracker ({layout} habit) - {size_name.upper()}',
                           'Free printable 30-day habit tracker for personal use')
            draw(c, *pagesize, size_name.upper())
            c.showPage()
            c.save()
            content = check(path, pagesize, THIRTY_DAY_PATH, ['30-day habit tracker'])
            assert all(str(day) in content.splitlines() for day in range(1, 31))
            assert '31' not in content.splitlines()
            generated.append(path.name)

        path = OUTPUT / f'year-in-pixels-{size_name}.pdf'
        c = new_canvas(path, size, f'Productify year in pixels - {size_name.upper()}',
                       'Free printable year in pixels tracker for personal use')
        year_in_pixels(c, *size, size_name.upper())
        c.showPage()
        c.save()
        content = check(path, size, PIXELS_PATH, ['Year in pixels', 'MY COLOR KEY'])
        positions = [content.index(month) for month in MONTHS]
        assert positions == sorted(positions)
        generated.append(path.name)

    assert len(generated) == 12
    print(f'Built and checked {len(generated)} one-page PDFs:', ', '.join(generated))


if __name__ == '__main__':
    build()
