"""Section header strips and the footer sign-off.

Headers replace markdown <h3>s: they scale with the page instead of
wrapping awkwardly on a phone, and match the terminal look.
"""
from kit import ACCENT, BG, CFG, DIM, FG, FONT, GREEN, LINE, MODES, blink, doc, esc, n, save, text, tw

SECTIONS = {
    "live": ("ls ~/live --deployed", lambda: f"{len(CFG['projects'])} apps"),
    "repos": ("ls ~/repos --featured", lambda: f"{len(CFG['repos'])} repos"),
    "links": ("./contact.sh", lambda: "say hi"),
}


def header(m, cmd, badge):
    W = 824 if not m.mobile else m.W   # desktop: same width as the two-card grid below it
    fs = 13 if not m.mobile else 17
    H = 44 if not m.mobile else 56
    y = H / 2 + fs * 0.36
    host = "tushar@github ~ $ " if not m.mobile else "~ $ "
    x_cmd = 4 + tw(host, fs)
    end = x_cmd + tw(cmd, fs)
    bfs = 10 if not m.mobile else 13
    bw = tw(badge, bfs) + 16
    bx = W - bw - 2
    body = (f'<text x="4" y="{n(round(y, 1))}" font-size="{fs}" fill="{ACCENT}" font-weight="bold">{esc(host)}'
            f'<tspan fill="{FG}">{esc(cmd)}</tspan></text>'
            + blink(end + 4, y - fs * 0.85, fs * 0.55, fs * 1.05, ACCENT)
            + f'<line x1="{end + fs:.1f}" y1="{H / 2:.1f}" x2="{bx - 10:.1f}" y2="{H / 2:.1f}" stroke="{LINE}" stroke-dasharray="3 5"/>'
            + f'<rect x="{bx:.1f}" y="{H / 2 - bfs * 0.95:.1f}" width="{bw:.1f}" height="{bfs * 1.9:.1f}" rx="{bfs * 0.95:.1f}" '
              f'fill="{ACCENT}" fill-opacity=".12" stroke="{ACCENT}" stroke-opacity=".4"/>'
            + text(bx + bw / 2, H / 2 + bfs * 0.36, badge, bfs, ACCENT, anchor="middle"))
    return doc(W, H, f'<g font-family="{FONT}">{body}</g>')


def typed(i, x, y, s, size, color, begin, cps=28, bold=False):
    w = tw(s, size)
    dur = len(s) / cps
    weight = ' font-weight="bold"' if bold else ""
    return (f'<clipPath id="t{i}"><rect x="{x}" y="{y - size}" height="{size * 1.4:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{w:.0f}" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" clip-path="url(#t{i})"{weight}>{esc(s)}</text>'), begin + dur


def footer(m):
    if not m.mobile:
        W, H = 860, 120
        lines = [("tushar@github:~$ exit", 12, DIM, False, 36), ("connection to tushar@github closed.", 12, FG, False, 62),
                 ("thanks for scrolling — if you're hiring, let's build something real.", 13, ACCENT, True, 92)]
        x = 30
    else:
        W, H = 480, 196
        lines = [("tushar@github:~$ exit", 15, DIM, False, 44), ("connection to tushar@github closed.", 15, FG, False, 74),
                 ("thanks for scrolling —", 18, ACCENT, True, 116), ("if you're hiring,", 18, ACCENT, True, 142),
                 ("let's build something real.", 18, ACCENT, True, 168)]
        x = 22
    out, t = [], 0.3
    for i, (s, size, col, bold, y) in enumerate(lines):
        piece, t = typed(i, x, y, s, size, col, t + (0.4 if i else 0), bold=bold)
        out.append(piece)
    last, size, y = lines[-1][0], lines[-1][1], lines[-1][4]
    out.append(f'<rect x="{x + tw(last, size) + 4:.0f}" y="{y - size * 0.9:.1f}" width="{size * 0.6:.1f}" height="{size * 1.15:.1f}" fill="{GREEN}" opacity="0">'
               f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
    return doc(W, H, f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{LINE}"/>'
                     f'<g font-family="{FONT}">{"".join(out)}</g>')


def main():
    for m in MODES:
        for key, (cmd, badge) in SECTIONS.items():
            save(m, f"head-{key}.svg", header(m, cmd, badge()))
        save(m, "footer.svg", footer(m))


if __name__ == "__main__":
    main()
