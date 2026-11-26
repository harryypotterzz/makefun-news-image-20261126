#!/usr/bin/env python3
"""Build-time renderer for the 26 November 2026 world-news image.

Draws entry.png (1024x1024, RGB) from eight verified headlines of
Thursday 26 November 2026. Newspaper front-page style: paper-white
page, black masthead, red date band, one numbered row per story with
a bold headline and one supporting line.

No network access. Run:  python3 gen_image.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# Palette: warm paper, black ink, signal red, grey supporting text.
PAPER = (251, 247, 238)
INK = (22, 22, 22)
RED = (180, 35, 24)
GREY = (92, 92, 88)
FAINT = (205, 198, 185)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


KICKER_FONT = load_font("DejaVuSans-Bold.ttf", 20)
TITLE_FONT = load_font("DejaVuSans-Bold.ttf", 62)
DATE_FONT = load_font("DejaVuSans-Bold.ttf", 26)
NUM_FONT = load_font("DejaVuSans-Bold.ttf", 30)
HEAD_FONT = load_font("DejaVuSans-Bold.ttf", 26)
SUB_FONT = load_font("DejaVuSans.ttf", 20)
FOOT_FONT = load_font("DejaVuSans.ttf", 17)

# (headline, supporting line) — all eight verified against Reuters / AP /
# KCNA / AFP reporting of 25-26 November 2026 (see README for sources).
STORIES = [
    (
        "Kim orders wider spread of tactical nuclear weapons",
        "North Korea's leader tells nuclear sites to deploy them more broadly — KCNA",
    ),
    (
        "US unveils sweeping new tariffs on 14 partners",
        "China hit hardest in the new duties; stocks slide on trade fears",
    ),
    (
        "Ukraine hits Russian air base; five jets damaged",
        "Three MiG-31s and two Su-34s knocked out at Savasleyka, Kyiv says",
    ),
    (
        "Russia strikes Kyiv with ballistic missiles",
        "Energy and gas sites hit; power cut in five regions of Ukraine",
    ),
    (
        "Judges urge dropping Netanyahu bribery case",
        "Israeli court recommends prosecutors drop one of three cases",
    ),
    (
        "Sudan drone strikes kill 19 civilians",
        "RSF drones hit homes in Damazin, Blue Nile state, rights group says",
    ),
    (
        "Colombia police free 20 supermarket hostages",
        "Seventeen-hour siege in Cartagena ends; one gunman killed",
    ),
    (
        "FCC clears SpaceX's 1m-satellite data centres",
        "'Starmind' would put AI computing in orbit; first satellite by 2033",
    ),
]


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap; returns the lines that fit inside max_width."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_globe(draw, cx, cy, r):
    """Small line-drawn globe for the masthead: circle plus meridians."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=INK, width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=INK, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 200, 340, fill=INK, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 20, 160, fill=INK, width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- Masthead -------------------------------------------------------
    draw.rectangle([0, 0, W, 10], fill=INK)
    kicker = "T H E   W O R L D   I N   O N E   I M A G E"
    kw = draw.textlength(kicker, font=KICKER_FONT)
    draw.text(((W - kw) / 2, 24), kicker, font=KICKER_FONT, fill=GREY)

    title = "WORLD NEWS"
    tw = draw.textlength(title, font=TITLE_FONT)
    draw.text(((W - tw) / 2 - 40, 52), title, font=TITLE_FONT, fill=INK)
    draw_globe(draw, W - 92, 92, 34)

    # Red date band naming the day this image sums up.
    draw.rectangle([0, 132, W, 176], fill=RED)
    date_text = "THURSDAY, 26 NOVEMBER 2026"
    dw = draw.textlength(date_text, font=DATE_FONT)
    draw.text(((W - dw) / 2, 140), date_text, font=DATE_FONT, fill=WHITE)
    draw.text((36, 142), "8 STORIES", font=DATE_FONT, fill=WHITE)
    draw.text((W - 36 - draw.textlength("ONE DAY", font=DATE_FONT), 142),
              "ONE DAY", font=DATE_FONT, fill=WHITE)

    # --- Story rows -----------------------------------------------------
    text_x = 104
    text_w = W - text_x - 36
    y = 196
    row_h = 98
    for i, (headline, sub) in enumerate(STORIES, start=1):
        # Red number.
        num = str(i)
        nw = draw.textlength(num, font=NUM_FONT)
        draw.text((52 - nw / 2, y + 8), num, font=NUM_FONT, fill=RED)

        head_lines = wrap_text(draw, headline, HEAD_FONT, text_w)
        sub_lines = wrap_text(draw, sub, SUB_FONT, text_w)
        # Guard: nothing may be silently cut off. Headlines get at most
        # two lines and supporting lines at most two; anything longer is
        # a bug in the story text, so fail loudly instead of shipping
        # a truncated line.
        if len(head_lines) > 2 or len(sub_lines) > 2:
            raise ValueError(
                f"story {i} does not fit its row: {headline!r} / {sub!r}"
            )
        ly = y + 2
        for line in head_lines:
            draw.text((text_x, ly), line, font=HEAD_FONT, fill=INK)
            ly += 32
        for line in sub_lines:
            draw.text((text_x, ly), line, font=SUB_FONT, fill=GREY)
            ly += 25

        # Thin rule between rows, except after the last one.
        if i < len(STORIES):
            draw.line([36, y + row_h - 8, W - 36, y + row_h - 8],
                      fill=FAINT, width=2)
        y += row_h

    # --- Footer ---------------------------------------------------------
    draw.line([36, H - 44, W - 36, H - 44], fill=INK, width=2)
    foot = "Sources: Reuters  ·  AP  ·  KCNA  ·  AFP"
    fw = draw.textlength(foot, font=FOOT_FONT)
    draw.text(((W - fw) / 2, H - 34), foot, font=FOOT_FONT, fill=GREY)

    img.save(OUT, format="PNG")
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
