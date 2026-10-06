"""Recent public activity as a `git log --graph` (live from GitHub events).

Pushes, new repos, merged PRs and releases from the last ~90 days, newest
first, with a commit graph down the left. Dates are absolute because the
card only refreshes daily.
"""
from kit import (ACCENT, AMBER, BLUE, CYAN, DIM, FG, FAINT, GREEN, LINE, MODES, VIOLET, esc, fade, fit, load, md,
                 pulse, save, text, window)

KIND = {"push": GREEN, "create": BLUE, "pr": VIOLET, "release": AMBER, "public": CYAN}


def build(m):
    gh = load("github.json", {}) or {}
    rows = (gh.get("activity") or [])[:6]
    bar, mob, W = m.bar, m.mobile, m.W
    px = 20 if mob else 24
    out = [text(px, bar + (36 if mob else 30), "$ git log --all --graph --since=90.days", 13 if mob else 11, DIM)]
    if not rows:
        y = bar + (70 if mob else 58)
        out.append(pulse(px + 5, y - 4, 3.5, ACCENT) + text(px + 18, y, "syncing recent activity from GitHub…", 14 if mob else 11, DIM))
        return window(m, "snapshot ~ git log", "".join(out), int(y + 30), w=W)

    gx = px + 8
    if not mob:
        rh, y0, fs = 30, bar + 62, 11.5
    else:
        rh, y0, fs = 58, bar + 76, 15
    y_last = y0 + (len(rows) - 1) * rh
    out.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y_last}" stroke="{LINE}" stroke-width="2">'
               f'<animate attributeName="y2" from="{y0}" to="{y_last}" begin=".3s" dur="{0.15 * len(rows):.2f}s" fill="freeze"/></line>')
    for i, r in enumerate(rows):
        y = y0 + i * rh
        col = KIND.get(r.get("kind"), DIM)
        dot = (pulse(gx, y - 4, 4.5, col) if i == 0 else
               f'<circle cx="{gx}" cy="{y - 4}" r="4.5" fill="{col}" stroke="#0d1117" stroke-width="2"/>')
        msg = r.get("text") or ""
        if not mob:
            date_x, repo_x = gx + 18, gx + 18 + 8 * fs * 0.6
            repo = r.get("repo", "")
            verb_x = repo_x + (len(repo) + 2) * fs * 0.6
            tail = r.get("verb", "") + (f" — {msg}" if msg else "")
            room = W - px - verb_x
            line = (text(date_x, y, md(r.get("date")), fs, FAINT)
                    + text(repo_x, y, repo, fs, FG, "bold")
                    + f'<text x="{verb_x:.1f}" y="{y}" font-size="{fs}" fill="{col}">{esc(fit(r.get("verb", ""), room, fs))}'
                    + (f'<tspan fill="{DIM}">{esc(fit(" — " + msg, max(room - len(r.get("verb", "")) * fs * 0.6, 0), fs))}</tspan>'
                       if msg and room > len(r.get("verb", "")) * fs * 0.6 + 40 else "")
                    + "</text>")
        else:
            line = (text(gx + 18, y, fit(r.get("repo", ""), W - px - gx - 18 - 70, 16), 16, FG, "bold")
                    + text(W - px, y, md(r.get("date")), 12.5, FAINT, anchor="end")
                    + f'<text x="{gx + 18}" y="{y + 22}" font-size="13.5" fill="{col}">{esc(fit(r.get("verb", ""), W - px - gx - 18, 13.5))}'
                    + (f'<tspan fill="{DIM}">{esc(fit(" — " + msg, max(W - px - gx - 18 - len(r.get("verb", "")) * 8.1, 0), 13.5))}</tspan>'
                       if msg and W - px - gx - 18 - len(r.get("verb", "")) * 8.1 > 60 else "")
                    + "</text>")
        out.append(fade(i, dot + line, step=0.15, start=0.4, dx=-6, dy=0))
    H = int(y_last + (26 if not mob else 48))
    return window(m, "snapshot ~ git log", "".join(out), H, w=W)


def main():
    for m in MODES:
        save(m, "activity.svg", build(m))


if __name__ == "__main__":
    main()
