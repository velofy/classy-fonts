#!/usr/bin/env python3
"""Download curated OFL/Apache stylish fonts as real woff2+ttf files, with per-font
license + designer metadata pulled from the google/fonts repo. Fully redistributable."""
import curl_reap as reap
import json, io, zipfile, os, re, sys, time

BUILD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BUILD, "classy-fonts-build")
FONTS_DIR = os.path.join(OUT, "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

# gwfh id (== google fonts folder slug), our display category
CURATED = {
  # ---- Display / editorial serif (the Bigilla / awwwards aesthetic) ----
  "display-serif": [
    "fraunces","playfair-display","dm-serif-display","dm-serif-text","bodoni-moda",
    "cormorant","cormorant-garamond","marcellus","marcellus-sc","italiana","prata",
    "gilda-display","forum","cinzel","cinzel-decorative","ibarra-real-nova",
    "libre-caslon-display","libre-caslon-text","libre-bodoni","libre-baskerville",
    "abril-fatface","ovo","yeseva-one","rozha-one","unna","sorts-mill-goudy",
    "rufina","playfair-display-sc","cormorant-infant","rozha-one",
  ],
  # ---- Editorial / text serif ----
  "editorial-serif": [
    "spectral","eb-garamond","newsreader","young-serif","instrument-serif","cardo",
    "lora","source-serif-4","noto-serif-display","crimson-pro","domine","bitter",
    "alegreya","faustina","hedvig-letters-serif","besley","literata","brygada-1918",
    "petrona","vollkorn","gelasio","zilla-slab",
  ],
  # ---- Display / expressive ----
  "display-expressive": [
    "syne","unbounded","bricolage-grotesque","big-shoulders-display","anton",
    "bebas-neue","staatliches","monoton","righteous","teko","archivo-black",
    "league-spartan","bungee","bungee-shade","rubik-mono-one","silkscreen",
    "press-start-2p","vt323","pixelify-sans","fascinate","alfa-slab-one",
    "fjalla-one","dela-gothic-one","bakbak-one","honk",
  ],
  # ---- Grotesk / classy sans ----
  "grotesk": [
    "space-grotesk","sora","epilogue","dm-sans","work-sans","manrope",
    "plus-jakarta-sans","outfit","urbanist","figtree","hanken-grotesk","onest",
    "schibsted-grotesk","instrument-sans","familjen-grotesk","inter-tight",
    "archivo","red-hat-display","albert-sans","geologica","hedvig-letters-sans",
  ],
  # ---- Mono ----
  "mono": [
    "space-mono","jetbrains-mono","ibm-plex-mono","dm-mono","martian-mono",
    "red-hat-mono","spline-sans-mono","fragment-mono","azeret-mono","overpass-mono",
    "source-code-pro","fira-code","victor-mono","sometype-mono",
  ],
}

DESIRED_WEIGHTS = ["300","regular","500","600","700","800","italic","700italic"]

s = reap.Session(impersonate="chrome124", retry_policy=reap.RetryPolicy(retries=3))

def meta_from_google(slug):
    """Pull designer + license + real family name from google/fonts METADATA.pb."""
    for lic in ("ofl","apache","ufl"):
        url = f"https://raw.githubusercontent.com/google/fonts/main/{lic}/{slug.replace('-','')}/METADATA.pb"
        r = s.get(url)
        if r.status == 200 and "name:" in r.text:
            t = r.text
            name = re.search(r'name:\s*"([^"]+)"', t)
            designer = re.search(r'designer:\s*"([^"]+)"', t)
            cat = re.search(r'category:\s*"?([A-Z_]+)"?', t)
            licf = re.search(r'license:\s*"?([A-Z0-9_\-]+)"?', t)
            licurl = f"https://raw.githubusercontent.com/google/fonts/main/{lic}/{slug.replace('-','')}/"
            # grab the actual license file
            lname = {"ofl":"OFL.txt","apache":"LICENSE.txt","ufl":"UFL.txt"}[lic]
            lr = s.get(licurl + lname)
            lic_text = lr.text if lr.status == 200 else ""
            return {
                "family": name.group(1) if name else slug.replace("-"," ").title(),
                "designer": designer.group(1) if designer else "",
                "gf_category": cat.group(1) if cat else "",
                "license": (licf.group(1) if licf else lic.upper()),
                "license_file": lname,
                "license_text": lic_text,
            }
    return None

manifest = []
seen = set()
fail = []
for category, slugs in CURATED.items():
    for slug in slugs:
        if slug in seen:
            continue
        seen.add(slug)
        try:
            meta = s.get(f"https://gwfh.mranftl.com/api/fonts/{slug}?subsets=latin")
            if meta.status != 200:
                fail.append((slug,"meta "+str(meta.status))); continue
            mj = json.loads(meta.text)
            avail = [v["id"] for v in mj.get("variants",[])]
            want = [w for w in DESIRED_WEIGHTS if w in avail] or (["regular"] if "regular" in avail else avail[:1])
            variants = ",".join(want)
            z = s.get(f"https://gwfh.mranftl.com/api/fonts/{slug}?download=zip&subsets=latin&variants={variants}&formats=woff2,ttf")
            if z.status != 200 or z.content[:2] != b"PK":
                fail.append((slug,"zip "+str(z.status))); continue
            zf = zipfile.ZipFile(io.BytesIO(z.content))
            fdir = os.path.join(FONTS_DIR, slug)
            os.makedirs(fdir, exist_ok=True)
            files = {"woff2":[], "ttf":[]}
            for n in zf.namelist():
                data = zf.read(n)
                base = os.path.basename(n)
                open(os.path.join(fdir, base),"wb").write(data)
                if base.endswith(".woff2"): files["woff2"].append(base)
                elif base.endswith(".ttf"): files["ttf"].append(base)
            gmeta = meta_from_google(slug) or {}
            if gmeta.get("license_text"):
                open(os.path.join(fdir, gmeta["license_file"]),"w").write(gmeta["license_text"])
            # pick a representative regular woff2 for @font-face
            reg = next((f for f in files["woff2"] if re.search(r'(regular|400)', f, re.I)), files["woff2"][0] if files["woff2"] else None)
            entry = {
                "slug": slug,
                "family": gmeta.get("family") or mj.get("family") or slug.replace("-"," ").title(),
                "designer": gmeta.get("designer",""),
                "category": category,
                "gf_category": gmeta.get("gf_category") or mj.get("category",""),
                "license": gmeta.get("license","OFL"),
                "license_file": gmeta.get("license_file",""),
                "weights_available": avail,
                "weights_included": want,
                "woff2": sorted(files["woff2"]),
                "ttf": sorted(files["ttf"]),
                "regular_woff2": reg,
                "source": f"https://fonts.google.com/specimen/{mj.get('family','').replace(' ','+')}",
            }
            manifest.append(entry)
            print(f"OK  {slug:26} {len(files['woff2'])}woff2 {len(files['ttf'])}ttf  {gmeta.get('license','?')}  [{gmeta.get('designer','')[:24]}]", flush=True)
            time.sleep(0.15)
        except Exception as e:
            fail.append((slug, str(e)[:60])); print(f"ERR {slug}: {str(e)[:60]}", flush=True)

json.dump(manifest, open(os.path.join(OUT,"commercial_ofl.json"),"w"), indent=2)
print(f"\nDONE ofl: {len(manifest)} fonts, {len(fail)} failed")
if fail:
    print("FAILURES:", fail)
