"""Language breakdown across every public, non-fork repo (live from GitHub).

An animated segmented bar (like GitHub's language bar) plus a legend with
share and repo counts. Shows a "syncing" state until the data exists.
"""
from kit import DIM, FAINT, FG, LINE, MODES, TILE, fade, load, n, pulse, save, text, window, ACCENT

COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#663399",
          "Jupyter Notebook": "#DA5B0B", "Java": "#b07219", "C++": "#f34b7d", "C": "#555555", "Go": "#00ADD8",
          "Rust": "#dea584", "Shell": "#89e051", "Dart": "#00B4AB", "Kotlin": "#A97BFF", "Swift": "#F05138",
          "PHP": "#4F5D95", "Ruby": "#701516", "Vue": "#41b883", "SCSS": "#c6538c", "Solidity": "#AA6746",
          "Dockerfile": "#384d54", "Svelte": "#ff3e00", "Astro": "#ff5a03", "MDX": "#fcb32c", "PLpgSQL": "#336790",
          "C#": "#178600", "Lua": "#000080", "R": "#198CE7", "Elixir": "#6e4a7e", "Scala": "#c22d40",
          "Haskell": "#5e5086", "Objective-C": "#438eff", "Batchfile": "#C1F12E", "PowerShell": "#012456"}
OTHER = "#6e7681"


def build(m):
    gh = load("github.json", {}) or {}
    langs = gh.get("languages") or {}
    bar = m.bar
    mob = m.mobile
    W = m.W
    px = 20 if mob else 24
    out = [text(px, bar + (36 if mob else 30), "$ ./langs --across=all-repos", 13 if mob else 11, DIM)]
    if not langs:
        y = bar + (70 if mob else 58)
        out.append(pulse(px + 5, y - 4, 3.5, ACCENT) + text(px + 18, y, "syncing language data from GitHub…", 14 if mob else 11, DIM))
        return window(m, "snapshot ~ ./langs", "".join(out), int(y + 30), w=W)

    total = sum(langs.values())
    items = sorted(langs.items(), key=lambda kv: -kv[1])
    top = items[:8] if len(items) > 9 else items
    rest = sum(v for _, v in items[len(top):])
    if rest:
        top.append(("other", rest))
    repos, stars = gh.get("repo_count") or total, gh.get("stars", 0)

    title_y = bar + (70 if mob else 54)
    out.append(text(px, title_y, f"{len(items)} languages · {repos} repos", 20 if mob else 16, FG, "bold"))
    meta = f"★ {stars} stars · {gh.get('public_repos', repos)} public repos"
    if mob:
        out.append(text(px, title_y + 24, meta, 13, DIM))
        by = title_y + 44
    else:
        out.append(text(W - px, title_y, meta, 11, DIM, anchor="end"))
        by = title_y + 18
    bh = 16 if mob else 12
    bw = W - 2 * px
    out.append(f'<clipPath id="lb"><rect x="{px}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}"/></clipPath>'
               f'<rect x="{px}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="{TILE}" stroke="{LINE}"/>')
    x, t = px, 0.4
    segs = []
    for name, v in top:
        w = bw * v / total
        d = 0.9 * v / total + 0.08
        col = COLORS.get(name, OTHER)
        segs.append(f'<rect x="{x:.1f}" y="{by}" width="0" height="{bh}" fill="{col}">'
                    f'<animate attributeName="width" from="0" to="{max(w - 1.5, .5):.1f}" begin="{t:.2f}s" dur="{d:.2f}s" fill="freeze"/></rect>')
        x += w
        t += d
    out.append(f'<g clip-path="url(#lb)">{"".join(segs)}</g>')

    cols = 2 if mob else 4
    cw = bw / cols
    fs = 14 if mob else 11
    rh = 30 if mob else 24
    ly = by + bh + (36 if mob else 30)
    for i, (name, v) in enumerate(top):
        cx, cy = px + (i % cols) * cw, ly + (i // cols) * rh
        pct = 100 * v / total
        item = (f'<circle cx="{cx + 5:.1f}" cy="{cy - fs * 0.35:.1f}" r="{5 if mob else 4.5}" fill="{COLORS.get(name, OTHER)}"/>'
                + text(cx + 16, cy, name, fs, FG)
                + text(cx + 16 + (len(name) + 1) * fs * 0.6, cy, f"{pct:.0f}%", fs, DIM)
                + text(cx + cw - 12, cy, f"{v}", fs - 1, FAINT, anchor="end"))
        out.append(fade(i, item, step=0.06, start=0.6, dy=4))
    H = int(ly + ((len(top) + cols - 1) // cols - 1) * rh + (26 if mob else 22))
    return window(m, "snapshot ~ ./langs", "".join(out), H, w=W)


def main():
    for m in MODES:
        save(m, "langs.svg", build(m))


if __name__ == "__main__":
    main()
