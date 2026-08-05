#!/usr/bin/env python3
"""
Emit the six flat HTML pages.

The deployed site is plain HTML/CSS/JS with no runtime build step; this script
exists only so the ~29 photos x 3 widths x 2 formats of srcset markup stay
consistent and correct rather than being hand-copied.
"""
import json
import os

BASE = "https://mathias1-creator.github.io/loves-plumbing"

# Typographic apostrophe throughout, so the brand name matches the curly
# apostrophes in surrounding prose ("it's", "site's") instead of sitting next
# to them as a straight tick. Spelling is unchanged: plural "Drains",
# lowercase "and".
NAME = "Love’s Plumbing and Drains"
OWNER = "Anthony Love"
TEL_DISPLAY = "(951) 595-9240"
TEL_LINK = "+19515959240"
EMAIL = "lovesplumbing_drains@yahoo.com"
LICENSE = "1138309"
INSTAGRAM = "https://www.instagram.com/loves_plumbing_and_drains/"
AREAS = ["Riverside", "San Diego", "Orange County"]

photos = {p["slug"]: p for p in json.load(open("assets/img/photos.json"))}

PAGES = [
    ("index.html", "", "Home"),
    ("services/index.html", "services/", "Services"),
    ("gallery/index.html", "gallery/", "Gallery"),
    ("about/index.html", "about/", "About"),
    ("contact/index.html", "contact/", "Contact"),
    ("privacy/index.html", "privacy/", "Privacy"),
]
NAV = [("", "Home"), ("services/", "Services"), ("gallery/", "Gallery"),
       ("about/", "About"), ("contact/", "Contact")]


def rel(path_prefix):
    """Relative path back to the site root — keeps the site portable to any
    base URL, which matters because Pages serves this from a subdirectory."""
    return "../" * path_prefix.count("/")


# ------------------------------------------------------------ media ------
def picture(slug, sizes, cls="", loading="lazy", fetchpriority=None, r=""):
    p = photos[slug]
    base = f"{r}assets/img/photos/{slug}"
    webp = ", ".join(f"{base}-{v['w']}.webp {v['w']}w" for v in p["variants"])
    jpg = ", ".join(f"{base}-{v['w']}.jpg {v['w']}w" for v in p["variants"])
    fb = p["variants"][min(1, len(p["variants"]) - 1)]["w"]
    fp = f' fetchpriority="{fetchpriority}"' if fetchpriority else ""
    return (
        f'<picture{f" class={cls!r}" if cls else ""}>'
        f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
        f'<img src="{base}-{fb}.jpg" srcset="{jpg}" sizes="{sizes}" '
        f'width="{p["width"]}" height="{p["height"]}" alt="{esc(p["alt"])}" '
        f'loading="{loading}" decoding="async"{fp}>'
        f"</picture>"
    )


def lb_attrs(slug, r=""):
    p = photos[slug]
    base = f"{r}assets/img/photos/{slug}"
    srcset = ", ".join(f"{base}-{v['w']}.jpg {v['w']}w" for v in p["variants"])
    return (f'data-lb data-lb-src="{base}-{p["variants"][-1]["w"]}.jpg" '
            f'data-lb-srcset="{srcset}"')


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


# ------------------------------------------------------------ chrome -----
IG_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
          '<path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41-.56-.22-.96-.48-1.38-.9-.42-.42-.68-.82-.9-1.38-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41 1.27-.06 1.65-.07 4.85-.07M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.3-1.46.72-2.13 1.38C1.35 2.68.93 3.35.63 4.14.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.3.79.72 1.46 1.38 2.13.67.66 1.34 1.08 2.13 1.38.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56.79-.3 1.46-.72 2.13-1.38.66-.67 1.08-1.34 1.38-2.13.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91-.3-.79-.72-1.46-1.38-2.13C21.32 1.35 20.65.93 19.86.63c-.76-.3-1.64-.5-2.91-.56C15.67.01 15.26 0 12 0z"/>'
          '<path d="M12 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84zM12 16a4 4 0 1 1 4-4 4 4 0 0 1-4 4z"/>'
          '<circle cx="18.41" cy="5.59" r="1.44"/></svg>')

PHONE_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
             '<path d="M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.03-.24 11.36 11.36 0 0 0 3.56.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.36 11.36 0 0 0 .57 3.56 1 1 0 0 1-.25 1.03l-2.2 2.2z"/></svg>')

SMS_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
           '<path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM7 9h10v2H7V9zm0 4h7v2H7v-2z"/></svg>')


# Drawn rather than typed: Google's latin webfont subset has no U+2192, so a
# text arrow would fall back to a system font and render inconsistently.
ARROW_SVG = ('<svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
             'aria-hidden="true" focusable="false"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')


