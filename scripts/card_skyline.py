"""Contributions: a flat heatmap that tilts into a 3D skyline, then back. Loops.

How it works (pure SMIL, no JS):
  1. the flat 53x7 heatmap wipes in
  2. its group animates translate/skewX/scale into an oblique projection
  3. at that instant it's swapped for an identical floor + pre-drawn 3D bars;
     a slanted clip rises so bars grow left-to-right out of the floor
  4. hold, then the clip falls, the floor swaps back and the grid un-tilts
Bar height ~ contributions (sqrt-ish, capped at the 95th percentile).
"""
import datetime as dt
import math

from kit import (ACCENT, AMBER, BLUE, DIM, FG, GREEN, LINE, MODES, chip, contrib, esc, fade, load, md, n, pulse,
                 save, text, window)

PALETTE = ["#262c26", "#3b5236", "#56744a", "#7f9f68", "#a9c98c", "#d6edbd"]
T = 16.0                                  # loop length (s)
TILT0, TILT1, SWITCH = 1.6, 2.8, 2.8
RISE0, RISE1 = 2.85, 4.9
FALL0, FALL1, BACK = 12.6, 13.6, 13.65
UNTILT0, UNTILT1 = 13.7, 14.9


def shade(hex_color, f):
    c = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{max(0, min(255, round(v * f))):02x}" for v in c)


def weeks_of(days):
    weeks = []
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        if not weeks or (date.weekday() + 1) % 7 == 0:
            weeks.append([])
        weeks[-1].append((date, d))
    return weeks[-53:]


def kt(*secs):
    return ";".join(f"{s / T:.4f}" for s in secs)


def layout(m):
    if m.mobile:
        return dict(W=480, H=496, s=7.8, c=6.4, dx=3.34, dy=3.9, ox=46, oy=282, bx=42, by=412, hmax=150,
                    fs_lab=8.5, months_every=2)
    return dict(W=860, H=408, s=14, c=11.5, dx=6, dy=7, ox=70, oy=172, bx=86, by=302, hmax=140,
                fs_lab=10, months_every=1)


