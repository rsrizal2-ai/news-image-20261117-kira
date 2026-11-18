"""Render the news poster for Tuesday 17 November 2026.

Draws a clean newspaper-style infographic with Pillow and real fonts:
a date masthead, six verified story cards with simple geometric icons,
and a ticker strip of further stories from the same day. No photos, no
generated imagery, no network access. Run from anywhere; the poster is
written to entry.png beside this script.

Stories were checked against news search results on 18 November 2026;
see RESEARCH.md for the sources behind each item.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 234)
NAVY = (18, 34, 60)
NAVY_SOFT = (31, 52, 86)
GOLD = (201, 162, 39)
INK = (26, 30, 36)
GREY = (88, 94, 104)
CARD = (255, 255, 255)
CARD_EDGE = (214, 208, 194)
WHITE = (255, 255, 255)
PALE = (216, 222, 232)

FONT_DIR = Path("/usr/share/fonts/truetype")
BOLD_PATHS = [
    FONT_DIR / "noto/NotoSans-Bold.ttf",
    FONT_DIR / "dejavu/DejaVuSans-Bold.ttf",
]
REGULAR_PATHS = [
    FONT_DIR / "noto/NotoSans-Regular.ttf",
    FONT_DIR / "dejavu/DejaVuSans.ttf",
]


def load_font(size, bold=False):
    for candidate in BOLD_PATHS if bold else REGULAR_PATHS:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw, y, text, font, fill, width=WIDTH):
    draw.text((width / 2, y), text, font=font, fill=fill, anchor="ma")


# ---- simple geometric icons, drawn in a square box ----

def icon_burst(draw, x, y, size, color):
    cx, cy = x + size / 2, y + size / 2
    outer = size / 2
    inner = size / 4
    points = []
    for step in range(16):
        angle = step * 3.14159 / 8
        radius = outer if step % 2 == 0 else inner
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(points, fill=color)
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=WHITE)


def icon_bridge(draw, x, y, size, color):
    deck_y = y + size * 0.30
    cx = x + size / 2
    half_gap = size * 0.14
    # Two solid deck ends with a gap where the span fell.
    draw.rectangle([x + 2, deck_y - 4, cx - half_gap, deck_y + 4], fill=color)
    draw.rectangle([cx + half_gap, deck_y - 4, x + size - 2, deck_y + 4], fill=color)
    # The fallen span, tilted as it drops toward the water.
    draw.line(
        [cx - half_gap + 2, deck_y + 8, cx + half_gap - 4, deck_y + 22],
        fill=color,
        width=7,
    )
    # One gentle wave line for the strait below.
    wave_y = y + size * 0.78
    points = []
    for step in range(7):
        px = x + 2 + step * (size - 4) / 6
        py = wave_y + (3 if step % 2 == 0 else -3)
        points.append((px, py))
    draw.line(points, fill=color, width=3)


def icon_globe(draw, x, y, size, color):
    box = [x + 4, y + 4, x + size - 4, y + size - 4]
    draw.ellipse(box, outline=color, width=5)
    draw.ellipse([x + size * 0.28, y + 4, x + size * 0.72, y + size - 4], outline=color, width=3)
    mid = y + size / 2
    draw.line([x + 4, mid, x + size - 4, mid], fill=color, width=3)
    draw.arc([x + 8, y + size * 0.18, x + size - 8, y + size * 0.52], 200, 340, fill=color, width=3)


def icon_chip(draw, x, y, size, color):
    pad = size * 0.18
    draw.rounded_rectangle(
        [x + pad, y + pad, x + size - pad, y + size - pad],
        radius=8,
        outline=color,
        width=5,
    )
    inner = size * 0.20
    draw.rectangle(
        [x + size / 2 - inner, y + size / 2 - inner, x + size / 2 + inner, y + size / 2 + inner],
        outline=color,
        width=4,
    )
    for frac in (0.32, 0.5, 0.68):
        pos = x + size * frac
        draw.line([pos, y + 2, pos, y + pad], fill=color, width=4)
        draw.line([pos, y + size - pad, pos, y + size - 2], fill=color, width=4)
        pos_y = y + size * frac
        draw.line([x + 2, pos_y, x + pad, pos_y], fill=color, width=4)
        draw.line([x + size - pad, pos_y, x + size - 2, pos_y], fill=color, width=4)


def icon_building(draw, x, y, size, color):
    cx = x + size / 2
    draw.polygon(
        [(x + 4, y + size * 0.34), (cx, y + 4), (x + size - 4, y + size * 0.34)],
        outline=color,
        width=5,
    )
    draw.line([x + 8, y + size * 0.40, x + size - 8, y + size * 0.40], fill=color, width=4)
    for frac in (0.24, 0.42, 0.58, 0.76):
        col_x = x + size * frac
        draw.line([col_x, y + size * 0.48, col_x, y + size * 0.82], fill=color, width=6)
    draw.line([x + 4, y + size * 0.88, x + size - 4, y + size * 0.88], fill=color, width=6)


def icon_shield(draw, x, y, size, color):
    cx = x + size / 2
    points = [
        (cx, y + 4),
        (x + size - 6, y + size * 0.24),
        (x + size - 6, y + size * 0.55),
        (cx, y + size - 4),
        (x + 6, y + size * 0.55),
        (x + 6, y + size * 0.24),
    ]
    draw.polygon(points, outline=color, width=5)
    bar = size * 0.09
    draw.rectangle([cx - bar, y + size * 0.30, cx + bar, y + size * 0.66], fill=color)
    draw.rectangle([cx - size * 0.18, y + size * 0.40, cx + size * 0.18, y + size * 0.56], fill=color)


ICONS = {
    "burst": icon_burst,
    "bridge": icon_bridge,
    "globe": icon_globe,
    "chip": icon_chip,
    "building": icon_building,
    "shield": icon_shield,
}

STORIES = [
    {
        "tag": "THE GULF",
        "accent": (178, 52, 36),
        "icon": "burst",
        "headline": "US strikes Iran's Qeshm Island",
        "body": "US jets hit a missile site after Iran fired drones at a US radar base in Bahrain.",
    },
    {
        "tag": "UKRAINE",
        "accent": (29, 78, 137),
        "icon": "bridge",
        "headline": "Kerch Bridge span falls after Ukraine strike",
        "body": "A road section fell into the strait on the second day of strikes. Zelenskyy called it 'unprecedented'.",
    },
    {
        "tag": "ASIA SUMMIT",
        "accent": (14, 124, 123),
        "icon": "globe",
        "headline": "Trump in Manila, headed for Xi-Putin talks",
        "body": "Quad leaders met in Manila and agreed critical-minerals deals ahead of a Shenzhen summit.",
    },
    {
        "tag": "TECH",
        "accent": (46, 125, 50),
        "icon": "chip",
        "headline": "Nvidia posts record $115.8bn; Huang stays out",
        "body": "Revenue doubled from a year earlier, but the board will not reinstate ousted CEO Jensen Huang.",
    },
    {
        "tag": "MONGOLIA",
        "accent": (171, 113, 20),
        "icon": "building",
        "headline": "Mongolia's president says he will resign",
        "body": "Khurelsukh denies railway bribery claims and says he will face investigators. Parliament must accept it.",
    },
    {
        "tag": "HEALTH",
        "accent": (178, 34, 91),
        "icon": "shield",
        "headline": "US loses measles-free status after 26 years",
        "body": "Over 5,400 cases and 10 deaths have been reported in the US this year.",
    },
]

TICKER_LINES = [
    "Ebola in DR Congo passes 11,000 cases  \u2022  Russian plane crash kills all 19 aboard, ministry says",
    "Five EU states plan a Rwanda return hub  \u2022  Japan scrambles jets after suspected Russian incursion",
]


def draw_card(draw, left, top, width, height, story):
    draw.rounded_rectangle(
        [left, top, left + width, top + height],
        radius=12,
        fill=CARD,
        outline=CARD_EDGE,
        width=2,
    )
    accent = story["accent"]
    draw.rounded_rectangle(
        [left, top, left + 8, top + height], radius=4, fill=accent
    )
    pad = 20
    tag_font = load_font(17, bold=True)
    tag_text = story["tag"]
    tag_w = draw.textlength(tag_text, font=tag_font) + 20
    tag_top = top + 15
    draw.rounded_rectangle(
        [left + pad, tag_top, left + pad + tag_w, tag_top + 26],
        radius=13,
        fill=accent,
    )
    draw.text(
        (left + pad + 10, tag_top + 4),
        tag_text,
        font=tag_font,
        fill=WHITE,
    )
    icon_size = 58
    ICONS[story["icon"]](
        draw, left + width - pad - icon_size, top + 12, icon_size, accent
    )
    head_font = load_font(28, bold=True)
    head_width = width - 2 * pad - 66
    head_lines = wrap_text(draw, story["headline"], head_font, head_width)[:2]
    hy = top + 52
    for line in head_lines:
        draw.text((left + pad, hy), line, font=head_font, fill=INK)
        hy += 34
    body_font = load_font(20)
    body_lines = wrap_text(draw, story["body"], body_font, width - 2 * pad)[:3]
    by = top + 128
    for line in body_lines:
        draw.text((left + pad, by), line, font=body_font, fill=GREY)
        by += 26


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    # Masthead
    draw.rectangle([0, 0, WIDTH, 198], fill=NAVY)
    draw.rectangle([0, 194, WIDTH, 198], fill=GOLD)
    draw_centered(draw, 26, "THE WORLD IN ONE DAY  \u2022  WORLD NEWS", load_font(20, bold=True), GOLD)
    draw_centered(draw, 56, "Tuesday, 17 November 2026", load_font(62, bold=True), WHITE)
    draw_centered(
        draw,
        146,
        "Six stories that defined the day, as reported on 17 November 2026",
        load_font(22),
        PALE,
    )

    # Story grid: 2 columns x 3 rows
    margin = 28
    gap = 14
    grid_top = 214
    grid_bottom = 872
    card_w = (WIDTH - 2 * margin - gap) // 2
    card_h = (grid_bottom - grid_top - 2 * gap) // 3
    for index, story in enumerate(STORIES):
        row, col = divmod(index, 2)
        left = margin + col * (card_w + gap)
        top = grid_top + row * (card_h + gap)
        draw_card(draw, left, top, card_w, card_h, story)

    # Ticker strip
    draw.rectangle([0, 886, WIDTH, 972], fill=NAVY_SOFT)
    draw_centered(draw, 894, "ALSO ON THIS DAY", load_font(18, bold=True), GOLD)
    ticker_font = load_font(19)
    ty = 918
    for line in TICKER_LINES:
        draw_centered(draw, ty, line, ticker_font, WHITE)
        ty += 26

    # Footer
    draw_centered(
        draw,
        982,
        "Every story happened or was first reported on Tuesday 17 November 2026. Sources include BBC, Reuters, AP, NPR and Al Jazeera.",
        load_font(15),
        GREY,
    )

    out_path = Path(__file__).resolve().parent / "entry.png"
    image.save(out_path, optimize=True)
    print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
