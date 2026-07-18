#!/usr/bin/env python3
"""Build the PERSONAL-USE tab from Fontesk's 'free for personal use' listing.
These fonts are free for personal projects only; their files are NOT vendored.
Each card shows a specimen image + designer credit + link to the source page."""
import curl_reap as reap
import re, os, json, time, html as htmlmod

BUILD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BUILD, "classy-fonts-build")
SPEC = os.path.join(OUT, "specimens", "personal")
os.makedirs(SPEC, exist_ok=True)

s = reap.Session(impersonate="chrome124", retry_policy=reap.RetryPolicy(retries=3))
PAGES = 6  # ~23 fonts/page

# Category guess from slug/name keywords -> our display buckets
def bucketize(name, cats):
    t = (name + " " + " ".join(cats)).lower()
    if any(k in t for k in ["serif","roman","antiqua","garamond","didone","bodoni"]):
        return "editorial-serif" if "text" in t else "display-serif"
    if any(k in t for k in ["mono","code"]): return "mono"
    if any(k in t for k in ["sans","grotesk","gothic","neue"]): return "grotesk"
    return "display-expressive"

# 1) collect font page urls from listing pages
font_urls = []
for p in range(1, PAGES + 1):
    url = "https://fontesk.com/license/free-for-personal-use/" + (f"page/{p}/" if p > 1 else "")
    r = s.get(url)
    if r.status != 200:
        print("listing", p, "->", r.status); continue
    for m in re.findall(r'href="(https://fontesk\.com/[a-z0-9\-]+-font/)"', r.text):
        if m not in font_urls:
            font_urls.append(m)
    time.sleep(0.2)
print("collected font pages:", len(font_urls))

def pick_preview(html_text):
    # prefer the 768 or 590 responsive variant; fall back to base jpg
    cands = re.findall(r'(https://fontesk\.com/wp-content/uploads/[0-9/]+[a-z0-9_\-]+?)(-\d+x\d+)?\.(jpg|png)', html_text)
    if not cands: return None
    base = cands[0][0]; ext = cands[0][2]
    return f"{base}-768x432.{ext}", f"{base}.{ext}"

manifest = []
for u in font_urls:
    try:
        r = s.get(u)
        if r.status != 200: continue
        t = r.text
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))
        slug = u.rstrip("/").split("/")[-1]
        name = re.search(r"<title>([^<|\-]+)", t)
        name = htmlmod.unescape(name.group(1).strip()) if name else slug.replace("-font","").replace("-"," ").title()
        name = re.sub(r"\s*(Font|Typeface)\s*$", "", name).strip() or name
        designer = re.search(r"Designed by:\s*([A-Za-z0-9 ,\.\-&']+?)\s+(?:Follow|Support|License)", txt)
        designer = designer.group(1).strip() if designer else ""
        lic = re.search(r"License:\s*(Free for personal use|100% Free|Free for commercial use)", txt)
        lic = lic.group(1) if lic else "Free for personal use"
        cats = re.findall(r"featured in\s+([A-Za-z ]+?)\s+By Fontesk", txt)
        # source: designer external link (behance/site), else the fontesk page
        ext_links = re.findall(r'href="(https?://(?:www\.)?(?:behance\.net|dribbble\.com|gumroad\.com|[a-z0-9\-]+\.myportfolio\.com|instagram\.com)/[^"]+)"', t)
        source = ext_links[0] if ext_links else u
        prev = pick_preview(t)
        img_file = ""
        if prev:
            for cand in prev:
                ir = s.get(cand)
                if ir.status == 200 and len(ir.content) > 2000:
                    ext = cand.rsplit(".", 1)[-1]
                    img_file = f"{slug}.{ext}"
                    open(os.path.join(SPEC, img_file), "wb").write(ir.content)
                    break
        if not img_file:
            continue  # no specimen -> skip
        manifest.append({
            "slug": slug,
            "family": name,
            "designer": designer,
            "category": bucketize(name, cats),
            "license": lic,
            "specimen": f"specimens/personal/{img_file}",
            "details": u,           # fontesk page
            "source": source,       # designer / download-from-source
        })
        print(f"OK  {name[:30]:30} [{designer[:22]:22}] {lic}", flush=True)
        time.sleep(0.15)
    except Exception as e:
        print("ERR", u, str(e)[:50], flush=True)

# keep only genuinely personal-use for this tab (commercial ones belong elsewhere)
personal = [m for m in manifest if m["license"] == "Free for personal use"]
json.dump(personal, open(os.path.join(OUT, "personal.json"), "w"), indent=2)
from collections import Counter
print(f"\nDONE personal: {len(personal)} fonts (of {len(manifest)} scraped)")
print("categories:", dict(Counter(m["category"] for m in personal)))
