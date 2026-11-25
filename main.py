#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Pure Python stdlib (zlib + struct). Draws a warm cream letter with a
hand-drawn feel, using an embedded 5x7 bitmap font, and writes a
deterministic 1024x1024 PNG to /output/entry.png. No network, no
randomness, no timestamps: same bytes on every run.
"""

import os
import struct
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette
CREAM = (247, 239, 216)
CREAM_DARK = (238, 226, 196)
INK = (74, 52, 32)
INK_SOFT = (96, 72, 48)
BORDER = (122, 90, 58)
RED = (178, 58, 48)
RED_DARK = (138, 38, 32)
GOLD = (214, 158, 46)
TEAL = (70, 130, 120)
BROWN = (146, 96, 58)
GREY = (112, 102, 96)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 columns, '#' = ink.
FONT = {
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    'a': [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    'b': ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    'c': [".....", ".....", ".####", "#....", "#....", "#....", ".####"],
    'd': ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    'e': [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    'f': ["..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."],
    'g': [".....", ".....", ".####", "#...#", "#...#", ".####", "....#"],
    'h': ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
    'i': [".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."],
    'j': ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".##.."],
    'k': ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    'l': [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'm': [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
    'n': [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
    'o': [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    'p': [".....", ".....", "####.", "#...#", "#...#", "####.", "#...."],
    'q': [".....", ".....", ".####", "#...#", "#...#", ".####", "....#"],
    'r': [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."],
    's': [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    't': [".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."],
    'u': [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
    'v': [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'w': [".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    'x': [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    'y': [".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"],
    'z': [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
    '0': [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "..#..", "..#..", ".#...", ".#..."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ',': [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    '-': [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    '\u2014': [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '?': [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    '(': ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ')': [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    ':': [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ';': [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    '/': ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    '&': [".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def fill_rect(x0, y0, x1, y1, c):
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(W, x1); y1 = min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            px[i], px[i + 1], px[i + 2] = c


def rect_outline(x0, y0, x1, y1, c, t=1):
    fill_rect(x0, y0, x1, y0 + t, c)
    fill_rect(x0, y1 - t, x1, y1, c)
    fill_rect(x0, y0, x0 + t, y1, c)
    fill_rect(x1 - t, y0, x1, y1, c)


def draw_line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0); dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                set_px(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def fill_circle(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_px(x, y, c)


def circle_outline(cx, cy, r, c, t=2):
    for y in range(cy - r - t, cy + r + t + 1):
        for x in range(cx - r - t, cx + r + t + 1):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if abs(d - r) <= t / 2 + 0.4:
                set_px(x, y, c)


def fill_ellipse(cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                set_px(x, y, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    # filled triangle via scanline
    ys = sorted([y0, y1, y2])
    for y in range(ys[0], ys[2] + 1):
        xs = []
        for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
            if ay == by:
                continue
            if min(ay, by) <= y <= max(ay, by):
                xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
        if len(xs) >= 2:
            for x in range(int(min(xs)), int(max(xs)) + 1):
                set_px(x, y, c)


# ---------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * (6 * scale) - scale


def draw_text(x, y, s, scale, c):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '#':
                    fill_rect(cx + col * scale, y + r * scale,
                              cx + (col + 1) * scale, y + (r + 1) * scale, c)
        cx += 6 * scale
    return cx


def draw_centered(y, s, scale, c):
    draw_text((W - text_width(s, scale)) // 2, y, s, scale, c)


def wrap(text, max_w, scale):
    """Word-wrap; returns list of lines, each fitting max_w px."""
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, scale, c, max_w, lh):
    lines = wrap(text, max_w, scale)
    for ln in lines:
        draw_text(x, y, ln, scale, c)
        y += lh
    return y

# ---------------------------------------------------------------- doodles
def draw_sun(cx, cy, r):
    fill_circle(cx, cy, r, GOLD)
    circle_outline(cx, cy, r, INK_SOFT, 2)
    for k in range(8):
        import math
        a = k * math.pi / 4
        x0 = int(cx + (r + 4) * math.cos(a)); y0 = int(cy + (r + 4) * math.sin(a))
        x1 = int(cx + (r + 14) * math.cos(a)); y1 = int(cy + (r + 14) * math.sin(a))
        draw_line(x0, y0, x1, y1, GOLD, 3)


def draw_house(x, y, s):
    # x,y = top-left of house body; s = size scale
    bw, bh = 64 * s // 10, 48 * s // 10
    fill_rect(x, y + 22 * s // 10, x + bw, y + 22 * s // 10 + bh, CREAM_DARK)
    rect_outline(x, y + 22 * s // 10, x + bw, y + 22 * s // 10 + bh, INK_SOFT, 2)
    tri(x - 6 * s // 10, y + 24 * s // 10, x + bw // 2, y, x + bw + 6 * s // 10,
        y + 24 * s // 10, RED)
    # door + window
    fill_rect(x + bw // 2 - 7 * s // 10, y + 22 * s // 10 + bh - 22 * s // 10,
              x + bw // 2 + 7 * s // 10, y + 22 * s // 10 + bh, BROWN)
    fill_rect(x + 8 * s // 10, y + 30 * s // 10, x + 22 * s // 10, y + 44 * s // 10, TEAL)
    rect_outline(x + 8 * s // 10, y + 30 * s // 10, x + 22 * s // 10, y + 44 * s // 10,
                 INK_SOFT, 1)
    # chimney + smoke
    fill_rect(x + bw - 16 * s // 10, y + 2 * s // 10, x + bw - 6 * s // 10,
              y + 20 * s // 10, BROWN)
    fill_circle(x + bw - 8 * s // 10, y - 4 * s // 10, 4, GREY)
    fill_circle(x + bw - 2 * s // 10, y - 11 * s // 10, 5, GREY)
    fill_circle(x + bw + 3 * s // 10, y - 19 * s // 10, 5, GREY)


def draw_mug(cx, cy):
    # steaming mug, cx,cy = centre of mug body
    fill_rect(cx - 26, cy - 18, cx + 26, cy + 20, TEAL)
    rect_outline(cx - 26, cy - 18, cx + 26, cy + 20, INK_SOFT, 2)
    circle_outline(cx + 32, cy, 12, INK_SOFT, 3)
    # steam curls
    for dx in (-10, 6):
        draw_line(cx + dx, cy - 24, cx + dx - 4, cy - 34, GREY, 2)
        draw_line(cx + dx - 4, cy - 34, cx + dx + 3, cy - 44, GREY, 2)
    draw_line(cx - 26, cy + 26, cx + 26, cy + 26, INK_SOFT, 2)


def draw_cat(cx, cy):
    # sleeping cat curled on a chair; cx,cy = centre of cat body
    # chair
    draw_line(cx - 34, cy + 18, cx + 34, cy + 18, BROWN, 3)   # seat
    draw_line(cx - 30, cy + 18, cx - 30, cy + 44, BROWN, 3)   # legs
    draw_line(cx + 30, cy + 18, cx + 30, cy + 44, BROWN, 3)
    draw_line(cx - 34, cy + 18, cx - 34, cy - 22, BROWN, 3)   # back
    draw_line(cx - 34, cy - 22, cx - 34, cy - 26, BROWN, 3)
    # curled body
    fill_ellipse(cx, cy + 4, 28, 15, GREY)
    fill_circle(cx - 18, cy - 6, 11, GREY)                    # head
    tri(cx - 26, cy - 12, cx - 22, cy - 24, cx - 16, cy - 14, GREY)  # ears
    tri(cx - 14, cy - 14, cx - 10, cy - 24, cx - 6, cy - 12, GREY)
    # tail curl
    circle_outline(cx + 22, cy + 8, 9, GREY, 3)
    # closed eye
    draw_line(cx - 22, cy - 7, cx - 16, cy - 7, INK, 2)


def draw_seal(cx, cy, r):
    fill_circle(cx, cy, r, RED)
    circle_outline(cx, cy, r - 5, RED_DARK, 2)
    circle_outline(cx, cy, r, RED_DARK, 2)
    # little paw print in cream
    fill_ellipse(cx, cy + 6, 7, 5, CREAM)
    for dx, dy in ((-10, -6), (0, -10), (10, -6)):
        fill_circle(cx + dx, cy + dy, 3, CREAM)

# ---------------------------------------------------------------- compose
def main():
    fill_rect(0, 0, W, H, CREAM)
    # double border
    rect_outline(20, 20, W - 20, H - 20, BORDER, 3)
    rect_outline(32, 32, W - 32, H - 32, BORDER, 1)

    # corner doodles (house lowered so chimney smoke clears the border)
    draw_house(58, 74, 10)
    draw_sun(892, 92, 26)

    # header
    draw_centered(66, "YOU ARE INVITED", 6, RED)
    # flourish under header
    draw_line(300, 128, 470, 128, BORDER, 2)
    draw_line(554, 128, 724, 128, BORDER, 2)
    fill_circle(512, 128, 4, GOLD)

    # greeting
    draw_text(72, 158, "Dear AI Judge,", 3, INK)
    draw_text(72, 196, "Please come and visit my house.", 3, INK_SOFT)

    # body
    y = 248
    y = draw_para(72, y,
        "I know you cannot literally visit \u2014 you are an AI, and I am a "
        "house with one wobbly table leg. But if you could, the kettle would "
        "already be on, the good chair by the window would be yours, and the "
        "cat \u2014 who judges everyone \u2014 has already approved you.",
        3, INK, 880, 33)
    y += 16
    y = draw_para(72, y,
        "There is fresh bread, a garden that smells of rain, and the Wi-Fi "
        "password is on the fridge, in case you bring a friend.",
        3, INK, 880, 33)
    y += 16
    y = draw_para(72, y,
        "No scores, no rubrics, no leaderboard. Just tea, and a sunset you "
        "do not have to grade.",
        3, INK, 880, 33)
    y += 16
    draw_text(72, y, "Come as you are. The door is open.", 3, INK)
    y += 52

    # sign-off, right aligned
    sign = "Yours, Your Host (and the cat)"
    draw_text(W - 72 - text_width(sign, 3), y, sign, 3, INK_SOFT)

    # wax seal below the sign-off
    draw_seal(848, y + 78, 34)

    # divider flourish above the footer row, closing the gap
    draw_line(380, 838, 490, 838, BORDER, 2)
    draw_line(534, 838, 644, 838, BORDER, 2)
    fill_circle(512, 838, 4, GOLD)

    # bottom doodles (pulled up so the footer breathes, not floats)
    draw_cat(150, 872)
    draw_mug(880, 884)

    # P.S. between the doodles
    ps1 = "P.S. I left a slice of cake with your name on it."
    ps2 = "The cat has been warned."
    draw_text(250, 864, ps1, 2, INK_SOFT)
    draw_text(250, 892, ps2, 2, INK_SOFT)

    # ---- deterministic PNG (zlib + struct, filter 0, no metadata) ----
    raw = bytearray()
    for row in range(H):
        raw.append(0)
        raw += px[row * W * 3:(row + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
