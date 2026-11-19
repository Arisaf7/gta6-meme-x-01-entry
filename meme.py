#!/usr/bin/env python3
"""gta6-meme-x-01 meme maker.

Draws the GTA 6 launch-week meme for the make.fun gta6-meme-x-01
competition and writes it to meme.png (or $MEME_OUT).

The joke: waited 13 years for GTA 6, finished it in 3 days, and now
the grind pays on make.fun. The make.fun ghost mascot holds a money
bag next to a Vice-City-style sunset street scene, with the make.fun
name in the bottom banner. Pure Python 3 standard library: a built-in
5x7 bitmap font and a hand-written PNG encoder (zlib + CRC). No
network, no randomness, no timestamps: two runs write identical bytes.
"""

import binascii
import math
import os
import struct
import zlib

WIDTH = 1200
HEIGHT = 675

NAVY = (16, 42, 67)
INK = (22, 30, 40)
WHITE = (255, 255, 255)
GOLD = (245, 200, 60)
PINK = (255, 80, 140)
BAG_GREEN = (40, 160, 80)
PALM_GREEN = (25, 130, 70)
TRUNK = (70, 40, 80)
ROAD = (38, 38, 48)
SEA = (18, 70, 130)
WAVE = (130, 190, 220)
SUN = (255, 225, 130)
RAY = (255, 200, 100)
SKY = [
    (255, 150, 70),
    (255, 120, 90),
    (255, 95, 130),
    (230, 80, 150),
    (170, 70, 170),
    (120, 60, 160),
]
CAR_WHITE = (245, 245, 245)
GLASS = (150, 210, 240)
TYRE = (20, 20, 25)
HUB = (180, 180, 180)
LIGHT_Y = (255, 220, 80)
LIGHT_R = (220, 40, 40)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, uppercase + digits + punctuation. Each glyph is 7 rows
# of 5 bits written as strings; "1" is an inked pixel.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

CHAR_W = 5
CHAR_H = 7


def text_width(text, scale):
    """Pixel width of text at the given scale (1px tracking)."""
    return len(text) * (CHAR_W * scale + scale) - scale


