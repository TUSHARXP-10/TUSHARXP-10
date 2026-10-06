"""Clickable item cards: live deployments, featured repos, contact buttons.

Each item is its own SVG so the README can wrap it in a link. Desktop cards
are 412 wide (two per row); mobile cards are 480 wide with larger type and
GitHub scales them to the phone's width.
"""
import re

from kit import (ACCENT, AMBER, BG, BLUE, CFG, DIM, FG, FONT, GREEN, LINE, MODES, RED, TILE, VIOLET, chip, doc, esc,
                 fit, load, md, n, pulse, save, text, wrap)

TAG_COLORS = {"trading": RED, "platform": ACCENT, "design": VIOLET, "real-estate": AMBER, "health": GREEN,
              "community": BLUE, "fashion": VIOLET, "showcase": AMBER}
LANG_COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
               "CSS": "#663399", "Jupyter Notebook": "#DA5B0B"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def initials(name):
    parts = [p for p in re.split(r"[-_ .]+", name) if p]
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else parts[0][1:2])).upper()


def frame(w, h, body, accent, delay=0.0):
    defs = (f'<linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{accent}" stop-opacity=".11"/>'
            f'<stop offset=".6" stop-color="{accent}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="c"><rect width="{w}" height="{h}" rx="10"/></clipPath>')
    inner = (f'<g clip-path="url(#c)" font-family="{FONT}" opacity="0">'
             f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".5s" fill="freeze"/>'
             f'<rect width="{w}" height="{h}" fill="{BG}"/><rect width="{w}" height="{h}" fill="url(#g)"/>'
             f'<rect x="-200" width="160" height="{h}" fill="url(#sweep)" transform="skewX(-20)">'
             f'<animate attributeName="x" values="-200;{w + 200};{w + 200}" keyTimes="0;.3;1" dur="7s" begin="{delay + 1:.2f}s" repeatCount="indefinite"/></rect>'
             f'<rect width="4" height="{h}" fill="{accent}"/>{body}</g>'
             f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" stroke="{LINE}"/>')
    return doc(w, h, inner, defs)


def monogram(x, y, size, label, color):
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * 0.24:.1f}" fill="{color}" fill-opacity=".14" '
            f'stroke="{color}" stroke-opacity=".5"/>'
            + text(x + size / 2, y + size / 2 + size * 0.13, label, round(size * 0.36, 1), color, "bold", anchor="middle"))


def project(m, i, name, desc, url, tag):
    col = TAG_COLORS.get(tag, ACCENT)
    domain = url.replace("https://", "")
    if not m.mobile:
        W, H, k = 412, 128, 1.0
        mono, nx = 44, 78
    else:
        W, H, k = 480, 156, 1.32
        mono, nx = 58, 94
    nfs, dfs, bfs = round(15 * k, 1), round(11 * k, 1), round(10.5 * k, 1)
    tag_svg, tag_w = chip(0, 0, tag, col, round(9 * k, 1))
    room = W - nx - 18 - tag_w - 10
    sep = 84 * (1 if not m.mobile else 1.2)
    by = H - 20 * (1 if not m.mobile else 1.15)
    body = (monogram(20, 20, mono, initials(name), col)
            + text(nx, 20 + mono * 0.42, fit(name, room, nfs), nfs, FG, "bold")
            + "".join(text(nx, 20 + mono * 0.42 + dfs * (1.75 + 1.3 * j), t, dfs, DIM)
                      for j, t in enumerate(wrap(desc, W - nx - 18, dfs, 2 if m.mobile else 1)))
            + f'<g transform="translate({W - 18 - tag_w:.1f} 18)">{tag_svg}</g>'
            + f'<line x1="20" y1="{sep:.1f}" x2="{W - 18}" y2="{sep:.1f}" stroke="{LINE}" stroke-dasharray="2 4"/>'
            + pulse(26, by - bfs * 0.35, 3 * k, GREEN)
            + text(36 * (1 if not m.mobile else 1.08), by, "live", bfs, GREEN, "bold")
            + text(76 * (1 if not m.mobile else 1.08), by, fit(domain, W - 76 * k - 70, bfs), bfs, BLUE)
            + text(W - 18, by, "open ↗", bfs, BLUE, anchor="end"))
    return frame(W, H, body, col, delay=0.1 * (i % 2))


