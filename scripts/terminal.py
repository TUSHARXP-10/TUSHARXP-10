"""Shared theme, content and SVG helpers for every generated card."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
CFG = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))

FONT = "'JetBrains Mono','SF Mono',Menlo,Consolas,'Liberation Mono','Courier New',monospace"
BAR_H = 24
PAD = 14
W, H = 415, 480          # whoami panels (two side by side + 30px gap = 860)

BG = "#0d1117"
TILE = "#161b22"
LINE = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"
ACCENT = "#a9c98c"       # sage green, matches the heatmap
GREEN = "#7ee787"
RED = "#ff6b6b"
AMBER = "#e0a458"
BLUE = "#79c0ff"
VIOLET = "#d2a8ff"


def esc(s):
    return escape(str(s))


def load(name, default=None):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def save(name, svg):
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def fade(i, inner, step=0.1, start=0.2, dx=0, dy=6, static=False):
    """Fade + slide a group in once, staggered by index."""
    if static:
        return f"<g>{inner}</g>"
    b = f"{start + i * step:.2f}s"
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{b}" dur=".45s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="{dx} {dy}" to="0 0" begin="{b}" '
            f'dur=".45s" fill="freeze" calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1"/>{inner}</g>')


def pulse(cx, cy, r, color, dur=1.6):
    """A solid dot with an expanding ring, like a live indicator."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="1.5">'
            f'<animate attributeName="r" values="{r};{r * 3}" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".9;0" dur="{dur}s" repeatCount="indefinite"/></circle>')


def chip(x, y, text, color=DIM, size=9):
    w = len(text) * size * 0.6 + 12
    return (f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{size + 8}" rx="{(size + 8) / 2}" fill="{color}" fill-opacity=".12" '
            f'stroke="{color}" stroke-opacity=".35"/>'
            f'<text x="{x + 6}" y="{y + size + 2.5}" font-size="{size}" fill="{color}">{esc(text)}</text>'), w


def window(title, body, defs="", style="", w=W, h=H, accent_dots=("#e0a458", "#d9b25c", "#c9a24f")):
    dots = "".join(f'<circle cx="{14 + i * 11}" cy="{BAR_H / 2}" r="3.2" fill="{c}"/>' for i, c in enumerate(accent_dots))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{style}</style>
<defs>{defs}</defs>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="{BG}" stroke="{LINE}"/>
<line x1="1" y1="{BAR_H}" x2="{w - 1}" y2="{BAR_H}" stroke="{LINE}" stroke-opacity=".6"/>
{dots}
<text x="{w / 2}" y="{BAR_H / 2 + 3}" text-anchor="middle" fill="{DIM}" font-family="{FONT}" font-size="8.5">{esc(title)}</text>
<g font-family="{FONT}">
{body}
</g>
</svg>
"""