def brand_svg(name):
    """Inline an official brand mark from assets/img.

    Kept as real files so they stay auditable and swappable, but inlined into
    the page so a visitor's browser makes no extra request for them. The marks
    are used unmodified — Google's four-colour G and Yelp's red burst — which
    is what both companies' brand guidelines require, and what makes them read
    as genuine third-party badges rather than site decoration.
    """
    svg = open(f"assets/img/logo-{name}.svg").read().strip()
    svg = svg.replace(' xmlns="http://www.w3.org/2000/svg"', "", 1)
    return svg.replace("<svg", '<svg aria-hidden="true" focusable="false"', 1)


def head(title, desc, path_prefix, og_type="website", extra=""):
    r = rel(path_prefix)
    url = f"{BASE}/{path_prefix}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">

<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(NAME)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(NAME)} — licensed plumbing, sewer and drain service">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}/assets/img/og-image.png">

<link rel="icon" href="{r}assets/img/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{r}assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<meta name="theme-color" content="#000000">

<link rel="preload" href="{r}assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/css/site.css">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(path_prefix, current):
    r = rel(path_prefix)
    aria = ' aria-current="page"'
    links = "".join(
        f'<a href="{r}{h}"{aria if h == current else ""}>{label}</a>'
        for h, label in NAV
    )
    return f"""<header class="site-header">
<div class="wrap header-inner">
<a class="brand" href="{r}">
<img src="{r}assets/img/logo-white-64.png"
     srcset="{r}assets/img/logo-white-64.png 64w, {r}assets/img/logo-white-128.png 128w"
     sizes="46px" width="46" height="46" alt="{esc(NAME)} home">
<span class="brand-name">Love&rsquo;s Plumbing<br>and Drains</span>
</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Menu"><span></span></button>
<nav class="nav" id="primary-nav" aria-label="Primary">{links}</nav>
<a class="btn btn--light header-cta" href="tel:{TEL_LINK}">{TEL_DISPLAY}</a>
</div>
</header>
"""


def footer(path_prefix):
    r = rel(path_prefix)
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="footer-grid">

<div class="footer-brand">
<img src="{r}assets/img/logo-white-128.png"
     srcset="{r}assets/img/logo-white-128.png 128w, {r}assets/img/logo-white-256.png 256w"
     sizes="104px" width="104" height="104" alt="{esc(NAME)}">
<p>Licensed plumbing, sewer and drain service. Owner-operated by {OWNER}, available 24 hours a day.</p>
</div>

<div class="footer-col">
<h2>Contact</h2>
<ul>
<li><a href="tel:{TEL_LINK}">{TEL_DISPLAY}</a></li>
<li><a href="sms:{TEL_LINK}">Text {TEL_DISPLAY}</a></li>
<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li class="muted">Open 24 hours &middot; Emergency service</li>
<li><a class="ig-link" href="{INSTAGRAM}" rel="noopener noreferrer" target="_blank">{IG_SVG}<span>Instagram</span></a></li>
</ul>
</div>

<div class="footer-col">
<h2>Service area</h2>
<ul>
<li class="muted">Riverside County</li>
<li class="muted">San Diego County</li>
<li class="muted">Orange County</li>
<li class="muted">&amp; surrounding areas</li>
</ul>
</div>

</div>
<div class="footer-bottom">
<span>&copy; 2026 {esc(NAME)} &middot; CSLB Lic. #{LICENSE} &middot; Licensed, Bonded &amp; Insured</span>
<a href="{r}privacy/">Privacy Policy</a>
</div>
</div>
</footer>
"""


def callbar():
    return f"""<div class="callbar">
<a class="call" href="tel:{TEL_LINK}">{PHONE_SVG}<span>Call</span></a>
<a class="text" href="sms:{TEL_LINK}">{SMS_SVG}<span>Text</span></a>
</div>
"""


def lightbox():
    return """<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer" aria-hidden="true">
