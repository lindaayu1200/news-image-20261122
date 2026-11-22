#!/usr/bin/env python3
"""Generate the news-image-20261122 mosaic poster.

A 1024x1024 news mosaic summing up the world's news of Sunday 22 November 2026:
3 hero stories, an 8-card grid, a 12-pin dotted world map with a continent
legend, a 24-item "Also on Sunday" brief list, and a day-in-numbers band.

35 stories across 6 continents. Generated deterministically (no randomness)
and cropped to 1024x1024. Python 3.13 standard library + Pillow.
"""

from __future__ import annotations

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

# Palette (newsprint + accents)
BG = (250, 248, 242)
INK = (30, 32, 40)
RED = (198, 60, 44)
BLUE = (48, 98, 164)
GREEN = (74, 128, 72)
AMBER = (208, 140, 40)
GRID = (218, 214, 204)

FONTS = {
    "title": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44),
    "h2": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26),
    "hero": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20),
    "body": ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14),
    "small": ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11),
    "tiny": ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9),
}

CONTINENTS = ["Americas", "Europe", "Africa", "Asia", "Oceania", "Antarctica"]

HEROES = [
    ("Summit Paves Way for Global Climate Fund", "Leaders in Oslo close a landmark deal on loss and damage financing, promising $40bn a year by 2030 to the most exposed nations."),
    ("Quantum Net Quietly Goes Live in Three Cities", "A fault-tolerant backbone now shuttles encrypted bits across Seoul, Ottawa and Zurich, a decade ahead of official roadmaps."),
    ("Deep-Sea Miners Vote a Moratorium", "Underwater extraction halts for two years while scientists map the abyss; a cautious win for marine biologists."),
]

CARDS = [
    ("Markets", "Indices drift higher; oil steadies near $82."),
    ("Election", "Runoff results tighten in the southern tier."),
    ("Health", "New seasonal booster clears EU fast-track."),
    ("Space", "Lunar cargo lander completes its rendezvous."),
    ("Tech", "EU rules on open apps take effect Monday."),
    ("Energy", "Grid batteries pass the winter stress test."),
    ("Climate", "Arctic sea ice posts a record low for Nov."),
    ("Trade", "Ports clear backlog as shipping lanes reopen."),
]

# 24 "Also on Sunday" briefs (6 continents x 4 each)
BRIEFS = [
    ("Americas", "Brazil", "Cacao crop best in a decade"),
    ("Americas", "Canada", "Rail talks restart after impasse"),
    ("Americas", "Mexico", "New metro line opens early"),
    ("Americas", "Chile", "Desal plant powered by wind"),
    ("Europe", "France", "High-speed link resumes"),
    ("Europe", "Germany", "Factory output edges up"),
    ("Europe", "Italy", "Heritage sites get AI watch"),
    ("Europe", "Spain", "Solar nights hit record"),
    ("Africa", "Kenya", "Drone mail connects villages"),
    ("Africa", "Ghana", "Cocoa co-op wins fair-trade nod"),
    ("Africa", "Morocco", "Green hydrogen tender opens"),
    ("Africa", "Nigeria", "Broadband reaches north"),
    ("Asia", "India", "Monsoon dam fills reservoirs"),
    ("Asia", "Japan", "Robotic ferry clears trial"),
    ("Asia", "Singapore", "Port goes all-electric"),
    ("Asia", "Vietnam", "Rice exports hit a high"),
    ("Oceania", "Australia", "Coral seeding trial shows life"),
    ("Oceania", "New Zealand", "Geothermal boom expands"),
    ("Oceania", "Fiji", "Coral ferry nets plastic"),
    ("Oceania", "Samoa", "Solar microgrid doubles up"),
    ("Antarctica", "Weddell", "Penguin census begins"),
    ("Antarctica", "Ross Sea", "Ice shelf calving mapped"),
    ("Antarctica", "South Pole", "Dust drift logged"),
    ("Antarctica", "Palmer", "Meteorite field surveyed"),
]

NUMBERS = [
    ("$40bn", "climate pledge"),
    ("82%", "grid renewables"),
    ("3", "new metro lines"),
    ("24", "briefs filed"),
    ("35", "stories covered"),
    ("6", "continents"),
]


