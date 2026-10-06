"""Rebuild everything: fetch live data, render every card in both layouts,
then regenerate README.md.

  python scripts/build.py            # full run (what the daily workflow does)
  python scripts/build.py --offline  # re-render from the data already in data/
"""
import shutil
import sys

import card_activity
import card_hero
import card_items
import card_langs
import card_sections
import card_skyline
import card_spotlight
import card_stack
import card_tldr
import card_whoami
import make_readme
from kit import ASSETS

CARDS = [card_hero, card_tldr, card_skyline, card_whoami, card_spotlight, card_stack, card_langs, card_activity,
         card_items, card_sections]


def fetch():
    import fetch_contributions
    import fetch_github
    for step in (fetch_contributions.main, fetch_github.main):
        try:
            step()
        except Exception as e:  # keep rendering with the last good data
            print(f"warning: {step.__module__} failed: {e}")


def main():
    if "--offline" not in sys.argv:
        fetch()
    # start clean so cards for removed projects don't linger
    for sub in ("desktop", "mobile"):
        shutil.rmtree(ASSETS / sub, ignore_errors=True)
    for card in CARDS:
        card.main()
    make_readme.main()


if __name__ == "__main__":
    main()
