"""Clickable cards: live deployments, featured repos, link buttons.

  python scripts/make_cards.py   ->  assets/cards/*.svg

Each card is its own SVG so the README can wrap it in a link; pairs are
shown at 49% width so they stay side by side on phones too.
"""
import datetime as dt
import re

from terminal import (ACCENT, AMBER, BLUE, CFG, DIM, FG, FONT, GREEN, LINE, RED, TILE, VIOLET, BG, chip, esc,
                      load, pulse, save)

CW, CH = 420, 126
TAG_COLORS = {"trading": RED, "platform": ACCENT, "design": VIOLET, "real-estate": AMBER, "health": GREEN,
              "community": BLUE, "fashion": VIOLET, "showcase": AMBER}
LANG_COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
               "CSS": "#563d7c", "Jupyter Notebook": "#DA5B0B"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def frame(body, accent, delay=0.0, h=CH):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{h}" viewBox="0 0 {CW} {h}">
<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
<stop offset="0" stop-color="{accent}" stop-opacity=".10"/><stop offset=".6" stop-color="{accent}" stop-opacity="0"/></linearGradient>
<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
<stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect width="{CW}" height="{h}" rx="10"/></clipPath></defs>
<g clip-path="url(#c)" font-family="{FONT}" opacity="0">
<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".5s" fill="freeze"/>
<rect width="{CW}" height="{h}" fill="{BG}"/><rect width="{CW}" height="{h}" fill="url(#g)"/>
<rect x="-200" width="160" height="{h}" fill="url(#sweep)" transform="skewX(-20)">
<animate attributeName="x" values="-200;{CW + 200};{CW + 200}" keyTimes="0;.3;1" dur="7s" begin="{delay + 1:.2f}s" repeatCount="indefinite"/></rect>
<rect width="4" height="{h}" fill="{accent}"/>
{body}
</g>
<rect x=".5" y=".5" width="{CW - 1}" height="{h - 1}" rx="10" fill="none" stroke="{LINE}"/>
</svg>
"""


def project_card(i, name, desc, url, tag):
    col = TAG_COLORS.get(tag, ACCENT)
    domain = url.replace("https://", "")
    if len(domain) > 46:
        domain = domain[:43] + "…"
    c, _ = chip(CW - 18 - (len(tag) * 9 * .6 + 12), 52, tag, col)
    body = (f'<text x="22" y="34" font-size="15" font-weight="bold" fill="{FG}">{esc(name)}</text>'
            f'<g transform="translate({CW - 72} 22)">{pulse(6, 7, 3, GREEN)}'
            f'<text x="16" y="11" font-size="10" fill="{GREEN}" font-weight="bold">live</text></g>'
            f'<text x="22" y="58" font-size="11" fill="{DIM}">{esc(desc)}</text>'
            f'{c}'
            f'<line x1="22" y1="84" x2="{CW - 18}" y2="84" stroke="{LINE}" stroke-dasharray="2 4"/>'
            f'<text x="22" y="106" font-size="10.5" fill="{BLUE}">{esc(domain)}</text>'
            f'<text x="{CW - 18}" y="106" font-size="12" fill="{BLUE}" text-anchor="end">↗</text>')
    return frame(body, col, delay=0.1 * (i % 2))


def ago(iso):
    if not iso:
        return None
    d = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    return "today" if d == 0 else f"{d}d ago" if d < 60 else f"{d // 30}mo ago"


def repo_card(i, name, fallback, meta):
    desc = (meta or {}).get("description") or fallback
    words, lines = desc.split(), [""]
    for w in words:
        if len(lines[-1]) + len(w) + 1 > 52:
            lines.append("")
        lines[-1] = (lines[-1] + " " + w).strip()
    lines = lines[:2]
    col = RED if "RED" in name.upper() else BLUE
    body = [f'<text x="22" y="30" font-size="9.5" fill="{DIM}">TUSHARXP-10 /</text>',
            f'<text x="22" y="48" font-size="15" font-weight="bold" fill="{FG}">{esc(name)}</text>']
    body += [f'<text x="22" y="{70 + j * 15}" font-size="10.5" fill="{DIM}">{esc(t)}</text>' for j, t in enumerate(lines)]
    x, y = 22, 112
    if meta:
        lang = meta.get("language")
        if lang:
            body.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{LANG_COLORS.get(lang, ACCENT)}"/>'
                        f'<text x="{x + 15}" y="{y}" font-size="10" fill="{FG}">{esc(lang)}</text>')
            x += 22 + len(lang) * 6
        for icon, key in (("★", "stargazers_count"), ("⑂", "forks_count")):
            v = meta.get(key)
            if v is not None:
                body.append(f'<text x="{x}" y="{y}" font-size="10" fill="{DIM}">{icon} <tspan fill="{FG}">{v}</tspan></text>')
                x += 22 + len(str(v)) * 6 + 12
        when = ago(meta.get("pushed_at"))
        if when:
            body.append(f'<text x="{CW - 18}" y="{y}" font-size="10" fill="{DIM}" text-anchor="end">pushed {when}</text>')
    else:
        body.append(f'<text x="{x}" y="{y}" font-size="10" fill="{DIM}">view repository ↗</text>')
    return frame("".join(body), col, delay=0.1 * i, h=130)


def link_button(i, label, url):
    w, h = 200, 46
    icon = {"portfolio": "◉", "linkedin": "in", "email": "@", "github": "</>"}.get(label, "→")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<g font-family="{FONT}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{i * .12:.2f}s" dur=".4s" fill="freeze"/>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{TILE}" stroke="{LINE}"/>
<rect x=".5" y="{h - 4}" width="{w - 1}" height="3.5" rx="1.5" fill="{ACCENT}" opacity=".5"/>
<text x="20" y="28" font-size="12" font-weight="bold" fill="{ACCENT}">{esc(icon)}</text>
<text x="52" y="28" font-size="12.5" fill="{FG}">{esc(label)}</text>
<text x="{w - 18}" y="28" font-size="12" fill="{DIM}" text-anchor="end">↗</text>
</g></svg>
"""


def main():
    for i, (name, desc, url, tag) in enumerate(CFG["projects"]):
        save(f"cards/project-{slug(name)}.svg", project_card(i, name, desc, url, tag))
    gh = load("github.json", {}) or {}
    for i, (name, desc) in enumerate(CFG["repos"]):
        save(f"cards/repo-{slug(name)}.svg", repo_card(i, name, desc, gh.get("repos", {}).get(name)))
    for i, (label, url) in enumerate(CFG["links"]):
        save(f"cards/link-{slug(label)}.svg", link_button(i, label, url))


if __name__ == "__main__":
    main()
