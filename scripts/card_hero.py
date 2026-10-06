"""Hero banner: a trading terminal that boots into the profile.

- a candlestick chart (seeded random walk — decoration, not real trades)
  prints left to right with a moving average that draws itself
- the name glitches in, then a typewriter cycles through what Tushar builds
- a stock-ticker tape scrolls live numbers from data/*.json forever
Desktop is a wide banner; mobile stacks the name large over two lines.
"""
import math
import random

from kit import (ACCENT, AMBER, BG, BLUE, CFG, DIM, FG, FONT, GREEN, LINE, MODES, RED, chip, contrib, doc, esc,
                 load, n, pulse, save, text, tw)

UP, DOWN = "#7f9f68", "#c96b6b"


def candles(x0, x1, y0, y1, count, begin=0.3, seed=29):
    rnd = random.Random(seed)
    p, rows = 100.0, []
    for _ in range(count):
        o = p
        c = o + rnd.gauss(0.45, 2.4)
        rows.append((o, max(o, c) + abs(rnd.gauss(0, 1.3)), min(o, c) - abs(rnd.gauss(0, 1.3)), c))
        p = c
    lo, hi = min(r[2] for r in rows), max(r[1] for r in rows)

    def sy(v):
        return y1 - (v - lo) / (hi - lo) * (y1 - y0)

    slot = (x1 - x0) / count
    bw = slot * 0.56
    out, pts = [], []
    for i, (o, h, l, c) in enumerate(rows):
        cx = x0 + i * slot + slot / 2
        col = UP if c >= o else DOWN
        top, bot = sy(max(o, c)), sy(min(o, c))
        bh = max(bot - top, 1)
        b = f"{begin + i * 0.045:.2f}s"
        out.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{b}"/>'
                   f'<line x1="{cx:.1f}" y1="{sy(h):.1f}" x2="{cx:.1f}" y2="{sy(l):.1f}" stroke="{col}"/>'
                   f'<rect x="{cx - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}">'
                   f'<animate attributeName="height" from="0" to="{bh:.1f}" begin="{b}" dur=".25s" fill="freeze"/></rect></g>')
        window = [r[3] for r in rows[max(0, i - 7):i + 1]]
        pts.append((cx, sy(sum(window) / len(window))))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    dur = 0.045 * count
    out.append(f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="1.6" stroke-dasharray="{length:.0f}" '
               f'stroke-dashoffset="{length:.0f}" opacity=".9"><animate attributeName="stroke-dashoffset" '
               f'from="{length:.0f}" to="0" begin="{begin}s" dur="{dur:.2f}s" fill="freeze"/></path>')
    lx, ly = pts[-1]
    out.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin + dur:.2f}s"/>'
               f'<line x1="{x0}" y1="{ly:.1f}" x2="{x1}" y2="{ly:.1f}" stroke="{ACCENT}" stroke-dasharray="2 4" opacity=".35"/>'
               f'{pulse(round(lx, 1), round(ly, 1), 3, ACCENT)}</g>')
    return "".join(out)


def typewriter(x, y, phrases, size, begin=1.6, idp="ph"):
    """Cycle phrases forever: type, hold, delete. One clip per phrase, one shared cursor."""
    cw = size * 0.6
    T = 3.4 * len(phrases)
    t_type, t_hold, t_del = 1.1 / T, 1.6 / T, 0.45 / T
    defs, texts, cur_t, cur_v = [], [], [], []
    for k, ph in enumerate(phrases):
        wk = len(ph) * cw
        a = k / len(phrases)
        times = [0, a + 1e-4, a + t_type, a + t_type + t_hold, a + t_type + t_hold + t_del, 1]
        vals = [0, 0, wk, wk, 0, 0]
        defs.append(f'<clipPath id="{idp}{k}"><rect x="{n(x)}" y="{n(y - size)}" height="{n(size * 1.35)}" width="0">'
                    f'<animate attributeName="width" values="{";".join(f"{v:.1f}" for v in vals)}" '
                    f'keyTimes="{";".join(f"{t:.4f}" for t in times)}" dur="{T:.1f}s" begin="{begin}s" '
                    f'repeatCount="indefinite"/></rect></clipPath>')
        texts.append(f'<text x="{n(x)}" y="{n(y)}" font-size="{n(size)}" fill="{ACCENT}" clip-path="url(#{idp}{k})">{esc(ph)}</text>')
        cur_t += times[1:5]
        cur_v += [x + v for v in vals[1:5]]
    cur_t, cur_v = [0] + cur_t + [1], [x] + cur_v + [x]
    cursor = (f'<rect x="{n(x)}" y="{n(round(y - size * 0.9, 1))}" width="{n(round(cw, 1))}" height="{n(round(size * 1.12, 1))}" fill="{ACCENT}">'
              f'<animate attributeName="x" values="{";".join(f"{v:.1f}" for v in cur_v)}" '
              f'keyTimes="{";".join(f"{t:.4f}" for t in cur_t)}" dur="{T:.1f}s" begin="{begin}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="1;1;.15;.15" dur="1s" repeatCount="indefinite"/></rect>')
    return "".join(defs), "".join(texts) + cursor


