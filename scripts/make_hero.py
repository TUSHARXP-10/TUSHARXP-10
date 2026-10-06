"""Hero banner: a trading terminal that boots into Tushar's profile.

  python scripts/make_hero.py   ->  assets/hero.svg

- a candlestick chart (seeded random walk, decorative) prints left to right
  behind the text, with a moving average that draws itself
- the name glitches in, then a typewriter cycles through what Tushar builds
- a stock-ticker tape scrolls live stats from data/*.json forever
"""
import math
import random

from terminal import (ACCENT, AMBER, BG, BLUE, CFG, DIM, FG, FONT, GREEN, LINE, RED, chip, esc, load,
                      pulse, save)

W, H = 860, 296
TAPE_H = 34
UP, DOWN = "#7f9f68", "#c96b6b"


def candles():
    rnd = random.Random(29)
    n, x0, x1, y0, y1 = 66, 24, W - 24, 46, H - TAPE_H - 28
    p, rows = 100.0, []
    for _ in range(n):
        o = p
        c = o + rnd.gauss(0.45, 2.4)
        hi = max(o, c) + abs(rnd.gauss(0, 1.3))
        lo = min(o, c) - abs(rnd.gauss(0, 1.3))
        rows.append((o, hi, lo, c))
        p = c
    lo_all = min(r[2] for r in rows)
    hi_all = max(r[1] for r in rows)

    def sy(v):
        return y1 - (v - lo_all) / (hi_all - lo_all) * (y1 - y0)

    slot = (x1 - x0) / n
    bw = slot * 0.56
    out, pts = [], []
    for i, (o, hi, lo, c) in enumerate(rows):
        cx = x0 + i * slot + slot / 2
        col = UP if c >= o else DOWN
        top, bot = sy(max(o, c)), sy(min(o, c))
        b = f"{0.3 + i * 0.045:.2f}s"
        out.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{b}"/>'
            f'<line x1="{cx:.1f}" y1="{sy(hi):.1f}" x2="{cx:.1f}" y2="{sy(lo):.1f}" stroke="{col}" stroke-width="1"/>'
            f'<rect x="{cx - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot - top, 1):.1f}" fill="{col}">'
            f'<animate attributeName="height" from="0" to="{max(bot - top, 1):.1f}" begin="{b}" dur=".25s" fill="freeze"/></rect></g>'
        )
        window = [r[3] for r in rows[max(0, i - 7):i + 1]]
        pts.append((cx, sy(sum(window) / len(window))))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    ma = (f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="1.6" stroke-dasharray="{length:.0f}" '
          f'stroke-dashoffset="{length:.0f}" opacity=".9"><animate attributeName="stroke-dashoffset" '
          f'from="{length:.0f}" to="0" begin=".3s" dur="{0.045 * n:.2f}s" fill="freeze"/></path>')
    lx, ly = pts[-1]
    last = (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{0.3 + 0.045 * n:.2f}s"/>'
            f'<line x1="{x0}" y1="{ly:.1f}" x2="{x1}" y2="{ly:.1f}" stroke="{ACCENT}" stroke-dasharray="2 4" opacity=".35"/>'
            f'{pulse(round(lx, 1), round(ly, 1), 3, ACCENT)}</g>')
    return "".join(out) + ma + last


def typewriter(x, y, phrases, size=17):
    """Cycle phrases forever: type, hold, delete — one clip rect each, one shared cursor."""
    cw = size * 0.6
    per = 3.4
    T = per * len(phrases)
    t_type, t_hold, t_del = 1.1 / T, 1.6 / T, 0.45 / T
    defs, texts, cur_vals, cur_times = [], [], [], []
    for k, ph in enumerate(phrases):
        wk = len(ph) * cw
        a = k / len(phrases)
        times = [0, a + 1e-4, a + t_type, a + t_type + t_hold, a + t_type + t_hold + t_del, 1]
        vals = [0, 0, wk, wk, 0, 0]
        defs.append(f'<clipPath id="ph{k}"><rect x="{x}" y="{y - size}" height="{size + 6}" width="0">'
                    f'<animate attributeName="width" values="{";".join(f"{v:.1f}" for v in vals)}" '
                    f'keyTimes="{";".join(f"{t:.4f}" for t in times)}" dur="{T}s" begin="1.6s" repeatCount="indefinite"/>'
                    f'</rect></clipPath>')
        texts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{ACCENT}" clip-path="url(#ph{k})">{esc(ph)}</text>')
        for t, v in zip(times[1:5], vals[1:5]):
            cur_times.append(t)
            cur_vals.append(x + v)
    cur_times = [0] + cur_times + [1]
    cur_vals = [x] + cur_vals + [x]
    cursor = (f'<rect x="{x}" y="{y - size + 2}" width="{cw:.1f}" height="{size + 2}" fill="{ACCENT}">'
              f'<animate attributeName="x" values="{";".join(f"{v:.1f}" for v in cur_vals)}" '
              f'keyTimes="{";".join(f"{t:.4f}" for t in cur_times)}" dur="{T}s" begin="1.6s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="1;1;.15;.15" dur="1s" repeatCount="indefinite"/></rect>')
    return "".join(defs), "".join(texts) + cursor


def tape(stats, gh):
    s = stats.get("stats", {})
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
    size, cw = 11, 11 * 0.6
    spans, n_chars = [], 0
    for label, val, mark, col in items:
        chunk = f"{label} {val} {mark}     "
        spans.append(f'<tspan fill="{DIM}">{esc(label)} </tspan><tspan fill="{FG}" font-weight="bold">{esc(val)} </tspan>'
                     f'<tspan fill="{col}">{mark}</tspan><tspan>     </tspan>')
        n_chars += len(chunk)
    one = n_chars * cw
    line = "".join(spans)
    y = H - TAPE_H / 2 + 4
    return (f'<rect x="0" y="{H - TAPE_H}" width="{W}" height="{TAPE_H}" fill="#0a0e0b"/>'
            f'<line x1="0" y1="{H - TAPE_H}" x2="{W}" y2="{H - TAPE_H}" stroke="{LINE}"/>'
            f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-one:.1f} 0" '
            f'dur="{one / 45:.1f}s" repeatCount="indefinite"/>'
            f'<text x="16" y="{y}" font-size="{size}" xml:space="preserve">{line}{line}{line}</text></g>')