<img class="lb-img" src="" alt="">
<button class="lb-close" type="button" aria-label="Close photo viewer"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
<button class="lb-prev" type="button" aria-label="Previous photo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 18 9 12l6-6"/></svg></button>
<button class="lb-next" type="button" aria-label="Next photo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg></button>
<p class="lb-counter"></p>
</div>
"""


def tail(path_prefix, with_lightbox=False):
    r = rel(path_prefix)
    return (footer(path_prefix) + callbar()
            + (lightbox() if with_lightbox else "")
            + f'<script src="{r}assets/js/site.js" defer></script>\n</body>\n</html>\n')


# ------------------------------------------------------------ schema -----
def schema(page_extra=None):
    """LocalBusiness / Plumber. `address` is deliberately omitted — the client
    does not publish a street address, so asserting one would be false."""
    data = {
        "@context": "https://schema.org",
        "@type": "Plumber",
        "@id": f"{BASE}/#business",
        "name": NAME,
        "url": f"{BASE}/",
        "telephone": TEL_DISPLAY,
        "email": EMAIL,
        "image": f"{BASE}/assets/img/og-image.png",
        "logo": f"{BASE}/assets/img/logo-white.png",
        "description": ("Owner-operated plumbing, sewer and drain contractor serving Riverside, "
                        "San Diego and Orange County. Water heaters, sewer and drain repair, "
                        "whole-house repipes. Licensed, bonded and insured, 24 hours a day."),
        "slogan": "Taking care of you with LOVE & Doing every job with LOVE.",
        "founder": {"@type": "Person", "name": OWNER},
        "areaServed": [{"@type": "AdministrativeArea", "name": a} for a in AREAS],
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59",
        }],
        "hasCredential": {
            "@type": "EducationalOccupationalCredential",
            "credentialCategory": "CSLB Contractor License",
            "identifier": LICENSE,
        },
        "sameAs": [INSTAGRAM],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Plumbing services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
                for n in ["Water heater installation, replacement and repair",
                          "Tankless water heater installation",
                          "Sewer and drain line repair and replacement",
                          "Drain cleanouts and camera inspection",
                          "Whole-house repipes in PEX and copper",
                          "Water filtration, softeners and reverse osmosis",
                          "Gas line installation and repair",
                          "Fixture installation and repair"]
            ],
        },
    }
    out = [data]
    if page_extra:
        out.append(page_extra)
    return ('<script type="application/ld+json">'
            + json.dumps(out if len(out) > 1 else out[0], separators=(",", ":"))
            + "</script>\n")


# ------------------------------------------------------------ content ----
SERVICES = [
    {
        "slug": "water-heaters",
        "title": "Water Heaters",
        "blurb": "Tankless installation, replacement, and repair.",
        "photo": "water-heater-tankless-navien-pair-01",
        "points": ["Tankless installation and replacement",
                   "Tank water heater replacement",
                   "Repairs, valves and gas connections",
                   "Residential and commercial systems"],
        "copy": "Whether a unit finally quit or you are moving to tankless, we handle the "
                "install, the gas and water connections, and the venting — sized for the "
                "house rather than whatever fits fastest.",
    },
    {
        "slug": "sewer-drain",
        "title": "Sewer &amp; Drain Repair",
        "blurb": "Line replacement, cleanouts, trenching, camera inspection.",
        "photo": "sewer-trench-caution-tape-01",
        "points": ["Sewer line repair and replacement",
                   "Cleanout installation",
                   "Trenching and under-slab work",
                   "Camera inspection"],
        "copy": "Sewer work is the part of the job most people never see. We locate the "
                "problem, open only what has to be opened, and put in line that will "
                "outlast the last one.",
    },
    {
        "slug": "repipes",
        "title": "Whole-House Repipes",
        "blurb": "PEX and copper.",
        "photo": "repipe-pex-ceiling-01",
        "points": ["Full-house repipes in PEX",
                   "Copper repipes and repairs",
                   "Failing galvanized replacement",
                   "Slab leak re-routes"],
        "copy": "When the pipe itself is the problem, patching it again just moves the next "
                "leak down the wall. A repipe replaces the run end to end, in PEX or copper.",
    },
    {
        "slug": "additional",
        "title": "Additional Services",
        "blurb": "Water filtration and softeners, reverse osmosis, gas lines, "
                 "fixture installation and repair.",
        "photo": "filtration-reverse-osmosis-undersink-01",
        "points": ["Water filtration and softeners",
                   "Reverse osmosis drinking water systems",
                   "Gas lines",
                   "Fixture installation and repair"],
        "copy": "Alongside the big jobs there is everything else a house needs — filtration, "
                "drinking water systems, gas lines and fixtures. If you are not sure whether "
                "it is something we do, call and ask.",
    },
]

FAQ = [
    ("What areas do you serve?",
     "Riverside, San Diego, and Orange County, plus surrounding areas."),
    ("Do you offer emergency service?",
     "Yes. Emergency service is available 24 hours a day."),
    ("Are you licensed and insured?",
     "Yes — licensed, bonded, and insured. CSLB License #1138309."),
    ("What kind of plumbing work do you do?",
     "Four main areas: water heaters, including tankless installation, replacement and repair; "
     "sewer and drain repair, including line replacement, cleanouts, trenching and camera "
     "inspection; whole-house repipes in PEX and copper; and additional work such as water "
     "filtration and softeners, reverse osmosis, gas lines, and fixture installation and repair."),
    ("I have water leaking right now — what should I do?",
     "Shut off the main water valve to the house, then call " + TEL_DISPLAY +
     ". If the leak is near anything electrical, stay clear of it and call from a safe spot."),
    ("How do I get in touch?",
     "Call or text " + TEL_DISPLAY + ", any time."),
]

TAGLINE = "Taking care of you with LOVE &amp; Doing every job with LOVE."

# Verbatim customer reviews. No aggregate rating, star count or review total
# anywhere — those go stale the moment a new review lands, and there is no
# Review/AggregateRating JSON-LD for the same reason.
GOOGLE_URL = ("https://www.google.com/maps/place/Love's+Plumbing+And+Drains/@0,0,9z/"
              "data=!4m18!1m9!3m8!1s0x2d89352209ad2d93:0xe2fe098130cb69d!"
              "2sLove's+Plumbing+And+Drains!8m2!3d33.2770784!4d-117.2098025!9m1!1b1!"
              "16s%2Fg%2F11yrfq4sx1!3m7!1s0x2d89352209ad2d93:0xe2fe098130cb69d!"
              "8m2!3d33.2770784!4d-117.2098025!9m1!1b1!16s%2Fg%2F11yrfq4sx1"
              "?entry=ttu&g_ep=EgoyMDI2MDgwMy4wIKXMDSoASAFQAw%3D%3D")
# Deliberately the business page, not /writeareview/ — a visitor following
# "Read More on Yelp" wants to read reviews, not be handed a submission form.
YELP_URL = "https://www.yelp.com/biz/love-s-plumbing-and-drains-san-diego-2"

REVIEWS_GOOGLE = [
    ("Anthony and his partner did not just an amazing job — they recovered my house "
     "from a very unprofessional fake plumber. He loves his profession, he knows what "
     "he is doing.", "Svetlana"),
    ("Immediate, fast service, very honest and reliable. Used him for ten years, always "
     "available when I need him, usually an emergency. This guy is the best.", "Steven C."),
    ("Anthony has continuously shown up for us at the drop of a hat, in the middle of the "
     "night, and under many strange circumstances — we are a 24-hour facility.", "Rachel D."),
    ("On time, good communication, very well priced and very clean. For me it was the "
     "honesty and how thorough he is.", "El E."),
]

REVIEWS_YELP = [
    ("He was the only person in the process who I genuinely felt cared that we were "
     "displaced and wanted to get us home — we weren’t just a job to him.",
     "Griff B., Encinitas"),
    ("Reliable, honest, and they do a great job. They did it at half the cost — my other "
     "plumber took a look and said I got a great deal.", "Sam C., Oceanside"),
    ("This was the best plumbing company I ever used. Anthony was cordial, professional "
     "and very competent.", "Matt S., Escondido"),
    ("Shianne and Anthony helped me out the same day and did great work double strapping "
     "the water heater for my client.", "Alexis C., Chula Vista"),
]

SELECTED = ["bathroom-dark-tile-finished-01", "water-heater-tankless-navien-pair-01",
            "sewer-trench-caution-tape-01", "repipe-pex-ceiling-01",
            "gas-line-commercial-kitchen-03", "sewer-vault-service-10"]

# Lead with the finished dark-tile bathroom — the most striking image in the set.
GALLERY = ["bathroom-dark-tile-finished-01",
           "water-heater-tankless-navien-pair-01", "sewer-trench-caution-tape-01",
           "repipe-pex-ceiling-01", "filtration-reverse-osmosis-undersink-01",
           "sewer-vault-service-10", "gas-line-commercial-kitchen-03",
           "bathroom-tub-shower-tile-02", "sewer-under-slab-tile-06",
           "repipe-copper-stucco-wall-02", "water-heater-commercial-bank-03",
           "sewer-cleanout-risers-02", "filtration-whole-house-tank-02",
           "repipe-copper-crawlspace-03", "sewer-trench-abs-cleanout-night-09",
           "water-heater-commercial-high-efficiency-02", "backflow-commercial-assembly-06",
           "sewer-cleanout-pair-04", "drain-rough-in-wall-12",
           "water-shutoff-smart-valve-04", "sewer-trench-cleanout-05",
           "repipe-abs-pex-ceiling-04", "water-heater-tank-replacement-04",
           "sewer-excavation-pvc-08", "backflow-preventer-copper-05",
           "sewer-cleanout-capped-03", "shower-enclosure-installed-03",
           "sewer-trench-slab-night-07", "sewer-line-excavation-11"]

SIZES_CARD = "(min-width: 900px) 30vw, (min-width: 560px) 45vw, 92vw"
SIZES_HALF = "(min-width: 860px) 46vw, 92vw"
SIZES_MASONRY = "(min-width: 1240px) 22vw, (min-width: 900px) 30vw, (min-width: 560px) 45vw, 92vw"


def cta_buttons(variant="light"):
    a = "btn--light" if variant == "light" else "btn--dark"
    b = "btn--outline-light" if variant == "light" else "btn--outline-dark"
    return (f'<div class="btn-row">'
            f'<a class="btn {a}" href="tel:{TEL_LINK}">Call {TEL_DISPLAY}</a>'
            f'<a class="btn {b}" href="sms:{TEL_LINK}">Text us</a>'
            f"</div>")


def review_column(platform, mark, reviews):
    items = "".join(
        f"<figure class=\"review\"><blockquote><p>&ldquo;{esc(q)}&rdquo;</p></blockquote>"
        f"<figcaption>{esc(who)}</figcaption></figure>"
        for q, who in reviews)
    return (f'<div class="reviews-col">'
            f'<h3 class="reviews-source">{mark}<span>{platform}</span></h3>'
            f'<div class="review-list">{items}</div>'
            f"</div>")


def reviews_section():
    return f"""<section class="section section--dark" aria-labelledby="rev-h">