def glitch(x, y, s, size, begin=0.5, idp="g"):
    """Name with a soft glow and a brief RGB-split glitch as it lands."""
    ghosts = "".join(
        f'<text x="{n(x + dx)}" y="{n(y)}" font-size="{n(size)}" font-weight="bold" fill="{col}" opacity="0">{esc(s)}'
        f'<animate attributeName="opacity" values="0;.85;0;.6;0;.4;0" dur=".9s" begin="{begin + d:.2f}s" fill="freeze"/></text>'
        for dx, col, d in ((-size * 0.08, "#ff4d6d", 0.05), (size * 0.08, "#4dd6ff", 0.1)))
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur=".3s" fill="freeze"/>'
            f'<text x="{n(x)}" y="{n(y)}" font-size="{n(size)}" font-weight="bold" fill="{FG}" filter="url(#soft)" opacity=".28">{esc(s)}</text>'
            f'<text x="{n(x)}" y="{n(y)}" font-size="{n(size)}" font-weight="bold" fill="{FG}">{esc(s)}</text></g>{ghosts}')


def tape(W, H, th, size, s, gh):
    items = [
        ("STREAK", f"{s.get('current_streak', {}).get('days', 0)}D", "▲", GREEN),
        ("CONTRIB/YR", f"{s.get('total', 0):,}", "▲", GREEN),
        ("RED-MACHINE", "LIVE", "●", RED),
        ("PUBLIC REPOS", f"{gh.get('public_repos') or '—'}", "▲", GREEN),
        ("BEST DAY", f"{s.get('best_day', {}).get('count', 0)}", "▲", GREEN),
        ("LIVE PRODUCTS", f"{len(CFG['projects'])}", "▲", GREEN),
        ("ACTIVE DAYS", f"{round(100 * s.get('active_days', 0) / max(s.get('days', 1), 1))}%", "▲", GREEN),
        ("STACK", "PY · TS · REACT · NEXT · NODE", "◆", BLUE),
        ("STATUS", "OPEN TO WORK", "●", GREEN),
    ]
    spans, chars = [], 0
    for label, val, mark, col in items:
        spans.append(f'<tspan fill="{DIM}">{esc(label)} </tspan><tspan fill="{FG}" font-weight="bold">{esc(val)} </tspan>'
                     f'<tspan fill="{col}">{mark}</tspan><tspan>     </tspan>')
        chars += len(f"{label} {val} {mark}     ")
    one = chars * size * 0.6
    line = "".join(spans)
    return (f'<rect x="0" y="{n(H - th)}" width="{W}" height="{n(th)}" fill="#0a0e0b"/>'
            f'<line x1="0" y1="{n(H - th)}" x2="{W}" y2="{n(H - th)}" stroke="{LINE}"/>'
            f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-one:.1f} 0" '
            f'dur="{one / 45:.1f}s" repeatCount="indefinite"/>'
            f'<text x="16" y="{n(round(H - th / 2 + size * 0.36, 1))}" font-size="{n(size)}" xml:space="preserve">{line}{line}{line}</text></g>')


def defs(W, H, vertical=False):
    veil = ('<linearGradient id="veil" x1="0" x2="0" y1="0" y2="1">'
            f'<stop offset="0" stop-color="{BG}" stop-opacity=".97"/><stop offset=".6" stop-color="{BG}" stop-opacity=".9"/>'
            f'<stop offset=".78" stop-color="{BG}" stop-opacity=".3"/><stop offset="1" stop-color="{BG}" stop-opacity=".05"/>'
            '</linearGradient>') if vertical else (
            '<linearGradient id="veil" x1="0" x2="1">'
            f'<stop offset="0" stop-color="{BG}" stop-opacity=".96"/><stop offset=".42" stop-color="{BG}" stop-opacity=".86"/>'
            f'<stop offset=".72" stop-color="{BG}" stop-opacity=".25"/><stop offset="1" stop-color="{BG}" stop-opacity=".05"/>'
            '</linearGradient>')
    return (f'<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">'
            f'<path d="M22 0H0V22" fill="none" stroke="#fff" stroke-opacity=".035"/></pattern>'
            f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="#000" fill-opacity=".18"/></pattern>{veil}'
            f'<radialGradient id="glow" cx=".85" cy=".15" r=".65"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".13"/>'
            f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>'
            f'<filter id="soft" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>')


