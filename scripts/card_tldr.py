"""Recruiter TL;DR: why shortlist Tushar, in ten seconds.

Four reasons that tick in (numbers come live from data/*.json), an
availability panel, and a tongue-in-cheek compatibility check that fills
to 100%. Two columns on desktop, stacked on mobile.
"""
from kit import (ACCENT, CFG, DIM, FG, GREEN, LINE, MODES, TILE, contrib, esc, fade, n, pulse, save, text, window,
                 wrap)


def fill(t, s):
    return t.format(live_count=len(CFG["projects"]),
                    streak=s.get("current_streak", {}).get("days", 0),
                    total=f"{s.get('total', 0):,}")


def check(x, y, size, begin):
    k = size / 16
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(size)}" height="{n(size)}" rx="{n(3 * k)}" fill="none" stroke="{LINE}"/>'
            f'<path d="M{n(x + 4 * k)} {n(y + 8 * k)} l{n(3 * k)} {n(3 * k)} l{n(6 * k)} {n(-7 * k)}" fill="none" stroke="{GREEN}" '
            f'stroke-width="{n(2 * k)}" stroke-linecap="round" stroke-dasharray="{n(14 * k)}" stroke-dashoffset="{n(14 * k)}">'
            f'<animate attributeName="stroke-dashoffset" from="{n(14 * k)}" to="0" begin="{begin:.2f}s" dur=".3s" fill="freeze"/></path>')


def availability(m, x, y, w):
    ks, vs = m.f(10.5), (13.5 if m.mobile else 10.5)
    row_h = 30 if m.mobile else 21
    key_w = 108 if m.mobile else 78
    rows = [("status", "open to work"), ("roles", CFG["open_to"]), ("based", f"{CFG['location']} · IST"),
            ("portfolio", CFG["portfolio"].replace("https://", "")), ("reach", CFG["email"])]
    h = (44 if m.mobile else 34) + len(rows) * row_h
    out = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="6" fill="{TILE}" stroke="{LINE}"/>',
           text(x + 14, y + (24 if m.mobile else 20), "$ cat availability.yml", m.f(9.5) if not m.mobile else 13, DIM)]
    for j, (k, v) in enumerate(rows):
        yy = y + (56 if m.mobile else 44) + j * row_h
        vx = x + 14 + key_w
        if k == "status":
            out.append(pulse(vx + vs * 0.35, yy - vs * 0.35, vs * 0.28, GREEN))
            vx += vs * 1.3
        out.append(text(x + 14, yy, f"{k}:", ks if not m.mobile else 13.5, ACCENT))
        out.append(text(vx, yy, v, vs, GREEN if k == "status" else FG))
    return "".join(out), h


def match(m, x, y, w, begin=2.0):
    done = begin + 1.4
    ps = 13 if m.mobile else 9.5
    bh = 14 if m.mobile else 10
    bw = w - (52 if m.mobile else 40)
    label = "$ ./match --role=yours" if m.mobile else "$ ./match --candidate=tushar --role=yours"
    vs = 17 if m.mobile else 10.5
    out = (text(x, y, label, ps, DIM)
           + f'<rect x="{n(x)}" y="{n(y + 10)}" width="{n(bw)}" height="{bh}" rx="{bh / 2}" fill="{TILE}" stroke="{LINE}"/>'
           + f'<rect x="{n(x)}" y="{n(y + 10)}" width="0" height="{bh}" rx="{bh / 2}" fill="{GREEN}">'
           + f'<animate attributeName="width" values="0;{bw * .35:.0f};{bw * .62:.0f};{bw * .9:.0f};{bw:.0f}" '
           + f'keyTimes="0;.25;.5;.8;1" begin="{begin}s" dur="1.4s" fill="freeze"/></rect>'
           + f'<text x="{n(x + bw + 8)}" y="{n(y + 10 + bh * 0.85)}" font-size="{ps + 0.5}" font-weight="bold" fill="{GREEN}" opacity="0">100%'
           + f'<set attributeName="opacity" to="1" begin="{done:.1f}s"/></text>'
           + f'<text x="{n(x)}" y="{n(y + 10 + bh + vs * 1.6)}" font-size="{vs}" fill="{FG}" opacity="0">→ verdict: '
           + f'<tspan fill="{GREEN}" font-weight="bold">shortlist ✓</tspan><set attributeName="opacity" to="1" begin="{done + .2:.1f}s"/></text>')
    return out, 10 + bh + vs * 1.6


def build(m):
    s = contrib()
    bar = m.bar
    out = []
    if not m.mobile:
        W, H = 860, 288
        out.append(text(24, bar + 30, "$ ./hire-me.sh --tldr", 11, DIM))
        out.append(text(24, bar + 52, f"why shortlist {CFG['name'].lower()}?", 16, FG, "bold"))
        y = bar + 84
        for i, (lead, detail) in enumerate(CFG["tldr"]):
            b = 0.5 + i * 0.35
            inner = (check(24, y - 12, 16, b + 0.25) + text(52, y, lead, 12.5, FG, "bold")
                     + text(52, y + 17, fill(detail, s), 10.5, DIM))
            out.append(fade(i, inner, step=0.35, start=0.5, dx=-8, dy=0))
            y += 44
        panel, ph = availability(m, 520, bar + 22, W - 520 - 22)
        out.append(fade(5, panel, start=0.3))
        bars, _ = match(m, 520, bar + 22 + ph + 30, W - 520 - 22)
        out.append(fade(6, bars, start=1.6))
    else:
        W = 480
        out.append(text(24, bar + 36, "$ ./hire-me.sh --tldr", 14, DIM))
        out.append(text(24, bar + 68, f"why shortlist {CFG['name'].lower()}?", 24, FG, "bold"))
        y = bar + 112
        for i, (lead, detail) in enumerate(CFG["tldr"]):
            b = 0.5 + i * 0.35
            lines = wrap(fill(detail, s), W - 60 - 20, 14)
            inner = check(24, y - 17, 22, b + 0.25) + text(60, y, lead, 18, FG, "bold")
            inner += "".join(text(60, y + 24 + j * 19, t, 14, DIM) for j, t in enumerate(lines))
            out.append(fade(i, inner, step=0.35, start=0.5, dx=-8, dy=0))
            y += 24 + len(lines) * 19 + 24
        panel, ph = availability(m, 20, y - 8, W - 40)
        out.append(fade(5, panel, start=0.3))
        y += ph + 26
        bars, bh = match(m, 24, y, W - 48)
        out.append(fade(6, bars, start=1.6))
        H = int(y + bh + 24)
    return window(m, "snapshot ~ ./hire-me.sh --tldr", "\n".join(out), H, w=W)


def main():
    for m in MODES:
        save(m, "tldr.svg", build(m))


if __name__ == "__main__":
    main()
