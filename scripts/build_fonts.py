#!/usr/bin/env python3
"""
Download Inter and subset it to the glyphs this site actually uses.

Self-hosted deliberately: linking Google's CDN would send every visitor's IP to
a third party and create a privacy obligation the site is otherwise free of.

Google serves Inter as a single *variable* font — requesting discrete weights
returns the same file each time — so one 300..800 axis file covers the light
body copy and heavy headlines with no separate weight downloads.

Run `python3 scripts/audit.py` afterwards; it re-checks that every character in
the rendered copy is present in the subset.
"""
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
import os
import re
import subprocess

OUT = "assets/fonts/inter-var.woff2"
CSS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300..800&display=swap"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0 Safari/537.36")

# Everything the site can render: ASCII plus the typographic marks used in the
# copy, nav, eyebrows, footer and link arrows. Keep this in sync with the copy —
# a character missing here silently falls back to a system font.
CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " .,:;!?'\"()[]{}/\\|&@#%*+-=_<>$"
    "’‘“”–—·©®™°…"
)
# Note: the arrows in .link-more are inline SVG, not text. Google's latin
# subset does not carry U+2192, so a text arrow would silently fall back to a
# system font and render inconsistently across platforms.


def sh(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


css = sh("curl", "-sS", "-A", UA, CSS_URL)
# Google emits one @font-face per unicode subset (cyrillic-ext, greek, latin,
# ...). Take the *latin* block specifically — grabbing the first url() in the
# file lands on cyrillic-ext, which contains none of the glyphs below.
block = re.search(r'/\*\s*latin\s*\*/\s*@font-face\s*\{(.*?)\}', css, re.S)
if not block:
    raise SystemExit("could not find the latin @font-face block")
url = re.search(r'url\((https://[^)]+\.woff2)\)', block.group(1)).group(1)
print("variable font (latin):", url.rsplit("/", 1)[-1])

os.makedirs("assets/fonts", exist_ok=True)
sh("curl", "-sS", "-o", "/tmp/inter-src.woff2", url)
before = os.path.getsize("/tmp/inter-src.woff2")

# Glyph subset, keeping the variation tables intact
subset.main(["/tmp/inter-src.woff2", f"--text={CHARS}", "--flavor=woff2",
             "--output-file=/tmp/inter-sub.woff2",
             "--layout-features=kern,liga,calt", "--no-hinting"])

# Clamp the weight axis to the range the design uses; still variable, just
# without deltas for weights nothing on the site asks for.
f = TTFont("/tmp/inter-sub.woff2")
f = instancer.instantiateVariableFont(f, {"wght": (300, 400, 800)}, updateFontNames=False)
f.flavor = "woff2"
f.save(OUT)

out = TTFont(OUT)
axis = out["fvar"].axes[0]
missing = [c for c in CHARS if c.strip() and ord(c) not in out.getBestCmap()]
print(f"axis {axis.axisTag}: {axis.minValue}..{axis.maxValue}")
print(f"glyphs: {len(out.getBestCmap())}  missing from request: {missing or 'none'}")
print(f"size: {before/1024:.1f}K -> {os.path.getsize(OUT)/1024:.1f}K")
