"""Recruiter TL;DR: why shortlist Tushar, in ten seconds.

  python scripts/make_tldr.py   ->  assets/tldr.svg

Left: four checked reasons (numbers come live from data/*.json).
Right: availability panel and a tongue-in-cheek "compatibility check"
progress bar that fills to 100%.
"""
from terminal import (ACCENT, BAR_H, CFG, DIM, FG, GREEN, LINE, TILE, esc, fade, load, pulse, save,
                      window)

W, H = 860, 288


def fill(text, stats):
    s = stats.get("stats", {})
    return text.format(
        live_count=len(CFG["projects"]),
        streak=s.get("current_streak", {}).get("days", 0),
        total=f"{s.get('total', 0):,}",
    )


def build():
    stats = load("contributions.json", {})
    out = [f'<text x="24" y="{BAR_H + 30}" font-size="11" fill="{DIM}">$ ./hire-me.sh --tldr</text>',
           f'<text x="24" y="{BAR_H + 52}" font-size="16" font-weight="bold" fill="{FG}">why shortlist {esc(CFG["name"].lower())}?</text>']
    y = BAR_H + 84
    for i, (lead, detail) in enumerate(CFG["tldr"]):
        b = 0.5 + i * 0.35
        check = (f'<rect x="24" y="{y - 12}" width="16" height="16" rx="3" fill="none" stroke="{LINE}"/>'
                 f'<path d="M28 {y - 4} l3 3 l6 -7" fill="none" stroke="{GREEN}" stroke-width="2" stroke-linecap="round" '
                 f'stroke-dasharray="14" stroke-dashoffset="14"><animate attributeName="stroke-dashoffset" from="14" to="0" '
                 f'begin="{b + 0.25:.2f}s" dur=".3s" fill="freeze"/></path>')
        text = (f'<text x="52" y="{y}" font-size="12.5" font-weight="bold" fill="{FG}">{esc(lead)}</text>'
                f'<text x="52" y="{y + 17}" font-size="10.5" fill="{DIM}">{esc(fill(detail, stats))}</text>')
        out.append(fade(i, check + text, step=0.35, start=0.5, dx=-8, dy=0))
        y += 44

    # availability panel
    px, py, pw = 520, BAR_H + 22, W - 520 - 22
    rows = [("status", "open to work"), ("roles", CFG["open_to"]), ("based", f"{CFG['location']} · IST"),
            ("portfolio", CFG["portfolio"].replace("https://", "")), ("reach", "tusharchandane8@gmail.com")]
    panel = [f'<rect x="{px}" y="{py}" width="{pw}" height="148" rx="6" fill="{TILE}" stroke="{LINE}"/>',
             f'<text x="{px + 14}" y="{py + 20}" font-size="9.5" fill="{DIM}">$ cat availability.yml</text>']
    for j, (k, v) in enumerate(rows):
        yy = py + 44 + j * 21
        val_x = px + 86
        if k == "status":
            panel.append(pulse(val_x + 4, yy - 4, 3, GREEN))
            val_x += 14
        panel.append(f'<text x="{px + 14}" y="{yy}" font-size="10.5" fill="{ACCENT}">{k}:</text>'
                     f'<text x="{val_x}" y="{yy}" font-size="10.5" fill="{GREEN if k == "status" else FG}">{esc(v)}</text>')
    out.append(fade(5, "".join(panel), start=0.3))

    # compatibility check bar
    by = py + 148 + 30
    bw = pw - 28
    done = 3.4
    bar = (f'<text x="{px}" y="{by}" font-size="9.5" fill="{DIM}">$ ./match --candidate=tushar --role=yours</text>'
           f'<rect x="{px}" y="{by + 10}" width="{bw}" height="10" rx="5" fill="{TILE}" stroke="{LINE}"/>'
           f'<rect x="{px}" y="{by + 10}" width="0" height="10" rx="5" fill="{GREEN}">'
           f'<animate attributeName="width" values="0;{bw * .35:.0f};{bw * .62:.0f};{bw * .9:.0f};{bw}" '
           f'keyTimes="0;.25;.5;.8;1" begin="2s" dur="{done - 2:.1f}s" fill="freeze"/></rect>'
           f'<text x="{px + bw + 8}" y="{by + 19}" font-size="10" font-weight="bold" fill="{GREEN}" opacity="0">100%'
           f'<set attributeName="opacity" to="1" begin="{done:.1f}s"/></text>'
           f'<text x="{px}" y="{by + 38}" font-size="10.5" fill="{FG}" opacity="0">→ verdict: <tspan fill="{GREEN}" '
           f'font-weight="bold">shortlist ✓</tspan><set attributeName="opacity" to="1" begin="{done + .2:.1f}s"/></text>')
    out.append(fade(6, bar, start=1.6))
    return window("snapshot ~ ./hire-me.sh --tldr", "\n".join(out), w=W, h=H)


def main():
    save("tldr.svg", build())


if __name__ == "__main__":
    main()