def prompt_line(x, y, s, size, idp="pr"):
    w = tw(s, size)
    return (f'<clipPath id="{idp}"><rect x="{n(x)}" y="{n(y - size)}" height="{n(size * 1.4)}" width="0">'
            f'<animate attributeName="width" from="0" to="{w:.0f}" begin=".1s" dur="1s" fill="freeze"/></rect></clipPath>',
            text(x, y, s, size, DIM, extra=f' clip-path="url(#{idp})"'))


def live_badge(x, y, k, date):
    w, h = 132 * k, 22 * k
    return (f'<g transform="translate({n(round(x, 1))} {n(y)})">'
            f'<rect width="{n(round(w, 1))}" height="{n(round(h, 1))}" rx="{n(round(h / 2, 1))}" fill="{RED}" fill-opacity=".1" stroke="{RED}" stroke-opacity=".4"/>'
            f'{pulse(round(14 * k, 1), round(h / 2, 1), round(3 * k, 1), RED, 1.2)}'
            + text(26 * k, h / 2 + 3.6 * k, "LIVE", round(10 * k, 1), RED, "bold")
            + text(58 * k, h / 2 + 3.2 * k, date, round(9 * k, 1), DIM) + "</g>")


def build(m):
    stats = load("contributions.json", {}) or {}
    s, gh = stats.get("stats", {}), load("github.json", {}) or {}
    date = (stats.get("fetched_at") or "")[:10]
    pills_spec = [("open to work", GREEN, True), (CFG["location"], DIM, False),
                  (f"{s.get('total', 0):,} contributions / yr", ACCENT, False),
                  (f"{len(CFG['projects'])} live products", AMBER, False)]
    if not m.mobile:
        W, H, th = 860, 296, 34
        pd, pr = prompt_line(40, 62, "tushar@github:~$ ./boot.sh --profile", 12)
        td, roles = typewriter(152, 168, CFG["roles"], 17)
        pills, x = [], 40
        for label, col, dot in pills_spec:
            c, w = chip(x, 192, label, col, 10, dot)
            pills.append(c)
            x += w + 8
        body = (candles(24, W - 24, 46, H - th - 28, 66)
                + f'<rect width="{W}" height="{H - th}" fill="url(#veil)"/>'
                + live_badge(W - 150, 18, 1, date) + pr
                + glitch(40, 124, CFG["full_name"].upper(), 38)
                + f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.3s" dur=".4s" fill="freeze"/>'
                + text(40, 168, "> building", 17, DIM) + roles + "</g>"
                + f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.8s" dur=".5s" fill="freeze"/>{"".join(pills)}</g>'
                + tape(W, H, th, 11, s, gh))
        extra_defs = pd + td
    else:
        W, H, th = 480, 590, 48
        first, _, rest = CFG["full_name"].upper().partition(" ")
        pd, pr = prompt_line(24, 70, "tushar@github:~$ ./boot.sh", 14)
        td, roles = typewriter(24, 290, CFG["roles"], 22)
        pills, rows = [], [pills_spec[:2], pills_spec[2:]]
        for r, row in enumerate(rows):
            x = 24
            for label, col, dot in row:
                c, w = chip(x, 318 + r * 36, label, col, 13, dot)
                pills.append(c)
                x += w + 10
        body = (candles(16, W - 16, 400, H - th - 22, 34)
                + f'<rect width="{W}" height="{H - th}" fill="url(#veil)"/>'
                + live_badge(W - 24 - 132 * 1.2, 20, 1.2, date) + pr
                + glitch(22, 156, first, 78)
                + glitch(24, 206, rest, 37, begin=0.75, idp="g2")
                + f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.3s" dur=".4s" fill="freeze"/>'
                + text(24, 252, "> building", 18, DIM) + roles + "</g>"
                + f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.8s" dur=".5s" fill="freeze"/>{"".join(pills)}</g>'
                + tape(W, H, th, 15, s, gh))
        extra_defs = pd + td
    inner = (f'<g clip-path="url(#card)" font-family="{FONT}">'
             f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#glow)"/>{body}'
             f'<rect width="{W}" height="{H}" fill="url(#scan)" opacity=".5"/></g>'
             f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{LINE}"/>')
    return doc(W, H, inner, defs(W, H, vertical=m.mobile) + extra_defs)


def main():
    for m in MODES:
        save(m, "hero.svg", build(m))


if __name__ == "__main__":
    main()
