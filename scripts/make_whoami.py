"""Combine the portrait and stats panels into one 860-wide image.

  python scripts/make_whoami.py   ->  assets/whoami.svg

One image instead of a two-cell table means it scales down cleanly on
phones instead of forcing a horizontal scroll.
"""
import re

from terminal import ASSETS, H, W, save

GAP = 860 - 2 * W


def inner(name, x):
    svg = (ASSETS / name).read_text(encoding="utf-8")
    svg = re.sub(r"^<!--.*?-->\s*", "", svg, flags=re.S)
    # namespace ids so the two panels can't collide
    prefix = name.split(".")[0] + "-"
    svg = re.sub(r'id="([^"]+)"', rf'id="{prefix}\1"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}\1)", svg)
    return svg.replace("<svg ", f'<svg x="{x}" y="0" ', 1)


def main():
    body = inner("portrait.svg", 0) + inner("stats.svg", W + GAP)
    save("whoami.svg", f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{H}" viewBox="0 0 860 {H}">\n'
                       f"{body}</svg>\n")


if __name__ == "__main__":
    main()
