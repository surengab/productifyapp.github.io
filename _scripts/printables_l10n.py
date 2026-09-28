#!/usr/bin/env python3
"""Localized printable PDFs for /de/, /fr/, /ja/ and /ko/ tools pages.

Run through build_printables.py (python3 _scripts/build_printables.py).
Outputs go to assets/printables/<lang>/ and each footer links back to the
localized page that offers the file.

Japanese and Korean need a font with CJK glyphs. reportlab can only embed
TrueType outlines, so the Noto Sans CJK OpenType collection is subset to the
characters these sheets use and converted to TrueType on the fly (fontTools).
Set NOTO_CJK_DIR if the fonts are not in /usr/share/fonts/opentype/noto.
Editing a string below is enough: the subset is rebuilt from the strings.
"""
import os
import tempfile
from pathlib import Path

from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader

import build_printables as bp
from build_printables import BLUE, INK, LINE, MUTED, PALE, MONTH_LENGTHS

ORIGIN = 'https://productifyapp.org'

L = {
    'de': dict(
        sizes=[('a4', A4)], week_starts=['monday'],
        brand='PRODUCTIFY  /  PLATZ FÜR EINE GEWOHNHEIT',
        landscape='Querformat', portrait='Hochformat', key='LEGENDE',
        days=['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'],
        months=['JAN', 'FEB', 'MÄR', 'APR', 'MAI', 'JUN', 'JUL', 'AUG', 'SEP', 'OKT', 'NOV', 'DEZ'],
        monthly=dict(title='Monatlicher Habit Tracker', sub='Ein Zeichen pro Tag. Eine kleine Routine reicht.',
                     month='MONAT / JAHR', focus='MEIN FOKUS DIESEN MONAT', col='GEWOHNHEIT + ZIEL',
                     key1='Haken = erledigt    Strich = nicht geplant    Leer = verpasst oder nicht eingetragen',
                     key2='Streiche Tage, die es in diesem Monat nicht gibt. Lege vorher fest, wann die Gewohnheit ansteht.',
                     worked='WAS HAT GUT FUNKTIONIERT?', change='EINE ÄNDERUNG FÜR NÄCHSTEN MONAT'),
        weekly=dict(title='Wöchentlicher Habit Tracker',
                    sub={'monday': 'Woche ab Montag. Lege vorher fest, an welchen Tagen jede Gewohnheit ansteht.',
                         'sunday': 'Woche ab Sonntag. Lege vorher fest, an welchen Tagen jede Gewohnheit ansteht.'},
                    week='WOCHE VOM', first='MEINE ERSTE GEWOHNHEIT', col='GEWOHNHEIT + ZIEL',
                    key1='Haken = erledigt    Strich = nicht geplant',
                    key2='Leer = verpasst oder nicht eingetragen. Du kannst auch eine Menge eintragen, z. B. Minuten.',
                    review='RÜCKBLICK AUF DIE GEPLANTEN TAGE', review_q='Was hat in deine Woche gepasst? Was kam dazwischen?',
                    change='EINE KLEINE ÄNDERUNG FÜR NÄCHSTE WOCHE'),
        single=dict(title='30-Tage Habit Tracker',
                    sub='Eine Gewohnheit, dreißig Tage. Hake jeden Tag ab; der Wochen-Check hält es realistisch.',
                    fields=['MEINE GEWOHNHEIT', 'TAGESZIEL', 'WARUM ES MIR WICHTIG IST'], start='STARTDATUM', end='ENDDATUM',
                    week_col='WOCHE', check_col='CHECK-IN', week='Woche {n}', prompt='Leichter oder schwerer?', day30='Tag 30:',
                    key1='Haken = erledigt    Strich = geplanter Ruhetag    Leer = verpasst oder nicht eingetragen',
                    key2='Ein verpasster Tag ist eine Information, kein Neustart. Mach am nächsten Tag weiter.',
                    done='ERLEDIGTE TAGE', easier='WAS HAT ES LEICHTER GEMACHT?', keep='WAS ICH NACH TAG 30 BEIBEHALTE ODER ÄNDERE'),
        multi=dict(title='30-Tage Habit Tracker',
                   sub='Bis zu acht Gewohnheiten über dreißig Tage. Starte an einem beliebigen Tag und zähle am Ende jede Zeile zusammen.',
                   start='STARTDATUM', focus='MEIN FOKUS FÜR DIESE 30 TAGE', col='GEWOHNHEIT + ZIEL',
                   key1='Haken = erledigt    Strich = nicht geplant    Leer = verpasst    Blaue Linien = Wochen',
                   key2='Trage oben das Startdatum ein und zähle ab dort. Das Blatt passt für beliebige 30 Tage, nicht nur für Kalendermonate.',
                   worked='WAS HAT GUT FUNKTIONIERT?', change='EINE ÄNDERUNG FÜR DIE NÄCHSTEN 30 TAGE'),
        pixels=dict(title='Year in Pixels',
                    sub='Ein Kästchen für jeden Tag des Jahres. Wähle ein Thema und fünf Farben, dann male jeden Abend ein Kästchen aus.',
                    year='JAHR', tracking='ICH HALTE FEST', key='MEINE FARBLEGENDE',
                    hint='Notiere, wofür jede Farbe steht. Stimmung: super, gut, okay, mies, schwer.',
                    habit='Gewohnheit: erledigt, teilweise, Ruhetag, verpasst, nicht geplant. Der Punkt markiert den 29. Februar.',
                    review='WAS HAT DIR DAS JAHR GEZEIGT?'),
    ),
    'fr': dict(
        sizes=[('a4', A4), ('letter', letter)], week_starts=['monday'],
        brand='PRODUCTIFY  /  DE LA PLACE POUR UNE HABITUDE',
        landscape='paysage', portrait='portrait', key='LÉGENDE',
        days=['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        months=['JANV', 'FÉVR', 'MARS', 'AVR', 'MAI', 'JUIN', 'JUIL', 'AOÛT', 'SEPT', 'OCT', 'NOV', 'DÉC'],
        monthly=dict(title='Habit tracker mensuel', sub='Une marque par jour. Une petite routine suffit.',
                     month='MOIS / ANNÉE', focus='MON OBJECTIF CE MOIS-CI', col='HABITUDE + OBJECTIF',
                     key1='Coche = fait    Tiret = non prévu    Vide = manqué ou non noté',
                     key2='Barrez les jours qui n’existent pas ce mois-ci. Décidez des jours prévus avant de commencer.',
                     worked='CE QUI A MARCHÉ', change='UN CHANGEMENT POUR LE MOIS PROCHAIN'),
        weekly=dict(title='Habit tracker hebdomadaire',
                    sub={'monday': 'Semaine du lundi au dimanche. Décidez quand chaque habitude est prévue avant de commencer.',
                         'sunday': 'Semaine du dimanche au samedi. Décidez quand chaque habitude est prévue avant de commencer.'},
                    week='SEMAINE DU', first='MA PREMIÈRE HABITUDE', col='HABITUDE + OBJECTIF',
                    key1='Coche = fait    Tiret = non prévu',
                    key2='Vide = manqué ou non noté. Vous pouvez aussi noter une quantité, par exemple des minutes.',
                    review='BILAN DES JOURS PRÉVUS', review_q='Qu’est-ce qui a trouvé sa place dans votre semaine ? Qu’est-ce qui a bloqué ?',
                    change='UN PETIT CHANGEMENT POUR LA SEMAINE PROCHAINE'),
        single=dict(title='Habit tracker 30 jours',
                    sub='Une habitude pendant trente jours. Cochez chaque jour ; le bilan hebdomadaire vous aide à rester réaliste.',
                    fields=['MON HABITUDE', 'OBJECTIF QUOTIDIEN', 'POURQUOI C’EST IMPORTANT'], start='DATE DE DÉBUT', end='DATE DE FIN',
                    week_col='SEMAINE', check_col='BILAN', week='Semaine {n}', prompt='Plus facile ou plus dur ?', day30='Jour 30 :',
                    key1='Coche = fait    Tiret = repos prévu    Vide = manqué ou non noté',
                    key2='Un jour manqué est une information, pas un retour à zéro. Reprenez le lendemain.',
                    done='JOURS RÉALISÉS', easier='QU’EST-CE QUI A AIDÉ ?', keep='CE QUE JE GARDE OU CHANGE APRÈS LE JOUR 30'),
        multi=dict(title='Habit tracker 30 jours',
                   sub='Jusqu’à huit habitudes sur trente jours. Commencez n’importe quel jour et faites le total de chaque ligne à la fin.',
                   start='DATE DE DÉBUT', focus='MON OBJECTIF POUR CES 30 JOURS', col='HABITUDE + OBJECTIF',
                   key1='Coche = fait    Tiret = non prévu    Vide = manqué    Lignes bleues = semaines',
                   key2='Notez la date de début en haut et comptez à partir de là. La feuille convient à n’importe quels 30 jours.',
                   worked='CE QUI A MARCHÉ', change='UN CHANGEMENT POUR LES 30 PROCHAINS JOURS'),
        pixels=dict(title='Year in Pixels',
                    sub='Une case pour chaque jour de l’année. Choisissez un thème et cinq couleurs, puis coloriez une case chaque soir.',
                    year='ANNÉE', tracking='CE QUE JE SUIS', key='MA LÉGENDE DE COULEURS',
                    hint='Notez ce que signifie chaque couleur. Humeur : super, bien, moyen, bas, difficile.',
                    habit='Habitude : fait, en partie, repos prévu, manqué, non prévu. Le point marque le 29 février.',
                    review='QU’A MONTRÉ CETTE ANNÉE ?'),
    ),
    'ja': dict(
        sizes=[('a4', A4)], week_starts=['monday', 'sunday'], cjk='JP',
        brand='PRODUCTIFY  /  ひとつの習慣のために',
        landscape='横向き', portrait='縦向き', key='凡例',
        days=['月', '火', '水', '木', '金', '土', '日'],
        months=['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
        monthly=dict(title='月間 習慣トラッカー', sub='1日1マーク。小さな習慣で十分です。',
                     month='年 / 月', focus='今月のテーマ', col='習慣 + 目標',
                     key1='チェック = できた    ー = 予定なし    空欄 = できなかった／未記録',
                     key2='その月にない日付には斜線を引きましょう。記録を始める前に、行う日を決めておきます。',
                     worked='うまくいったこと', change='来月変えてみること'),
        weekly=dict(title='週間 習慣トラッカー',
                    sub={'monday': '月曜始まり。始める前に、それぞれの習慣を行う日を決めましょう。',
                         'sunday': '日曜始まり。始める前に、それぞれの習慣を行う日を決めましょう。'},
                    week='週の始まり', first='はじめる習慣', col='習慣 + 目標',
                    key1='チェック = できた    ー = 予定なし',
                    key2='空欄 = できなかった／未記録。時間（分）などの数値を書き込んでもOKです。',
                    review='予定した日のふりかえり', review_q='今週の生活になじんだことは？ 妨げになったことは？',
                    change='来週変えてみる小さなこと'),
        single=dict(title='30日間 習慣トラッカー',
                    sub='ひとつの習慣を30日間。できた日にチェックし、週ごとのふりかえりで無理なく続けましょう。',
                    fields=['私の習慣', '1日の目標', '続けたい理由'], start='開始日', end='終了日',
                    week_col='週', check_col='ふりかえり', week='{n}週目', prompt='楽になった？ 大変だった？', day30='30日目：',
                    key1='チェック = できた    ー = 予定していた休み    空欄 = できなかった／未記録',
                    key2='1日休んでもリセットではありません。次の日からまた続けましょう。',
                    done='できた日数', easier='続けやすくしてくれたこと', keep='30日後に続けること・変えること'),
        multi=dict(title='30日間 習慣トラッカー',
                   sub='最大8つの習慣を30日間。好きな日に始めて、最後に各行の合計を記入します。',
                   start='開始日', focus='この30日間のテーマ', col='習慣 + 目標',
                   key1='チェック = できた    ー = 予定なし    空欄 = できなかった    青い線 = 週の区切り',
                   key2='上に開始日を書き、そこから数えます。カレンダーの月に限らず、どの30日間にも使えます。',
                   worked='うまくいったこと', change='次の30日間で変えてみること'),
        pixels=dict(title='Year in Pixels（イヤー・イン・ピクセル）',
                    sub='1年の毎日に1マス。記録するものと5つの色を決めて、毎晩1マスずつ塗りましょう。',
                    year='年', tracking='記録するもの', key='色の凡例',
                    hint='それぞれの色の意味を書きましょう。気分の例：とても良い、良い、ふつう、低調、つらい。',
                    habit='習慣の例：できた、一部できた、休みの日、できなかった、予定なし。点はうるう年の2月29日です。',
                    review='この1年でわかったこと'),
    ),
    'ko': dict(
        sizes=[('a4', A4)], week_starts=['monday', 'sunday'], cjk='KR',
        brand='PRODUCTIFY  /  습관 하나를 위한 자리',
        landscape='가로', portrait='세로', key='범례',
        days=['월', '화', '수', '목', '금', '토', '일'],
        months=['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
        monthly=dict(title='월간 해빗 트래커', sub='하루에 표시 하나. 작은 루틴이면 충분합니다.',
                     month='연도 / 월', focus='이번 달의 목표', col='습관 + 목표',
                     key1='체크 = 완료    대시(–) = 계획 없음    빈칸 = 놓침 또는 기록 안 함',
                     key2='이번 달에 없는 날짜에는 줄을 그으세요. 기록 전에 습관을 할 요일을 정해 두세요.',
                     worked='잘된 점', change='다음 달에 바꿀 한 가지'),
        weekly=dict(title='주간 해빗 트래커',
                    sub={'monday': '월요일 시작. 시작하기 전에 각 습관을 할 요일을 정하세요.',
                         'sunday': '일요일 시작. 시작하기 전에 각 습관을 할 요일을 정하세요.'},
                    week='주 시작일', first='나의 첫 습관', col='습관 + 목표',
                    key1='체크 = 완료    대시(–) = 계획 없음',
                    key2='빈칸 = 놓침 또는 기록 안 함. 분 단위 시간처럼 수치를 적어도 좋습니다.',
                    review='계획한 날 돌아보기', review_q='이번 주에 잘 맞았던 것은? 방해가 된 것은?',
                    change='다음 주에 바꿀 작은 한 가지'),
        single=dict(title='30일 해빗 트래커',
                    sub='하나의 습관을 30일 동안. 해낸 날에 체크하고, 주간 점검으로 무리 없이 이어가세요.',
                    fields=['나의 습관', '하루 목표', '이 습관이 중요한 이유'], start='시작일', end='종료일',
                    week_col='주', check_col='점검', week='{n}주차', prompt='쉬워졌나요, 어려워졌나요?', day30='30일째:',
                    key1='체크 = 완료    대시(–) = 계획한 휴식일    빈칸 = 놓침 또는 기록 안 함',
                    key2='하루를 놓쳐도 처음부터 다시 시작할 필요는 없습니다. 다음 날 이어가세요.',
                    done='완료한 날', easier='도움이 된 것', keep='30일 후에 유지하거나 바꿀 것'),
        multi=dict(title='30일 해빗 트래커',
                   sub='최대 8개의 습관을 30일 동안. 원하는 날 시작하고, 마지막에 줄마다 합계를 적으세요.',
                   start='시작일', focus='이번 30일의 목표', col='습관 + 목표',
                   key1='체크 = 완료    대시(–) = 계획 없음    빈칸 = 놓침    파란 선 = 주 구분',
                   key2='위에 시작일을 적고 그날부터 세어 보세요. 달력의 한 달이 아니어도 어떤 30일에나 쓸 수 있습니다.',
                   worked='잘된 점', change='다음 30일에 바꿀 한 가지'),
        pixels=dict(title='Year in Pixels (이어 인 픽셀)',
                    sub='1년의 하루하루에 한 칸씩. 기록할 것과 다섯 가지 색을 정하고, 매일 저녁 한 칸을 칠하세요.',
                    year='연도', tracking='기록할 것', key='나의 색 범례',
                    hint='각 색의 의미를 적으세요. 기분 예시: 아주 좋음, 좋음, 보통, 저조, 힘듦.',
                    habit='습관 예시: 완료, 일부 완료, 휴식일, 놓침, 계획 없음. 점은 윤년의 2월 29일 표시입니다.',
                    review='올해 알게 된 것'),
    ),
}

# Where each sheet is offered, and so what its footer links to.
PAGES = {'monthly': 'habit-tracker-printable', 'weekly': 'habit-tracker-printable',
         'single': '30-day-habit-tracker', 'multi': '30-day-habit-tracker', 'pixels': 'year-in-pixels'}


def all_strings(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from all_strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from all_strings(v)
    elif isinstance(value, str):
        yield value


def cjk_fonts(code, tag):
    """Subset Noto Sans CJK to this locale's text and convert it to TrueType."""
    from fontTools import subset
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTCollection, newTable

    noto = Path(os.environ.get('NOTO_CJK_DIR', '/usr/share/fonts/opentype/noto'))
    text = ''.join(all_strings(L[code])) + ''.join(chr(i) for i in range(32, 127)) + '–—’/'
    names = {}
    for weight in ('Regular', 'Bold'):
        font = next(f for f in TTCollection(str(noto / f'NotoSansCJK-{weight}.ttc')).fonts
                    if tag in f['name'].getDebugName(1))
        options = subset.Options()
        options.desubroutinize = True
        options.notdef_outline = True
        subsetter = subset.Subsetter(options)
        subsetter.populate(text=text)
        subsetter.subset(font)
        order = font.getGlyphOrder()
        glyph_set = font.getGlyphSet()
        glyphs = {}
        for name in order:
            pen = TTGlyphPen(None)
            glyph_set[name].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
            glyphs[name] = pen.glyph()
        font['loca'] = newTable('loca')
        glyf = font['glyf'] = newTable('glyf')
        glyf.glyphOrder, glyf.glyphs = order, glyphs
        del font['CFF ']
        if 'VORG' in font:
            del font['VORG']
        glyf.compile(font)
        maxp = font['maxp'] = newTable('maxp')
        maxp.tableVersion = 0x00010000
        for attr in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs', 'maxInstructionDefs',
                     'maxStackElements', 'maxSizeOfInstructions', 'maxComponentElements', 'maxComponentDepth'):
            setattr(maxp, attr, 0)
        maxp.maxZones = 1
        maxp.numGlyphs = len(order)
        font['post'].formatType = 3.0
        font['head'].glyphDataFormat = 0
        font.sfntVersion = '\x00\x01\x00\x00'
        out = Path(tempfile.gettempdir()) / f'productify-noto-{tag}-{weight}.ttf'
        font.save(out)
        name = f'NotoSansCJK{tag}-{weight}'
        pdfmetrics.registerFont(TTFont(name, str(out)))
        names[weight] = name
    return {'regular': names['Regular'], 'bold': names['Bold']}


# --- drawing helpers ---------------------------------------------------------

def fit(c, x, y, value, size=10, bold=False, color=INK, max_width=None, min_size=6.5):
    """Draw text, shrinking it until it fits max_width."""
    font = bp.FONTS['bold'] if bold else bp.FONTS['regular']
    if max_width:
        while size > min_size and c.stringWidth(value, font, size) > max_width:
            size -= 0.25
    bp.text(c, x, y, value, size, bold, color)
    return c.stringWidth(value, font, size)


def label_rule(c, x, y, label, end, size=8):
    """A small caps label followed by a writing line up to `end`."""
    width = fit(c, x, y, label, size, True, MUTED)
    bp.rule(c, x + width + 10, y - 3, max(20, end - (x + width + 10)))


def header(c, width, height, t, title, subtitle, size_label, path):
    bp.text(c, 36, height - 35, t['brand'], 9, True, BLUE)
    fit(c, 36, height - 72, title, 29, True, max_width=width - 72, min_size=18)
    fit(c, 36, height - 94, subtitle, 10, color=MUTED, max_width=width - 72)
    label = 'productifyapp.org' + path
    bp.text(c, width - 36 - c.stringWidth(size_label, bp.FONTS['regular'], 8), 27, size_label, 8, color=MUTED)
    bp.text(c, 36, 27, label, 8, color=MUTED)
    c.linkURL(ORIGIN + path, (36, 23, 36 + c.stringWidth(label, bp.FONTS['regular'], 8), 37), relative=0)


def key_lines(c, x, y, t, first, second, width):
    fit(c, x, y, t['key'] + '  ' + first, 9, color=MUTED, max_width=width)
    fit(c, x, y - 16, second, 9, color=MUTED, max_width=width)


# --- layouts -----------------------------------------------------------------

def monthly(c, width, height, t, size_label, path):
    m = t['monthly']
    header(c, width, height, t, m['title'], m['sub'], size_label, path)
    label_rule(c, 36, height - 126, m['month'], 300)
    label_rule(c, 338, height - 126, m['focus'], width - 36)
    widths = [160] + [(width - 72 - 160) / 31] * 31
    bottom = bp.grid(c, height - 150, widths, [m['col']] + [str(d) for d in range(1, 32)], 8, 29, 27)
    key_lines(c, 36, bottom - 20, t, m['key1'], m['key2'], width - 72)
    fit(c, 36, bottom - 65, m['worked'], 8, True, max_width=width / 2 - 60)
    fit(c, width / 2 + 12, bottom - 65, m['change'], 8, True, max_width=width / 2 - 48)
    bp.rule(c, 36, bottom - 87, width / 2 - 60)
    bp.rule(c, width / 2 + 12, bottom - 87, width / 2 - 48)


def weekly(c, width, height, t, size_label, path, start):
    w = t['weekly']
    days = t['days'] if start == 'monday' else t['days'][-1:] + t['days'][:-1]
    header(c, width, height, t, w['title'], w['sub'][start], size_label, path)
    label_rule(c, 36, height - 132, w['week'], 252)
    label_rule(c, 36, height - 159, w['first'], width - 36)
    widths = [176] + [(width - 72 - 176) / 7] * 7
    bottom = bp.grid(c, height - 185, widths, [w['col']] + days, 5, 55, 32)
    key_lines(c, 36, bottom - 24, t, w['key1'], w['key2'], width - 72)
    fit(c, 36, bottom - 73, w['review'], 9, True, max_width=width - 72)
    fit(c, 36, bottom - 91, w['review_q'], 10, color=MUTED, max_width=width - 72)
    bp.rule(c, 36, bottom - 115, width - 72)
    fit(c, 36, bottom - 143, w['change'], 9, True, max_width=width - 72)
    bp.rule(c, 36, bottom - 170, width - 72)


def single(c, width, height, t, size_label, path):
    s = t['single']
    header(c, width, height, t, s['title'], s['sub'], size_label, path)
    for label, y in zip(s['fields'], (height - 132, height - 158, height - 184)):
        fit(c, 36, y, label, 8, True, MUTED, max_width=118)
        bp.rule(c, 160, y - 3, width - 196)
    label_rule(c, 36, height - 210, s['start'], 280)
    label_rule(c, 300, height - 210, s['end'], width - 36)
    left, top = 36, height - 236
    label_w, review_w = 58, 92
    cell = (width - 72 - label_w - review_w) / 7
    row_h = min(cell, 66)
    c.setFillColor(PALE)
    c.rect(left, top - 22, width - 72, 22, stroke=0, fill=1)
    fit(c, left + 8, top - 15, s['week_col'], 8, True, max_width=label_w - 12)
    fit(c, left + label_w + cell * 7 + 8, top - 15, s['check_col'], 8, True, max_width=review_w - 14)
    y = top - 22
    c.setLineWidth(0.5)
    for week in range(5):
        c.setStrokeColor(LINE)
        c.rect(left, y - row_h, width - 72, row_h, stroke=1, fill=0)
        fit(c, left + 8, y - row_h / 2 - 3, s['week'].format(n=week + 1), 9, True, max_width=label_w - 12)
        for i in range(7):
            x = left + label_w + cell * i
            c.line(x, y - row_h, x, y)
            day = week * 7 + i + 1
            if day <= 30:
                bp.text(c, x + 5, y - 12, str(day), 8, True, MUTED)
            else:
                c.setFillColor(PALE)
                c.rect(x + 0.5, y - row_h + 0.5, cell - 1, row_h - 1, stroke=0, fill=1)
        c.line(left + label_w + cell * 7, y - row_h, left + label_w + cell * 7, y)
        fit(c, left + label_w + cell * 7 + 6, y - 12, s['day30'] if week == 4 else s['prompt'], 7, color=MUTED,
            max_width=review_w - 12, min_size=5.5)
        y -= row_h
    bottom = y
    key_lines(c, 36, bottom - 22, t, s['key1'], s['key2'], width - 72)
    done_w = fit(c, 36, bottom - 70, s['done'], 8, True)
    bp.rule(c, 46 + done_w, bottom - 73, 50)
    bp.text(c, 102 + done_w, bottom - 70, '/ 30', 9, color=MUTED)
    label_rule(c, 150 + done_w, bottom - 70, s['easier'], width - 36)
    fit(c, 36, bottom - 100, s['keep'], 8, True, max_width=width - 72)
    bp.rule(c, 36, bottom - 124, width - 72)


def multi(c, width, height, t, size_label, path):
    m = t['multi']
    header(c, width, height, t, m['title'], m['sub'], size_label, path)
    label_rule(c, 36, height - 126, m['start'], 254)
    label_rule(c, 290, height - 126, m['focus'], width - 36)
    first, total_w = 150, 40
    day_w = (width - 72 - first - total_w) / 30
    widths = [first] + [day_w] * 30 + [total_w]
    bottom = bp.grid(c, height - 150, widths, [m['col']] + [str(d) for d in range(1, 31)] + ['/30'], 8, 29, 27)
    c.setStrokeColor(BLUE)
    c.setLineWidth(1)
    for day in (7, 14, 21, 28):
        x = 36 + first + day_w * day
        c.line(x, bottom, x, height - 150)
    c.setLineWidth(0.5)
    key_lines(c, 36, bottom - 20, t, m['key1'], m['key2'], width - 72)
    fit(c, 36, bottom - 65, m['worked'], 8, True, max_width=width / 2 - 60)
    fit(c, width / 2 + 12, bottom - 65, m['change'], 8, True, max_width=width / 2 - 48)
    bp.rule(c, 36, bottom - 87, width / 2 - 60)
    bp.rule(c, width / 2 + 12, bottom - 87, width / 2 - 48)


def pixels(c, width, height, t, size_label, path):
    p = t['pixels']
    header(c, width, height, t, p['title'], p['sub'], size_label, path)
    label_rule(c, 36, height - 124, p['year'], 140)
    label_rule(c, 160, height - 124, p['tracking'], width - 36)
    legend_h = 118
    top = height - 146
    grid_bottom = 36 + legend_h
    row_h = (top - grid_bottom) / 32
    day_w = 24
    cell_w = min((width - 72 - day_w) / 12, row_h * 1.9)
    grid_w = day_w + cell_w * 12
    left = (width - grid_w) / 2
    c.setFillColor(PALE)
    c.rect(left + day_w, top - row_h, cell_w * 12, row_h, stroke=0, fill=1)
    for i, name in enumerate(t['months']):
        c.setFillColor(INK)
        c.setFont(bp.FONTS['bold'], 7)
        c.drawCentredString(left + day_w + cell_w * i + cell_w / 2, top - row_h + (row_h - 7) / 2 + 1, name)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for d in range(1, 32):
        y = top - row_h * (d + 1)
        c.setFillColor(MUTED)
        c.setFont(bp.FONTS['bold'], 7)
        c.drawRightString(left + day_w - 6, y + (row_h - 7) / 2 + 1, str(d))
        for i in range(12):
            x = left + day_w + cell_w * i
            if d > MONTH_LENGTHS[i]:
                c.setFillColor(PALE)
                c.rect(x, y, cell_w, row_h, stroke=0, fill=1)
                c.setStrokeColor(LINE)
                c.line(x + 3, y + 3, x + cell_w - 3, y + row_h - 3)
            elif i == 1 and d == 29:
                c.setFillColor(LINE)
                c.circle(x + cell_w - 4, y + row_h - 4, 1.2, stroke=0, fill=1)
    c.setStrokeColor(LINE)
    c.rect(left + day_w, top - row_h * 32, cell_w * 12, row_h * 32, stroke=1, fill=0)
    for i in range(1, 12):
        x = left + day_w + cell_w * i
        c.line(x, top - row_h * 32, x, top)
    for r in range(1, 32):
        y = top - row_h * r
        c.line(left + day_w, y, left + grid_w, y)
    ly = grid_bottom - 26
    key_w = fit(c, 36, ly, p['key'], 8, True)
    fit(c, 36 + key_w + 14, ly, p['hint'], 8, color=MUTED, max_width=width - 72 - key_w - 14)
    swatch_w = (width - 72) / 5
    for i in range(5):
        x = 36 + swatch_w * i
        c.setStrokeColor(LINE)
        c.rect(x, ly - 30, 16, 16, stroke=1, fill=0)
        bp.rule(c, x + 22, ly - 28, swatch_w - 34)
    fit(c, 36, ly - 52, p['habit'], 8, color=MUTED, max_width=width - 72)
    label_rule(c, 36, ly - 76, p['review'], width - 36)


# --- build -------------------------------------------------------------------

def build_localized():
    generated = []
    for code, t in L.items():
        bp.FONTS = cjk_fonts(code, t['cjk']) if t.get('cjk') else {'regular': 'Helvetica', 'bold': 'Helvetica-Bold'}
        out_dir = bp.OUTPUT / code
        out_dir.mkdir(parents=True, exist_ok=True)
        jobs = []
        for size_name, size in t['sizes']:
            label = size_name.upper() if size_name == 'a4' else 'US LETTER'
            jobs.append(('monthly', f'habit-tracker-monthly-{size_name}', landscape(size), label + ' / ' + t['landscape'], monthly, {}))
            for start in t['week_starts']:
                jobs.append(('weekly', f'habit-tracker-weekly-{start}-{size_name}', size, label + ' / ' + t['portrait'], weekly, {'start': start}))
            jobs.append(('single', f'30-day-habit-tracker-single-{size_name}', size, label + ' / ' + t['portrait'], single, {}))
            jobs.append(('multi', f'30-day-habit-tracker-multi-{size_name}', landscape(size), label + ' / ' + t['landscape'], multi, {}))
            jobs.append(('pixels', f'year-in-pixels-{size_name}', size, label + ' / ' + t['portrait'], pixels, {}))
        for kind, name, pagesize, size_label, draw, extra in jobs:
            path = f'/{code}/tools/{PAGES[kind]}/'
            pdf_path = out_dir / f'{name}.pdf'
            c = canvas.Canvas(str(pdf_path), pagesize=pagesize, pageCompression=1, invariant=1)
            title = t[kind]['title']
            c.setTitle(f'Productify – {title} ({size_label.split(" /")[0]})')
            c.setAuthor('Productify')
            c.setSubject(title)
            draw(c, *pagesize, t, size_label, path, **extra)
            c.showPage()
            c.save()
            pdf = PdfReader(pdf_path)
            assert len(pdf.pages) == 1
            page = pdf.pages[0]
            assert abs(float(page.mediabox.width) - pagesize[0]) < 0.1
            assert abs(float(page.mediabox.height) - pagesize[1]) < 0.1
            assert [a.get_object()['/A']['/URI'] for a in page.get('/Annots', [])] == [ORIGIN + path]
            content = page.extract_text()
            assert 'productifyapp.org' + path in content, (pdf_path, path)
            generated.append(f'{code}/{pdf_path.name}')
    bp.FONTS = {'regular': 'Helvetica', 'bold': 'Helvetica-Bold'}
    print(f'Built and checked {len(generated)} localized PDFs:', ', '.join(generated))
    return generated
