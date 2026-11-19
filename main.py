#!/usr/bin/env python3
"""The World in One Day -- Thursday 19 November 2026.

Draws a newspaper front page (1024x1024 PNG) summing up six verified
stories from Thursday 19 November 2026. Pure Python 3.13 standard
library only (os, struct, zlib). No network access, no files read.
Deterministic: two runs produce byte-identical output.

Layout: a navy masthead naming the day, then six story panels in a
2 x 3 grid. Each panel has a coloured kicker, a two-line headline,
a factual subline, and a small flat vector icon drawn from code.
All text is rendered with a 5x7 bitmap font defined below.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (245, 239, 224)   # warm newsprint
INK = (28, 28, 28)       # body text
NAVY = (22, 35, 63)      # masthead band
GOLD = (201, 162, 39)    # masthead rule and date line
WHITE = (255, 255, 255)  # panel cards
MUTED = (110, 106, 98)   # secondary text

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, '1' = on, '0' = off.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
}

# ------------------------------------------------------------- pixel buffer
buf = bytearray(W * H * 3)


def fill(c):
    """Fill the whole canvas with one colour."""
    buf[:] = bytes(c) * (W * H)


def rect(x, y, w, h, c):
    """Axis-aligned filled rectangle, clipped to the canvas."""
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + (x1 - x0) * 3] = row


def disc(cx, cy, r, c):
    """Filled circle."""
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def line(x1, y1, x2, y2, c, t=1):
    """Bresenham line with square brush of size t."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    err = dx - dy
    x, y = x1, y1
    while True:
        rect(x, y, t, t, c)
        if x == x2 and y == y2:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def triangle(x1, y1, x2, y2, x3, y3, c):
    """Filled triangle, scanline rasterised."""
    pts = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts

    def edge(xa, ya, xb, yb, y):
        if yb == ya:
            return float(xa)
        return xa + (xb - xa) * (y - ya) / (yb - ya)

    for y in range(ay, cy + 1):
        if y < by:
            xa = edge(ax, ay, bx, by, y)
            xb = edge(ax, ay, cx, cy, y)
        else:
            xa = edge(bx, by, cx, cy, y)
            xb = edge(ax, ay, cx, cy, y)
        x0 = int(min(xa, xb))
        x1 = int(max(xa, xb))
        rect(x0, y, x1 - x0 + 1, 1, c)


