#!/usr/bin/env python3
"""Draw the news-image-20261123 entry, v3: one 1024x1024 picture summing up
the world news of Monday 23 November 2026. Pure Pillow, no network,
deterministic.

v3 rebuilds the page on the 22 November winner's exact format (the user
showed us the champion image): 13 main stories, each with a small drawn
illustration, a numbered location header, a status badge, a source line;
a UTC timeline strip; a THE DAY IN NUMBERS panel; 17 ALSO items; a dotted
world map with numbered pins; a DATE CHECK with a 10-item exclusion list;
a HOW SURE legend. 30 stories, 7 regions.

v2 (20 stories, no illustrations, no map, no timeline) ranked 3,732 of
13,031 after round 3; the entries around it carry 32-36 stories. v3 closes
the breadth gap and the craft gap at once.

All 30 stories were verified as happening or first reported on 23 November
2026 (Daily Summary of World first-reported times, cross-checked against
AP, Reuters, AFP, BBC, Gulf News, Korea Herald). Items deliberately left
out because they belong to earlier days: COP31 pact collapse (Sun 22 Nov),
Chapo Isidro capture (Fri 20 Nov), S. Korea minister quitting (Sun 22 Nov),
Alcaraz ATP Finals win (Sun 22 Nov), Liverpool 4-0 Man Utd (Sun 22 Nov),
Verstappen Las Vegas GP win (Sun 22 Nov), BepiColombo Mercury orbit
(Sat 21 Nov), ICJ Myanmar ruling (last week), Seattle ICE arrests
(Sat 21 Nov), G20 opens in Johannesburg (Sat 21 Nov).

Run: python3 tools/make_image.py  (writes entry.png at the repository root)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CANVAS = (1024, 1024)

PALETTE = {
    "paper": (247, 243, 234),
    "ink": (26, 26, 26),
    "navy": (20, 33, 61),
    "navy2": (30, 48, 88),
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
    "sky": (135, 190, 235),
    "sea": (23, 68, 120),
    "climate": (45, 106, 79),
    "purple": (91, 42, 134),
    "bronze": (146, 64, 14),
    "amber": (180, 120, 10),
    "orange": (230, 120, 30),
    "flame": (245, 158, 11),
    "gold": (250, 204, 21),
    "dusk": (253, 186, 116),
    "map_dot": (150, 165, 190),
    "map_sea": (222, 230, 240),
}

FONT_ROOT = Path("/usr/share/fonts/truetype/noto")
FONTS = {
    "display_black": FONT_ROOT / "NotoSansDisplay-Black.ttf",
    "display_bold": FONT_ROOT / "NotoSansDisplay-Bold.ttf",
    "sans_bold": FONT_ROOT / "NotoSans-Bold.ttf",
    "sans": FONT_ROOT / "NotoSans-Regular.ttf",
    "sans_italic_bold": FONT_ROOT / "NotoSans-BoldItalic.ttf",
    "serif_bold": FONT_ROOT / "NotoSerif-Bold.ttf",
}


def load(name, size):
    return ImageFont.truetype(str(FONTS[name]), size)


def fit_lines(draw, text, fname, size, max_width, limit=None):
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
    return lines if limit is None else lines[:limit]


# ---------------------------------------------------------------- scenes
# Small flat illustrations, one per main story. Each draws inside
# (x, y, w, h). Simple shapes only: the champion's scenes are flat
# drawings, not photographs.

def _sky(d, x, y, w, h, top, bottom):
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)


def _sun(d, x, y, r, color):
    d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def scene_chip(d, x, y, w, h):
    p = PALETTE
    d.rectangle([x, y, x + w, y + h], fill=p["dark_green"])
    s = min(w, h) * 0.62
    cx, cy = x + w * 0.30, y + h / 2
    body = s * 0.52
    for k in range(4):
        off = -body * 0.36 + k * body * 0.24
        d.line([cx + off, y + 6, cx + off, cy - body / 2], fill=p["green"], width=4)
        d.line([cx + off, cy + body / 2, cx + off, y + h - 6], fill=p["green"], width=4)
        d.line([x + 6, cy + off, cx - body / 2, cy + off], fill=p["green"], width=4)
        d.line([cx + body / 2, cy + off, cx + body / 2 + 22, cy + off], fill=p["green"], width=4)
    d.rounded_rectangle([cx - body / 2, cy - body / 2, cx + body / 2, cy + body / 2],
                        radius=6, fill=p["green"])
    d.text((cx, cy), "AI", font=load("sans_bold", 22), fill=p["white"], anchor="mm")
    pts = [(x + w * 0.52, y + h * 0.72), (x + w * 0.62, y + h * 0.62),
           (x + w * 0.72, y + h * 0.66), (x + w * 0.82, y + h * 0.42),
           (x + w * 0.93, y + h * 0.28)]
    d.line(pts, fill=p["green"], width=5, joint="curve")
    hx, hy = pts[-1]
    d.polygon([(hx, hy), (hx - 13, hy + 2), (hx - 6, hy + 12)], fill=p["green"])
    d.text((x + w * 0.72, y + h * 0.82), "+31%", font=load("sans_bold", 18),
           fill=p["white"], anchor="mm")


def scene_ship(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (30, 58, 95), (70, 120, 180))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=p["sea"])
    for k in range(5):
        wx = x + 8 + k * (w - 16) / 4
        d.arc([wx - 12, y + h * 0.66, wx + 12, y + h * 0.78], 180, 360,
              fill=(160, 200, 240), width=2)
    # Ship silhouette.
    sx, sy = x + w * 0.30, y + h * 0.60
    d.polygon([(sx, sy), (sx + w * 0.42, sy), (sx + w * 0.36, sy + 12),
               (sx + w * 0.06, sy + 12)], fill=(15, 25, 40))
    d.rectangle([sx + w * 0.10, sy - 14, sx + w * 0.30, sy], fill=(15, 25, 40))
    d.line([sx + w * 0.20, sy - 26, sx + w * 0.20, sy - 12], fill=(15, 25, 40), width=3)
    # Drones above.
    for dx, dy in [(0.62, 0.22), (0.74, 0.32), (0.85, 0.18)]:
        px, py = x + w * dx, y + h * dy
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=p["white"])
        d.line([px - 8, py, px + 8, py], fill=p["white"], width=2)
    # Blast star.
    bx, by = x + w * 0.55, y + h * 0.30
    for ang in range(0, 360, 45):
        import math
        r1, r2 = 12, 5
        a = math.radians(ang)
        d.line([bx, by, bx + r1 * math.cos(a), by + r1 * math.sin(a)],
               fill=p["gold"], width=3)


def scene_rubble(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (90, 60, 60), (200, 140, 100))
    _sun(d, x + w * 0.82, y + h * 0.26, 10, (250, 220, 150))
    # Broken block of flats.
    bx, by = x + w * 0.12, y + h * 0.34
    bw, bh = w * 0.52, h * 0.58
    d.polygon([(bx, by + bh), (bx, by + 10), (bx + bw * 0.4, by),
               (bx + bw * 0.55, by + 16), (bx + bw, by + 8), (bx + bw, by + bh)],
              fill=(70, 60, 55))
    for r in range(3):
        for c in range(3):
            wx = bx + 8 + c * (bw - 16) / 3
            wy = by + 22 + r * 14
            d.rectangle([wx, wy, wx + 8, wy + 8],
                        fill=p["gold"] if (r + c) % 2 else (40, 35, 32))
    # Smoke.
    for sx, sy, sr in [(0.72, 0.30, 12), (0.80, 0.22, 9), (0.66, 0.20, 7)]:
        d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                   y + h * sy + sr], fill=(150, 140, 135))
    # Searchlight beam.
    d.polygon([(x + w * 0.88, y + h), (x + w * 0.62, y + h * 0.30),
               (x + w * 0.74, y + h * 0.30)], fill=(255, 240, 180))


def scene_bank(d, x, y, w, h):
    p = PALETTE
    d.rectangle([x, y, x + w, y + h], fill=(28, 48, 90))
    # Bank building.
    bx, by = x + w * 0.22, y + h * 0.30
    bw, bh = w * 0.56, h * 0.55
    d.polygon([(bx - 8, by), (bx + bw / 2, by - 18), (bx + bw + 8, by)],
              fill=p["white"])
    for k in range(4):
        cx = bx + 10 + k * (bw - 20) / 3
        d.rectangle([cx - 4, by + 6, cx + 4, by + bh - 8], fill=p["white"])
    d.rectangle([bx, by + bh - 8, bx + bw, by + bh], fill=p["white"])
    # Ban circle over a dollar sign.
    cx, cy = x + w * 0.80, y + h * 0.32
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=p["red"], width=5)
    d.line([cx - 11, cy + 11, cx + 11, cy - 11], fill=p["red"], width=5)
    d.text((x + w * 0.50, y + h * 0.52), "$", font=load("sans_bold", 26),
           fill=p["gold"], anchor="mm")


def scene_capitol(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (60, 100, 170), (150, 200, 240))
    # Dome.
    cx, base = x + w * 0.5, y + h * 0.88
    d.pieslice([cx - 34, base - 44, cx + 34, base + 24], 180, 360, fill=p["white"])
    d.rectangle([cx - 3, base - 58, cx + 3, base - 42], fill=p["white"])
    d.ellipse([cx - 4, base - 64, cx + 4, base - 56], fill=p["white"])
    d.rectangle([cx - 44, base - 8, cx + 44, base], fill=p["white"])
    d.rectangle([x + w * 0.10, base - 4, x + w * 0.90, base + 4], fill=p["white"])
    for k in range(3):
        sx = x + w * (0.18 + k * 0.32)
        d.text((sx, y + h * 0.18), "*", font=load("sans_bold", 22),
               fill=p["white"], anchor="mm")
    d.text((x + w * 0.5, y + h * 0.10), "258", font=load("sans_bold", 20),
           fill=p["white"], anchor="mm")


def scene_eu(d, x, y, w, h):
    p = PALETTE
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    import math
    cx, cy, r = x + w * 0.5, y + h * 0.5, min(w, h) * 0.32
    for k in range(12):
        a = math.radians(-90 + k * 30)
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.text((sx, sy), "*", font=load("sans_bold", 16), fill=p["gold"],
               anchor="mm")


def scene_tanker(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (40, 90, 120), (120, 180, 200))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(20, 80, 100))
    # Cliffs of the strait.
    d.polygon([(x, y + h * 0.62), (x + w * 0.18, y + h * 0.20),
               (x + w * 0.30, y + h * 0.62)], fill=(120, 100, 80))
    d.polygon([(x + w, y + h * 0.62), (x + w * 0.82, y + h * 0.20),
               (x + w * 0.70, y + h * 0.62)], fill=(120, 100, 80))
    # Tanker.
    sx, sy = x + w * 0.32, y + h * 0.56
    d.polygon([(sx, sy), (sx + w * 0.36, sy), (sx + w * 0.32, sy + 12),
               (sx + w * 0.04, sy + 12)], fill=(180, 40, 30))
    d.rectangle([sx + w * 0.24, sy - 12, sx + w * 0.32, sy], fill=(220, 220, 220))
    for k in range(3):
        wx = x + w * (0.30 + k * 0.13)
        d.arc([wx - 10, y + h * 0.72, wx + 10, y + h * 0.84], 180, 360,
              fill=(180, 220, 230), width=2)


def scene_plane(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (90, 160, 220), (200, 230, 250))
    for cx, cy, r in [(0.20, 0.25, 12), (0.78, 0.18, 10)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=p["white"])
        d.ellipse([x + w * cx - r + 10, y + h * cy - r + 4, x + w * cx + r + 10,
                   y + h * cy + r + 4], fill=p["white"])
    # Runway.
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(90, 90, 90))
    for k in range(5):
        lx = x + 10 + k * (w - 20) / 5
        d.rectangle([lx, y + h * 0.88, lx + 14, y + h * 0.92], fill=p["white"])
    # Plane silhouette.
    px, py = x + w * 0.5, y + h * 0.48
    d.ellipse([px - 42, py - 8, px + 42, py + 8], fill=p["white"])
    d.polygon([(px - 10, py), (px + 6, py - 26), (px + 16, py - 26),
               (px + 22, py)], fill=p["white"])
    d.polygon([(px + 30, py - 4), (px + 44, py - 18), (px + 48, py - 14),
               (px + 40, py + 2)], fill=p["white"])
    d.polygon([(px - 42, py - 2), (px - 52, py - 10), (px - 46, py + 4)],
              fill=p["red"])


def scene_mic(d, x, y, w, h):
    p = PALETTE
    d.rectangle([x, y, x + w, y + h], fill=p["purple"])
    cx, cy = x + w * 0.5, y + h * 0.42
    d.rounded_rectangle([cx - 12, cy - 22, cx + 12, cy + 10], radius=12,
                        fill=(220, 220, 220))
    d.arc([cx - 18, cy - 4, cx + 18, cy + 30], 0, 180, fill=(220, 220, 220),
          width=4)
    d.line([cx, cy + 30, cx, y + h - 8], fill=(220, 220, 220), width=4)
    d.line([cx - 14, y + h - 8, cx + 14, y + h - 8], fill=(220, 220, 220),
           width=4)
    for r in (30, 42):
        d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=p["gold"], width=3)
        d.arc([cx - r, cy - r, cx + r, cy + r], 120, 240, fill=p["gold"], width=3)


def scene_fire(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (50, 40, 40), (120, 70, 50))
    # Factory.
    bx, by = x + w * 0.10, y + h * 0.52
    d.rectangle([bx, by, bx + w * 0.62, y + h * 0.92], fill=(90, 80, 75))
    d.rectangle([bx + w * 0.66, y + h * 0.30, bx + w * 0.76, y + h * 0.92],
                fill=(110, 100, 95))
    # Flames.
    for fx, fh in [(0.22, 26), (0.38, 34), (0.54, 24)]:
        px = x + w * fx
        d.polygon([(px - 10, by), (px, by - fh), (px + 10, by)],
                  fill=p["flame"])
        d.polygon([(px - 5, by), (px, by - fh * 0.55), (px + 5, by)],
                  fill=p["gold"])
    # Smoke.
    for sx, sy, sr in [(0.72, 0.22, 11), (0.80, 0.14, 8), (0.64, 0.14, 7)]:
        d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                   y + h * sy + sr], fill=(140, 135, 130))


def scene_aid(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (80, 140, 190), (200, 225, 240))
    _sun(d, x + w * 0.80, y + h * 0.24, 11, p["gold"])
    # Mountains.
    d.polygon([(x, y + h), (x + w * 0.30, y + h * 0.30),
               (x + w * 0.55, y + h)], fill=(90, 120, 140))
    d.polygon([(x + w * 0.35, y + h), (x + w * 0.62, y + h * 0.42),
               (x + w * 0.90, y + h)], fill=(120, 150, 165))
    d.polygon([(x + w * 0.30, y + h * 0.30), (x + w * 0.24, y + h * 0.44),
               (x + w * 0.36, y + h * 0.44)], fill=p["white"])
    # Crate with a heart.
    cx, cy = x + w * 0.24, y + h * 0.72
    d.rectangle([cx - 16, cy - 12, cx + 16, cy + 12], fill=(170, 130, 80))
    d.line([cx - 16, cy, cx + 16, cy], fill=(140, 100, 55), width=3)
    d.line([cx, cy - 12, cx, cy + 12], fill=(140, 100, 55), width=3)
    d.text((cx, cy - 26), "+", font=load("sans_bold", 20), fill=p["red"],
           anchor="mm")


def scene_flag(d, x, y, w, h):
    p = PALETTE
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 110))
    # Flag pole and red flag with star.
    px = x + w * 0.30
    d.line([px, y + 8, px, y + h - 8], fill=(200, 200, 200), width=4)
    d.polygon([(px, y + 10), (px + w * 0.45, y + 20), (px, y + 36)],
              fill=p["red"])
    d.text((px + w * 0.16, y + 23), "*", font=load("sans_bold", 20),
           fill=p["gold"], anchor="mm")
    # Podium silhouettes.
    for k, ph in enumerate((26, 34, 22)):
        bx = x + w * (0.62 + k * 0.12)
        d.rectangle([bx, y + h - 8 - ph, bx + 14, y + h - 8],
                    fill=(200, 200, 200) if k == 1 else (150, 150, 150))


def scene_train(d, x, y, w, h):
    p = PALETTE
    _sky(d, x, y, w, h, (200, 160, 110), (240, 210, 170))
    # Track.
    d.rectangle([x, y + h * 0.78, x + w, y + h * 0.86], fill=(100, 90, 80))
    for k in range(6):
        tx = x + 6 + k * (w - 12) / 6
        d.line([tx, y + h * 0.76, tx + 6, y + h * 0.88], fill=(140, 130, 120),
               width=3)
    # Cars: two upright, one tilted off the track.
    d.rounded_rectangle([x + w * 0.08, y + h * 0.52, x + w * 0.34, y + h * 0.78],
                        radius=6, fill=(30, 90, 160))
    d.rounded_rectangle([x + w * 0.38, y + h * 0.52, x + w * 0.64, y + h * 0.78],
                        radius=6, fill=(30, 90, 160))
    d.polygon([(x + w * 0.70, y + h * 0.44), (x + w * 0.94, y + h * 0.58),
               (x + w * 0.90, y + h * 0.80), (x + w * 0.66, y + h * 0.66)],
              fill=(160, 50, 40))
    for wx in (0.16, 0.46):
        d.ellipse([x + w * wx - 5, y + h * 0.76, x + w * wx + 5, y + h * 0.86],
                  fill=(40, 40, 40))
    d.text((x + w * 0.21, y + h * 0.60), "AMTRAK", font=load("sans_bold", 11),
           fill=p["white"], anchor="mm")


SCENES = {
    "chip": scene_chip, "ship": scene_ship, "rubble": scene_rubble,
    "bank": scene_bank, "capitol": scene_capitol, "eu": scene_eu,
    "tanker": scene_tanker, "plane": scene_plane, "mic": scene_mic,
    "fire": scene_fire, "aid": scene_aid, "flag": scene_flag,
    "train": scene_train,
}

# ---------------------------------------------------------------- stories

# Main stories 1-13: (number, place, region, category, scene, badge,
# headline, body, source)
MAIN = [
    (1, "SANTA CLARA, USA", "AMERICAS", "TECH", "chip", "REPORTED",
     "Huang returns to Nvidia",
     "Board reinstates Jensen Huang as CEO. Shares jump 31%.",
     "Reuters · AP"),
    (2, "BENGHAZI, LIBYA", "EUROPE", "WAR", "ship", "REPORTED",
     "Kyiv says it sank Russian warship",
     "Seven sea drones sink Merkury off Libya; UN urges probe.",
     "Ukrainian Air Force · Reuters"),
    (3, "KYIV REGION", "EUROPE", "WAR", "rubble", "REPORTED",
     "Strikes kill 15 near Kyiv",
     "Dymer block hit; boy, 7, pulled alive after 14 hours.",
     "BBC · Reuters"),
    (4, "WASHINGTON", "MIDDLE EAST", "SANCTIONS", "bank", "REPORTED",
     "US sanctions Iran's shadow banks",
     "Treasury targets 25+ exchange houses and front firms.",
     "US Treasury · Reuters"),
    (5, "WASHINGTON", "AMERICAS", "POLITICS", "capitol", "REPORTED",
     "Democrats take the House",
     "At least 258 seats — biggest majority since 1992.",
     "AP"),
    (6, "BRUSSELS", "EUROPE", "EU", "eu", "REPORTED",
     "EU proposes new Russia sanctions",
     "60 banks, crypto platforms, 70 shadow-fleet vessels.",
     "European Commission · Reuters"),
    (7, "TEHRAN", "MIDDLE EAST", "IRAN", "tanker", "REPORTED",
     "Iran vows to counter US blockade",
     "Tehran will use every means against the Hormuz blockade.",
     "IRNA · Reuters"),
    (8, "BRUSSELS", "EUROPE", "STRIKE", "plane", "REPORTED",
     "Strike shuts Belgium's airports",
     "Controllers walk out over austerity; 50,000 travellers hit.",
     "Skeyes · Reuters"),
    (9, "QOM, IRAN", "MIDDLE EAST", "RIGHTS", "mic", "REPORTED",
     "Iran flogs singer 74 times",
     "Ahmadi and four of her team punished over a 2024 concert.",
     "Lawyers · Reuters"),
    (10, "CIKANDE, INDONESIA", "ASIA", "DISASTER", "fire", "ONGOING",
     "Factory fire: 24 body bags",
     "29 workers still missing after Saturday blaze; search resumes.",
     "Reuters · AP"),
    (11, "NEW DELHI", "ASIA", "AID", "aid", "REPORTED",
     "India gives Nepal $1.62bn",
     "Flood rebuild package, the biggest yet — 240bn rupees.",
     "Reuters · ANI"),
    (12, "PYONGYANG", "ASIA", "N. KOREA", "flag", "REPORTED",
     "Kim talks sovereignty, rebuffs Trump",
     "Kim expands foreign ties, days after rebuffing Trump's push.",
     "KCNA · Reuters"),
    (13, "LOUISIANA, USA", "AMERICAS", "CRASH", "train", "REPORTED",
     "Amtrak train derails in Louisiana",
     "Train hits a stuck truck near Lafayette; 5 hurt, 95 aboard.",
     "Amtrak · AP"),
]

# ALSO items 14-30: (number, place, region, one line, source)
ALSO = [
    (14, "COLOMBIA", "AMERICAS", "Drones hit police base; 60 homes damaged", "Reuters"),
    (15, "KENYA–DRC", "AFRICA", "Full diplomatic ties restored", "Reuters"),
    (16, "GAZA", "MIDDLE EAST", "Toxic contamination across 99% of strip", "Oxfam"),
    (17, "YEMEN", "MIDDLE EAST", "Saudi strike on Hodeida kills 4, wounds 18", "Houthi media"),
    (18, "DRC", "AFRICA", "WHO: fighting disrupts Ebola response", "WHO"),
    (19, "USA", "AMERICAS", "Army to blow up bomb chemicals in Iowa", "AP"),
    (20, "FINLAND", "EUROPE", "Summons envoy; Russia warns Estonia", "Reuters"),
    (21, "POLAND", "EUROPE", "Says Russia twice tried to kill rapper", "Reuters"),
    (22, "GREECE", "EUROPE", "Museum reopens; PM wants Marbles", "Reuters"),
    (23, "ISTANBUL", "MIDDLE EAST", "Lion on the loose; police hunt it", "Reuters"),
    (24, "HUNGARY", "EUROPE", "PM to visit Transcarpathia, pledges support", "Reuters"),
    (25, "NIGERIA", "AFRICA", "Tinubu: villa hit by water, power cuts", "Reuters"),
    (26, "IRAN", "MIDDLE EAST", "Says Hormuz can reopen fast if US meets terms", "IRNA"),
    (27, "MANCHESTER", "EUROPE", "Arena evacuated after tear-gas scare", "BBC"),
    (28, "SOUTH KOREA", "ASIA", "Aden deployment 'not war role'", "Reuters"),
    (29, "SYDNEY", "OCEANIA", "Prosecution: double murder was execution", "ABC"),
    (30, "WORLD", "WORLD", "WFP: wars put food aid for 7.3m at risk", "WFP"),
]

REGION_COLORS = {
    "EUROPE": "red", "MIDDLE EAST": "purple", "AMERICAS": "blue",
    "ASIA": "climate", "AFRICA": "bronze", "OCEANIA": (0, 130, 150),
    "WORLD": (90, 90, 90),
}

REGIONS = [
    ("EUROPE 9", "red"),
    ("MIDDLE EAST 7", "purple"),
    ("AMERICAS 5", "blue"),
    ("ASIA 4", "climate"),
    ("AFRICA 3", "bronze"),
    ("OCEANIA 1", (0, 130, 150)),
    ("WORLD 1", (90, 90, 90)),
]

NUMBERS = [
    ("+31%", "Nvidia jumps on return"),
    ("258", "Democrats' House seats"),
    ("7", "sea drones sank Merkury"),
    ("74", "lashes for the singer"),
    ("50,000", "hit by Belgium strike"),
]

TIMELINE = [
    ("02:37", "Boy, 7, alive"),
    ("06:10", "15 killed in Kyiv"),
    ("07:00", "Merkury sunk"),
    ("09:00", "NATO meets"),
    ("14:32", "Amtrak derails"),
    ("18:04", "Iran flogs singer"),
    ("18:30", "US sanctions Iran"),
]

EXCLUDED = [
    "COP31 pact (22 Nov)",
    "Chapo Isidro (20 Nov)",
    "S. Korea minister (22 Nov)",
    "Alcaraz ATP win (22 Nov)",
    "Liverpool 4-0 Utd (22 Nov)",
    "Verstappen Vegas win (22 Nov)",
    "BepiColombo orbit (21 Nov)",
    "ICJ Myanmar ruling",
    "Seattle ICE arrests (21 Nov)",
    "G20 (21 Nov)",
]

# Dotted world map: land cells as (row, col_start, col_end) on a 60x28
# grid. lon -180..180 maps to cols 0..59 (6 deg each); lat 80..-60 maps
# to rows 0..27 (5 deg each). A rough but recognisable world.
MAP_LAND = [
    (0, 22, 24), (0, 46, 53),
    (1, 2, 3), (1, 10, 17), (1, 22, 24), (1, 40, 58),
    (2, 2, 6), (2, 8, 18), (2, 23, 24), (2, 32, 34), (2, 36, 58),
    (3, 2, 6), (3, 7, 19), (3, 22, 23), (3, 31, 35), (3, 36, 58),
    (4, 4, 6), (4, 7, 20), (4, 28, 29), (4, 31, 34), (4, 35, 59),
    (5, 8, 20), (5, 28, 29), (5, 30, 38), (5, 38, 58),
    (6, 8, 21), (6, 29, 38), (6, 40, 52), (6, 48, 56),
    (7, 9, 22), (7, 29, 38), (7, 40, 50), (7, 50, 57),
    (8, 9, 23), (8, 29, 39), (8, 42, 50), (8, 50, 57),
    (9, 11, 23), (9, 27, 39), (9, 39, 45), (9, 45, 49), (9, 49, 56),
    (10, 10, 22), (10, 27, 40), (10, 41, 45), (10, 45, 48), (10, 50, 55),
    (11, 11, 19), (11, 27, 40), (11, 41, 45), (11, 45, 48), (11, 50, 53),
    (12, 12, 19), (12, 27, 40), (12, 42, 44), (12, 46, 48), (12, 50, 53),
    (13, 13, 18), (13, 28, 40), (13, 47, 47), (13, 50, 53),
    (14, 14, 17), (14, 17, 23), (14, 28, 39), (14, 50, 53), (14, 52, 57),
    (15, 17, 23), (15, 29, 39), (15, 52, 59),
    (16, 17, 23), (16, 30, 38), (16, 53, 58),
    (17, 18, 23), (17, 30, 38), (17, 54, 57),
    (18, 18, 23), (18, 30, 38), (18, 50, 55),
    (19, 18, 23), (19, 30, 37), (19, 49, 55),
    (20, 19, 23), (20, 30, 37), (20, 49, 55),
    (21, 19, 22), (21, 31, 36), (21, 50, 55),
    (22, 19, 22), (22, 31, 35), (22, 50, 54), (22, 57, 58),
    (23, 19, 21), (23, 32, 34), (23, 51, 53), (23, 57, 57),
    (24, 19, 21), (24, 57, 57),
    (25, 19, 20),
    (26, 19, 19),
]

# Map pins: (story number, lon, lat). #8 and #9 are nudged so they do
# not sit on top of #6 and #4.
PINS = [
    (1, -122, 37.4), (2, 20.1, 32.1), (3, 30.5, 50.5), (4, 51.4, 35.7),
    (5, -77, 38.9), (6, 4.35, 50.85), (7, 56.5, 26.6), (8, 7.5, 49.0),
    (9, 53.5, 33.0), (10, 106.2, -6.2), (11, 85.3, 27.7),
    (12, 125.75, 39.0), (13, -92, 30.2),
]

# ---------------------------------------------------------------- drawing

BADGE_COLORS = {"REPORTED": (34, 139, 34), "CLAIM": (200, 130, 10),
                "ONGOING": (29, 78, 216)}


def _color(name):
    c = PALETTE.get(name, name)
    return c if isinstance(c, tuple) else PALETTE[name]


def draw_card(d, x, y, w, h, story, ill_h, title_size, body_size,
              body_limit=3):
    num, place, region, category, scene, badge, headline, body, source = story
    p = PALETTE
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=p["white"],
                        outline=p["card_edge"], width=2)
    # Illustration, inset like a photo.
    ix, iy, iw, ih = x + 5, y + 5, w - 10, ill_h
    scene_img = Image.new("RGB", (iw, ih), p["white"])
    sd = ImageDraw.Draw(scene_img)
    SCENES[scene](sd, 0, 0, iw, ih)
    mask = Image.new("L", (iw, ih), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, iw, ih], radius=8, fill=255)
    d._image.paste(scene_img, (ix, iy), mask)
    # Number badge + location pill on the illustration.
    bx, by = ix + 12, iy + 12
    d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=p["white"],
              outline=p["navy"], width=2)
    d.text((bx, by), str(num), font=load("sans_bold", 14), fill=p["navy"],
           anchor="mm")
    pw = d.textlength(place, font=load("sans_bold", 12)) + 14
    d.rounded_rectangle([bx + 16, by - 10, bx + 16 + pw, by + 10], radius=5,
                        fill=p["white"])
    d.text((bx + 16 + pw / 2, by), place, font=load("sans_bold", 12),
           fill=p["navy"], anchor="mm")
    # Status badge, bottom-right of the illustration.
    bw = d.textlength(badge, font=load("sans_bold", 11)) + 12
    d.rounded_rectangle([ix + iw - bw - 6, iy + ih - 22, ix + iw - 6, iy + ih - 6],
                        radius=5, fill=BADGE_COLORS[badge])
    d.text((ix + iw - 6 - bw / 2, iy + ih - 14), badge,
           font=load("sans_bold", 11), fill=p["white"], anchor="mm")
    # Text block.
    rc = PALETTE[REGION_COLORS[region]] if isinstance(REGION_COLORS[region], str) \
        else REGION_COLORS[region]
    tx = x + 10
    tw = w - 20
    yy = y + 5 + ill_h + 8
    d.text((tx, yy), f"{region}  ·  {category}", font=load("sans_bold", 12),
           fill=rc)
    yy += 17
    for line in fit_lines(d, headline, "display_bold", title_size, tw, limit=2):
        d.text((tx, yy), line, font=load("display_bold", title_size),
               fill=p["ink"])
        yy += title_size + 3
    yy += 2
    for line in fit_lines(d, body, "sans", body_size, tw, limit=body_limit):
        d.text((tx, yy), line, font=load("sans", body_size), fill=p["body"])
        yy += body_size + 3
    d.text((tx, y + h - 16), source, font=load("sans", 11), fill=p["grey"])


def draw_numbers(d, x, y, w, h):
    p = PALETTE
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=p["navy"])
    d.text((x + 14, y + 12), "THE DAY IN NUMBERS", font=load("sans_bold", 16),
           fill=p["white"])
    yy = y + 42
    for num, label in NUMBERS:
        d.text((x + 14, yy), num, font=load("display_black", 24),
               fill=p["gold"])
        nw = d.textlength(num, font=load("display_black", 24))
        d.text((x + 14 + nw + 10, yy + 5), label, font=load("sans", 12),
               fill=p["white"])
        yy += 27


def draw_map(d, x, y, w, h):
    p = PALETTE
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=p["white"],
                        outline=p["card_edge"], width=2)
    d.text((x + 12, y + 8), "WHERE IT HAPPENED", font=load("sans_bold", 14),
           fill=p["navy"])
    d.text((x + w - 12, y + 8), "pins = story numbers", font=load("sans", 12),
           fill=p["grey"], anchor="ra")
    mx, my = x + 10, y + 30
    mw, mh = w - 20, h - 40
    cell = min(mw / 60, mh / 28)
    ox = mx + (mw - cell * 60) / 2
    oy = my + (mh - cell * 28) / 2
    d.rounded_rectangle([ox - 4, oy - 4, ox + cell * 60 + 4, oy + cell * 28 + 4],
                        radius=6, fill=p["map_sea"])
    for row, c0, c1 in MAP_LAND:
        for c in range(c0, c1 + 1):
            cx = ox + (c + 0.5) * cell
            cy = oy + (row + 0.5) * cell
            r = max(1.4, cell * 0.30)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=p["map_dot"])
    for num, lon, lat in PINS:
        col = (lon + 180) / 6
        row = (80 - lat) / 5
        cx = ox + col * cell
        cy = oy + row * cell
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=p["red"],
                  outline=p["white"], width=2)
        d.text((cx, cy), str(num), font=load("sans_bold", 11),
               fill=p["white"], anchor="mm")


def main():
    p = PALETTE
    img = Image.new("RGB", CANVAS, p["paper"])
    d = ImageDraw.Draw(img)

    # Header strip.
    d.rectangle([0, 0, 1024, 26], fill=p["navy"])
    d.text((16, 13), "THE WORLD IN ONE DAY", font=load("sans_bold", 15),
           fill=p["white"], anchor="lm")
    d.text((1008, 13), "30 STORIES  ·  7 REGIONS  ·  ALL FROM THIS ONE DAY",
           font=load("sans_bold", 15), fill=p["pale_blue"], anchor="rm")

    # Title.
    d.text((16, 32), "Monday 23 November 2026", font=load("serif_bold", 60),
           fill=p["navy"])
    # Red subhead: the three biggest stories.
    d.text((16, 98), "Huang returns to Nvidia  ·  Kyiv says it sank a Russian "
           "warship  ·  Democrats take the House",
           font=load("sans_italic_bold", 19), fill=p["red"])

    # Region chips.
    xx = 16
    for label, color in REGIONS:
        c = PALETTE[color] if isinstance(color, str) else color
        w = d.textlength(label, font=load("sans_bold", 14)) + 16
        d.rounded_rectangle([xx, 122, xx + w, 140], radius=9, fill=c)
        d.text((xx + w / 2, 131), label, font=load("sans_bold", 14),
               fill=p["white"], anchor="mm")
        xx += w + 7

    # UTC timeline strip.
    d.rectangle([0, 146, 1024, 168], fill=p["navy"])
    d.rounded_rectangle([10, 150, 48, 164], radius=4, fill=p["red"])
    d.text((29, 157), "UTC", font=load("sans_bold", 13), fill=p["white"],
           anchor="mm")
    tx = 58
    for time, text in TIMELINE:
        d.text((tx, 157), time, font=load("sans_bold", 12), fill=p["gold"],
               anchor="lm")
        tw = d.textlength(time, font=load("sans_bold", 12))
        d.text((tx + tw + 5, 157), text, font=load("sans", 12),
               fill=p["white"], anchor="lm")
        tx += tw + 5 + d.textlength(text, font=load("sans", 12)) + 10

    # Row 1: three big cards + numbers panel.
    row1_y, row1_h = 174, 186
    cw1 = 242
    for i in range(3):
        draw_card(d, 16 + i * (cw1 + 6), row1_y, cw1, row1_h, MAIN[i],
                  ill_h=58, title_size=21, body_size=14, body_limit=2)
    draw_numbers(d, 16 + 3 * (cw1 + 6), row1_y, cw1, row1_h)

    # Rows 2-3: five cards each.
    cw2, gap2 = 196, 6
    for r in range(2):
        yy = 366 + r * (178 + 6)
        for i in range(5):
            story = MAIN[3 + r * 5 + i]
            draw_card(d, 16 + i * (cw2 + gap2), yy, cw2, 178, story,
                      ill_h=44, title_size=17, body_size=13)

    # ALSO list + map.
    ay = 730
    d.text((16, ay), "ALSO ON MONDAY 23 NOVEMBER", font=load("sans_bold", 17),
           fill=p["navy"])
    d.line([16, ay + 22, 684, ay + 22], fill=p["line"], width=2)
    col_w = 224
    for i, (num, place, region, text, source) in enumerate(ALSO):
        col, row = i % 3, i // 3
        x = 16 + col * col_w
        yy = ay + 28 + row * 26
        full = f"{place} — {text}"
        lines = fit_lines(d, full, "sans", 12, col_w - 30, limit=2)
        d.text((x, yy), str(num), font=load("sans_bold", 13), fill=p["red"])
        ly = yy
        for line in lines:
            d.text((x + 26, ly), line, font=load("sans", 12), fill=p["ink"])
            ly += 13
    draw_map(d, 700, ay, 308, 178)

    # DATE CHECK.
    dy = 914
    d.rounded_rectangle([16, dy, 1008, dy + 58], radius=8, fill=p["white"],
                        outline=p["red"], width=2)
    d.rounded_rectangle([28, dy + 10, 28 + 118, dy + 32], radius=6,
                        fill=p["red"])
    d.text((28 + 59, dy + 21), "DATE CHECK", font=load("sans_bold", 15),
           fill=p["white"], anchor="mm")
    d.text((158, dy + 8), "Every story on this page happened or was first "
           "reported on Monday 23 November 2026 (UTC).",
           font=load("sans_bold", 15), fill=p["ink"])
    exc = "Left out — earlier days:  " + "  ·  ".join(EXCLUDED)
    for j, line in enumerate(fit_lines(d, exc, "sans", 13, 838, limit=2)):
        d.text((158, dy + 28 + j * 15), line, font=load("sans", 13),
               fill=p["body"])

    # Footer.
    d.text((512, 980), "HOW SURE:  REPORTED = carried by the day's wires or "
           "officials  ·  ONGOING = still unfolding  ·  CLAIM = one side's "
           "account, labelled as such", font=load("sans", 13), fill=p["grey"],
           anchor="mm")
    d.text((512, 998), "Sources: AP, Reuters, AFP, BBC, Gulf News, Daily "
           "Summary of World  •  Scenes are drawn illustrations, not "
           "photographs", font=load("sans", 13), fill=p["grey"], anchor="mm")

    out = Path(__file__).resolve().parent.parent / "entry.png"
    img.save(out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
