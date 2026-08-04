# Love’s Plumbing and Drains — website

Marketing site for Love’s Plumbing and Drains (Anthony Love), serving Riverside,
San Diego and Orange County.

Flat HTML, CSS and vanilla JS. **No framework and no runtime build step** — what
is committed here is exactly what GitHub Pages serves.

## Structure

```
index.html              Home
services/index.html     Services
gallery/index.html      Gallery (masonry + lightbox)
about/index.html        About
contact/index.html      Contact
privacy/index.html      Privacy Policy
.nojekyll               stops Pages from running Jekyll over the files
sitemap.xml robots.txt
assets/
  css/site.css          whole design system, one file
  js/site.js            nav, FAQ, scroll reveal, lightbox
  fonts/                self-hosted Inter (variable, subset)
  img/                  logo variants, favicons, OG image
  img/photos/           29 job photos x 3 widths x WebP + JPEG
  img/photos.json       generated manifest (slug, alt text, dimensions)
scripts/                build tooling — see below
```

## Editing

For normal copy changes, edit the HTML directly. It is plain, readable markup.

The `scripts/` directory holds the tooling that produced the assets and pages.
It exists because the gallery alone needs ~29 photos × 3 widths × 2 formats of
`srcset` markup, which is not realistic to maintain by hand. If you re-run
`build_site.py` it will regenerate the six HTML files from the templates in that
script, overwriting hand edits — so pick one approach and stay with it.

| Script | Does |
|---|---|
| `build_logo.py` | Keys the black background out of the source badge; emits `logo-white`/`logo-black` ladders, favicons, apple-touch-icon, OG image |
| `build_images.py` | Bakes EXIF rotation, normalises to sRGB, strips **all** metadata, crops burned-in overlays, emits WebP + JPEG at 480/960/1600 |
| `build_site.py` | Emits the six pages, `sitemap.xml`, `robots.txt`, `.nojekyll` |
| `audit.py` | Checks the delivery checklist: phone numbers, metadata, alt text, claims, weights, links |

### Regenerating assets

The raw camera originals are **not in this repo** (see `.gitignore`). At least
one carries GPS coordinates from a customer's home, so publishing them would
leak an address the site is otherwise careful never to reveal. They live in
Google Drive under *My Drive → Camilli Services → Love’s Plumbing*. Pull them
into `assets/source/` first, then:

```bash
pip install Pillow numpy fonttools brotli
python3 scripts/build_logo.py
python3 scripts/build_images.py
python3 scripts/build_site.py
python3 scripts/audit.py
```

## Things worth knowing

- **Every call to action is `tel:+19515959240` or `sms:+19515959240`.** There is
  no contact form anywhere, by design.
- **No street address is published**, including in the JSON-LD, which omits
  `address` deliberately.
- **No third-party requests at runtime.** Fonts are self-hosted, so no visitor
  IP reaches a font CDN. There is no analytics, no pixel and no embedded map,
  which is what lets the privacy page say the site sets no cookies.
  **If tracking or an Ads conversion tag is ever added, `privacy/index.html`
  must be updated** — there is a comment in that file saying so.
- **Photo metadata is stripped**, GPS included. Anything added later must go
  through `build_images.py`, not be dropped into `assets/img/photos/` by hand.
- The site makes **no claims about pricing, warranties, free estimates or
  financing**, because we do not have that information.

## Deploying

The site is committed ready-to-serve; there is nothing to build. Pages must be
switched on once by a repository admin — the automation token is not permitted
to create a Pages site (`Resource not accessible by integration`).

**Settings → Pages → Build and deployment → Source:**

- **"GitHub Actions"** — `.github/workflows/pages.yml` publishes on every push.
- **"Deploy from a branch"** — pick this branch and the `/ (root)` folder, then
  delete the workflow file.

Either way the site lands at:

```
https://mathias1-creator.github.io/loves-plumbing/
```

If a custom domain is added later, update `BASE` in `scripts/build_site.py` and
re-run it so the canonical, OpenGraph and sitemap URLs match.
