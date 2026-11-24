#!/usr/bin/env python3
"""Draw the news-image-20261123 entry: one 1024x1024 picture summing up the
world news of Monday 23 November 2026. Pure Pillow, no network, deterministic.

Six stories, each first reported on 23 November 2026 and verified against
live news the same evening (AP via the Korea Herald, BusinessWorld, Daily
Summary of World):
  hero  Nvidia's board reinstates Jensen Huang as CEO (Trump intervened)
  grid  Ukraine sinks a Russian warship off Libya; Democrats take the House
        with 258 seats; COP31 collapses; US sanctions Iran's shadow banks
  strip Indonesia factory fire kills 24, about 30 still missing

Run: python3 tools/make_image.py  (writes entry.png at the repository root)
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CANVAS = (1024, 1024)

PALETTE = {
    "paper": (247, 243, 234),
    "ink": (26, 26, 26),
    "navy": (20, 33, 61),
    "red": (193, 18, 31),
    "white": (255, 255, 255),
    "grey": (90, 90, 90),
    "body": (60, 60, 60),
    "line": (200, 195, 180),
    "card_edge": (210, 205, 190),
    "pale_blue": (170, 190, 220),
    "green": (118, 185, 0),
    "dark_green": (38, 84, 0),
    "blue": (29, 78, 216),
    "climate": (45, 106, 79),
    "purple": (91, 42, 134),
    "bronze": (146, 64, 14),
    "flame": (234, 88, 12),
    "ember": (250, 204, 21),
}

FONT_ROOT = Path("/usr/share/fonts/truetype/noto")
FONTS = {
    "display_black": FONT_ROOT / "NotoSansDisplay-Black.ttf",
    "display_bold": FONT_ROOT / "NotoSansDisplay-Bold.ttf",
    "sans_bold": FONT_ROOT / "NotoSans-Bold.ttf",
    "sans": FONT_ROOT / "NotoSans-Regular.ttf",
    "serif_bold": FONT_ROOT / "NotoSerif-Bold.ttf",
}


def load(name, size):
    return ImageFont.truetype(str(FONTS[name]), size)


def fit_lines(draw, text, fname, size, max_width):
    """Split text into lines that fit max_width at the given font."""
    fnt = load(fname, size)
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=fnt) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- icons
# Each icon draws inside a square box (x, y, size) in one colour.

def icon_chip(d, x, y, s, color, dark):
    cx, cy = x + s / 2, y + s / 2
    body = s * 0.52
    for side in range(4):
        for k in range(4):
            off = -body * 0.36 + k * body * 0.24
            if side == 0:
                d.line([cx + off, y, cx + off, cy - body / 2], fill=color, width=5)
            elif side == 1:
                d.line([cx + off, cy + body / 2, cx + off, y + s], fill=color, width=5)
            elif side == 2:
                d.line([x, cy + off, cx - body / 2, cy + off], fill=color, width=5)
            else:
                d.line([cx + body / 2, cy + off, x + s, cy + off], fill=color, width=5)
    d.rounded_rectangle([cx - body / 2, cy - body / 2, cx + body / 2, cy + body / 2],
                        radius=8, fill=color)
    inner = body * 0.45
    d.rounded_rectangle([cx - inner, cy - inner, cx + inner, cy + inner],
                        radius=5, fill=dark)
    d.text((cx, cy), "AI", font=load("sans_bold", 26), fill=PALETTE["white"],
           anchor="mm")


def icon_ship(d, x, y, s, color):
    # Sea drone overhead.
    dx, dy = x + s * 0.60, y + 2
    d.ellipse([dx - 8, dy, dx + 2, dy + 8], fill=color)
    d.ellipse([dx + 20, dy, dx + 30, dy + 8], fill=color)
    d.rectangle([dx + 2, dy + 3, dx + 20, dy + 9], fill=color)
    d.line([dx - 4, dy + 1, dx + 26, dy + 1], fill=color, width=2)
    # Hull and tower.
    d.polygon([(x + 2, y + s * 0.52), (x + s - 2, y + s * 0.52),
               (x + s * 0.86, y + s * 0.80), (x + s * 0.14, y + s * 0.80)],
              fill=color)
    d.rectangle([x + s * 0.30, y + s * 0.22, x + s * 0.58, y + s * 0.52],
                fill=color)
    d.rectangle([x + s * 0.62, y + s * 0.30, x + s * 0.72, y + s * 0.52],
                fill=color)
    d.line([x + s * 0.44, y + s * 0.06, x + s * 0.44, y + s * 0.22],
           fill=color, width=4)
    d.polygon([(x + s * 0.44, y + s * 0.06), (x + s * 0.60, y + s * 0.11),
               (x + s * 0.44, y + s * 0.16)], fill=color)
    for k in range(3):
        wx = x + k * s * 0.33
        d.arc([wx, y + s * 0.86, wx + s * 0.30, y + s * 0.98],
              start=180, end=360, fill=color, width=4)


def icon_capitol(d, x, y, s, color):
    cx = x + s / 2
    d.pieslice([cx - s * 0.26, y + s * 0.10, cx + s * 0.26, y + s * 0.52],
               start=180, end=360, fill=color)
    d.rectangle([x + s * 0.20, y + s * 0.10, x + s * 0.80, y + s * 0.16],
                fill=color)
    d.line([cx, y, cx, y + s * 0.10], fill=color, width=3)
    d.rectangle([cx, y + s * 0.02, cx + s * 0.10, y + s * 0.08], fill=color)
    d.rectangle([x + s * 0.14, y + s * 0.50, x + s * 0.86, y + s * 0.58],
                fill=color)
    for k in range(4):
        px = x + s * 0.18 + k * s * 0.19
        d.rectangle([px, y + s * 0.60, px + s * 0.07, y + s * 0.84], fill=color)
    d.rectangle([x + s * 0.08, y + s * 0.86, x + s * 0.92, y + s * 0.94],
                fill=color)


def icon_globe(d, x, y, s, color):
    d.ellipse([x, y, x + s, y + s], outline=color, width=6)
    d.ellipse([x + s * 0.30, y + 2, x + s * 0.70, y + s - 2], outline=color,
              width=4)
    d.ellipse([x + s * 0.10, y + s * 0.22, x + s * 0.90, y + s * 0.78],
              outline=color, width=3)
    d.line([x + 2, y + s / 2, x + s - 2, y + s / 2], fill=color, width=4)


def icon_bank(d, x, y, s, color):
    # A bank front with a sanctions slash across it.
    d.polygon([(x, y + s * 0.24), (x + s, y + s * 0.24),
               (x + s / 2, y + s * 0.04)], fill=color)
    d.rectangle([x + s * 0.06, y + s * 0.26, x + s * 0.94, y + s * 0.34],
                fill=color)
    for k in range(3):
        px = x + s * 0.14 + k * s * 0.30
        d.rectangle([px, y + s * 0.38, px + s * 0.10, y + s * 0.80], fill=color)
    d.rectangle([x + s * 0.04, y + s * 0.82, x + s * 0.96, y + s * 0.92],
                fill=color)
    d.line([x + s * 0.06, y + s * 0.94, x + s * 0.94, y + s * 0.06],
           fill=PALETTE["red"], width=7)


def icon_flame(d, x, y, s, color):
    # Outer flame: a flicking teardrop; inner flame in ember yellow.
    outer = [(0.50, 0.02), (0.62, 0.20), (0.74, 0.34), (0.80, 0.52),
             (0.76, 0.72), (0.62, 0.88), (0.40, 0.94), (0.22, 0.84),
             (0.12, 0.64), (0.14, 0.44), (0.26, 0.28), (0.36, 0.12)]
    d.polygon([(x + fx * s, y + fy * s) for fx, fy in outer], fill=color)
    inner = [(0.50, 0.34), (0.60, 0.48), (0.64, 0.62), (0.58, 0.78),
             (0.44, 0.82), (0.34, 0.70), (0.34, 0.54), (0.42, 0.42)]
    d.polygon([(x + fx * s, y + fy * s) for fx, fy in inner],
              fill=PALETTE["ember"])
    for sx, sy, r in [(0.12, 0.10, 3), (0.88, 0.16, 3), (0.92, 0.72, 2)]:
        d.ellipse([x + sx * s - r, y + sy * s - r, x + sx * s + r,
                   y + sy * s + r], fill=color)


ICONS = {
    "ship": icon_ship,
    "capitol": icon_capitol,
    "globe": icon_globe,
    "bank": icon_bank,
    "flame": icon_flame,
}

# ---------------------------------------------------------------- stories

GRID = [
    {"tag": "WAR  •  UKRAINE", "color": "red", "icon": "ship",
     "headline": "KYIV SAYS IT SANK RUSSIAN WARSHIP",
     "summary": "Sea drones sink the corvette Merkury off Libya. "
                "Russian strikes kill 15 near Kyiv."},
    {"tag": "POLITICS  •  USA", "color": "blue", "icon": "capitol",
     "headline": "DEMOCRATS TAKE THE HOUSE",
     "summary": "Biggest House majority since 1992: at least 258 seats."},
    {"tag": "CLIMATE  •  COP31", "color": "climate", "icon": "globe",
     "headline": "COP31 COLLAPSES",
     "summary": "Climate talks end with no deal as the EU rejects a text "
                "silent on fossil fuels."},
    {"tag": "SANCTIONS  •  IRAN", "color": "purple", "icon": "bank",
     "headline": "US SANCTIONS IRAN'S SHADOW BANKS",
     "summary": "Treasury targets dozens of exchange houses and front firms."},
]


def draw_cell(d, x, y, w, h, story):
    color = PALETTE[story["color"]]
    d.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=PALETTE["white"],
                        outline=PALETTE["card_edge"], width=2)
    d.rounded_rectangle([x, y, x + w, y + 36], radius=12, fill=color)
    d.rectangle([x, y + 24, x + w, y + 36], fill=color)
    d.text((x + 16, y + 18), story["tag"], font=load("sans_bold", 21),
           fill=PALETTE["white"], anchor="lm")
    text_w = w - 32 - 88
    yy = y + 48
    for line in fit_lines(d, story["headline"], "display_bold", 30, text_w)[:2]:
        d.text((x + 16, yy), line, font=load("display_bold", 30),
               fill=PALETTE["ink"])
        yy += 32
    yy = y + 118
    for line in fit_lines(d, story["summary"], "sans", 23, text_w)[:3]:
        d.text((x + 16, yy), line, font=load("sans", 23),
               fill=PALETTE["body"])
        yy += 27
    ICONS[story["icon"]](d, x + w - 88, y + 58, 68, color)


def draw_hero_visual(d, x, y, w, h):
    """Dark green panel: NVDA label, chip, rising chart."""
    p = PALETTE
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=p["dark_green"])
    cx = x + w // 2
    d.text((cx, y + 30), "NVDA  SURGES", font=load("sans_bold", 32),
           fill=p["white"], anchor="mm")
    icon_chip(d, cx - 62, y + 66, 124, p["green"], p["dark_green"])
    pts = []
    for k, drop in enumerate([28, 40, 35, 52, 62, 74]):
        pts.append((x + 32 + k * 57, y + h - drop))
    d.line(pts, fill=p["green"], width=6, joint="curve")
    hx, hy = pts[-1]
    d.polygon([(hx, hy), (hx - 18, hy + 2), (hx - 8, hy + 16)], fill=p["green"])


def main():
    p = PALETTE
    img = Image.new("RGB", CANVAS, p["paper"])
    d = ImageDraw.Draw(img)

    # Masthead: the day, named loud.
    d.rectangle([0, 0, 1024, 146], fill=p["navy"])
    d.text((512, 28), "THE WORLD IN ONE DAY", font=load("sans_bold", 24),
           fill=p["pale_blue"], anchor="mm")
    d.text((512, 88), "MONDAY, 23 NOVEMBER 2026", font=load("serif_bold", 54),
           fill=p["white"], anchor="mm")
    d.rectangle([0, 146, 1024, 152], fill=p["red"])

    # Hero: Huang returns to Nvidia.
    d.text((28, 166), "TECH  •  UNITED STATES", font=load("sans_bold", 23),
           fill=p["red"])
    d.text((28, 192), "HUANG RETURNS", font=load("display_black", 68),
           fill=p["navy"])
    d.text((28, 260), "TO NVIDIA", font=load("display_black", 68),
           fill=p["navy"])
    hero = ("Nvidia's board reinstates Jensen Huang as CEO after Trump "
            "intervenes. Shares jump.")
    yy = 340
    for line in fit_lines(d, hero, "sans", 25, 600):
        d.text((28, yy), line, font=load("sans", 25), fill=p["ink"])
        yy += 32
    draw_hero_visual(d, 648, 164, 348, 272)
    d.line([28, 452, 996, 452], fill=p["line"], width=2)

    # Grid of four stories.
    gx, gy, cw, ch, hgap, vgap = 28, 468, 474, 200, 20, 12
    for i, story in enumerate(GRID):
        cx = gx + (i % 2) * (cw + hgap)
        cy = gy + (i // 2) * (ch + vgap)
        draw_cell(d, cx, cy, cw, ch, story)

    # Bottom strip: the Indonesia factory fire.
    y = 892
    d.rounded_rectangle([28, y, 996, y + 94], radius=12, fill=p["white"],
                        outline=p["card_edge"], width=2)
    d.text((48, y + 10), "DISASTER  •  INDONESIA", font=load("sans_bold", 21),
           fill=p["bronze"])
    d.text((48, y + 32), "FACTORY FIRE KILLS 24",
           font=load("display_bold", 33), fill=p["ink"])
    d.text((48, y + 66), "Blaze at a Banten confectionery factory kills 24; "
           "some 30 still missing.", font=load("sans", 23), fill=p["body"])
    icon_flame(d, 908, y + 12, 72, p["flame"])

    # Footer.
    d.text((512, 1002), "Six stories that defined the day  •  Sources: AP, "
           "Reuters, BusinessWorld, Daily Summary of World  •  23 November 2026",
           font=load("sans", 18), fill=p["grey"], anchor="mm")

    out = Path(__file__).resolve().parent.parent / "entry.png"
    img.save(out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
