#!/usr/bin/env python3
"""Assemble the final repo: normalize manifests -> data/fonts.json, generate
@font-face CSS from vendored OFL files, and copy everything into ./classy-fonts."""
import json, os, re, shutil, glob

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "classy-fonts-build")
SITE = os.path.join(HERE, "site")
REPO = os.path.join(HERE, "classy-fonts")

ofl = json.load(open(os.path.join(BUILD, "commercial_ofl.json")))
fsh = json.load(open(os.path.join(BUILD, "commercial_fontshare.json")))
personal = json.load(open(os.path.join(BUILD, "personal.json")))

def parse_weight(fname):
    m = re.search(r"-latin-([a-z0-9]+)\.(woff2|ttf)$", fname)
    suf = m.group(1) if m else "regular"
    italic = "italic" in suf
    digits = re.sub(r"\D", "", suf)
    w = int(digits) if digits else 400
    return w, italic, suf

WLABEL = {100:"Thin",200:"ExtraLight",300:"Light",400:"Regular",500:"Medium",
          600:"SemiBold",700:"Bold",800:"ExtraBold",900:"Black"}

# ---------- UI faces (declared from the actual downloaded filenames) ----------
def ui_face(ui_name, slug, want):
    """want: {css_weight: (suffix, style)} -> @font-face rules using real files."""
    rules = []
    for weight, (suffix, style) in want.items():
        hits = glob.glob(os.path.join(BUILD, "fonts", slug, f"*-latin-{suffix}.woff2"))
        if not hits:
            continue
        fn = os.path.basename(hits[0])
        style_css = f";font-style:{style}" if style != "normal" else ""
        rules.append(f"@font-face{{font-family:'{ui_name}';src:url('../fonts/{slug}/{fn}') "
                     f"format('woff2');font-weight:{weight}{style_css};font-display:swap}}")
    return rules

ui_rules = []
ui_rules += ui_face("UI Display", "fraunces", {400:("regular","normal"),600:("600","normal"),800:("800","normal"),"400 italic":("italic","italic")})
# fix: italic key must be numeric weight; redo italic explicitly
ui_rules = []
ui_rules += ui_face("UI Display", "fraunces", {400:("regular","normal"),600:("600","normal"),800:("800","normal")})
ital = glob.glob(os.path.join(BUILD,"fonts","fraunces","*-latin-italic.woff2"))
if ital:
    ui_rules.append(f"@font-face{{font-family:'UI Display';src:url('../fonts/fraunces/{os.path.basename(ital[0])}') format('woff2');font-weight:400;font-style:italic;font-display:swap}}")
ui_rules += ui_face("UI Sans", "hanken-grotesk", {400:("regular","normal"),500:("500","normal"),700:("700","normal")})
ui_rules += ui_face("UI Mono", "space-mono", {400:("regular","normal"),700:("700","normal")})
assert any("UI Sans" in r for r in ui_rules), "UI Sans face missing: check hanken-grotesk download"
assert any("UI Mono" in r for r in ui_rules), "UI Mono face missing: check space-mono download"

# ---------- OFL (local, vendored) ----------
css_rules = []
commercial = []
ofl_families = set()
for e in ofl:
    slug = e["slug"]; fam = e["family"]; ofl_families.add(fam.lower())
    # pair files by suffix
    by_suf = {}
    for f in e["woff2"]:
        w, it, suf = parse_weight(f); by_suf.setdefault(suf, {})["woff2"] = f; by_suf[suf].update(w=w, it=it)
    for f in e["ttf"]:
        w, it, suf = parse_weight(f); by_suf.setdefault(suf, {})["ttf"] = f; by_suf[suf].update(w=w, it=it)
    files = []
    for suf, d in sorted(by_suf.items(), key=lambda kv: (kv[1]["w"], kv[1]["it"])):
        style = "italic" if d["it"] else "normal"
        if d.get("woff2"):
            css_rules.append(
                f"@font-face{{font-family:'{fam}';"
                f"src:url('../fonts/{slug}/{d['woff2']}') format('woff2');"
                f"font-weight:{d['w']};font-style:{style};font-display:swap}}")
        lbl = WLABEL.get(d["w"], str(d["w"])) + (" Italic" if d["it"] else "")
        if d.get("ttf"):
            files.append({"w": lbl, "ttf": f"fonts/{slug}/{d['ttf']}", "woff2": f"fonts/{slug}/{d.get('woff2','')}"})
    weights = sorted({d["w"] for d in by_suf.values()})
    reg_ttf = next((x["ttf"] for x in files if x["w"] == "Regular"), files[0]["ttf"] if files else "")
    commercial.append({
        "id": "ofl-" + slug, "family": fam, "css": fam, "designer": e.get("designer", ""),
        "category": e["category"], "license": f"SIL Open Font License 1.1" if e.get("license","OFL").upper().startswith("OFL") else e.get("license",""),
        "licenseKind": "apache" if "APACHE" in e.get("license","").upper() else "ofl",
        "hosting": "local", "weights": weights, "italic": any(d["it"] for d in by_suf.values()),
        "download": reg_ttf, "files": files, "source": e.get("source", ""), "tags": [],
    })