<div class="wrap">
<div class="section-head" style="text-align:center;margin-inline:auto">
<span class="eyebrow">Reviews</span>
<h2 id="rev-h">What customers say.</h2>
</div>
<div class="reviews-grid reveal">
{review_column("Google", brand_svg("google"), REVIEWS_GOOGLE)}
{review_column("Yelp", brand_svg("yelp"), REVIEWS_YELP)}
</div>
<div class="btn-row" style="justify-content:center;margin-top:clamp(2.5rem,5vw,3.5rem)">
<a class="btn btn--light" href="{esc(GOOGLE_URL)}" target="_blank" rel="noopener noreferrer">Read More on Google</a>
<a class="btn btn--light" href="{esc(YELP_URL)}" target="_blank" rel="noopener noreferrer">Read More on Yelp</a>
</div>
</div>
</section>
"""


def final_cta(r=""):
    return f"""<section class="section section--dark" aria-labelledby="cta-h">
<div class="wrap" style="text-align:center">
<span class="eyebrow">Available 24 hours</span>
<h2 id="cta-h" class="reveal">Call or text and talk to Anthony directly.</h2>
<p class="lede reveal" style="margin:1.25rem auto 2.25rem">No call center, no dispatcher &mdash; the person who answers is the person doing the work.</p>
<a class="contact-big" href="tel:{TEL_LINK}">{TEL_DISPLAY}</a>
<div class="reveal" style="display:flex;justify-content:center">{cta_buttons('light')}</div>
<p class="hero-license">Licensed, Bonded &amp; Insured &middot; CSLB #{LICENSE}</p>
</div>
</section>
"""


# ------------------------------------------------------------- pages -----
def build_index():
    pfx, r = "", ""
    faq_schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
    }
    h = head(
        f"{NAME} — Plumbing, Sewer &amp; Drain Repair | Riverside, San Diego &amp; Orange County",
        "Owner-operated plumbing, sewer and drain contractor serving Riverside, San Diego and "
        "Orange County. Water heaters, sewer repair, whole-house repipes. Licensed, bonded and "
        "insured. Call or text (951) 595-9240, 24 hours a day.",
        pfx, extra=schema(faq_schema))

    cards = "".join(
        f'<a class="svc-card reveal" href="{r}services/#{s["slug"]}">'
        f'<div class="svc-media">{picture(s["photo"], SIZES_CARD, r=r)}</div>'
        f'<div class="svc-body"><h3>{s["title"]}</h3><p>{s["blurb"]}</p></div></a>'
        for s in SERVICES)

    work = "".join(
        f'<a href="{r}gallery/">{picture(sl, SIZES_CARD, r=r)}</a>' for sl in SELECTED)

    faq_items = "".join(
        f'<div class="faq-item">'
        f'<h3><button class="faq-q" type="button" id="faq-q{i}" aria-controls="faq-a{i}" aria-expanded="true">'
        f'<span>{q}</span><span class="faq-icon" aria-hidden="true"></span></button></h3>'
        f'<div class="faq-a" id="faq-a{i}" role="region" aria-labelledby="faq-q{i}"><p>{a}</p></div>'
        f"</div>" for i, (q, a) in enumerate(FAQ))

    trust = "".join(f"<li>{t}</li>" for t in [
        "24/7 Emergency", "Licensed &amp; Insured", "10+ Years Experience",
        "Riverside", "San Diego", "Orange County"])

    return h + header(pfx, "") + f"""<main id="main">

