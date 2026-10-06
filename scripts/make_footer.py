"""Sign-off: `$ exit` and a typed goodbye.

  python scripts/make_footer.py   ->  assets/footer.svg
"""
from terminal import ACCENT, BG, DIM, FG, FONT, GREEN, LINE, esc, save

W, H = 860, 120


def typed(i, x, y, text, size, color, begin, cps=28, bold=False):
    w = len(text) * size * 0.6
    weight = ' font-weight="bold"' if bold else ""
    dur = len(text) / cps
    return (f'<clipPath id="t{i}"><rect x="{x}" y="{y - size}" height="{size + 6}" width="0">'
            f'<animate attributeName="width" from="0" to="{w:.0f}" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" clip-path="url(#t{i})"{weight}>{esc(text)}</text>'), begin + dur


def build():
    out = []
    a, t = typed(0, 30, 36, "tushar@github:~$ exit", 12, DIM, 0.3)
    out.append(a)
    b, t = typed(1, 30, 62, "connection to tushar@github closed.", 12, FG, t + 0.4)
    out.append(b)
    c, t = typed(2, 30, 92, "thanks for scrolling — if you're hiring, let's build something real.", 13, ACCENT, t + 0.5, bold=True)
    out.append(c)
    cx = 30 + len("thanks for scrolling — if you're hiring, let's build something real.") * 13 * 0.6 + 4
    out.append(f'<rect x="{cx:.0f}" y="80" width="8" height="15" fill="{GREEN}" opacity="0">'
               f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{LINE}"/>
<g font-family="{FONT}">{"".join(out)}</g>
</svg>
"""


def main():
    save("footer.svg", build())


if __name__ == "__main__":
    main()
