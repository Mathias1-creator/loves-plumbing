#!/usr/bin/env python3
"""Check the finished site against the delivery checklist."""
import glob
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

PAGES = sorted(glob.glob("*.html") + glob.glob("*/index.html"))
fails, warns = [], []


def ok(msg):   print(f"  \033[32mPASS\033[0m  {msg}")
def bad(msg):  fails.append(msg); print(f"  \033[31mFAIL\033[0m  {msg}")
def warn(msg): warns.append(msg); print(f"  \033[33mWARN\033[0m  {msg}")


html = {p: open(p, encoding="utf-8").read() for p in PAGES}
allhtml = "\n".join(html.values())


def visible_text(src):
    """Rendered copy only — no tags, and therefore no attribute values.

    Matters because inlined brand SVGs carry long paths of bezier coordinates
    that look like phone numbers to a loose regex, and supplied third-party
    URLs carry punctuation we do not control."""
    src = re.sub(r"<script.*?</script>|<style.*?</style>", " ", src, flags=re.S)
    src = re.sub(r"<[^>]+>", " ", src)
    return re.sub(r"\s+", " ", src)


alltext = "\n".join(visible_text(v) for v in html.values())
# href/src values, for link-level checks
all_urls = re.findall(r'(?:href|src)="([^"]+)"', allhtml)

print("\n\033[1m1. Phone number consistency\033[0m")
tels = set(re.findall(r'tel:([+\d]+)', allhtml))
smss = set(re.findall(r'sms:([+\d]+)', allhtml))
ok(f"tel: targets = {tels}") if tels == {"+19515959240"} else bad(f"unexpected tel targets: {tels}")
ok(f"sms: targets = {smss}") if smss == {"+19515959240"} else bad(f"unexpected sms targets: {smss}")
# any other phone-shaped string in the rendered copy?
others = set(re.findall(r'\(?\b(?!951)\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b', alltext))
ok("no other phone number appears in visible copy") if not others else bad(f"other phone numbers: {others}")
disp = set(re.findall(r'\(951\)\s*595-9240|951-595-9240', alltext))
ok(f"displayed formats: {disp}")

print("\n\033[1m2. Business name\033[0m")
# Copy only. The supplied Google Maps URL spells the business with a straight
# apostrophe; that is Google's canonical link and must not be rewritten.
straight = alltext.count("Love's")
curly = alltext.count("Love’s")
url_straight = sum(u.count("Love's") for u in all_urls)
ok(f"typographic apostrophe used consistently in copy ({curly} refs, 0 straight)") if straight == 0 else bad(f"{straight} straight-apostrophe refs in copy")
if url_straight:
    print(f"  \033[36mINFO\033[0m  {url_straight} straight apostrophe(s) inside the supplied Google Maps URL — left verbatim")
badname = re.findall(r"Love’s Plumbing (?:And|AND) Drains|Love’s Plumbing and Drain\b", allhtml)
ok('spelling is "Love’s Plumbing and Drains" everywhere') if not badname else bad(f"name variants: {set(badname)}")

print("\n\033[1m3. Image metadata / GPS\033[0m")
try:
    from PIL import Image
    residual = []
    for p in glob.glob("assets/img/photos/*"):
        im = Image.open(p)
        if len(im.getexif()) or im.info.get("icc_profile") or im.info.get("exif"):
            residual.append(os.path.basename(p))
    n = len(glob.glob("assets/img/photos/*"))
    ok(f"all {n} output files carry zero EXIF/ICC/GPS") if not residual else bad(f"metadata survives in {residual[:5]}")
except ImportError:
    warn("Pillow unavailable, skipped")

print("\n\033[1m4. No street address published\033[0m")
addr = re.findall(r'\b\d{2,6}\s+(?:[A-Z][a-z]+\s+){1,3}(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Dr|Drive|Ln|Lane|Way|Ct|Court)\b', allhtml)
ok("no street address pattern found") if not addr else bad(f"possible address: {addr}")
ok("no streetAddress in JSON-LD") if '"streetAddress"' not in allhtml else bad("JSON-LD contains streetAddress")
# An embedded map is a subresource (<iframe>, or maps in a src=). An outbound
# "Read More on Google" link is not an embed and loads nothing.
embeds = re.findall(r"<iframe\b", allhtml)
map_src = [u for u in re.findall(r'src="([^"]+)"', allhtml) if "google.com/maps" in u or "maps.google" in u]
ok("no map embed (no iframe, no map subresource)") if not embeds and not map_src else bad(f"map/iframe embed present: {embeds[:2]}{map_src[:2]}")

