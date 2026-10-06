"""`tree ~/stack`: the tech stack as an animated directory tree.

Four folders side by side on desktop, a 2x2 grid on mobile.
"""
from kit import ACCENT, AMBER, BLUE, CFG, DIM, FG, FAINT, MODES, RED, VIOLET, esc, save, text, window

COLORS = [RED, ACCENT, BLUE, AMBER, VIOLET]


def column(x, y, folder, items, color, fs_dir, fs_item, lh, t0):
    out, lines = [], [(f"{folder}/", True)] + [(("└── " if i == len(items) - 1 else "├── ") + it, False)
                                               for i, it in enumerate(items)]
    for j, (label, is_dir) in enumerate(lines):
        b = f"{t0 + j * 0.09:.2f}s"
        if is_dir:
            sq = fs_dir * 0.62
            inner = (f'<rect x="{x}" y="{y - sq - fs_dir * 0.12:.1f}" width="{sq:.1f}" height="{sq:.1f}" rx="2" fill="{color}"/>'
                     + text(x + sq + 6, y, label, fs_dir, color, "bold"))
        else:
            inner = (f'<text x="{x}" y="{y}" font-size="{fs_item}" xml:space="preserve"><tspan fill="{FAINT}">{label[:4]}</tspan>'
                     f'<tspan fill="{FG}">{esc(label[4:])}</tspan></text>')
        out.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{b}" dur=".3s" fill="freeze"/>{inner}</g>')
        y += lh
    return "".join(out), y


def build(m):
    groups = CFG["stack"]
    bar = m.bar
    files = sum(len(i) for _, i in groups)
    if not m.mobile:
        W, fs_dir, fs_item, lh = 860, 12, 11, 19
        top = bar + 30
        out = [text(24, top, "$ tree ~/stack", 11, DIM), text(24, top + 22, "~/stack", 12, FG, "bold")]
        cw = (W - 48) / len(groups)
        bottom = 0
        for g, (folder, items) in enumerate(groups):
            col, end = column(24 + g * cw, top + 50, folder, items, COLORS[g % len(COLORS)], fs_dir, fs_item, lh,
                              0.3 + g * 0.05)
            out.append(col)
            bottom = max(bottom, end)
        sy = bottom + 10
        H = int(bottom + 34)
        summary_fs = 10
    else:
        W, fs_dir, fs_item, lh = 480, 16, 14, 24
        top = bar + 36
        out = [text(20, top, "$ tree ~/stack", 13, DIM), text(20, top + 28, "~/stack", 16, FG, "bold")]
        cw = (W - 40) / 2
        y = top + 66
        for r in range(0, len(groups), 2):
            row_end = y
            for c, (folder, items) in enumerate(groups[r:r + 2]):
                g = r + c
                col, end = column(20 + c * cw, y, folder, items, COLORS[g % len(COLORS)], fs_dir, fs_item, lh,
                                  0.3 + g * 0.08)
                out.append(col)
                row_end = max(row_end, end)
            y = row_end + 18
        sy = y - 4
        H = int(y + 22)
        summary_fs = 13
    out.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="1.2s"/>'
               + text(24 if not m.mobile else 20, sy, f"{len(groups)} directories, {files} files", summary_fs, DIM) + "</g>")
    return window(m, "snapshot ~ tree ~/stack", "\n".join(out), H, w=W)


def main():
    for m in MODES:
        save(m, "stack.svg", build(m))


if __name__ == "__main__":
    main()
