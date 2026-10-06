"""`tree ~/stack`: the tech stack as an animated directory tree.

  python scripts/make_stack.py   ->  assets/stack.svg
"""
from terminal import ACCENT, AMBER, BAR_H, BLUE, CFG, DIM, FG, LINE, RED, VIOLET, esc, save, window

W = 860
COLORS = [RED, ACCENT, BLUE, AMBER, VIOLET]
LH = 19


def build():
    groups = CFG["stack"]
    cols = len(groups)
    cw = (W - 48) / cols
    top = BAR_H + 30
    out = [f'<text x="24" y="{top}" font-size="11" fill="{DIM}">$ tree ~/stack</text>',
           f'<text x="24" y="{top + 22}" font-size="12" fill="{FG}" font-weight="bold">~/stack</text>']
    t, longest = 0.3, 0
    for g, (folder, items) in enumerate(groups):
        x = 24 + g * cw
        y = top + 50
        col = COLORS[g % len(COLORS)]
        lines = [(f"{folder}/", col, True)] + [
            (("└── " if i == len(items) - 1 else "├── ") + it, FG, False) for i, it in enumerate(items)]
        for j, (text, c, is_dir) in enumerate(lines):
            b = f"{t + j * 0.09 + g * 0.05:.2f}s"
            if is_dir:
                body = (f'<rect x="{x}" y="{y - 10}" width="8" height="8" rx="2" fill="{c}"/>'
                        f'<text x="{x + 14}" y="{y - 2}" font-size="12" font-weight="bold" fill="{c}">{esc(text)}</text>')
            else:
                branch, name = text[:4], text[4:]
                body = (f'<text x="{x}" y="{y - 2}" font-size="11" xml:space="preserve"><tspan fill="{LINE}">{branch}</tspan>'
                        f'<tspan fill="{FG}">{esc(name)}</tspan></text>')
            out.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{b}" dur=".3s" fill="freeze"/>{body}</g>')
            y += LH
        longest = max(longest, y)
    files = sum(len(i) for _, i in groups)
    h = int(longest + 34)
    out.append(f'<text x="24" y="{longest + 10}" font-size="10" fill="{DIM}" opacity="0">{cols} directories, {files} files'
               f'<set attributeName="opacity" to="1" begin="{t + 0.09 * 7 + 0.3:.2f}s"/></text>')
    return window("snapshot ~ tree ~/stack", "\n".join(out), w=W, h=h)


def main():
    save("stack.svg", build())


if __name__ == "__main__":
    main()
