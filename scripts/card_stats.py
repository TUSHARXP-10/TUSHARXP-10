"""Contribution stats dashboard panel (used inside whoami).

Tiles: current/longest streak with dates, total, active days, best day,
average per active day; then a contributions-per-month bar chart whose
bars grow from the baseline. Tiles fade in on a stagger, once.
"""
import datetime as dt

from kit import ACCENT, DIM, FG, LINE, TILE, contrib, esc, fade, md, n, text, window

BAR = "#7f9f68"
BAR_TOP = "#a9c98c"


def span(streak):
    return f"{md(streak.get('start'))} – {md(streak.get('end'))}" if streak.get("days") else "start one today"


def tile(x, y, w, h, k, label, value, unit="", sub="", color=FG):
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="5" fill="{TILE}" stroke="{LINE}" stroke-opacity=".7"/>'
            + text(x + 10 * k, y + 15 * k, f"$ {label}", round(8.5 * k, 1), DIM)
            + f'<text x="{n(round(x + 10 * k, 1))}" y="{n(round(y + 39 * k, 1))}" font-size="{n(round(21 * k, 1))}" font-weight="bold" fill="{color}">{esc(value)}'
            + (f'<tspan font-size="{n(round(9 * k, 1))}" font-weight="normal" fill="{DIM}">  {esc(unit)}</tspan>' if unit else "")
            + "</text>" + text(x + 10 * k, y + 54 * k, sub, round(8 * k, 1), DIM))


def chart(x, y, w, h, k, monthly):
    items = list(monthly.items())[-13:]
    peak = max((v for _, v in items), default=0) or 1
    out = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="5" fill="{TILE}" stroke="{LINE}" stroke-opacity=".7"/>',
           text(x + 10 * k, y + 15 * k, "$ contributions / month", round(8.5 * k, 1), DIM)]
    slot = (w - 20 * k) / max(len(items), 1)
    bw = slot * 0.62
    base, top = y + h - 20 * k, y + 40 * k
    lfs = round(7.5 * k, 1)
    for i, (month, v) in enumerate(items):
        bh = max(1.5, (base - top) * v / peak) if v else 1.5
        bx = x + 10 * k + i * slot + (slot - bw) / 2
        delay = f"{1.0 + i * 0.06:.2f}s"
        out.append(f'<rect x="{bx:.1f}" y="{base:.1f}" width="{bw:.1f}" height="0" rx="1.5" fill="{BAR_TOP if v == peak else BAR}">'
                   f'<animate attributeName="height" from="0" to="{bh:.1f}" begin="{delay}" dur=".5s" fill="freeze" '
                   f'calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1"/>'
                   f'<animate attributeName="y" from="{base:.1f}" to="{base - bh:.1f}" begin="{delay}" dur=".5s" fill="freeze" '
                   f'calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1"/></rect>')
        out.append(text(bx + bw / 2, base + 12 * k, dt.date.fromisoformat(month + "-01").strftime("%b")[0], lfs, DIM, anchor="middle"))
        if v == peak and v:
            out.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="1.6s"/>'
                       + text(bx + bw / 2, base - bh - 4 * k, f"{v:,}", lfs, FG, anchor="middle") + "</g>")
    return "".join(out)


def panel(m, w, h):
    s = contrib()
    k = 1.0 if not m.mobile else 1.38
    pad, gap = m.f(14), 8 * k
    th = 64 * k
    tw_ = (w - 2 * pad - gap) / 2
    x1, x2, y = pad, pad + tw_ + gap, m.bar + pad
    pct = round(100 * s.get("active_days", 0) / s["days"]) if s.get("days") else 0
    best = s.get("best_day", {})
    cur, lng = s.get("current_streak", {}), s.get("longest_streak", {})
    tiles = [
        tile(x1, y, tw_, th, k, "current streak", cur.get("days", 0), "days", span(cur), ACCENT),
        tile(x2, y, tw_, th, k, "longest streak", lng.get("days", 0), "days", span(lng)),
        tile(x1, y + th + gap, tw_, th, k, "contributions", f"{s.get('total', 0):,}", "", "in the last year"),
        tile(x2, y + th + gap, tw_, th, k, "active days", s.get("active_days", 0), f"/ {s.get('days', 0)}", f"{pct}% of the year"),
        tile(x1, y + 2 * (th + gap), tw_, th, k, "best day", best.get("count", 0), "", md(best.get("date")) if best.get("count") else "—"),
        tile(x2, y + 2 * (th + gap), tw_, th, k, "avg / active day", s.get("avg_per_active_day", 0), "", "contributions"),
    ]
    body = [fade(i, t, step=0.12) for i, t in enumerate(tiles)]
    cy = y + 3 * (th + gap)
    body.append(fade(6, chart(x1, cy, w - 2 * pad, h - pad - cy, k, s.get("monthly", {})), step=0.12))
    return window(m, "snapshot ~ ./stats.sh", "\n".join(body), h, w=w)