def draw_text(px, x, y, text, scale, color):
    """Draw uppercase text; unknown chars fall back to a blank."""
    cx = x
    step = CHAR_W * scale + scale
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(CHAR_H):
            bits = glyph[row]
            for col in range(CHAR_W):
                if bits[col] == "1":
                    fill_rect(px, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += step


def draw_text_centered(px, cx, y, text, scale, color):
    draw_text(px, cx - text_width(text, scale) // 2, y, text, scale, color)


# ------------------------------------------------------------- canvas -----
def new_canvas():
    return bytearray((255, 255, 255) * WIDTH * HEIGHT)


def set_px(px, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(px, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    for yy in range(y0, y1):
        base = (yy * WIDTH + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def draw_hline(px, x, y, w, color):
    fill_rect(px, x, y, w, 1, color)


def draw_vline(px, x, y, h, color):
    fill_rect(px, x, y, 1, h, color)


def draw_line(px, x0, y0, x1, y1, color):
    """Bresenham line, 1px wide."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(px, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_thick_line(px, x0, y0, x1, y1, r, color):
    """Line drawn as a chain of filled circles of radius r."""
    dist = max(1, int(math.hypot(x1 - x0, y1 - y0)))
    for i in range(dist + 1):
        t = i / dist
        fill_circle(px, int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t),
                    r, color)


def fill_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(px, xx, yy, color)


def fill_polygon(px, points, color):
    """Scanline fill of a simple polygon (even-odd rule)."""
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(HEIGHT, max(ys)) + 1):
        nodes = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                nodes.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
        nodes.sort()
        for i in range(0, len(nodes) - 1, 2):
            draw_hline(px, nodes[i], y, nodes[i + 1] - nodes[i], color)


def draw_star(px, cx, cy, r, color):
    """Five-point star as a filled polygon."""
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else int(r * 0.45)
        pts.append((int(cx + rr * math.cos(ang)),
                    int(cy + rr * math.sin(ang))))
    fill_polygon(px, pts, color)


# -------------------------------------------------------------- png ------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(px):
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)  # filter: none
        raw += px[y * WIDTH * 3:(y + 1) * WIDTH * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------ artwork ----
def draw_sky(px):
    band_h = 70
    for i, color in enumerate(SKY):
        fill_rect(px, 0, i * band_h, WIDTH, band_h, color)


def draw_sun(px):
    cx, cy = 300, 300
    for k in range(12):
        ang = math.radians(k * 30)
        x0 = int(cx + 100 * math.cos(ang))
        y0 = int(cy + 100 * math.sin(ang))
        x1 = int(cx + 122 * math.cos(ang))
        y1 = int(cy + 122 * math.sin(ang))
        draw_thick_line(px, x0, y0, x1, y1, 2, RAY)
    fill_circle(px, cx, cy, 85, SUN)


def draw_birds(px):
    for bx, by in ((470, 140), (540, 118), (620, 152)):
        draw_line(px, bx - 12, by, bx, by - 8, INK)
        draw_line(px, bx, by - 8, bx + 12, by, INK)


def draw_ocean(px):
    fill_rect(px, 0, 420, WIDTH, 85, SEA)
    for wy in (440, 462, 484):
        for wx in range(20, WIDTH - 20, 64):
            draw_hline(px, wx, wy, 32, WAVE)


def draw_road(px):
    fill_rect(px, 0, 505, WIDTH, HEIGHT - 505, ROAD)
    draw_hline(px, 0, 505, WIDTH, WHITE)


def draw_palm(px, base_x, top_x, top_y):
    draw_thick_line(px, base_x, 505, top_x, top_y, 5, TRUNK)
    tips = [(top_x - 55, top_y - 35), (top_x - 35, top_y - 62),
            (top_x, top_y - 72), (top_x + 38, top_y - 60),
            (top_x + 58, top_y - 32), (top_x + 62, top_y - 2)]
    for tx, ty in tips:
        draw_thick_line(px, top_x, top_y, tx, ty, 4, PALM_GREEN)
    fill_circle(px, top_x - 8, top_y + 8, 6, (120, 80, 40))
    fill_circle(px, top_x + 8, top_y + 8, 6, (120, 80, 40))


def draw_car(px):
    # speed lines behind the car
    for sx, sy, sw in ((330, 552, 46), (312, 566, 54), (338, 580, 38)):
        draw_hline(px, sx, sy, sw, (200, 200, 210))
    # shadow
    fill_rect(px, 390, 606, 420, 6, (25, 25, 35))
    # body
    fill_rect(px, 400, 540, 400, 42, CAR_WHITE)
    fill_circle(px, 400, 561, 21, CAR_WHITE)
    fill_circle(px, 800, 561, 21, CAR_WHITE)
    # pink stripe
    fill_rect(px, 400, 556, 400, 8, PINK)
    # cabin + windows
    fill_rect(px, 520, 512, 160, 30, CAR_WHITE)
    fill_rect(px, 530, 518, 60, 22, GLASS)
    fill_rect(px, 610, 518, 60, 22, GLASS)
    # lights
    fill_rect(px, 792, 548, 10, 8, LIGHT_Y)
    fill_rect(px, 398, 548, 8, 8, LIGHT_R)
    # wheels
    for wx in (470, 730):
        fill_circle(px, wx, 584, 24, TYRE)
        fill_circle(px, wx, 584, 10, HUB)


def draw_wanted_stars(px):
    for i, sx in enumerate((960, 1000, 1040, 1080, 1120)):
        draw_star(px, sx, 95, 20, GOLD)


def draw_ghost(px):
    # sheet body: round top, straight sides, wavy bottom
    fill_circle(px, 935, 250, 75, WHITE)
    fill_rect(px, 860, 250, 150, 95, WHITE)
    for bx in (885, 935, 985):
        fill_circle(px, bx, 345, 25, WHITE)
    # eyes + smile
    fill_circle(px, 905, 270, 11, INK)
    fill_circle(px, 965, 270, 11, INK)
    draw_line(px, 920, 298, 935, 308, INK)
    draw_line(px, 935, 308, 950, 298, INK)
    # arms
    draw_thick_line(px, 872, 302, 834, 330, 6, WHITE)
    draw_thick_line(px, 998, 302, 1032, 326, 6, WHITE)


def draw_money_bag(px):
    # knot + sack with a $ on it
    fill_polygon(px, [(1048, 306), (1072, 306), (1060, 322)], BAG_GREEN)
    fill_circle(px, 1060, 352, 34, BAG_GREEN)
    draw_text(px, 1052, 340, "$", 3, GOLD)


def draw_bubble(px):
    # speech bubble with a tail pointing at the ghost
    fill_rect(px, 520, 195, 310, 105, WHITE)
    draw_hline(px, 520, 195, 310, NAVY)
    draw_hline(px, 520, 299, 310, NAVY)
    draw_vline(px, 520, 195, 105, NAVY)
    draw_vline(px, 829, 195, 105, NAVY)
    fill_polygon(px, [(790, 300), (830, 300), (862, 252)], WHITE)
    draw_line(px, 790, 300, 862, 252, NAVY)
    draw_line(px, 830, 300, 862, 252, NAVY)
    draw_text_centered(px, 675, 218, "FINISHED IT", 3, NAVY)
    draw_text_centered(px, 675, 252, "IN 3 DAYS.", 3, NAVY)


def draw_banners(px):
    fill_rect(px, 0, 0, WIDTH, 64, NAVY)
    draw_text_centered(px, WIDTH // 2, 14, "WAITED 13 YEARS FOR GTA 6",
                       6, WHITE)
    fill_rect(px, 0, 618, WIDTH, HEIGHT - 618, NAVY)
    first = "NOW THE GRIND PAYS ME - "
    second = "MAKE.FUN"
    total = text_width(first, 4) + 12 + text_width(second, 4)
    x = (WIDTH - total) // 2
    draw_text(px, x, 634, first, 4, WHITE)
    draw_text(px, x + text_width(first, 4) + 12, 634, second, 4, GOLD)


# -------------------------------------------------------------- build ----
def build():
    px = new_canvas()
    draw_sky(px)
    draw_sun(px)
    draw_birds(px)
    draw_ocean(px)
    draw_road(px)
    draw_palm(px, 70, 55, 310)
    draw_palm(px, 1150, 1165, 320)
    draw_car(px)
    draw_wanted_stars(px)
    draw_ghost(px)
    draw_money_bag(px)
    draw_bubble(px)
    draw_banners(px)
    return encode_png(px)


def main():
    out = os.environ.get("MEME_OUT", "meme.png")
    data = build()
    with open(out, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (out, len(data)))


if __name__ == "__main__":
    main()
