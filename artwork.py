#!/usr/bin/env python3
"""Deterministic generator for entry.png — newspaper front page, 18 Nov 2026."""
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = "#f8f3e6"
INK = "#14100c"
RED = "#b3202a"
NAVY = "#1d3557"
GOLD = "#e9c46a"
BLUE_CIRCLE = "#457b9d"
WHITE = "#ffffff"

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MARGIN = 40
CONTENT_W = W - 2 * MARGIN


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def fit_font(draw, text, path, max_size, max_width, min_size=10):
    size = max_size
    while size > min_size:
        f = font(path, size)
        if text_w(draw, text, f) <= max_width:
            return f
        size -= 2
    return font(path, min_size)


def draw_centered(draw, y, text, f, fill):
    w = text_w(draw, text, f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)
    # return height
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[3] - bbox[1]


def wrap(draw, text, f, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped_centered(draw, text, f, y, max_width, line_h, fill):
    lines = wrap(draw, text, f, max_width)
    for line in lines:
        w = text_w(draw, line, f)
        draw.text(((W - w) / 2, y), line, font=f, fill=fill)
        y += line_h
    return y


def draw_wrapped_left(draw, text, f, x, y, max_width, line_h, fill):
    lines = wrap(draw, text, f, max_width)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += line_h
    return y


def main():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Top small caps ---
    f_small = font(SANS_BOLD, 17)
    draw_centered(draw, 22, "THE WORLD'S NEWS  ·  IN ONE IMAGE", f_small, INK)
    # thin rules
    draw.line([(MARGIN, 52), (W - MARGIN, 52)], fill=INK, width=2)
    draw.line([(MARGIN, 57), (W - MARGIN, 57)], fill=INK, width=1)

    # --- Masthead ---
    f_mast = fit_font(draw, "WORLD TODAY", SERIF_BOLD, 96, CONTENT_W)
    draw_centered(draw, 64, "WORLD TODAY", f_mast, INK)

    draw.line([(MARGIN, 168), (W - MARGIN, 168)], fill=INK, width=1)

    # --- Red date band ---
    band_y0, band_y1 = 176, 214
    draw.rectangle([MARGIN, band_y0, W - MARGIN, band_y1], fill=RED)
    f_date = fit_font(draw, "WEDNESDAY, NOVEMBER 18, 2026", SANS_BOLD, 22, CONTENT_W - 40)
    # vertically center in band
    bbox = draw.textbbox((0, 0), "WEDNESDAY, NOVEMBER 18, 2026", font=f_date)
    th = bbox[3] - bbox[1]
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, band_y0 + (band_y1 - band_y0 - th) / 2 - bbox[1]),
              "WEDNESDAY, NOVEMBER 18, 2026", font=f_date, fill=WHITE)

    # --- Headline ---
    headline = "THREE PRESIDENTS, ONE CITY"
    f_head = fit_font(draw, headline, SERIF_BOLD, 52, CONTENT_W)
    draw_centered(draw, 228, headline, f_head, INK)

    # --- Subhead ---
    subhead = ("Trump lands in Shenzhen to a welcome from Xi Jinping; Putin joins them as "
               "APEC opens \u2014 and on Thursday the three sit down together for the first "
               "US\u2013China\u2013Russia trilateral in history.")
    f_sub = font(SANS, 19)
    y_after_sub = draw_wrapped_centered(draw, subhead, f_sub, 288, CONTENT_W - 20, 26, INK)

    # --- Navy graphic band ---
    gfx_y0 = 372
    gfx_y1 = 568
    draw.rectangle([MARGIN, gfx_y0, W - MARGIN, gfx_y1], fill=NAVY)

    # Gold sun
    sun_cx, sun_cy, sun_r = 830, gfx_y0 + 52, 30
    draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=GOLD)

    # Stars (deterministic)
    rng = random.Random(42)
    for _ in range(40):
        sx = rng.randint(MARGIN + 10, W - MARGIN - 10)
        sy = rng.randint(gfx_y0 + 10, gfx_y0 + 70)
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255, 180))

    # Skyline silhouette along bottom of band
    sky_base = gfx_y1 - 28  # leave room for caption strip
    buildings = [70, 110, 85, 140, 95, 125, 75, 135, 90, 115, 80, 130, 100, 70, 120, 88]
    bx = MARGIN + 8
    rng2 = random.Random(7)
    for bh in buildings:
        bw = rng2.randint(38, 58)
        if bx + bw > W - MARGIN - 8:
            bw = W - MARGIN - 8 - bx
            if bw <= 10:
                break
        draw.rectangle([bx, sky_base - bh, bx + bw, sky_base], fill="#0d1b2a")
        # lit windows
        for wy in range(sky_base - bh + 10, sky_base - 10, 16):
            for wx in range(bx + 7, bx + bw - 7, 13):
                if rng2.random() > 0.45:
                    draw.rectangle([wx, wy, wx + 5, wy + 7], fill=GOLD)
        bx += bw + 6
        if bx >= W - MARGIN - 20:
            break

    # Three overlapping circles (leaders) — drawn on top of skyline, centered
    cy = gfx_y0 + 72
    circles = [(462, RED), (512, GOLD), (562, BLUE_CIRCLE)]
    r = 38
    for cx, col in circles:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=WHITE, width=3)

    # Caption strip at bottom of band
    draw.rectangle([MARGIN, sky_base, W - MARGIN, gfx_y1], fill="#0d1b2a")
    f_cap = font(SANS_BOLD, 16)
    cap = "SHENZHEN \u2014 APEC SUMMIT OPENS"
    cw = text_w(draw, cap, f_cap)
    draw.text(((W - cw) / 2, sky_base + 5), cap, font=f_cap, fill=WHITE)

    # --- Six stories: 2 rows x 3 columns ---
    stories = [
        ("DRONES OVER THE GULF",
         "Iran sends drones at a US base in Kuwait; Bahrain downs attacks before dawn. Oil near $93."),
        ("141 DRONES OVER UKRAINE",
         "Kyiv says 126 Russian drones were downed overnight; six hurt in Dnipro."),
        ("GAZA TRUCE ON THE BRINK",
         "The peace board warns the ceasefire could collapse; 950,000 displaced face floods."),
        ("DEMOCRATS TAKE THE SENATE",
         "Peltola's Alaska win seals a 56\u201344 majority. Jesse Jackson dies at 84."),
        ("CYCLONE AKVAN LASHES ODISHA",
         "A severe storm batters India's east coast; schools shut, thousands evacuated."),
        ("NVIDIA AFTER HUANG",
         "The board rules out founder Jensen Huang's return as CEO \u2014 then beats the forecast."),
    ]
    col_gap = 24
    col_w = (CONTENT_W - 2 * col_gap) // 3
    row_y = [592, 772]
    f_story_head = font(SANS_BOLD, 16)
    f_story_body = font(SANS, 15)

    # horizontal rule above stories
    draw.line([(MARGIN, 582), (W - MARGIN, 582)], fill=INK, width=1)

    for idx, (head, body) in enumerate(stories):
        row = idx // 3
        col = idx % 3
        x = MARGIN + col * (col_w + col_gap)
        y = row_y[row]
        # headline (wrapped, red bold)
        y2 = draw_wrapped_left(draw, head, f_story_head, x, y, col_w, 20, RED)
        y2 += 4
        # body
        draw_wrapped_left(draw, body, f_story_body, x, y2, col_w, 20, INK)
        # vertical dividers between columns
        if col < 2:
            dx = x + col_w + col_gap // 2
            draw.line([(dx, y), (dx, y + 150)], fill="#c9bfa5", width=1)

    # horizontal rule between rows
    draw.line([(MARGIN, 752), (W - MARGIN, 752)], fill="#c9bfa5", width=1)
    # rule above footer
    draw.line([(MARGIN, 942), (W - MARGIN, 942)], fill=INK, width=2)
    draw.line([(MARGIN, 947), (W - MARGIN, 947)], fill=INK, width=1)

    # --- Footer ticker ---
    ticker = "QUAD MEETS IN MANILA  \u00b7  US LOSES MEASLES-FREE STATUS  \u00b7  SIBERIA CRASH KILLS 19"
    f_tick = fit_font(draw, ticker, SANS_BOLD, 15, CONTENT_W)
    draw_centered(draw, 962, ticker, f_tick, INK)
    f_ed = font(SANS, 12)
    draw_centered(draw, 986, "WORLD TODAY  \u00b7  ONE PAGE  \u00b7  ALL THE NEWS THAT FITS", f_ed, "#6b6252")

    img.save("entry.png", "PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
