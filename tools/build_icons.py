#!/usr/bin/env python3
"""Generate the home-screen / favicon set.

    pip install pillow
    python3 tools/build_icons.py

Draws the site's own identity: the QM monogram over the dispersed-beam rule.
Backgrounds are opaque on purpose - iOS composites any alpha against black and
applies its own rounded mask, so a transparent icon comes out looking broken.
"""
import os, sys
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required:  pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.environ.get("BRICOLAGE_TTF", "/tmp/Bricolage.ttf")

BG   = (16, 23, 26)        # near-black, matches the dark theme ground
FG   = (242, 245, 243)     # off-white
# the beam, sampled from --beam in the stylesheet
BEAM = [(0.00, (109, 74, 255)), (0.34, (11, 158, 138)), (0.56, (127, 191, 58)),
        (0.78, (242, 167, 59)), (1.00, (225, 80, 60))]


def beam_colour(t):
    """Linear interpolation along the beam gradient at position t in [0,1]."""
    for i in range(len(BEAM) - 1):
        p0, c0 = BEAM[i]
        p1, c1 = BEAM[i + 1]
        if p0 <= t <= p1:
            f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
            return tuple(round(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
    return BEAM[-1][1]


def load_font(px):
    f = ImageFont.truetype(FONT, px)
    try:                       # variable font: pin the weight
        f.set_variation_by_axes([96, 800, 100])   # opsz, wght, wdth (this font's order)
    except Exception:
        pass
    return f


def render(size, scale=4):
    """Render at `scale` times the target and downsample, for clean edges."""
    S = size * scale
    img = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(img)

    text = "QM"
    fs = int(S * 0.40)
    font = load_font(fs)
    # measure and centre on the glyph ink, not the font's line box
    box = d.textbbox((0, 0), text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    tx = (S - tw) / 2 - box[0]
    ty = (S - th) / 2 - box[1] - S * 0.020
    d.text((tx, ty), text, font=font, fill=FG)

    # beam rule beneath the monogram
    bw, bh = int(S * 0.42), max(1, int(S * 0.035))
    bx, by = (S - bw) // 2, int(ty + th + S * 0.13)
    r = bh / 2
    for i in range(bw):
        d.rectangle([bx + i, by, bx + i, by + bh], fill=beam_colour(i / (bw - 1)))
    # round the bar's ends
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=r, fill=255)
    bar = img.crop((bx, by, bx + bw, by + bh))
    flat = Image.new("RGB", (bw, bh), BG)
    flat.paste(bar, (0, 0), mask)
    img.paste(flat, (bx, by))

    return img.resize((size, size), Image.LANCZOS)


def main():
    out = os.path.join(ROOT, "assets")
    os.makedirs(out, exist_ok=True)
    for name, size in [("apple-touch-icon.png", 180), ("icon-192.png", 192),
                       ("icon-512.png", 512), ("favicon-32.png", 32)]:
        p = os.path.join(out, name)
        render(size).save(p, "PNG", optimize=True)
        print("  %-22s %3dpx  %5d bytes" % (name, size, os.path.getsize(p)))


if __name__ == "__main__":
    main()
