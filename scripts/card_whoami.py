"""whoami: ASCII portrait + stats dashboard as one image.

Desktop puts the two panels side by side (415 + 30 + 415 = 860); mobile
stacks them so each stays readable on a phone.
"""
import re

import card_portrait
import card_stats
from kit import MODES, doc, save


def nest(svg, x, y, prefix):
    """Embed a standalone panel SVG at (x, y), namespacing its ids."""
    svg = re.sub(r'id="([^"]+)"', rf'id="{prefix}\1"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}\1)", svg)
    return svg.replace("<svg ", f'<svg x="{x}" y="{y}" ', 1)


def build(m, rows):
    if not m.mobile:
        pw, ph = 415, 480
        left = card_portrait.panel(m, pw, ph, rows)
        right = card_stats.panel(m, pw, ph)
        return doc(860, ph, nest(left, 0, 0, "a-") + nest(right, 860 - pw, 0, "b-"))
    top_h, bottom_h, gap = 552, 624, 16
    top = card_portrait.panel(m, 480, top_h, rows)
    bottom = card_stats.panel(m, 480, bottom_h)
    return doc(480, top_h + gap + bottom_h, nest(top, 0, 0, "a-") + nest(bottom, 0, top_h + gap, "b-"))


def main():
    rows = card_portrait.rows()
    for m in MODES:
        save(m, "whoami.svg", build(m, rows))


if __name__ == "__main__":
    main()
