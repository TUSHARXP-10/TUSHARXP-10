"""Flagship spotlight: THE-RED-MACHINE architecture, animated.

  python scripts/make_spotlight.py   ->  assets/spotlight.svg

Five pipeline stages with data packets flowing between them, a dashed
auto-retraining loop from live execution back to the model, stage borders
lighting up in sequence, and the four capabilities underneath.
"""
from terminal import (BAR_H, CFG, DIM, FG, LINE, RED, TILE, chip, esc, fade, pulse, save, window)

W, H = 860, 326
SP = CFG["spotlight"]
NODE_W, NODE_H, GAP = 136, 60, 33
NY = BAR_H + 108


def build():
    out = []
    # header
    out.append(f'<text x="24" y="{BAR_H + 30}" font-size="11" fill="{DIM}">$ ./the-red-machine --architecture</text>')
    out.append(f'<text x="24" y="{BAR_H + 56}" font-size="20" font-weight="bold" fill="{RED}">{esc(SP["name"])}</text>')
    out.append(f'<text x="24" y="{BAR_H + 75}" font-size="11" fill="{DIM}">{esc(SP["tagline"])}</text>')
    x = W - 24
    for t in reversed(SP["stack"]):
        w = len(t) * 9 * 0.6 + 12
        x -= w
        c, _ = chip(x, BAR_H + 44, t, RED)
        out.append(c)
        x -= 6
    out.append(f'<g transform="translate({W - 96} {BAR_H + 22})">{pulse(6, 0, 3, RED, 1.2)}'
               f'<text x="16" y="3.5" font-size="9.5" fill="{RED}" font-weight="bold">RUNNING</text></g>')

    # pipeline
    n = len(SP["pipeline"])
    cycle = 0.6 * n + 1.2
    centers = []
    for i, (title, sub) in enumerate(SP["pipeline"]):
        nx = 24 + i * (NODE_W + GAP)
        centers.append(nx)
        t0 = 0.6 * i / cycle
        glow = (f'<animate attributeName="stroke" values="{LINE};{LINE};{RED};{LINE};{LINE}" '
                f'keyTimes="0;{t0:.3f};{t0 + .06:.3f};{min(t0 + .2, .99):.3f};1" dur="{cycle}s" begin="1.5s" repeatCount="indefinite"/>')
        node = (f'<rect x="{nx}" y="{NY}" width="{NODE_W}" height="{NODE_H}" rx="7" fill="{TILE}" stroke="{LINE}" stroke-width="1.4">{glow}</rect>'
                f'<text x="{nx + 12}" y="{NY + 18}" font-size="8.5" fill="{DIM}">0{i + 1}</text>'
                f'<text x="{nx + 12}" y="{NY + 36}" font-size="12" font-weight="bold" fill="{FG}">{esc(title)}</text>'
                f'<text x="{nx + 12}" y="{NY + 51}" font-size="9" fill="{DIM}">{esc(sub)}</text>')
        out.append(fade(i, node, step=0.15, start=0.3))

    # edges + packets
    for i in range(n - 1):
        x1, x2, y = centers[i] + NODE_W, centers[i + 1], NY + NODE_H / 2
        path = f"M{x1 + 2},{y} L{x2 - 4},{y}"
        out.append(f'<path d="{path}" stroke="{LINE}" stroke-width="1.5" fill="none"/>'
                   f'<path d="M{x2 - 8},{y - 4} L{x2 - 3},{y} L{x2 - 8},{y + 4}" stroke="{DIM}" fill="none" stroke-width="1.4"/>')
        for k in range(2):
            out.append(f'<circle r="2.6" fill="{RED}" opacity="0"><set attributeName="opacity" to="1" begin="{1.2 + k * .55 + i * .12:.2f}s"/>'
                       f'<animateMotion path="{path}" dur="1.1s" begin="{1.2 + k * .55 + i * .12:.2f}s" repeatCount="indefinite"/></circle>')

    # retraining loop: bottom of live execution back to the model
    sx = centers[4] + NODE_W / 2
    ex = centers[2] + NODE_W / 2
    by = NY + NODE_H
    loop = f"M{sx},{by + 2} C{sx},{by + 52} {ex},{by + 52} {ex},{by + 6}"
    out.append(fade(6, f'<path d="{loop}" fill="none" stroke="{RED}" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="5 5">'
                       f'<animate attributeName="stroke-dashoffset" from="0" to="-40" dur="1.4s" repeatCount="indefinite"/></path>'
                       f'<path d="M{ex - 4},{by + 12} L{ex},{by + 5} L{ex + 4},{by + 12}" stroke="{RED}" fill="none" stroke-width="1.5"/>'
                       f'<rect x="{(sx + ex) / 2 - 78}" y="{by + 30}" width="156" height="18" rx="9" fill="{BG_FILL}" stroke="{RED}" stroke-opacity=".35"/>'
                       f'<text x="{(sx + ex) / 2}" y="{by + 42.5}" font-size="9.5" fill="{RED}" text-anchor="middle">↺ automated retraining</text>',
                    start=1.2))
    out.append(f'<circle r="3" fill="{RED}" opacity="0"><set attributeName="opacity" to="1" begin="2s"/>'
               f'<animateMotion path="{loop}" dur="2.2s" begin="2s" repeatCount="indefinite"/></circle>')

    # capabilities row
    fy = H - 66
    fw = (W - 48 - 3 * 12) / 4
    for i, f in enumerate(SP["features"]):
        fx = 24 + i * (fw + 12)
        tile = (f'<rect x="{fx:.1f}" y="{fy}" width="{fw:.1f}" height="44" rx="6" fill="{TILE}" stroke="{LINE}"/>'
                f'<rect x="{fx:.1f}" y="{fy}" width="3" height="44" rx="1.5" fill="{RED}"/>'
                f'<text x="{fx + 14:.1f}" y="{fy + 19}" font-size="8.5" fill="{DIM}">capability_0{i + 1}</text>'
                f'<text x="{fx + 14:.1f}" y="{fy + 33}" font-size="10.5" fill="{FG}">{esc(f)}</text>')
        out.append(fade(8 + i, tile, step=0.12, start=0.6))
    return window(f"snapshot ~ ./red-machine --arch", "\n".join(out), w=W, h=H,
                  accent_dots=("#ff6b6b", "#e0a458", "#7ee787"))


BG_FILL = "#0d1117"


def main():
    save("spotlight.svg", build())


if __name__ == "__main__":
    main()
