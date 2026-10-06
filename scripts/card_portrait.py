"""ASCII portrait panel.

The character grid is cached in data/portrait.json:
  - prep_photo.py writes it from your own photo   (source: "photo", kept forever)
  - otherwise it is rebuilt from your GitHub avatar each run (source: "avatar")
  - offline with no cache, your name in block letters (source: "name")
Only ASCII rows are stored — never the photo itself.

Each row is revealed by a left-to-right wipe with a block cursor riding the
edge, staggered top to bottom; it prints once and freezes.
"""
import io
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from kit import ACCENT, CFG, DATA, DIM, FG, MODES, esc, n, save, text, window

RAMP = " .`:-=+*cs#%@"      # bright (sparse) -> dark (dense); white background -> space
COLS = 100
GLYPH_ASPECT = 0.55         # glyph width / line height
CACHE = DATA / "portrait.json"
INK = "#b1bac4"


def grid_from_image(img, cols=COLS):
    img = img.convert("L")
    rows = max(1, round(img.height / img.width * cols * GLYPH_ASPECT))
    px = np.asarray(img.resize((cols, rows), Image.LANCZOS), dtype=np.float32) / 255
    idx = ((1 - px) * (len(RAMP) - 1)).round().astype(int)
    lines = ["".join(RAMP[i] for i in r).rstrip() for r in idx]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def avatar_image():
    import requests
    r = requests.get(f"https://avatars.githubusercontent.com/u/{CFG['github_id']}?s=460", timeout=30)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGBA")
    gray = ImageOps.autocontrast(Image.alpha_composite(Image.new("RGBA", img.size, "white"), img).convert("L"), cutoff=1)
    # avatars keep their background: push light tones (walls, sky) to white so they print as
    # spaces, and fade anything outside an ellipse around the subject
    opts = CFG.get("portrait", {})
    px = np.asarray(gray, dtype=np.float32) / 255
    px = np.clip((px - 0.06) / (opts.get("white_point", 0.62) - 0.06), 0, 1) ** 1.1
    h, w = px.shape
    yy, xx = np.mgrid[0:h, 0:w]
    d = ((xx - w * opts.get("cx", 0.5)) / (w * 0.45)) ** 2 + ((yy - h * 0.55) / (h * 0.55)) ** 2
    keep = np.clip((1.0 - d) / 0.12, 0, 1)
    return Image.fromarray(((px * keep + (1 - keep)) * 255).astype(np.uint8), "L")


def name_image(label):
    font = ImageFont.load_default()
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"):
        try:
            font = ImageFont.truetype(name, 220)
            break
        except OSError:
            pass
    box = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), label, font=font)
    img = Image.new("L", (box[2] - box[0] + 60, box[3] - box[1] + 60), 255)
    ImageDraw.Draw(img).text((30 - box[0], 30 - box[1]), label, fill=0, font=font)
    return img


def write_cache(rows, source):
    DATA.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps({"source": source, "cols": COLS, "rows": rows}, indent=0), encoding="utf-8")


def rows():
    cached = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else None
    if cached and cached.get("source") == "photo":
        return cached["rows"]
    try:
        r = grid_from_image(avatar_image())
        write_cache(r, "avatar")
        return r
    except Exception as e:  # offline, no avatar, …
        print(f"avatar unavailable ({e})")
    if cached:
        return cached["rows"]
    return grid_from_image(name_image(CFG["name"]))


def panel(m, w, h, lines, begin=0.0):
    """A terminal window of width w/height h that prints the portrait."""
    bar, pad = m.bar, m.f(14)
    prompt_h = m.f(24)
    area_w, area_h = w - 2 * pad, h - bar - 2 * pad - prompt_h
    cols = max(len(l) for l in lines) if lines else 1
    cw = area_w / COLS
    lh = cw / GLYPH_ASPECT
    if len(lines) * lh > area_h:  # tall image: shrink to fit the height
        lh = area_h / len(lines)
        cw = lh * GLYPH_ASPECT
    fs = cw / 0.6
    top = bar + pad + (area_h - len(lines) * lh) / 2
    left = pad + (area_w - COLS * cw) / 2
    row_delay, row_dur = 0.045, 0.3
    defs, body = [], [f'<g font-size="{n(round(fs, 2))}" fill="{INK}">']
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = top + (i + 1) * lh - lh * 0.22
        lw = len(line) * cw
        t = esc(line).replace(" ", " ")  # NBSPs keep leading spaces
        b, end = begin + i * row_delay, begin + i * row_delay + row_dur
        ry = top + i * lh
        defs.append(f'<clipPath id="pr{i}"><rect x="{n(round(left, 1))}" y="{n(round(ry, 2))}" width="0" height="{n(round(lh + .5, 2))}">'
                    f'<animate attributeName="width" from="0" to="{n(round(lw, 1))}" begin="{b:.2f}s" dur="{row_dur}s" fill="freeze"/>'
                    f"</rect></clipPath>")
        body.append(f'<text x="{n(round(left, 1))}" y="{n(round(y, 2))}" textLength="{n(round(lw, 1))}" '
                    f'lengthAdjust="spacingAndGlyphs" clip-path="url(#pr{i})">{t}</text>')
        body.append(f'<rect x="{n(round(left, 1))}" y="{n(round(ry, 2))}" width="{n(round(cw * 1.6, 1))}" height="{n(round(lh, 2))}" '
                    f'fill="{FG}" opacity="0"><set attributeName="opacity" to=".85" begin="{b:.2f}s"/>'
                    f'<animate attributeName="x" from="{n(round(left, 1))}" to="{n(round(left + lw, 1))}" begin="{b:.2f}s" '
                    f'dur="{row_dur}s" fill="freeze"/><set attributeName="opacity" to="0" begin="{end:.2f}s"/></rect>')
    body.append("</g>")
    done = begin + len(lines) * row_delay + row_dur
    py = h - pad
    ps = m.f(8.5)
    label = "snapshot:~ $ whoami  "
    prompt = (f'<text x="{n(pad)}" y="{n(py)}" font-size="{n(ps)}" fill="{DIM}">{esc(label)}'
              f'<tspan fill="{FG}" font-weight="bold">{esc(CFG["name"])}</tspan></text>')
    cx = pad + (len(label) + len(CFG["name"]) + 0.6) * ps * 0.6
    body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{done:.2f}s"/>{prompt}'
                f'<rect x="{n(round(cx, 1))}" y="{n(round(py - ps, 1))}" width="{n(round(ps * .6, 1))}" height="{n(round(ps * 1.15, 1))}" fill="{ACCENT}">'
                f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect></g>')
    return window(m, f"snapshot ~ ./{CFG['handle']}.sh", "\n".join(body), h, w=w, defs="".join(defs))


if __name__ == "__main__":
    r = rows()
    print(f"{len(r)} rows")