<section class="hero">
<div class="wrap">
<img class="hero-badge" src="{r}assets/img/logo-white-400.png"
     srcset="{r}assets/img/logo-white-256.png 256w, {r}assets/img/logo-white-400.png 400w, {r}assets/img/logo-white-600.png 600w"
     sizes="(min-width: 900px) 292px, 27vw"
     width="600" height="600" alt="{esc(NAME)}" fetchpriority="high">
<h1>Plumbing, sewer and drain repair in Riverside, San Diego and Orange County</h1>
<p class="hero-tagline">{TAGLINE}</p>
<p class="lede">Water heaters, sewer and drain lines, and whole-house repipes. Owner-operated, and available 24 hours a day when something gives out.</p>
{cta_buttons('light')}
<p class="hero-license">Licensed, Bonded &amp; Insured &middot; CSLB #{LICENSE}</p>
</div>
</section>

<section class="trust" aria-label="At a glance">
<div class="wrap"><ul>{trust}</ul></div>
</section>

<section class="section section--light" aria-labelledby="svc-h">
<div class="wrap">
<div class="section-head">
<span class="eyebrow">What we do</span>
<h2 id="svc-h">Four things, done properly.</h2>
</div>
<div class="svc-grid">{cards}</div>
</div>
</section>

<section class="section section--dark" aria-labelledby="work-h">
<div class="wrap">
<div class="section-head">
<span class="eyebrow">Selected work</span>
<h2 id="work-h">Real jobs, real sites.</h2>
<p class="lede" style="margin-top:1.25rem">Every photo on this site is work {OWNER} did himself.</p>
</div>
<div class="work-grid reveal">{work}</div>
<p style="margin-top:2.5rem"><a class="link-more" href="{r}gallery/">See the full gallery {ARROW_SVG}</a></p>
</div>
</section>