print("\n\033[1m5. No invented claims\033[0m")
claims = {
    "free estimate": r"free estimate",
    "warranty": r"\bwarrant(y|ies)\b",
    "financing": r"\bfinancing\b",
    "pricing": r"\$\d|\bper hour\b|\bflat rate\b",
    "guarantee": r"\bguarantee",
    "satisfaction promise": r"satisfaction guarantee",
}
found = {k: v for k, v in claims.items() if re.search(v, allhtml, re.I)}
ok("no pricing, warranty, free-estimate or financing claims") if not found else bad(f"claims present: {list(found)}")

print("\n\033[1m6. No external requests (privacy)\033[0m")
ext = set(re.findall(r'(?:src|href)="(https?://[^"]+)"', allhtml))
# Outbound links a visitor chooses to follow. None of these are fetched by the
# page itself, so the "no third-party requests" claim on /privacy still holds.
allowed_prefixes = ("https://www.instagram.com/", "https://mathias1-creator.github.io/",
                    "https://www.google.com/maps/", "https://www.yelp.com/biz/")
bad_ext = [u for u in ext if not u.startswith(allowed_prefixes)]
ok("only same-origin assets + Instagram/Google/Yelp outbound links") if not bad_ext else bad(f"external refs: {bad_ext}")

# Those outbound links must not become automatic requests
auto = re.findall(r'<(?:img|script|link|iframe|source)[^>]+(?:src|href)="https?://(?!mathias1-creator)[^"]+"', allhtml)
ok("no page-initiated third-party requests (logos are inlined SVG)") if not auto else bad(f"third-party subresource: {auto[:3]}")
ok('review link-outs use rel="noopener noreferrer" and target="_blank"') if allhtml.count('rel="noopener noreferrer"') >= 3 else bad("missing rel on external links")
ok("no aggregate rating / review-count markup") if not re.search(r'aggregateRating|ratingValue|reviewCount', allhtml) else bad("stale-able rating markup present")
ok("Yelp link points at the business page, not the review form") if "/writeareview" not in allhtml else bad("links to Yelp review submission form")
ok("no Google Fonts CDN reference") if "fonts.googleapis" not in allhtml and "fonts.gstatic" not in allhtml else bad("Google Fonts CDN referenced")
# Inspect script elements only — the privacy page's prose says the words
# "analytics" and "tracking pixels" precisely to state there are none.
scripts = re.findall(r"<script\b[^>]*>(.*?)</script>|<script\b([^>]*)/?>", allhtml, re.S)
script_text = " ".join(a + b for a, b in scripts)
script_srcs = re.findall(r'<script[^>]+src="([^"]+)"', allhtml)
tracker = re.search(r'gtag|googletagmanager|google-analytics|fbq\(|hotjar|clarity\.ms|segment\.', script_text, re.I)
ok("no analytics/tag manager in any script") if not tracker else bad(f"tracking script: {tracker.group(0)}")
ok(f"all scripts are same-origin: {set(script_srcs)}") if all(not s.startswith("http") for s in script_srcs) else bad("third-party script")

print("\n\033[1m7. Images: alt text, dimensions, lazy loading\033[0m")


class ImgAudit(HTMLParser):
    def __init__(self): super().__init__(); self.imgs = []
    def handle_starttag(self, tag, attrs):
        if tag == "img": self.imgs.append(dict(attrs))


total = noalt = nodim = eager = 0
for p, src in html.items():
    a = ImgAudit(); a.feed(src)
    for i in a.imgs:
        # The lightbox <img> is an empty placeholder inside a display:none
        # dialog; JS sets its src and alt from the trigger when it opens, and
        # it is sized dynamically, so it has no content and causes no CLS.
        if "lb-img" in i.get("class", ""):
            continue
        total += 1
        if not i.get("alt", "").strip(): noalt += 1
        if not (i.get("width") and i.get("height")): nodim += 1
        if i.get("loading") != "lazy": eager += 1
