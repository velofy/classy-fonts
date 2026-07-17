#!/usr/bin/env python3
"""Build the Fontshare commercial manifest. Fonts render LIVE via the official
Fontshare CDN (their license explicitly permits API/CDN serving). Files are NOT
vendored. Each entry links to the official free download."""
import json, os, re

BUILD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BUILD, "classy-fonts-build")
raw = json.load(open(os.path.join(OUT, "fontshare_raw.json")))

CAT_MAP = {  # normalize Fontshare category -> our display bucket
    "Serif": "editorial-serif", "Sans": "grotesk", "Sans Serif": "grotesk",
    "Display": "display-expressive", "Monospace": "mono", "Mono": "mono",
    "Handwriting": "display-expressive", "Slab": "editorial-serif",
}

def weight_num(st):
    w = st.get("weight")
    if isinstance(w, dict):
        return int(w.get("weight") or w.get("value") or 400)
    try: return int(w)
    except Exception: return 400

manifest = []
for f in raw:
    slug = f["slug"]
    styles = f.get("styles", [])
    weights = sorted({weight_num(st) for st in styles if not st.get("is_italic")}) or [400]
    has_italic = any(st.get("is_italic") for st in styles)
    designers = [d.get("name") for d in (f.get("designers") or []) if d.get("name")]
    if not designers and f.get("publisher"):
        designers = [f["publisher"]]
    tags = [t for t in (f.get("font_tags") or []) if isinstance(t, str)][:6]
    cat = f.get("category", "")
    # CDN css: request up to a few representative weights
    wsel = weights if len(weights) <= 6 else [weights[0], weights[len(weights)//2], weights[-1]]
    css_url = f"https://api.fontshare.com/v2/css?f[]={slug}@{','.join(str(w) for w in wsel)}&display=swap"
    manifest.append({
        "slug": slug,
        "family": f["name"],
        "designer": ", ".join(designers),
        "category": CAT_MAP.get(cat, "display-expressive"),
        "fontshare_category": cat,
        "weights": weights,
        "has_italic": has_italic,
        "variable": bool(f.get("axes")),
        "tags": tags,
        "is_hot": f.get("is_hot", False),
        "is_new": f.get("is_new", False),
        "css_url": css_url,
        "css_family": f["name"],
        "download": f"https://api.fontshare.com/v2/fonts/download/{slug}",
        "source": f"https://www.fontshare.com/fonts/{slug}",
        "license": "ITF Free Font License (free for personal & commercial use)",
        "hosting": "cdn",
    })

manifest.sort(key=lambda x: (not x["is_hot"], x["family"].lower()))
json.dump(manifest, open(os.path.join(OUT, "commercial_fontshare.json"), "w"), indent=2)
from collections import Counter
print("Fontshare fonts:", len(manifest))
print("categories:", dict(Counter(m["category"] for m in manifest)))
print("sample:", [m["family"] for m in manifest[:12]])
