"""Shared kit for every card: content, theme, layout modes and SVG helpers.

Every card renders twice: desktop (860 wide) and mobile (480 wide with larger
type). The README serves the right one through <picture media="…">, so text
stays readable on a phone instead of shrinking an 860px image to 300px.
"""
import datetime as dt
import json
import os
import textwrap
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("PROFILE_DATA_DIR", ROOT / "data"))
ASSETS = Path(os.environ.get("PROFILE_ASSETS_DIR", ROOT / "assets"))
CFG = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))

FONT = ("'JetBrains Mono','SF Mono',Menlo,'Roboto Mono','DejaVu Sans Mono',Consolas,"
        "'Liberation Mono','Courier New',monospace")
ADV = 0.6  # monospace advance width per unit of font size

BG = "#0d1117"
BG2 = "#090c10"
TILE = "#161b22"
LINE = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"
FAINT = "#484f58"
ACCENT = "#a9c98c"   # sage green — the signature colour, matches the heatmap
GREEN = "#7ee787"
RED = "#ff6b6b"
AMBER = "#e0a458"
BLUE = "#79c0ff"
VIOLET = "#d2a8ff"
CYAN = "#56d4dd"
DOTS = ("#e0a458", "#d9b25c", "#c9a24f")


@dataclass(frozen=True)
class Mode:
    key: str     # "desktop" or "mobile" — also the asset sub-directory
    W: int       # canvas width
    k: float     # type/spacing scale relative to desktop

    @property
    def mobile(self):
        return self.key == "mobile"

    def f(self, size):
        """Scale a desktop size (font, gap, radius) for this mode."""
        return round(size * self.k, 2)

    @property
    def bar(self):
        return round(24 * self.k)

    @property
    def pad(self):
        return 20 if self.mobile else 24


DESKTOP = Mode("desktop", 860, 1.0)
MOBILE = Mode("mobile", 480, 1.4)
MODES = (DESKTOP, MOBILE)


# ---------------------------------------------------------------- text

def esc(s):
    return escape(str(s), {'"': "&quot;"})


def n(v):
    """Compact number formatting for SVG attributes."""
    return f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def tw(s, size):
    """Width of a monospace string at a font size."""
    return len(str(s)) * size * ADV


def fit(s, width, size):
    """Truncate a string with an ellipsis so it fits a width."""
    s, cap = str(s), max(1, int(width // (size * ADV)))
    return s if len(s) <= cap else s[:cap - 1].rstrip() + "…"


def wrap(s, width, size, max_lines=None):
    cap = max(1, int(width // (size * ADV)))
    lines = textwrap.wrap(str(s), cap) or [""]
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        lines[-1] = (last if len(last) < cap else last[:cap - 1].rstrip()) + "…"
    return lines


def text(x, y, s, size, fill=FG, weight=None, anchor=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{n(x)}" y="{n(y)}" font-size="{n(size)}" fill="{fill}"{w}{a}{extra}>{esc(s)}</text>'


# ---------------------------------------------------------------- motion

def fade(i, inner, step=0.1, start=0.2, dx=0, dy=6, dur=0.45):
    """Fade + slide a group in once, staggered by index."""
    b = f"{start + i * step:.2f}s"
    move = (f'<animateTransform attributeName="transform" type="translate" from="{n(dx)} {n(dy)}" to="0 0" '
            f'begin="{b}" dur="{dur}s" fill="freeze" calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1"/>'
            if dx or dy else "")
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{b}" dur="{dur}s" '
            f'fill="freeze"/>{move}{inner}</g>')


def pulse(cx, cy, r, color, dur=1.6):
    """A solid dot with an expanding ring, like a live indicator."""
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{color}"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="{color}" stroke-width="1.5">'
            f'<animate attributeName="r" values="{n(r)};{n(r * 3)}" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".9;0" dur="{dur}s" repeatCount="indefinite"/></circle>')


def blink(x, y, w, h, color, begin=0.0):
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{color}">'
            f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" begin="{begin:.2f}s" '
            f'repeatCount="indefinite"/></rect>')


# ---------------------------------------------------------------- shapes

def chip(x, y, label, color=DIM, size=9, dot=False):
    """Pill with a tinted fill. Returns (svg, width)."""
    h = size + 8
    lead = size * 1.25 if dot else 0
    w = tw(label, size) + 12 + lead
    out = (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{color}" '
           f'fill-opacity=".12" stroke="{color}" stroke-opacity=".38"/>')
    if dot:
        out += pulse(x + 6 + size * 0.35, y + h / 2, size * 0.28, color)
    out += text(x + 6 + lead, y + h / 2 + size * 0.36, label, size, color)
    return out, w


def doc(w, h, body, defs="", style=""):
    st = f"<style>{style}</style>" if style else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(w)}" height="{n(h)}" viewBox="0 0 {n(w)} {n(h)}">'
            f"{st}<defs>{defs}</defs>{body}</svg>\n")


def window(m, title, body, h, w=None, defs="", style="", dots=DOTS):
    """Terminal window chrome: rounded frame, title bar with three dots."""
    w = w or m.W
    bar = m.bar
    r = m.f(3.2)
    dot_svg = "".join(f'<circle cx="{n(m.f(14) + i * m.f(11))}" cy="{n(bar / 2)}" r="{n(r)}" fill="{c}"/>'
                      for i, c in enumerate(dots))
    frame = (f'<rect x=".5" y=".5" width="{n(w - 1)}" height="{n(h - 1)}" rx="{n(m.f(8))}" fill="{BG}" stroke="{LINE}"/>'
             f'<line x1="1" y1="{bar}" x2="{n(w - 1)}" y2="{bar}" stroke="{LINE}" stroke-opacity=".6"/>{dot_svg}'
             + text(w / 2, bar / 2 + m.f(3), title, m.f(8.5), DIM, anchor="middle"))
    return doc(w, h, f'<g font-family="{FONT}">{frame}{body}</g>', defs, style)


# ---------------------------------------------------------------- data & io

def load(name, default=None):
    p = DATA / name
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except ValueError:
        return default


def contrib():
    return (load("contributions.json", {}) or {}).get("stats", {})


def md(date):
    """'2026-03-08' -> 'Mar 8'."""
    if not date:
        return "—"
    d = dt.date.fromisoformat(date[:10])
    return f"{d:%b} {d.day}"


def save(m, name, svg):
    path = ASSETS / m.key / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    try:
        shown = path.relative_to(ROOT)
    except ValueError:
        shown = path
    print(f"wrote {shown}")