def repo(m, i, name, fallback, meta):
    meta = meta or {}
    col = RED if "RED" in name.upper() else BLUE
    if not m.mobile:
        W, H, k = 412, 136, 1.0
    else:
        W, H, k = 480, 172, 1.32
    lines = wrap(meta.get("description") or fallback, W - 40, round(10.5 * k, 1), 2)
    fs = round(10.5 * k, 1)
    body = [text(22, 30 * k, f"{CFG['github_user']} /", round(9.5 * k, 1), DIM),
            text(22, 48 * k, fit(name, W - 44, round(15 * k, 1)), round(15 * k, 1), FG, "bold")]
    body += [text(22, (70 + j * 15) * k, t, fs, DIM) for j, t in enumerate(lines)]
    x, y = 22, H - 18 * k
    lang = meta.get("language")
    if lang:
        body.append(f'<circle cx="{x + 5 * k:.1f}" cy="{y - 4 * k:.1f}" r="{5 * k:.1f}" fill="{LANG_COLORS.get(lang, ACCENT)}"/>'
                    + text(x + 15 * k, y, lang, round(10 * k, 1), FG))
        x += 15 * k + (len(lang) + 2) * 10 * k * 0.6
    for icon, key in (("★", "stargazers_count"), ("⑂", "forks_count")):
        v = meta.get(key)
        if v is not None:
            body.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{round(10 * k, 1)}" fill="{DIM}">{icon} <tspan fill="{FG}">{v}</tspan></text>')
            x += (len(str(v)) + 4) * 10 * k * 0.6
    if meta.get("pushed_at"):
        body.append(text(W - 18, y, f"pushed {md(meta['pushed_at'])}", round(10 * k, 1), DIM, anchor="end"))
    elif not lang:
        body.append(text(x, y, "view repository ↗", round(10 * k, 1), DIM))
    return frame(W, H, "".join(body), col, delay=0.1 * i)


GLYPH = {"portfolio": "◉", "linkedin": "in", "email": "@", "github": "</>"}


def button(m, i, label):
    if not m.mobile:
        W, H, fs, gx, lx = 200, 52, 13, 18, 52
    else:
        W, H, fs, gx, lx = 150, 64, 14, 12, 40
    inner = (f'<g font-family="{FONT}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{i * .12:.2f}s" dur=".4s" fill="freeze"/>'
             f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9" fill="{TILE}" stroke="{LINE}"/>'
             f'<rect x="1" y="{H - 4}" width="{W - 2}" height="3" rx="1.5" fill="{ACCENT}" opacity=".55"/>'
             + text(gx, H / 2 + fs * 0.38, GLYPH.get(label, "→"), fs, ACCENT, "bold")
             + text(lx, H / 2 + fs * 0.38, label, fs, FG)
             + text(W - (10 if m.mobile else 14), H / 2 + fs * 0.38, "↗", fs, DIM, anchor="end") + "</g>")
    return doc(W, H, inner)


def main():
    gh = load("github.json", {}) or {}
    for m in MODES:
        for i, (name, desc, url, tag) in enumerate(CFG["projects"]):
            save(m, f"items/project-{slug(name)}.svg", project(m, i, name, desc, url, tag))
        for i, (name, desc) in enumerate(CFG["repos"]):
            save(m, f"items/repo-{slug(name)}.svg", repo(m, i, name, desc, gh.get("repos", {}).get(name)))
        for i, (label, _) in enumerate(CFG["links"]):
            save(m, f"items/link-{slug(label)}.svg", button(m, i, label))


if __name__ == "__main__":
    main()
