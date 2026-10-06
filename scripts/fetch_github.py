"""Fetch public profile numbers and featured-repo metadata.

  python scripts/fetch_github.py   ->  data/github.json

Uses the REST API; GITHUB_TOKEN (set automatically in Actions) raises the
rate limit but isn't required. Anything that fails is simply left out, and
the cards fall back to profile.json text.
"""
import datetime as dt
import json
import os

import requests

from terminal import CFG, DATA, ROOT

API = "https://api.github.com"


def get(session, path):
    try:
        r = session.get(f"{API}{path}", timeout=30)
        if r.ok:
            return r.json()
        print(f"warning: {path} -> HTTP {r.status_code}")
    except requests.RequestException as e:
        print(f"warning: {path} -> {e}")
    return None


def main():
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json", "User-Agent": "profile-art-bot"})
    if os.environ.get("GITHUB_TOKEN"):
        s.headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"

    user = CFG["github_user"]
    out = {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "repos": {}}
    u = get(s, f"/users/{user}")
    if u:
        out["public_repos"] = u.get("public_repos")
        out["followers"] = u.get("followers")
    for name, _ in CFG["repos"]:
        r = get(s, f"/repos/{user}/{name}")
        if r:
            out["repos"][name] = {k: r.get(k) for k in (
                "description", "language", "stargazers_count", "forks_count", "pushed_at", "topics", "html_url")}

    # keep the last good values for anything that failed this time
    path = DATA / "github.json"
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        for k in ("public_repos", "followers"):
            out.setdefault(k, old.get(k))
        for k, v in old.get("repos", {}).items():
            out["repos"].setdefault(k, v)
    DATA.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
