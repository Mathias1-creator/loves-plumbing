#!/usr/bin/env python3
"""
Turn raw iPhone job-site photos into web-ready responsive assets.

Order matters here:
  1. bake EXIF rotation   (6 of these display sideways otherwise)
  2. normalise to sRGB    (before the profile is discarded, or P3 shots shift)
  3. rebuild from raw px  (guarantees no metadata survives -- one source photo
                           carries GPS coordinates from a customer's home)
  4. crop burned-in overlays
  5. emit WebP + JPEG at each responsive width

Writes assets/img/photos/ plus a manifest the page builder consumes.
"""
from PIL import Image, ImageOps, ImageCms
import io
import json
import os

SRC = "assets/source"
OUT = "assets/img/photos"
QUALITY = 82
TARGETS = [480, 960, 1600]

os.makedirs(OUT, exist_ok=True)

# slug, source file, category, alt text, optional bottom-crop ratio
#
# Categorised by opening every photo, not by filename. Anything that did not
# clearly show a given service was left out of that service rather than forced.
PHOTOS = [
    # ---- Water heaters -------------------------------------------------
    ("water-heater-tankless-navien-pair-01", "IMG_8900.JPG", "water-heaters",
     "Two white Navien tankless water heaters mounted side by side on a wall, connected with copper manifolds, isolation valves and yellow gas lines", None),
    ("water-heater-commercial-high-efficiency-02", "IMG_8961.JPG", "water-heaters",
     "High-efficiency Bradford White commercial water heater with copper supply lines and a gas shutoff in a mechanical room", None),
    ("water-heater-commercial-bank-03", "IMG_8949.JPG", "water-heaters",
     "Bank of commercial water heaters with insulated supply piping, expansion tank and stainless storage tank in a mechanical room", 0.87),
    ("water-heater-tank-replacement-04", "FBCC1BD7-1821-47C1-8CA0-35C5473F6154.jpg", "water-heaters",
     "Newly installed residential tank water heater with expansion tank, copper connections and a gas shutoff valve", 0.80),

    # ---- Sewer & drain -------------------------------------------------
    ("sewer-trench-caution-tape-01", "IMG_8892.JPG", "sewer-drain",
     "Long open trench running along a driveway with a new black ABS sewer line and cleanout fitting, cordoned off with caution tape", None),
    ("sewer-cleanout-risers-02", "IMG_8882.JPG", "sewer-drain",
     "Two white PVC cleanout risers set into an open trench, with sections of removed cast iron pipe stacked at the edge", None),
    ("sewer-cleanout-capped-03", "IMG_8920.JPG", "sewer-drain",
     "Capped black ABS sewer cleanout riser installed on a new drain line in an excavated trench", None),
    ("sewer-cleanout-pair-04", "IMG_8924.JPG", "sewer-drain",
     "Pair of black ABS cleanout risers joined to a newly installed sewer line at the bottom of an open trench", None),
    ("sewer-trench-cleanout-05", "IMG_8908.JPG", "sewer-drain",
     "New PVC sewer line and green-capped cleanout installed in a trench alongside a building foundation", None),
    ("sewer-under-slab-tile-06", "IMG_8936.JPG", "sewer-drain",
     "Under-slab drain replacement with new black ABS pipe and fittings run through an opened tile floor", None),
    ("sewer-trench-slab-night-07", "IMG_8878.JPG", "sewer-drain",
     "New white PVC drain lines rising from a trench cut through a concrete slab, photographed at night", None),
    ("sewer-excavation-pvc-08", "IMG_8962.JPG", "sewer-drain",
     "New white PVC sewer piping assembled at the bottom of a deep excavation", None),
    ("sewer-trench-abs-cleanout-night-09", "IMG_9878.JPG", "sewer-drain",
     "Black ABS sewer line with a white cleanout riser installed in an open trench, photographed at night under work lights", None),
    ("sewer-vault-service-10", "IMG_9584.JPG", "sewer-drain",
     "Plumber working inside a below-grade concrete vault, installing new PVC piping above standing water", None),
    ("sewer-line-excavation-11", "IMG_8915.JPG", "sewer-drain",
     "Existing sewer line uncovered in a shallow trench alongside a building during a drain repair", None),
    ("drain-rough-in-wall-12", "IMG_8983.JPG", "sewer-drain",
     "New PVC drain and vent rough-in inside an opened interior wall, with plastic sheeting hung for dust containment", None),

    # ---- Repipes -------------------------------------------------------
    ("repipe-pex-ceiling-01", "IMG_8890.JPG", "repipes",
     "Red and blue PEX water lines running through open ceiling joists during a whole-house repipe", None),
    ("repipe-copper-stucco-wall-02", "IMG_9852.JPG", "repipes",
     "New copper water line running inside an opened stucco exterior wall during a repipe", None),
    ("repipe-copper-crawlspace-03", "IMG_8913.JPG", "repipes",
     "New copper supply manifold installed against a concrete foundation wall in a crawlspace", None),
    ("repipe-abs-pex-ceiling-04", "IMG_8889.JPG", "repipes",
     "Black ABS drain lines and blue PEX water lines installed through open ceiling framing", None),

    # ---- Additional services -------------------------------------------
    ("filtration-reverse-osmosis-undersink-01", "IMG_9917.JPG", "additional",
     "Under-sink iSpring reverse osmosis drinking water system with storage tank and filter housings, labeled with a Love’s Plumbing and Drains sticker", None),
    ("filtration-whole-house-tank-02", "IMG_8901.JPG", "additional",
     "Whole-house water filtration tank connected with copper piping and a bypass valve against a stucco exterior wall", None),
    ("gas-line-commercial-kitchen-03", "IMG_8902.JPG", "additional",
     "Blue commercial gas connectors and shutoff valves running along a stainless steel commercial kitchen wall", None),
    ("water-shutoff-smart-valve-04", "IMG_8965.JPG", "additional",
     "Smart automatic water shutoff and leak detection valve installed on a copper main water line", None),
    ("backflow-preventer-copper-05", "IMG_8988.JPG", "additional",
     "Zurn backflow prevention assembly installed on copper risers at a property water service", None),
    ("backflow-commercial-assembly-06", "IMG_8959.JPG", "additional",
     "Large commercial backflow prevention assembly with red gate valves being set on a new water service line", None),

    # ---- Finished fixture work -----------------------------------------
    ("bathroom-dark-tile-finished-01", "CAC45319-315F-416E-9A20-E2A41F8690BB.png", "fixtures",
     "Finished bathroom with dark textured wave tile, a black soaking tub, matte black shower fixtures and a lit recessed niche", None),
    ("bathroom-tub-shower-tile-02", "IMG_0230.jpeg", "fixtures",
     "Finished tub and shower surround in grey textured wave tile with a black tub and handheld shower fixture", None),
    ("shower-enclosure-installed-03", "IMG_9955.jpeg", "fixtures",
     "Newly installed white shower enclosure with sliding glass doors and a brushed nickel valve", None),
]