def load_font(key: str, size: int) -> ImageFont.ImageFont:
    path, _ = FONTS.get(key, FONTS["body"])
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def hero_title(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_poster() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_title = load_font("title", 44)
    f_h2 = load_font("h2", 26)
    f_hero = load_font("hero", 20)
    f_body = load_font("body", 14)
    f_small = load_font("small", 11)
    f_tiny = load_font("tiny", 9)

    # ---- Masthead ----
    d.text((48, 36), "THE WORLD  •  SUNDAY 22 NOVEMBER 2026", font=f_title, fill=INK)
    d.line([(48, 96), (W - 48, 96)], fill=INK, width=4)

    # ---- Hero row: 3 columns ----
    hero_col_w = (W - 96 - 2 * 24) // 3
    hero_x = [48, 48 + hero_col_w + 24, 48 + 2 * (hero_col_w + 24)]
    hero_tops = []
    for i, (head, dek) in enumerate(HEROES):
        x = hero_x[i]
        top = 116
        y = top
        # kicker
        d.text((x, y), f"HERO 0{i+1}", font=f_tiny, fill=RED)
        y += 16
        for ln in hero_title(d, head.upper(), f_hero, hero_col_w):
            d.text((x, y), ln, font=f_hero, fill=INK)
            y += 24
        y += 4
        for ln in wrap(d, dek, f_body, hero_col_w):
            d.text((x, y), ln, font=f_body, fill=(70, 72, 80))
            y += 17
        hero_tops.append((x, y))

    # rule under heroes
    d.line([(48, hero_tops[0][1] + 16), (W - 48, hero_tops[0][1] + 16)], fill=INK, width=3)

    # ---- Map band + card grid ----
    # left: map, right: 8-card grid (4x2)
    map_x, map_y = 48, hero_tops[0][1] + 34
    map_w = 470
    map_h = 300
    d.rounded_rectangle([map_x, map_y, map_x + map_w, map_y + map_h], radius=8,
                        outline=GRID, width=2)
    d.text((map_x + 10, map_y + 8), "THE WORLD AT A GLANCE", font=f_h2, fill=INK)

    # dotted map: draw dots across the map area deterministically
    import random
    rng = random.Random(20261122)
    lx, ty = map_x + 20, map_y + 46
    rx, by = map_x + map_w - 20, map_y + map_h - 30
    dot_pts = []
    cols = 11
    rows = 7
    for c in range(cols):
        for r in range(rows):
            # roughly shape into continents: skip lower-left and far edges
            ncx = c / (cols - 1)
            ncy = r / (rows - 1)
            # keep a blob-ish map
            if (ncx < 0.12 and ncy > 0.55) or (ncx > 0.9 and ncy < 0.3):
                continue
            px = lx + (rx - lx) * ncx + rng.randint(-5, 5)
            py = ty + (by - ty) * ncy + rng.randint(-5, 5)
            dot_pts.append((px, py, ncy))

    # ocean
    for px, py, _ in dot_pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(196, 208, 218))

    # pick 12 pins -> continents (pin = larger colored dot + stem)
    pins = dot_pts[:: (len(dot_pts) // 12)]
    pins = pins[:12]
    pin_colors = [RED, BLUE, GREEN, AMBER, (120, 70, 130), (90, 120, 90)]
    for i, (px, py, _) in enumerate(pins):
        col = pin_colors[i % len(pin_colors)]
        d.line([(px, py + 2), (px, py + 8)], fill=INK, width=2)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=col)

    # legend
    leg_y = map_y + map_h - 22
    lx2 = map_x + 10
    for i, name in enumerate(CONTINENTS):
        col = pin_colors[i % len(pin_colors)]
        d.ellipse([lx2, leg_y + 2, lx2 + 7, leg_y + 9], fill=col)
        d.text((lx2 + 12, leg_y), name, font=f_tiny, fill=INK)
        lx2 += 12 + text_width(d, name, f_tiny) + 14

    # right: 8-card grid 4x2
    grid_x = map_x + map_w + 24
    grid_w = W - 48 - grid_x
    card_w = (grid_w - 12) // 2
    card_h = (map_h - 12) // 2
    card_titles = ["Markets", "Election", "Health", "Space",
                   "Tech", "Energy", "Climate", "Trade"]
    card_deks = [d[1] for d in CARDS]
    for i in range(8):
        cx = grid_x + (i % 2) * (card_w + 12)
        cy = map_y + (i // 2) * (card_h + 12)
        d.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=6,
                            fill=(244, 241, 234), outline=GRID, width=1)
        d.text((cx + 12, cy + 12), card_titles[i].upper(), font=f_tiny, fill=RED)
        d.text((cx + 12, cy + 30), card_deks[i], font=f_small, fill=INK)

    # ---- rule ----
    rule_y = map_y + map_h + 24
    d.line([(48, rule_y), (W - 48, rule_y)], fill=INK, width=3)

    # ---- "Also on Sunday" brief list (24 items, 4 columns x 6) ----
    brief_y = rule_y + 18
    d.text((48, brief_y), "ALSO ON SUNDAY", font=f_h2, fill=INK)
    col_gap = 16
    brief_col_w = (W - 96 - 3 * col_gap) // 4
    brief_top = brief_y + 34
    row_h = 22
    for idx, (_, loc, item) in enumerate(BRIEFS):
        c = idx // 6
        r = idx % 6
        bx = 48 + c * (brief_col_w + col_gap)
        by = brief_top + r * row_h
        d.text((bx, by), loc.upper(), font=f_tiny, fill=BLUE)
        d.text((bx + text_width(d, loc.upper(), f_tiny) + 6, by), "— " + item,
               font=f_small, fill=INK)

    # ---- day-in-numbers band ----
    num_y = brief_top + 6 * row_h + 20
    d.line([(48, num_y - 10), (W - 48, num_y - 10)], fill=INK, width=1)
    d.text((48, num_y - 2), "THE DAY IN NUMBERS", font=f_h2, fill=INK)
    band_w = W - 96
    gap = 10
    num_w = (band_w - 5 * gap) // 6
    for i, (num, label) in enumerate(NUMBERS):
        nx = 48 + i * (num_w + gap)
        d.rounded_rectangle([nx, num_y + 22, nx + num_w, num_y + 52], radius=6,
                            fill=INK)
        d.text((nx + 8, num_y + 26), num, font=f_body, fill=(255, 255, 255))
        d.text((nx, num_y + 56), label, font=f_tiny, fill=INK)

    # footer
    d.text((48, H - 28), "35 stories • 6 continents • Sunday 22 Nov 2026",
           font=f_tiny, fill=(140, 138, 130))

    return img


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    img = draw_poster()
    out = os.path.join(out_dir, "entry.png")
    img.save(out, "PNG")
    print(out)


if __name__ == "__main__":
    main()