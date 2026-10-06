"""Regenerate every card. Network steps are skipped with --offline.

  python scripts/build.py [--offline]
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NETWORK = ["fetch_contributions.py", "fetch_github.py"]
RENDER = ["render_heatmap_svg.py", "render_stats_svg.py", "make_ascii_svg.py --auto", "make_whoami.py",
          "make_hero.py", "make_tldr.py", "make_spotlight.py", "make_stack.py", "make_cards.py", "make_footer.py"]


def run(cmd):
    script, *args = cmd.split()
    print(f"→ {cmd}")
    return subprocess.run([sys.executable, str(HERE / script), *args]).returncode


def main():
    failed = []
    if "--offline" not in sys.argv:
        failed += [c for c in NETWORK if run(c)]  # keep the last good data if a fetch fails
    for c in RENDER:
        if run(c):
            sys.exit(f"render step failed: {c}")
    if failed:
        print(f"warning: fetch failed ({', '.join(failed)}); rendered with the previous data")


if __name__ == "__main__":
    main()