SRGB = ImageCms.createProfile("sRGB")


# Source extensions are inconsistent (.JPG/.jpg/.jpeg/.png), so match on stem.
BY_STEM = {os.path.splitext(f)[0]: f for f in os.listdir(SRC)}


def resolve(fname):
    stem = os.path.splitext(fname)[0]
    if stem not in BY_STEM:
        raise FileNotFoundError(f"no source file for {stem!r}")
    return os.path.join(SRC, BY_STEM[stem])


def load_clean(path, crop_ratio):
    """Rotation baked, colour normalised, all metadata gone."""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)          # 1. bake rotation

    icc = im.info.get("icc_profile")          # 2. normalise colour
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            im = ImageCms.profileToProfile(im, src, SRGB, outputMode="RGB")
        except Exception:
            im = im.convert("RGB")
    else:
        im = im.convert("RGB")

    # 3. rebuild from raw pixels so nothing rides along in im.info
    clean = Image.frombytes("RGB", im.size, im.tobytes())

    if crop_ratio:                            # 4. drop burned-in overlays
        w, h = clean.size
        clean = clean.crop((0, 0, w, int(h * crop_ratio)))

    return clean


def widths_for(src_w):
    ws = [t for t in TARGETS if t < src_w]
    ws.append(min(src_w, TARGETS[-1]))
    return sorted(set(ws))


manifest = []
for slug, fname, cat, alt, crop in PHOTOS:
    im = load_clean(resolve(fname), crop)
    sw, sh = im.size

    variants = []
    for w in widths_for(sw):
        h = round(sh * w / sw)
        r = im.resize((w, h), Image.LANCZOS)
        r.save(f"{OUT}/{slug}-{w}.webp", "WEBP", quality=QUALITY, method=6)
        r.save(f"{OUT}/{slug}-{w}.jpg", "JPEG", quality=QUALITY,
               optimize=True, progressive=True)
        variants.append({"w": w, "h": h})

    manifest.append({
        "slug": slug, "category": cat, "alt": alt,
        "width": variants[-1]["w"], "height": variants[-1]["h"],
        "variants": variants,
        "aspect": round(sw / sh, 4),
    })
    print(f"{slug:<44} {sw}x{sh}  ->  {[v['w'] for v in variants]}")

with open("assets/img/photos.json", "w") as f:
    json.dump(manifest, f, indent=1)
print(f"\n{len(manifest)} photos processed")