# ---------- Fontshare (cdn): skip families already vendored as OFL ----------
for e in fsh:
    if e["family"].lower() in ofl_families:
        continue
    commercial.append({
        "id": "fs-" + e["slug"], "family": e["family"], "css": e["css_family"],
        "designer": e.get("designer", ""), "category": e["category"],
        "license": e["license"], "licenseKind": "fontshare", "hosting": "cdn",
        "cssUrl": e["css_url"], "weights": e["weights"], "italic": e.get("has_italic", False),
        "download": e["download"], "source": e["source"], "tags": e.get("tags", []),
    })

# ---------- Personal (image specimens) ----------
def clean_name(n):
    n = re.split(r"\s*[›|\-]\s*Fontesk", n)[0]
    n = re.sub(r"\s*›\s*Fontesk.*$", "", n)
    n = re.sub(r"\s*(Font|Typeface)\s*$", "", n).strip()
    return n or "Untitled"

pers = []
for e in personal:
    pers.append({
        "id": "p-" + e["slug"], "family": clean_name(e["family"]), "designer": e.get("designer", ""),
        "category": e["category"], "license": "Free for personal use", "licenseKind": "personal",
        "hosting": "image", "specimen": e["specimen"], "download": e.get("source") or e.get("details"),
        "source": e.get("details"), "tags": [],
    })

# sort: serif-first flavour, then alpha
CAT_RANK = {"display-serif":0,"editorial-serif":1,"display-expressive":2,"grotesk":3,"mono":4}
commercial.sort(key=lambda f: (f["hosting"] != "local", CAT_RANK.get(f["category"],9), f["family"].lower()))
pers.sort(key=lambda f: (CAT_RANK.get(f["category"],9), f["family"].lower()))

# ---------- assemble repo ----------
if os.path.exists(REPO): shutil.rmtree(REPO)
os.makedirs(os.path.join(REPO, "assets"))
os.makedirs(os.path.join(REPO, "data"))
shutil.copytree(os.path.join(BUILD, "fonts"), os.path.join(REPO, "fonts"))
shutil.copytree(os.path.join(BUILD, "specimens"), os.path.join(REPO, "specimens"))
shutil.copy(os.path.join(SITE, "index.html"), REPO)
shutil.copy(os.path.join(SITE, "assets", "styles.css"), os.path.join(REPO, "assets"))
shutil.copy(os.path.join(SITE, "assets", "app.js"), os.path.join(REPO, "assets"))
open(os.path.join(REPO, "assets", "fonts.css"), "w").write(
    "/* auto-generated. UI faces first, then the catalogue's vendored OFL/Apache fonts */\n"
    + "\n".join(ui_rules) + "\n\n" + "\n".join(css_rules) + "\n")

data = {
    "generated": "2026-07-18",
    "commercial": commercial, "personal": pers,
    "counts": {"commercial": len(commercial), "personal": len(pers),
               "local": sum(1 for f in commercial if f["hosting"]=="local"),
               "cdn": sum(1 for f in commercial if f["hosting"]=="cdn")},
}
json.dump(data, open(os.path.join(REPO, "data", "fonts.json"), "w"), indent=1)

# scripts for reproducibility
os.makedirs(os.path.join(REPO, "scripts"), exist_ok=True)
for s in ("dl_ofl.py", "build_fontshare.py", "build_personal.py", "generate_site.py"):
    if os.path.exists(os.path.join(HERE, s)):
        shutil.copy(os.path.join(HERE, s), os.path.join(REPO, "scripts", s))

print("commercial:", len(commercial), "| local", data["counts"]["local"], "cdn", data["counts"]["cdn"])
print("personal:", len(pers))
print("css @font-face rules:", len(css_rules))
from collections import Counter
print("commercial cats:", dict(Counter(f["category"] for f in commercial)))
print("personal cats:", dict(Counter(f["category"] for f in pers)))
sz = sum(os.path.getsize(os.path.join(dp,f)) for dp,_,fs in os.walk(REPO) for f in fs)
print(f"repo size: {sz/1e6:.1f} MB")
