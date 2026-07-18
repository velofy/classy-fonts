# Classy Fonts

A curated cabinet of **324 free typefaces**, split by licence and browsable as a live
type-specimen gallery. The interface is set in the very fonts it catalogues (Fraunces,
Hanken Grotesk, Space Mono).

**Live:** https://anishfyi.github.io/classy-fonts

Fonts were gathered with [curl_reap](https://github.com/anishfyi/curl_reap).

---

## The two tabs

Free to **use** and free to **redistribute** are different rights, so the cabinet keeps
them apart instead of dumping every file into one folder.

### Commercial use: 192 faces
Safe for commercial work, all free.

- **110 OFL / Apache faces** are **vendored in this repo** as real `.woff2` + `.ttf`
  files under [`fonts/`](fonts/), each with its own `OFL.txt` and designer credit.
  These are genuinely yours to download, use, and redistribute.
- **82 Fontshare faces** (Indian Type Foundry) are **served live from the foundry's own
  CDN**, which their licence explicitly permits. They are *not* re-hosted here; each
  card links to the official free download.

### Personal use: 132 faces
Free for personal projects only. Shown as **specimens** that link through to the
designer's page. The font files are **not** vendored, because their licences do not grant
redistribution. Not for commercial use without a licence from the author.

---

## Why some fonts are links, not files

Every font here is free to use. But a "free" font is not automatically free to
*re-host*. The Fontshare EULA, for example, permits unlimited personal and commercial
use yet forbids uploading the files to a public server, while serving them from their
CDN is allowed. Most "free for personal use" display fonts are the same or stricter.

So the rule this repo follows is simple: **vendor a font file only when its licence
grants redistribution** (OFL, Apache, public domain). Everything else is rendered the way
its licence allows and linked to its source. You lose nothing: the fonts render
identically and every download is one click away, and the foundries keep what their
licence protects.

---

## Layout

```
classy-fonts/
  index.html            two-tab specimen gallery
  assets/
    styles.css          design system
    app.js              filtering, live type-tester, lazy font loading, modal
    fonts.css           auto-generated @font-face for the vendored OFL faces
  data/fonts.json       the catalogue manifest
  fonts/<slug>/         vendored OFL/Apache families (woff2 + ttf + OFL.txt)
  specimens/personal/   specimen images for the personal-use faces
  scripts/              the build pipeline (reproducible)
```

## Rebuilding

```bash
pip install curl-reap pillow
python scripts/dl_ofl.py          # download the OFL faces (real files)
python scripts/build_fontshare.py # Fontshare CDN manifest
python scripts/build_personal.py  # personal-use specimens
python scripts/generate_site.py   # assemble the site + data + @font-face css
```

## Credits & licensing

- **Sources:** [Fontshare](https://www.fontshare.com), [Google Fonts](https://fonts.google.com), [Fontesk](https://fontesk.com).
- **Designers:** every face credits its designer in the gallery and in `data/fonts.json`.
- **The vendored fonts** keep their own licences (SIL OFL 1.1 / Apache 2.0), included per
  family. **The site code** (HTML/CSS/JS and the build scripts) is MIT; see
  [`LICENSE`](LICENSE).

Nothing here is sold or relicensed. If you are a designer and want a face removed or a
credit corrected, open an issue.