<section class="section section--light" aria-labelledby="about-h">
<div class="wrap about-split">
<div class="about-copy reveal">
<span class="eyebrow">About</span>
<h2 id="about-h" style="margin-bottom:1.5rem">Straight answers, and the work done right the first time.</h2>
<p>{NAME} is owned and operated by {OWNER} — more than ten years in the trade, two years running his own shop.</p>
<p>That means no upselling, and no disappearing halfway through a job. You deal with Anthony directly.</p>
<p style="margin-top:2rem"><a class="link-more" href="{r}about/">More about Anthony {ARROW_SVG}</a></p>
</div>
<div class="reveal">{picture('repipe-copper-crawlspace-03', SIZES_HALF, r=r)}</div>
</div>
</section>

{reviews_section()}
<section class="section section--grey" aria-labelledby="faq-h">
<div class="wrap">
<div class="section-head" style="text-align:center;margin-inline:auto">
<span class="eyebrow">Questions</span>
<h2 id="faq-h">Frequently asked.</h2>
</div>
<div class="faq">{faq_items}</div>
</div>
</section>

{final_cta(r)}
</main>
""" + tail(pfx)


def build_services():
    pfx = "services/"
    r = rel(pfx)
    h = head(
        f"Plumbing Services — Water Heaters, Sewer &amp; Drain, Repipes | {NAME}",
        "Tankless and tank water heaters, sewer and drain line repair, cleanouts and trenching, "
        "whole-house repipes in PEX and copper, water filtration, gas lines and fixtures. "
        "Serving Riverside, San Diego and Orange County.",
        pfx, extra=schema())

    blocks = []
    for i, s in enumerate(SERVICES):
        dark = i % 2 == 1
        sec = "section--dark" if dark else "section--light"
        flip = " svc-detail--flip" if dark else ""
        pts = "".join(f"<li>{p}</li>" for p in s["points"])
        blocks.append(f"""<section class="section {sec}" id="{s['slug']}" aria-labelledby="{s['slug']}-h">
<div class="wrap">
<div class="svc-detail{flip}">
<div class="svc-detail-media reveal">{picture(s['photo'], SIZES_HALF, r=r)}</div>
<div class="svc-detail-body reveal">
<span class="eyebrow">0{i + 1}</span>
<h2 id="{s['slug']}-h">{s['title']}</h2>
<p class="lede" style="margin-top:1.25rem">{s['blurb']}</p>
<p style="margin-top:1.25rem">{s['copy']}</p>
<ul>{pts}</ul>
<div style="margin-top:2rem">{cta_buttons('dark' if not dark else 'light')}</div>
</div>
</div>
</div>
</section>""")

    return h + header(pfx, "services/") + f"""<main id="main">