def build():
    stats = load("contributions.json", {})
    gh = load("github.json", {})
    s = stats.get("stats", {})

    tdefs, roles = typewriter(152, 168, CFG["roles"])
    name = CFG["full_name"].upper()
    name_fs = 38
    glitch = "".join(
        f'<text x="{40 + dx}" y="124" font-size="{name_fs}" font-weight="bold" fill="{col}" opacity="0">{esc(name)}'
        f'<animate attributeName="opacity" values="0;.85;0;.6;0;.4;0" dur=".9s" begin="{b}s" fill="freeze"/></text>'
        for dx, col, b in ((-3, "#ff4d6d", 0.55), (3, "#4dd6ff", 0.6))
    )
    prompt = "tushar@github:~$ ./boot.sh --profile"
    pw = len(prompt) * 12 * 0.6

    pills, x = [], 40
    for text, col in ((f"open to work", GREEN), (CFG["location"], DIM),
                      (f"{s.get('total', 0):,} contributions / yr", ACCENT),
                      (f"{len(CFG['projects'])} live products", AMBER)):
        c, w = chip(x + (14 if col == GREEN else 0), 196, text, col, size=10)
        pills.append(c)
        x += w + 8 + (14 if col == GREEN else 0)
    pills.insert(0, pulse(46, 205, 3.2, GREEN))

    defs = f"""
<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">
  <path d="M22 0H0V22" fill="none" stroke="#ffffff" stroke-opacity=".035"/>
</pattern>
<linearGradient id="veil" x1="0" x2="1">
  <stop offset="0" stop-color="{BG}" stop-opacity=".96"/>
  <stop offset=".42" stop-color="{BG}" stop-opacity=".86"/>
  <stop offset=".72" stop-color="{BG}" stop-opacity=".25"/>
  <stop offset="1" stop-color="{BG}" stop-opacity=".05"/>
</linearGradient>
<radialGradient id="glow" cx=".85" cy=".2" r=".6">
  <stop offset="0" stop-color="{ACCENT}" stop-opacity=".12"/>
  <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
</radialGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<clipPath id="pr"><rect x="40" y="48" height="18" width="0">
  <animate attributeName="width" from="0" to="{pw:.0f}" begin=".1s" dur="1s" fill="freeze"/></rect></clipPath>
<filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
{tdefs}"""

    live_tag = (f'<g transform="translate({W - 150} 18)">'
                f'<rect width="132" height="22" rx="11" fill="{RED}" fill-opacity=".1" stroke="{RED}" stroke-opacity=".4"/>'
                f'{pulse(14, 11, 3, RED, 1.2)}'
                f'<text x="26" y="15" font-size="10" fill="{RED}" font-weight="bold">LIVE</text>'
                f'<text x="58" y="15" font-size="9" fill="{DIM}">{esc((stats.get("fetched_at") or "")[:10])}</text></g>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{defs}</defs>
<g clip-path="url(#card)" font-family="{FONT}">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
{candles()}
<rect width="{W}" height="{H - TAPE_H}" fill="url(#veil)"/>
{live_tag}
<text x="40" y="62" font-size="12" fill="{DIM}" clip-path="url(#pr)">{esc(prompt)}</text>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin=".5s" dur=".3s" fill="freeze"/>
  <text x="40" y="124" font-size="{name_fs}" font-weight="bold" fill="{FG}" filter="url(#soft)" opacity=".25">{esc(name)}</text>
  <text x="40" y="124" font-size="{name_fs}" font-weight="bold" fill="{FG}">{esc(name)}</text>
</g>
{glitch}
<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.3s" dur=".4s" fill="freeze"/>
  <text x="40" y="168" font-size="17" fill="{DIM}">&gt; building</text>
  {roles}
</g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.8s" dur=".5s" fill="freeze"/>{"".join(pills)}</g>
{tape(stats, gh)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{LINE}"/>
</svg>
"""


def main():
    save("hero.svg", build())


if __name__ == "__main__":
    main()
