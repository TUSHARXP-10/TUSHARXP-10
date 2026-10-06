"""Flagship spotlight: THE-RED-MACHINE architecture, animated.

Pipeline stages with data packets flowing between them, a dashed
auto-retraining loop from live execution back to the model, stage borders
lighting up in sequence, and the capabilities underneath. Horizontal on
desktop, vertical on mobile.
"""
from kit import BG, CFG, DIM, FG, LINE, MODES, RED, TILE, chip, fade, n, pulse, save, text, window, wrap

SP = CFG["spotlight"]
DOTS = ("#ff6b6b", "#e0a458", "#7ee787")


def node(x, y, w, h, i, title, sub, k, cycle):
    t0 = 0.6 * i / cycle
    glow = (f'<animate attributeName="stroke" values="{LINE};{LINE};{RED};{LINE};{LINE}" '
            f'keyTimes="0;{t0:.3f};{t0 + .06:.3f};{min(t0 + .2, .99):.3f};1" dur="{cycle}s" begin="1.5s" repeatCount="indefinite"/>')
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="7" fill="{TILE}" stroke="{LINE}" stroke-width="1.4">{glow}</rect>'
            + text(x + 12 * k, y + 18 * k, f"0{i + 1}", round(8.5 * k, 1), DIM)
            + text(x + 12 * k, y + 36 * k, title, round(12 * k, 1), FG, "bold")
            + text(x + 12 * k, y + 51 * k, sub, round(9 * k, 1), DIM))


def packets(path, i, r=2.6):
    return "".join(f'<circle r="{r}" fill="{RED}" opacity="0"><set attributeName="opacity" to="1" begin="{1.2 + j * .55 + i * .12:.2f}s"/>'
                   f'<animateMotion path="{path}" dur="1.1s" begin="{1.2 + j * .55 + i * .12:.2f}s" repeatCount="indefinite"/></circle>'
                   for j in range(2))


def loop_path(path, label_svg, arrow, begin=1.2):
    return fade(6, f'<path d="{path}" fill="none" stroke="{RED}" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="5 5">'
                   f'<animate attributeName="stroke-dashoffset" from="0" to="-40" dur="1.4s" repeatCount="indefinite"/></path>'
                   f'{arrow}{label_svg}', start=begin) + (
        f'<circle r="3" fill="{RED}" opacity="0"><set attributeName="opacity" to="1" begin="2s"/>'
        f'<animateMotion path="{path}" dur="2.2s" begin="2s" repeatCount="indefinite"/></circle>')


def header(m, W, k):
    bar = m.bar
    out = [text(24 if not m.mobile else 20, bar + (30 if not m.mobile else 36),
                "$ ./the-red-machine --architecture" if not m.mobile else "$ ./the-red-machine --arch",
                11 if not m.mobile else 13, DIM)]
    if not m.mobile:
        out.append(text(24, bar + 56, SP["name"], 20, RED, "bold"))
        out.append(text(24, bar + 75, SP["tagline"], 11, DIM))
        x = W - 24
        for t in reversed(SP["stack"]):
            w = len(t) * 9 * 0.6 + 12
            x -= w
            out.append(chip(x, bar + 44, t, RED, 9)[0])
            x -= 6
        out.append(f'<g transform="translate({W - 96} {bar + 22})">{pulse(6, 0, 3, RED, 1.2)}'
                   + text(16, 3.5, "RUNNING", 9.5, RED, "bold") + "</g>")
        return "".join(out), bar + 108
    out.append(text(20, bar + 74, SP["name"], 26, RED, "bold"))
    out.append(text(20, bar + 98, SP["tagline"], 14, DIM))
    x = 20
    for t in SP["stack"]:
        c, w = chip(x, bar + 112, t, RED, 12)
        out.append(c)
        x += w + 8
    out.append(f'<g transform="translate({W - 116} {bar + 31})">{pulse(7, 0, 3.6, RED, 1.2)}'
               + text(20, 4.5, "RUNNING", 13, RED, "bold") + "</g>")
    return "".join(out), bar + 160