def build(m):
    data = load("contributions.json", {}) or {}
    s = data.get("stats", {})
    L = layout(m)
    W, H, S, C = L["W"], L["H"], L["s"], L["c"]
    weeks = weeks_of(data.get("days", []))

    # projection: flat (x, y) -> A·(x, y) + t
    a12, a22 = -L["dx"] / S, L["dy"] / S
    tx = L["bx"] - (L["ox"] + a12 * L["oy"])
    ty = L["by"] - a22 * L["oy"]
    theta = math.degrees(math.atan(a12 / a22))

    def M(x, y):
        return (x + a12 * y + tx, a22 * y + ty)

    affine = f"translate({tx:.3f} {ty:.3f}) skewX({theta:.3f}) scale(1 {a22:.4f})"

    counts = sorted(d["count"] for w in weeks for _, d in w if d["count"])
    peak = counts[-1] if counts else 1
    neon = counts[int(len(counts) * 0.95)] if len(counts) >= 20 else float("inf")

    def height(cnt):
        # scaled against the best day: steady days form the "city", big days become towers
        return 0 if not cnt else max(3.0, L["hmax"] * (cnt / peak) ** 0.75)

    # ---- flat heatmap + floor share the same cells and labels
    cells, labels, last_month, month_i = [], [], None, 0
    prisms, glow = [], []
    last = None
    for x, week in enumerate(weeks):
        for date, d in week:
            r = (date.weekday() + 1) % 7
            lvl = 5 if d["level"] == 4 and d["count"] >= neon else d["level"]
            fx, fy = L["ox"] + x * S, L["oy"] + r * S
            cells.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{C}" height="{C}" rx="2" fill="{PALETTE[lvl]}"/>')
            if r == 0 and date.month != last_month and date.day <= 7 and x < len(weeks) - 2:
                if month_i % L["months_every"] == 0:
                    labels.append(text(fx, L["oy"] - 6, f"{date:%b}", L["fs_lab"], DIM))
                last_month = date.month
                month_i += 1
            h = height(d["count"])
            last = (fx, fy, h, d)
            if not h:
                continue
            fl, fr = M(fx, fy + C), M(fx + C, fy + C)
            br, bl = M(fx + C, fy), M(fx, fy)
            base = PALETTE[max(lvl, 1)]
            pts = lambda ps: " ".join(f"{px:.1f},{py:.1f}" for px, py in ps)  # noqa: E731
            prisms.append((r, x,
                           f'<rect x="{fl[0]:.1f}" y="{fl[1] - h:.1f}" width="{fr[0] - fl[0]:.1f}" height="{h:.1f}" fill="url(#f{max(lvl, 1)})"/>'
                           f'<polygon points="{pts([fr, br, (br[0], br[1] - h), (fr[0], fr[1] - h)])}" fill="{shade(base, .5)}"/>'
                           f'<polygon points="{pts([(p[0], p[1] - h) for p in (fl, fr, br, bl)])}" fill="{base}"/>'))
            if lvl == 5:
                glow.append(f'<polygon points="{pts([(p[0], p[1] - h) for p in (fl, fr, br, bl)])}" fill="{PALETTE[5]}"/>')
    prisms.sort(key=lambda p: (p[0], p[1]))
    day_labels = "".join(text(L["ox"] - 6, L["oy"] + i * S + C * 0.8, nm, L["fs_lab"], DIM, anchor="end")
                         for i, nm in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    grid_w, grid_h = len(weeks) * S - (S - C), 7 * S - (S - C)
    plate = (f'<rect x="{L["ox"] - 5}" y="{L["oy"] - 5}" width="{grid_w + 10:.1f}" height="{grid_h + 10:.1f}" '
             f'rx="5" fill="#10151c" stroke="{LINE}"/>')
    flat_inner = plate + "".join(cells) + "".join(labels)

    # slab edge under the floor in 3D
    p_fl, p_fr = M(L["ox"] - 5, L["oy"] + grid_h + 5), M(L["ox"] + grid_w + 5, L["oy"] + grid_h + 5)
    p_br = M(L["ox"] + grid_w + 5, L["oy"] - 5)
    slab_t = 7 if not m.mobile else 6
    slab = (f'<polygon points="{p_fl[0]:.1f},{p_fl[1]:.1f} {p_fr[0]:.1f},{p_fr[1]:.1f} {p_fr[0]:.1f},{p_fr[1] + slab_t:.1f} '
            f'{p_fl[0]:.1f},{p_fl[1] + slab_t:.1f}" fill="#0b0f14" stroke="{LINE}"/>'
            f'<polygon points="{p_fr[0]:.1f},{p_fr[1]:.1f} {p_br[0]:.1f},{p_br[1]:.1f} {p_br[0]:.1f},{p_br[1] + slab_t:.1f} '
            f'{p_fr[0]:.1f},{p_fr[1] + slab_t:.1f}" fill="#080b0f" stroke="{LINE}"/>')

    today = ""
    if last and last[2]:
        fx, fy, h, d = last
        cx, cy = M(fx + C / 2, fy + C / 2)
        today = (pulse(round(cx, 1), round(cy - h - 9, 1), 2.6 if not m.mobile else 2.4, GREEN)
                 + text(cx - 7, cy - h - 6, "today", m.f(8) if not m.mobile else 11, GREEN, anchor="end"))

    floor_bottom = p_fl[1] + slab_t + 2
    slope = 140 if not m.mobile else 90
    rise = floor_bottom + slope + 30
    spl = ".4 0 .2 1;"
    clip_anim = (f'<animateTransform attributeName="transform" type="translate" '
                 f'values="0 0;0 0;0 {-rise:.0f};0 {-rise:.0f};0 0;0 0" keyTimes="{kt(0, RISE0, RISE1, FALL0, FALL1, T)}" '
                 f'calcMode="spline" keySplines="0 0 1 1;{spl}0 0 1 1;{spl}0 0 1 1" dur="{T}s" repeatCount="indefinite"/>')
    defs = (f'<clipPath id="rise"><polygon points="0,{floor_bottom:.1f} {W},{floor_bottom + slope:.1f} {W},{H * 4} 0,{H * 4}">'
            f'{clip_anim}</polygon></clipPath>'
            f'<clipPath id="intro"><rect x="0" y="0" height="{H}" width="0">'
            f'<animate attributeName="width" from="0" to="{W}" begin=".2s" dur="1.2s" fill="freeze"/></rect></clipPath>'
            f'<filter id="neon" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
            + "".join(f'<linearGradient id="f{i}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{shade(c, .9)}"/>'
                      f'<stop offset="1" stop-color="{shade(c, .45)}"/></linearGradient>' for i, c in enumerate(PALETTE)))

    tilt_kt = kt(0, TILT0, TILT1, UNTILT0, UNTILT1, T)
    tilt_spl = f'calcMode="spline" keySplines="0 0 1 1;{spl}0 0 1 1;{spl}0 0 1 1"'
    flat = (f'<g>'
            f'<animateTransform attributeName="transform" type="translate" additive="sum" '
            f'values="0 0;0 0;{tx:.3f} {ty:.3f};{tx:.3f} {ty:.3f};0 0;0 0" keyTimes="{tilt_kt}" {tilt_spl} dur="{T}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="skewX" additive="sum" '
            f'values="0;0;{theta:.3f};{theta:.3f};0;0" keyTimes="{tilt_kt}" {tilt_spl} dur="{T}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="scale" additive="sum" '
            f'values="1 1;1 1;1 {a22:.4f};1 {a22:.4f};1 1;1 1" keyTimes="{tilt_kt}" {tilt_spl} dur="{T}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;0;1" keyTimes="{kt(0, SWITCH, BACK)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>'
            f'<g clip-path="url(#intro)">{flat_inner}{day_labels}</g></g>')
    sky = (f'<g opacity="0">'
           f'<animate attributeName="opacity" values="0;1;0" keyTimes="{kt(0, SWITCH, BACK)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>'
           f'{slab}<g transform="{affine}">{flat_inner}</g>'
           f'<g clip-path="url(#rise)">{"".join(p[2] for p in prisms)}'
           f'<g filter="url(#neon)" opacity=".5"><animate attributeName="opacity" values=".25;.8;.25" dur="2.4s" repeatCount="indefinite"/>'
           f'{"".join(glow)}</g>{today}</g></g>')

    # ---- header, chips, legend, mode indicator
    bar = m.bar
    total = s.get("total", 0)
    streak = s.get("current_streak", {}).get("days", 0)
    best = s.get("best_day", {})
    pct = round(100 * s.get("active_days", 0) / max(s.get("days", 1), 1))
    chips_spec = [(f"▲ {streak}-day streak", GREEN), (f"best day {best.get('count', 0)} · {md(best.get('date'))}", AMBER),
                  (f"{pct}% days active", BLUE)]
    head = []
    if not m.mobile:
        head.append(text(24, bar + 30, "$ ./contributions.sh --render=3d", 11, DIM))
        head.append(text(24, bar + 70, f"{total:,}", 34, FG, "bold"))
        head.append(text(24 + len(f"{total:,}") * 20.4 + 12, bar + 70, "contributions in the last year", 12, DIM))
        x = W - 24
        built = []
        for label, col in reversed(chips_spec):
            w = len(label) * 10 * 0.6 + 12
            x -= w
            built.append(chip(x, bar + 18, label, col, 10)[0])
            x -= 8
        head += built
        ly = H - 20
    else:
        head.append(text(20, bar + 38, "$ ./contributions.sh --3d", 13, DIM))
        head.append(text(20, bar + 92, f"{total:,}", 46, FG, "bold"))
        head.append(text(20, bar + 118, "contributions in the last year", 15, DIM))
        rows = [chips_spec[:1] + chips_spec[2:], chips_spec[1:2]]
        for j, row in enumerate(rows):
            x = 20
            for label, col in row:
                c, w = chip(x, bar + 136 + j * 32, label, col, 13)
                head.append(c)
                x += w + 10
        ly = H - 18
    sw = 9 if not m.mobile else 11
    lx = W - 24 - 6 * (sw + 3) - (34 if not m.mobile else 40)
    lfs = 9.5 if not m.mobile else 12
    legend = (text(lx - 6, ly, "less", lfs, DIM, anchor="end")
              + "".join(f'<rect x="{lx + i * (sw + 3)}" y="{ly - sw + 1}" width="{sw}" height="{sw}" rx="2" fill="{c}"/>'
                        for i, c in enumerate(PALETTE))
              + text(lx + 6 * (sw + 3) + 3, ly, "more", lfs, DIM))
    mode_fs = 9.5 if not m.mobile else 12
    m2d, _ = chip(20 if m.mobile else 24, ly - mode_fs - 2, "2D · heatmap", DIM, mode_fs)
    m3d, _ = chip(20 if m.mobile else 24, ly - mode_fs - 2, "3D · skyline", ACCENT, mode_fs)
    mode = (f'<g><animate attributeName="opacity" values="1;0;1" keyTimes="{kt(0, SWITCH, BACK)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>{m2d}</g>'
            f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="{kt(0, SWITCH, BACK)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>{m3d}</g>')

    body = flat + sky + fade(0, "".join(head), start=0.1, dy=4) + legend + mode
    return window(m, "snapshot ~ ./contributions.sh", body, H, w=W, defs=defs)


def main():
    for m in MODES:
        save(m, "skyline.svg", build(m))


if __name__ == "__main__":
    main()
