#!/usr/bin/env python3
"""
Derive every logo asset from the single source badge.

The source is white artwork on a solid black square. Because it is effectively
two-tone (1.31M pure-black px, 223K pure-white px, 36K antialiased edge px),
luminance doubles as a perfect alpha channel: keying on it preserves the
antialiasing instead of producing the jagged edges a hard threshold would give.
"""
from PIL import Image, ImageDraw
import numpy as np
import os

SRC = "assets/source/logo.png"
OUT = "assets/img"
os.makedirs(OUT, exist_ok=True)

src = Image.open(SRC).convert("RGB")
lum = np.array(src.convert("L"))


def keyed(rgb):
    """Artwork in `rgb`, alpha taken from source luminance, cropped square to the badge."""
    h, w = lum.shape
    a = np.zeros((h, w, 4), dtype=np.uint8)
    a[..., 0], a[..., 1], a[..., 2] = rgb
    a[..., 3] = lum
    im = Image.fromarray(a, "RGBA")

    ys, xs = np.where(lum > 40)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    side = max(x1 - x0, y1 - y0) + 1
    box = (round(cx - side / 2), round(cy - side / 2),
           round(cx + side / 2), round(cy + side / 2))
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im.crop(box), (0, 0))
    return sq


white = keyed((255, 255, 255))
black = keyed((0, 0, 0))

# The badge appears at wildly different sizes (40px in the header, ~300px in
# the hero). One large file everywhere would make the header pay hero weight,
# so emit a ladder and let srcset pick. Saved as LA (grey+alpha) rather than
# RGBA: the artwork is single-value, so two channels carry it losslessly at
# roughly a quarter of the file size.
WIDTHS = [64, 128, 256, 400, 600]


def save_mono(im, path, level, w):
    small = im.resize((w, w), Image.LANCZOS)
    la = Image.new("LA", small.size, (level, 0))
    la.putalpha(small.getchannel("A"))
    la.save(path, optimize=True)


for name, art, level in (("logo-white", white, 255), ("logo-black", black, 0)):
    for w in WIDTHS:
        save_mono(art, f"{OUT}/{name}-{w}.png", level, w)
    # Unsuffixed copy = the largest, for og/meta and any non-srcset reference.
    save_mono(art, f"{OUT}/{name}.png", level, WIDTHS[-1])
print("logo ladders:", WIDTHS)

# --- simplified mark: heart inside a ring, no arced type ------------------
# The full badge's arced phone number turns to mush below ~64px, so the icon
# keeps only the circular silhouette and the heart.
HEART_BOX = (389, 530, 571, 708)  # located by column-profile analysis
heart_lum = lum[HEART_BOX[1]:HEART_BOX[3], HEART_BOX[0]:HEART_BOX[2]]


def mark(size, disc_fill, art, pad_ratio=0.0):
    """Heart-in-a-circle. `disc_fill` may be None for a transparent interior."""
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    inset = S * pad_ratio
    r = (S - 2 * inset) / 2
    cx = cy = S / 2

    if disc_fill is not None:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=disc_fill)

    stroke = S * 0.052
    ro = r * 0.995
    d.ellipse([cx - ro, cy - ro, cx + ro, cy + ro], outline=art, width=round(stroke))

    hw = round(S * 0.40 * (1 - pad_ratio * 2))
    hh = round(hw * heart_lum.shape[0] / heart_lum.shape[1])
    ha = Image.fromarray(heart_lum, "L").resize((hw, hh), Image.LANCZOS)
    tint = Image.new("RGBA", (hw, hh), art)
    tint.putalpha(ha)
    im.alpha_composite(tint, (round(cx - hw / 2), round(cy - hh / 2)))

    return im.resize((size, size), Image.LANCZOS)


# Black disc + white ring/heart: faithful to the real badge and legible on both
# light and dark browser tab bars.
DISC = (0, 0, 0, 255)
ART = (255, 255, 255, 255)

mark(32, DISC, ART).save(f"{OUT}/favicon-32.png", optimize=True)
mark(180, DISC, ART, pad_ratio=0.06).convert("RGB").save(f"{OUT}/apple-touch-icon.png", optimize=True)

ico = mark(256, DISC, ART)
ico.save(f"{OUT}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print("favicon-32.png / apple-touch-icon.png / favicon.ico")

# --- OG image: badge centred on black, generous clear space ---------------
og = Image.new("RGB", (1200, 630), (0, 0, 0))
d = og.height - 2 * round(og.height * 0.16)  # >=25% of diameter clear top & bottom
badge = white.resize((d, d), Image.LANCZOS)
og.paste(badge, ((1200 - d) // 2, (630 - d) // 2), badge)
og.save(f"{OUT}/og-image.png", optimize=True)
print("og-image.png", og.size, "badge", d)