def capabilities(m, W, y, k):
    feats = SP["features"]
    out = []
    if not m.mobile:
        fw = (W - 48 - 3 * 12) / 4
        for i, f in enumerate(feats):
            fx = 24 + i * (fw + 12)
            out.append(fade(8 + i, f'<rect x="{fx:.1f}" y="{y}" width="{fw:.1f}" height="44" rx="6" fill="{TILE}" stroke="{LINE}"/>'
                                   f'<rect x="{fx:.1f}" y="{y}" width="3" height="44" rx="1.5" fill="{RED}"/>'
                                   + text(fx + 14, y + 19, f"capability_0{i + 1}", 8.5, DIM) + text(fx + 14, y + 33, f, 10.5, FG),
                            step=0.12, start=0.6))
        return "".join(out), 44
    fw, fh = (W - 40 - 12) / 2, 74
    for i, f in enumerate(feats):
        fx = 20 + (i % 2) * (fw + 12)
        fy = y + (i // 2) * (fh + 12)
        lines = wrap(f, fw - 28, 14, 2)
        out.append(fade(8 + i, f'<rect x="{fx:.1f}" y="{fy}" width="{fw:.1f}" height="{fh}" rx="7" fill="{TILE}" stroke="{LINE}"/>'
                               f'<rect x="{fx:.1f}" y="{fy}" width="4" height="{fh}" rx="2" fill="{RED}"/>'
                               + text(fx + 16, fy + 22, f"capability_0{i + 1}", 11, DIM)
                               + "".join(text(fx + 16, fy + 44 + j * 18, t, 14, FG) for j, t in enumerate(lines)),
                        step=0.12, start=0.6))
    return "".join(out), 2 * fh + 12


def build(m):
    k = 1.0 if not m.mobile else 1.42
    W = m.W
    head, y0 = header(m, W, k)
    steps = SP["pipeline"]
    cycle = 0.6 * len(steps) + 1.2
    body = [head]
    if not m.mobile:
        NW, NH, GAP = 136, 60, 33
        xs = [24 + i * (NW + GAP) for i in range(len(steps))]
        for i, (t, sub) in enumerate(steps):
            body.append(fade(i, node(xs[i], y0, NW, NH, i, t, sub, 1, cycle), step=0.15, start=0.3))
        for i in range(len(steps) - 1):
            x1, x2, y = xs[i] + NW, xs[i + 1], y0 + NH / 2
            path = f"M{x1 + 2},{y} L{x2 - 4},{y}"
            body.append(f'<path d="{path}" stroke="{LINE}" stroke-width="1.5" fill="none"/>'
                        f'<path d="M{x2 - 8},{y - 4} L{x2 - 3},{y} L{x2 - 8},{y + 4}" stroke="{DIM}" fill="none" stroke-width="1.4"/>'
                        + packets(path, i))
        sx, ex, by = xs[4] + NW / 2, xs[2] + NW / 2, y0 + NH
        loop = f"M{sx},{by + 2} C{sx},{by + 52} {ex},{by + 52} {ex},{by + 6}"
        label = (f'<rect x="{(sx + ex) / 2 - 78}" y="{by + 30}" width="156" height="18" rx="9" fill="{BG}" stroke="{RED}" stroke-opacity=".35"/>'
                 + text((sx + ex) / 2, by + 42.5, "↺ automated retraining", 9.5, RED, anchor="middle"))
        arrow = f'<path d="M{ex - 4},{by + 12} L{ex},{by + 5} L{ex + 4},{by + 12}" stroke="{RED}" fill="none" stroke-width="1.5"/>'
        body.append(loop_path(loop, label, arrow))
        caps, ch = capabilities(m, W, by + 70, k)
        body.append(caps)
        H = int(by + 70 + ch + 22)
    else:
        NW, NH, GAP = 300, 86, 30
        x = 20
        ys = [y0 + i * (NH + GAP) for i in range(len(steps))]
        for i, (t, sub) in enumerate(steps):
            body.append(fade(i, node(x, ys[i], NW, NH, i, t, sub, 1.42, cycle), step=0.15, start=0.3))
        cx = x + NW / 2
        for i in range(len(steps) - 1):
            y1, y2 = ys[i] + NH, ys[i + 1]
            path = f"M{cx},{y1 + 2} L{cx},{y2 - 4}"
            body.append(f'<path d="{path}" stroke="{LINE}" stroke-width="1.5" fill="none"/>'
                        f'<path d="M{cx - 5},{y2 - 9} L{cx},{y2 - 3} L{cx + 5},{y2 - 9}" stroke="{DIM}" fill="none" stroke-width="1.5"/>'
                        + packets(path, i, 3.2))
        sy, ey, rx = ys[4] + NH / 2, ys[2] + NH / 2, x + NW
        loop = f"M{rx + 2},{sy} C{rx + 120},{sy} {rx + 120},{ey} {rx + 8},{ey}"
        mid = (sy + ey) / 2
        label = (text(rx + 46, mid - 6, "↺ auto-", 13, RED, anchor="middle")
                 + text(rx + 46, mid + 12, "retrain", 13, RED, anchor="middle"))
        arrow = f'<path d="M{rx + 15},{ey - 5} L{rx + 7},{ey} L{rx + 15},{ey + 5}" stroke="{RED}" fill="none" stroke-width="1.6"/>'
        body.append(loop_path(loop, label, arrow))
        cap_y = ys[-1] + NH + 34
        caps, ch = capabilities(m, W, cap_y, k)
        body.append(caps)
        H = int(cap_y + ch + 22)
    return window(m, "snapshot ~ ./red-machine --arch", "\n".join(body), H, w=W, dots=DOTS)


def main():
    for m in MODES:
        save(m, "spotlight.svg", build(m))


if __name__ == "__main__":
    main()