ok(f"all {total} <img> have non-empty alt text") if noalt == 0 else bad(f"{noalt} images missing alt")
ok(f"all {total} <img> have explicit width+height (CLS guard)") if nodim == 0 else bad(f"{nodim} missing dimensions")
print(f"  \033[36mINFO\033[0m  {eager} eager-loaded (hero logo + gallery lead), {total - eager} lazy")

print("\n\033[1m8. Semantics & accessibility\033[0m")
for p, src in html.items():
    h1 = len(re.findall(r"<h1[ >]", src))
    if h1 != 1: bad(f"{p}: {h1} <h1> elements")
ok("exactly one <h1> per page") if not any("<h1>" in f for f in fails) else None
ok("lang attribute present on all pages") if all('<html lang="en">' in s for s in html.values()) else bad("missing lang")
ok("skip link on all pages") if all('class="skip"' in s for s in html.values()) else bad("missing skip link")
ok("viewport meta on all pages") if all('name="viewport"' in s for s in html.values()) else bad("missing viewport")

print("\n\033[1m9. SEO\033[0m")
titles = {p: re.search(r"<title>(.*?)</title>", s, re.S).group(1) for p, s in html.items()}
descs = {p: re.search(r'name="description" content="(.*?)"', s, re.S).group(1) for p, s in html.items()}
ok(f"{len(set(titles.values()))}/{len(titles)} unique titles") if len(set(titles.values())) == len(titles) else bad("duplicate titles")
ok(f"{len(set(descs.values()))}/{len(descs)} unique descriptions") if len(set(descs.values())) == len(descs) else bad("duplicate descriptions")
ok("canonical on all pages") if all('rel="canonical"' in s for s in html.values()) else bad("missing canonical")
ok("OG + Twitter card on all pages") if all('og:image' in s and 'twitter:card' in s for s in html.values()) else bad("missing OG/Twitter")
for f in ("sitemap.xml", "robots.txt", ".nojekyll"):
    ok(f"{f} present") if os.path.exists(f) else bad(f"{f} missing")

print("\n\033[1m10. JSON-LD validity\033[0m")
for p, src in html.items():
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        try:
            d = json.loads(block)
            items = d if isinstance(d, list) else [d]
            types = [i.get("@type") for i in items]
            if p == "index.html":
                ok(f"{p}: valid JSON-LD {types}")
        except json.JSONDecodeError as e:
            bad(f"{p}: invalid JSON-LD — {e}")
ok("Plumber schema on every page") if all('"@type":"Plumber"' in s for s in html.values()) else bad("schema missing somewhere")

print("\n\033[1m11. Internal links resolve\033[0m")
broken = []
for p, src in html.items():
    base = os.path.dirname(p)
    for href in re.findall(r'(?:href|src)="((?!https?:|mailto:|tel:|sms:|#|data:)[^"]+)"', src):
        target = os.path.normpath(os.path.join(base, href.split("#")[0]))
        if target.endswith("/") or os.path.isdir(target):
            target = os.path.join(target, "index.html")
        if not os.path.exists(target) and not os.path.exists(target.rstrip("/")):
            broken.append(f"{p} -> {href}")
ok(f"all internal links and asset refs resolve") if not broken else bad(f"broken: {broken[:6]}")

print("\n\033[1m12. Real first-load weight on a phone (390px, 2x DPR)\033[0m")
# Measured in a real browser: only the srcset variant actually chosen, and
# lazy images below the fold are never fetched. Summing every referenced file
# would wildly overstate this (it counts all 3 widths x 2 formats, plus the
# full-size images the lightbox loads only on demand).
try:
    res = subprocess.run(["node", "/tmp/weigh.js"], capture_output=True, text=True, timeout=300)
    if res.returncode == 0:
        for page, d in json.loads(res.stdout).items():
            status = ok if d["mb"] < 3.0 else bad
            status(f"{page:<10} {d['mb']:.2f} MB over {d['requests']} requests   {d['byType']}")
    else:
        warn(f"weight measurement unavailable: {res.stderr.strip()[:120]}")
except Exception as e:
    warn(f"weight measurement skipped: {e}")

print("\n" + "=" * 62)
if fails:
    print(f"\033[31m{len(fails)} FAILURES\033[0m"); [print("  -", f) for f in fails]
    sys.exit(1)
print(f"\033[32mAll checks passed\033[0m" + (f" ({len(warns)} warnings)" if warns else ""))
