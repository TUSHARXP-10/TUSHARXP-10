"""Render the `cat about.txt` terminal window from profile.json.

  python scripts/make_about_card.py   ->  about-card.svg

Full-width (860) window: name and tagline, key/value facts, focus areas and
stack. Lines fade in on a stagger, once. STATIC=1 emits the final frame.
"""
import os

from terminal import ACCENT, BAR_H, CFG, DIM, FG, LINE, PAD, ROOT, TILE, esc, window

OUT = ROOT / "about-card.svg"
W = 860
LH = 19
COL2 = W / 2 + 6
KEY_W = 11            # characters reserved for keys
CH = 11.5 * 0.6       # char width at 11.5px
STATIC = os.environ.get("STATIC") == "1"


def fade(i, inner):
    if STATIC:
        return inner
    b = f"{0.2 + i * 0.08:.2f}s"
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{b}" dur=".4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-6 0" to="0 0" begin="{b}" dur=".4s" fill="freeze"/>'
            f"{inner}</g>")


def kv(x, y, key, value):
    return (f'<text x="{x}" y="{y}" font-size="11.5"><tspan fill="{ACCENT}">{esc(key)}</tspan>'
            f'<tspan x="{x + KEY_W * CH:.1f}" fill="{FG}">{esc(value)}</tspan></text>')


def heading(x, y, text):
    return f'<text x="{x}" y="{y}" font-size="10" fill="{DIM}">$ {esc(text)}</text>'


def build():
    out, i = [], 0
    x1, x2 = PAD + 6, COL2
    y = BAR_H + PAD + 20

    out.append(fade(i, f'<text x="{x1}" y="{y}" font-size="20" font-weight="bold" fill="{FG}">{esc(CFG["full_name"])}</text>'))
    i += 1
    y += 22
    out.append(fade(i, f'<text x="{x1}" y="{y}" font-size="11.5" fill="{DIM}">{esc(CFG["tagline"])}</text>'))
    i += 1
    y += 16
    out.append(f'<line x1="{x1}" y1="{y}" x2="{W - PAD - 6}" y2="{y}" stroke="{LINE}"/>')
    y += 24

    # left column: facts + focus; right column: stack
    top = y
    out.append(fade(i, heading(x1, y, "cat facts")))
    i += 1
    y += LH
    for k, v in CFG["about"]:
        out.append(fade(i, kv(x1, y, k, v)))
        i += 1
        y += LH
    y += 10
    out.append(fade(i, heading(x1, y, "ls focus/")))
    i += 1
    y += LH
    for f in CFG["focus"]:
        out.append(fade(i, f'<text x="{x1}" y="{y}" font-size="11.5"><tspan fill="{ACCENT}">→ </tspan>'
                           f'<tspan fill="{FG}">{esc(f)}</tspan></text>'))
        i += 1
        y += LH
    left_end = y

    y = top
    out.append(fade(i, heading(x2, y, "cat stack.txt")))
    i += 1
    y += LH
    for k, v in CFG["stack"]:
        out.append(fade(i, kv(x2, y, k, v)))
        i += 1
        y += LH
    y += 10
    out.append(fade(i, heading(x2, y, "echo $MOTTO")))
    i += 1
    y += 8
    box_h = 46
    out.append(fade(i, f'<rect x="{x2}" y="{y}" width="{W - PAD - 6 - x2}" height="{box_h}" rx="5" fill="{TILE}" stroke="{LINE}"/>'
                       + "".join(f'<text x="{x2 + 12}" y="{y + 19 + j * 16}" font-size="10.5" fill="{FG}" font-style="italic">{esc(t)}</text>'
                                 for j, t in enumerate(_wrap(CFG["motto"], 52)))))
    i += 1
    y += box_h + LH

    bottom = max(left_end, y)
    h = int(bottom + PAD)
    if not STATIC:
        cy = bottom + 8
        h = int(cy + PAD + 4)
        out.append(f'<text x="{x1}" y="{cy}" font-size="10" fill="{DIM}" opacity="0">'
                   f'<set attributeName="opacity" to="1" begin="{0.2 + i * 0.08:.2f}s"/>tushar@github:~$ </text>'
                   f'<rect x="{x1 + 17 * 6:.1f}" y="{cy - 8}" width="6" height="10" fill="{ACCENT}" opacity="0">'
                   f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" begin="{0.2 + i * 0.08:.2f}s" repeatCount="indefinite"/></rect>')
    return window("snapshot ~ cat about.txt", "\n".join(out), w=W, h=h)


def _wrap(text, width):
    import textwrap
    return textwrap.wrap(text, width)[:2]


def main():
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
