<p align="center">
  <a href="https://velofy.co/classy-fonts/"><picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/velofy/classy-fonts/main/assets/tile-dark.svg">
    <img alt="Classy Fonts" src="https://raw.githubusercontent.com/velofy/classy-fonts/main/assets/tile-light.svg" width="360">
  </picture></a>
</p>

# Classy Fonts

A cabinet of **324 free typefaces**, split by licence, with a live specimen gallery.

**Docs and live gallery:** https://velofy.co/classy-fonts/
**Gallery:** https://velofy.co/classy-fonts/gallery/

Fonts were gathered with [curl_reap](https://github.com/anishfyi/curl_reap).

## What is in the cabinet

Free to **use** and free to **redistribute** are different rights, so the cabinet keeps them apart.

### Commercial use: 192 faces

- **110 OFL faces** are stored in this repository as real `.woff2` and `.ttf` files under [`fonts/`](fonts/), each family with its own `OFL.txt` and designer credit.
- **82 Fontshare faces** (Indian Type Foundry) load from the foundry's own CDN, which their licence permits. They are not re-hosted here. Each entry links to the official free download.

### Personal use: 132 faces

Free for personal projects only. The repository holds a specimen image for each and a link to the designer's page. The font files are not stored, because their licences do not grant redistribution. Commercial use needs a licence from the author.

## Using a font

Download an OFL family from [`fonts/`](fonts/), or load it in CSS from the public repository:

```css
@font-face {
  font-family: "Anton";
  src: url("https://cdn.jsdelivr.net/gh/velofy/classy-fonts@main/fonts/anton/anton-v27-latin-regular.woff2")
    format("woff2");
  font-display: swap;
}
```

Read the family's `OFL.txt` first. See [Using the fonts](https://velofy.co/classy-fonts/using-the-fonts/).

## Why some fonts are links, not files

A "free" font is not automatically free to re-host. The Fontshare licence permits unlimited personal and commercial use but forbids uploading the files to a public server, while serving them from their CDN is allowed. Most "free for personal use" display fonts are the same or stricter.

The rule here: vendor a font file only when its licence grants redistribution (OFL, Apache, public domain). Everything else is rendered as its licence allows and linked to its source.

## Documentation

- [Overview](https://velofy.co/classy-fonts/)
- [Using the fonts](https://velofy.co/classy-fonts/using-the-fonts/)
- [Licences](https://velofy.co/classy-fonts/licences/)
- [How the collection was gathered](https://velofy.co/classy-fonts/how-it-was-gathered/)
- [Data format](https://velofy.co/classy-fonts/data-format/)
- [Project status](https://velofy.co/classy-fonts/project-status/)

## Layout

```text
classy-fonts/
  index.html            redirect to velofy.co/classy-fonts/
  404.html              same redirect for old links
  assets/               styles, script and @font-face CSS of the original gallery
  data/fonts.json       the catalogue manifest
  fonts/<slug>/         vendored OFL families (woff2, ttf, OFL.txt)
  specimens/personal/   specimen images for personal-use faces
  scripts/              the build pipeline
```

The gallery on velofy.co loads `data/`, `fonts/` and `specimens/` from this repository through jsDelivr, so keep those paths in place.

## Rebuilding

```bash
pip install curl-reap pillow
python scripts/dl_ofl.py           # download the OFL faces
python scripts/build_fontshare.py  # Fontshare CDN manifest
python scripts/build_personal.py   # personal-use specimens
python scripts/generate_site.py    # assemble data and @font-face CSS
```

## Contributing

If you are a designer and want a face removed or a credit corrected, [open an issue](https://github.com/velofy/classy-fonts/issues).

## Credits and licence

- **Sources:** [Fontshare](https://www.fontshare.com), [Google Fonts](https://fonts.google.com), [Fontesk](https://fontesk.com).
- **Designers:** every face credits its designer in `data/fonts.json`.
- **Fonts** keep their own licences (SIL OFL 1.1, or the terms stated by their designers). The licence file that comes with each font governs.
- **Site code** (HTML, CSS, JS and build scripts) is MIT; see [`LICENSE`](LICENSE). The MIT grant does not extend to any font.

Nothing here is sold or relicensed.