<section class="section section--dark">
<div class="wrap">
<span class="eyebrow">Services</span>
<h1>What we do, and how we do it.</h1>
<p class="lede" style="margin-top:1.5rem">Four areas of work, each backed by photos of the actual jobs. Licensed, bonded and insured, across Riverside, San Diego and Orange County.</p>
<div style="margin-top:2.5rem">{cta_buttons('light')}</div>
</div>
</section>
{''.join(blocks)}
{final_cta(r)}
</main>
""" + tail(pfx)


def build_gallery():
    pfx = "gallery/"
    r = rel(pfx)
    h = head(
        f"Gallery — Plumbing, Sewer &amp; Repipe Job Photos | {NAME}",
        "Photographs of completed plumbing work across Riverside, San Diego and Orange County: "
        "tankless water heaters, sewer trenches and cleanouts, PEX and copper repipes, "
        "filtration systems and finished bathrooms.",
        pfx, extra=schema())

    # Every photo sits in the masonry on equal terms — no feature image — so the
    # gallery reads as one consistent grid. The first tile is the LCP element,
    # so it loads eagerly; everything after it stays lazy.
    items = "".join(
        f'<button class="masonry-item" type="button" {lb_attrs(sl, r)} '
        f'aria-label="Open photo: {esc(photos[sl]["alt"])}">'
        f'{picture(sl, SIZES_MASONRY, r=r, loading="eager" if i == 0 else "lazy", fetchpriority="high" if i == 0 else None)}</button>'
        for i, sl in enumerate(GALLERY))

    return h + header(pfx, "gallery/") + f"""<main id="main">
<section class="section section--dark" style="padding-bottom:clamp(2rem,4vw,3rem)">
<div class="wrap">
<span class="eyebrow">Gallery</span>
<h1>The work, photographed on site.</h1>
<p class="lede" style="margin-top:1.5rem">Water heaters, sewer lines, repipes and finished fixtures — photographed on site. Select any photo to enlarge it.</p>
</div>
</section>

<section class="section section--light" style="padding-top:clamp(2rem,4vw,3rem)" aria-label="Job photographs">
<div class="wrap">
<div class="masonry">{items}</div>
</div>
</section>

{final_cta(r)}
</main>
""" + tail(pfx, with_lightbox=True)


def build_about():
    pfx = "about/"
    r = rel(pfx)
    h = head(
        f"About {OWNER} — Owner-Operated Plumbing | {NAME}",
        "Love’s Plumbing and Drains is owned and operated by Anthony Love. More than ten years "
        "in the trade, two years running his own shop. Licensed, bonded and insured. "
        "CSLB License #1138309.",
        pfx, og_type="profile", extra=schema())

    return h + header(pfx, "about/") + f"""<main id="main">
<section class="section section--dark">
<div class="wrap">
<span class="eyebrow">About</span>
<h1>{OWNER}</h1>
</div>
</section>

<section class="section section--light" aria-label="About the business">
<div class="wrap about-split">
<div class="about-copy reveal">
<p class="first">{NAME} is owned and operated by {OWNER}.</p>
<p>After more than ten years in the trade, Anthony started his own shop two years ago on a simple idea: tell people the truth about what their home actually needs, and do the work right the first time.</p>
<p>That means straight answers, no upselling, and no disappearing halfway through a job. Whether it&rsquo;s a water heater that quit on a Sunday night or a sewer line that finally gave out, you deal with Anthony directly.</p>
<p>Licensed, bonded, and insured. CSLB License #{LICENSE}. Serving Riverside, San Diego, and Orange County &mdash; 24 hours a day.</p>
<div class="about-sig">
<div style="margin-bottom:1.5rem">CSLB Lic. #{LICENSE} &middot; Licensed, Bonded &amp; Insured</div>
{cta_buttons('dark')}
</div>
</div>
<div class="reveal">{picture('water-heater-tankless-navien-pair-01', SIZES_HALF, r=r)}</div>
</div>
</section>

{final_cta(r)}
</main>
""" + tail(pfx)


def build_contact():
    pfx = "contact/"
    r = rel(pfx)
    h = head(
        f"Contact — Call or Text (951) 595-9240 | {NAME}",
        "Call or text Love’s Plumbing and Drains at (951) 595-9240, 24 hours a day. "
        "Serving Riverside, San Diego and Orange County. Licensed, bonded and insured, "
        "CSLB License #1138309.",
        pfx, extra=schema())

    return h + header(pfx, "contact/") + f"""<main id="main">
<section class="section section--dark">
<div class="wrap">
<span class="eyebrow">Contact</span>
<h1>Call or text, any time.</h1>
<p class="lede" style="margin-top:1.5rem">There is no form and no answering service. The fastest way to reach {OWNER} is the phone.</p>
</div>
</section>

<section class="section section--light">
<div class="wrap contact-grid">

<div class="reveal">
<span class="eyebrow">Phone</span>
<a class="contact-big" href="tel:{TEL_LINK}">{TEL_DISPLAY}</a>
{cta_buttons('dark')}
<p style="margin-top:2rem;color:var(--muted-on-light);max-width:44ch">If it is an emergency, call rather than text &mdash; the phone is answered 24 hours a day.</p>
</div>