# ------------------------------------------------------------------- text
def text_width(s, scale):
    """Pixel width of a string at a given scale (6 units per char)."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, c, string):
    """Draw a string left-aligned at (x, y), uppercase font."""
    string = string.upper()
    cx = x
    for ch in string:
        glyph = FONT.get(ch)
        if glyph is not None:
            for r, row in enumerate(glyph):
                for col, bit in enumerate(row):
                    if bit == '1':
                        rect(cx + col * s, y + r * s, s, s, c)
        cx += 6 * s


def wrap(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines = []
    for word in text.split(' '):
        if not lines or len(lines[-1]) + 1 + len(word) > max_chars:
            lines.append(word)
        else:
            lines[-1] += ' ' + word
    return lines


# ------------------------------------------------------------------ icons
# Each icon draws inside an 88x88 box whose top-left is (x, y).

def icon_summit(x, y, c):
    # Three leaders at a table: three figures side by side.
    for i in range(3):
        fx = x + 10 + i * 26
        disc(fx + 8, y + 16, 8, c)
        rect(fx, y + 28, 16, 34, c)
    rect(x + 4, y + 66, 80, 4, c)


def icon_scales(x, y, c):
    # Scales of justice.
    rect(x + 42, y + 8, 4, 58, c)
    rect(x + 10, y + 12, 68, 4, c)
    triangle(x + 16, y + 18, x + 2, y + 42, x + 30, y + 42, c)
    triangle(x + 72, y + 18, x + 58, y + 42, x + 86, y + 42, c)
    rect(x + 28, y + 66, 32, 4, c)


def icon_bridge(x, y, c):
    # Arched bridge with two towers and a deck.
    rect(x + 14, y + 22, 6, 44, c)
    rect(x + 68, y + 22, 6, 44, c)
    rect(x + 2, y + 62, 84, 5, c)
    # Arch: polyline from left tower base up to the crown and down.
    pts = [(6, 60), (16, 44), (30, 34), (44, 30), (58, 34), (72, 44), (82, 60)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(x + ax, y + ay, x + bx, y + by, c, 3)
    # Suspenders.
    for sx in (22, 34, 54, 66):
        rect(x + sx, y + 40, 3, 22, c)


def icon_tank(x, y, c):
    # Tank in profile, barrel pointing right.
    rect(x + 8, y + 34, 56, 18, c)
    rect(x + 26, y + 22, 24, 12, c)
    line(x + 50, y + 27, x + 84, y + 20, c, 4)
    for wx in (18, 36, 54):
        disc(x + wx, y + 56, 6, c)
    rect(x + 2, y + 66, 84, 3, c)


def icon_cyclone(x, y, c):
    # Spiral storm: concentric rings around a calm eye.
    cx, cy = x + 44, y + 44
    for r in (32, 22, 12):
        disc(cx, cy, r, c)
        disc(cx, cy, r - 4, WHITE)
    disc(cx, cy, 5, c)


def icon_globe(x, y, c):
    # Globe with latitude lines and a meridian.
    cx, cy = x + 44, y + 44
    disc(cx, cy, 32, c)
    disc(cx, cy, 28, WHITE)
    rect(x + 18, y + 32, 52, 3, c)
    rect(x + 13, y + 42, 62, 3, c)
    rect(x + 18, y + 52, 52, 3, c)
    rect(x + 42, y + 14, 3, 60, c)


ICONS = {
    'summit': icon_summit,
    'scales': icon_scales,
    'bridge': icon_bridge,
    'tank': icon_tank,
    'cyclone': icon_cyclone,
    'globe': icon_globe,
}

# ---------------------------------------------------------------- stories
# Headlines and sublines are kept strictly to the verified facts.
STORIES = [
    {
        'kicker': 'SUMMIT',
        'color': (122, 31, 43),
        'icon': 'summit',
        'head': ['TRUMP, XI, PUTIN', 'MEET IN SHENZHEN'],
        'sub': 'First three-way summit ends with a joint declaration on '
               'nuclear risks and stable energy flows.',
    },
    {
        'kicker': 'THE HAGUE',
        'color': (31, 78, 121),
        'icon': 'scales',
        'head': ['ICJ RULES AGAINST', 'MYANMAR'],
        'sub': 'Court finds Myanmar liable in the Rohingya genocide case '
               'brought by The Gambia in 2019.',
    },
    {
        'kicker': 'UKRAINE',
        'color': (192, 86, 33),
        'icon': 'bridge',
        'head': ['KERCH BRIDGE HIT', 'THIRD TIME IN WEEK'],
        'sub': 'Ukraine strikes the Crimean bridge again, the third '
               'attack in seven days.',
    },
    {
        'kicker': 'GAZA',
        'color': (91, 44, 111),
        'icon': 'tank',
        'head': ['ISRAELI TANKS PUSH', 'INTO CENTRAL GAZA'],
        'sub': 'Advance beyond the ceasefire line draws a Hamas '
               'accusation of a violation.',
    },
    {
        'kicker': 'WEATHER',
        'color': (14, 116, 144),
        'icon': 'cyclone',
        'head': ['CYCLONE AKVAN', 'NEARS INDIA COAST'],
        'sub': 'Severe storm to hit Andhra Pradesh-Odisha on Friday, '
               'winds 90-100 km/h, gusts to 110.',
    },
    {
        'kicker': 'CLIMATE',
        'color': (46, 125, 50),
        'icon': 'globe',
        'head': ['COP31 TALKS ENTER', 'FINAL STAGE'],
        'sub': 'Fossil-fuel wording still unresolved as negotiators '
               'weigh transition away vs phaseout.',
    },
]

# ------------------------------------------------------------------ layout
MASTHEAD_H = 156
GRID_X, GRID_Y = 12, 168
PANEL_W, PANEL_H = 494, 272
GAP = 12


def draw_masthead():
    rect(0, 0, W, MASTHEAD_H, NAVY)
    title = 'THE WORLD IN ONE DAY'
    tw = text_width(title, 6)
    draw_text((W - tw) // 2, 26, 6, WHITE, title)
    rect(212, 84, 600, 3, GOLD)
    date = 'THURSDAY 19 NOVEMBER 2026'
    dw = text_width(date, 3)
    draw_text((W - dw) // 2, 98, 3, GOLD, date)
    tag = 'SIX STORIES FROM AROUND THE GLOBE'
    gw = text_width(tag, 2)
    draw_text((W - gw) // 2, 128, 2, (180, 186, 200), tag)


def draw_panel(px, py, story):
    # Card with a thin ink border.
    rect(px, py, PANEL_W, PANEL_H, WHITE)
    rect(px, py, PANEL_W, 2, INK)
    rect(px, py + PANEL_H - 2, PANEL_W, 2, INK)
    rect(px, py, 2, PANEL_H, INK)
    rect(px + PANEL_W - 2, py, 2, PANEL_H, INK)
    # Coloured kicker band.
    rect(px + 2, py + 2, PANEL_W - 4, 32, story['color'])
    draw_text(px + 14, py + 11, 2, WHITE, story['kicker'])
    # Headline, two lines, scale 3, on the left; icon on the right.
    hy = py + 46
    for i, hline in enumerate(story['head']):
        draw_text(px + 14, hy + i * 26, 3, INK, hline)
    ICONS[story['icon']](px + PANEL_W - 102, py + 42, story['color'])
    # Subline, scale 2, full card width.
    sy = py + 138
    for i, sline in enumerate(wrap(story['sub'], 38)):
        draw_text(px + 14, sy + i * 17, 2, MUTED, sline)
    # Thin coloured rule near the foot of the card.
    rect(px + 14, py + PANEL_H - 22, PANEL_W - 28, 2, story['color'])


def draw():
    fill(PAPER)
    draw_masthead()
    for idx, story in enumerate(STORIES):
        col = idx % 2
        row = idx // 2
        px = GRID_X + col * (PANEL_W + GAP)
        py = GRID_Y + row * (PANEL_H + GAP)
        draw_panel(px, py, story)


# --------------------------------------------------------------------- PNG
def png_bytes():
    raw = b''.join(
        b'\x00' + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H)
    )
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        body = tag + data
        return (struct.pack('>I', len(data)) + body +
                struct.pack('>I', zlib.crc32(body) & 0xffffffff))

    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', 'out')
    os.makedirs(out_dir, exist_ok=True)
    draw()
    path = os.path.join(out_dir, 'entry.png')
    with open(path, 'wb') as f:
        f.write(png_bytes())


if __name__ == '__main__':
    main()