<div class="reveal">
<dl class="detail-list">
<div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
<div><dt>Hours</dt><dd>Open 24 hours &middot; Emergency service available</dd></div>
<div><dt>Service area</dt><dd>Riverside, San Diego, and Orange County, plus surrounding areas</dd></div>
<div><dt>License</dt><dd>CSLB Lic. #{LICENSE} &middot; Licensed, Bonded &amp; Insured</dd></div>
<div><dt>Instagram</dt><dd><a class="ig-link" href="{INSTAGRAM}" rel="noopener noreferrer" target="_blank">{IG_SVG}<span>@loves_plumbing_and_drains</span></a></dd></div>
</dl>
</div>

</div>
</section>

{final_cta(r)}
</main>
""" + tail(pfx)


def build_privacy():
    pfx = "privacy/"
    r = rel(pfx)
    h = head(
        f"Privacy Policy | {NAME}",
        "This site has no forms, no analytics, no tracking pixels and no cookies. "
        "Fonts are self-hosted. Contact happens by phone or text only.",
        pfx, extra=schema())

    return h + header(pfx, "") + f"""<main id="main">
<!--
  IMPORTANT: this page states that the site sets no cookies and collects
  nothing. That is only true while the site stays as built. If analytics,
  a Google Ads conversion tag, a Meta pixel, a chat widget, a contact form
  or any third-party embed is ever added, this page MUST be updated to say
  so — and a cookie consent banner may then be legally required.
-->
<section class="section section--dark">
<div class="wrap">
<span class="eyebrow">Legal</span>
<h1>Privacy Policy</h1>
<p class="lede" style="margin-top:1.5rem">Short version: this website collects nothing about you.</p>
</div>
</section>

<section class="section section--light">
<div class="wrap prose">

<h2>What this site collects</h2>
<p>Nothing. This website has no contact forms, no analytics, no advertising or tracking pixels, no embedded maps, no social media widgets and no chat tools. It sets no cookies, and it does not store anything in your browser.</p>
<p>Because there is nothing to consent to, there is no cookie banner.</p>

<h2>Fonts and other files</h2>
<p>The typeface used here is stored on this site&rsquo;s own server rather than loaded from a font CDN. That means your visit does not send your IP address to a third-party font provider. Every image, stylesheet and script on the site is served from the same place as the page itself.</p>

<h2>Hosting</h2>
<p>This site is hosted on GitHub Pages. Like virtually every web host, GitHub&rsquo;s servers process standard technical request data — such as IP address and browser user agent — in order to deliver the page to you and to protect the service. That processing is GitHub&rsquo;s, not ours, and we do not have access to it or to any analytics derived from it.</p>

<h2>How we contact each other</h2>
<p>Contact happens by phone or text message on <a href="tel:{TEL_LINK}">{TEL_DISPLAY}</a>, or by email at <a href="mailto:{EMAIL}">{EMAIL}</a>. If you call, text or email, we will have whatever you choose to tell us — your name, your number and the details of the job — and we use it only to do the work and to reach you about it. We do not sell it, rent it or share it for marketing.</p>

<h2>Photographs</h2>
<p>The job photographs on this site have had their embedded metadata removed, including any location data recorded by the camera. No customer address appears anywhere on this site.</p>

<h2>Changes</h2>
<p>If this site ever adds analytics, advertising conversion tracking or any other third-party tool, this page will be updated to say exactly what was added before it goes live.</p>

<h2>Questions</h2>
<p>Call or text <a href="tel:{TEL_LINK}">{TEL_DISPLAY}</a>, or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

<p style="margin-top:2.5rem;color:var(--muted-on-light)">Last updated 4 August 2026.</p>
</div>
</section>
</main>
""" + tail(pfx)


BUILDERS = {
    "index.html": build_index,
    "services/index.html": build_services,
    "gallery/index.html": build_gallery,
    "about/index.html": build_about,
    "contact/index.html": build_contact,
    "privacy/index.html": build_privacy,
}

for path, fn in BUILDERS.items():
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(fn())
    print(f"  wrote {path:<26} {os.path.getsize(path) / 1024:6.1f}K")

# ------------------------------------------------------- sitemap/robots --
urls = "".join(
    f"<url><loc>{BASE}/{p}</loc><changefreq>monthly</changefreq>"
    f"<priority>{'1.0' if p == '' else '0.8' if p in ('services/', 'gallery/') else '0.5'}</priority></url>"
    for _, p, _ in PAGES)
with open("sitemap.xml", "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + urls + "</urlset>\n")

with open("robots.txt", "w") as f:
    f.write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")

open(".nojekyll", "w").close()
print("  wrote sitemap.xml, robots.txt, .nojekyll")
