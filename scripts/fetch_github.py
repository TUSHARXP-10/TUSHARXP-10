"""Fetch public profile data: counts, featured repos, languages, recent activity.

  python scripts/fetch_github.py   ->  data/github.json

Uses the REST API; GITHUB_TOKEN (set automatically in Actions) raises the rate
limit but isn't required. Anything that fails keeps its last good value.
"""
import datetime as dt
import json
import os
import re
from collections import Counter

import requests

from kit import CFG, DATA

API = "https://api.github.com"
USER = CFG["github_user"]
# never show the profile's own bookkeeping as "activity"
SKIP_REPOS = {r.lower() for r in CFG.get("activity_skip", [])} | {USER.lower()}


def get(s, path, params=None):
    try:
        r = s.get(f"{API}{path}", params=params, timeout=30)
        if r.ok:
            return r.json()
        print(f"warning: {path} -> HTTP {r.status_code}")
    except (requests.RequestException, ValueError) as e:
        print(f"warning: {path} -> {e}")
    return None


def all_repos(s):
    repos, page = [], 1
    while page <= 10:
        batch = get(s, f"/users/{USER}/repos", {"per_page": 100, "page": page, "type": "owner", "sort": "pushed"})
        if not batch:
            break
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    return repos


def one_line(msg, cap=80):
    msg = re.sub(r"\s+", " ", (msg or "").split("\n")[0]).strip()
    return msg if len(msg) <= cap else msg[:cap - 1] + "…"


def activity(events):
    """Turn raw public events into short, recruiter-readable lines."""
    out = []
    for e in events or []:
        repo_full = (e.get("repo") or {}).get("name", "")
        owner, _, name = repo_full.partition("/")
        if name.lower() in SKIP_REPOS:
            continue
        repo = name if owner.lower() == USER.lower() else repo_full
        p = e.get("payload") or {}
        t = e.get("type")
        if t == "PushEvent":
            commits = p.get("commits") or []
            msg = one_line(commits[-1].get("message")) if commits else ""
            branch = (p.get("ref") or "").replace("refs/heads/", "")
            count = p.get("size") or len(commits)
            verb = f"pushed {count} commit{'s' if count != 1 else ''}" if count else "pushed"
            item = ("push", verb + (f" to {branch}" if branch and not msg else ""), msg)
        elif t == "CreateEvent" and p.get("ref_type") == "repository":
            item = ("create", "created repository", one_line(p.get("description") or ""))
        elif t == "PullRequestEvent" and p.get("action") in ("opened", "closed"):
            pr = p.get("pull_request") or {}
            merged = p.get("action") == "closed" and pr.get("merged")
            if p.get("action") == "closed" and not merged:
                continue
            item = ("pr", f"{'merged' if merged else 'opened'} PR #{pr.get('number', '')}", one_line(pr.get("title")))
        elif t == "ReleaseEvent":
            rel = p.get("release") or {}
            item = ("release", f"released {rel.get('tag_name', '')}".strip(), one_line(rel.get("name") or ""))
        elif t == "PublicEvent":
            item = ("public", "open-sourced", "")
        else:
            continue
        row = {"date": (e.get("created_at") or "")[:10], "kind": item[0], "repo": repo,
               "verb": item[1], "text": item[2]}
        # collapse runs of the same thing on the same repo
        if out and out[-1]["repo"] == row["repo"] and out[-1]["kind"] == row["kind"]:
            continue
        out.append(row)
        if len(out) >= 8:
            break
    return out


def main():
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json", "User-Agent": "profile-art-bot"})
    if os.environ.get("GITHUB_TOKEN"):
        s.headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"

    out = {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "repos": {}}
    u = get(s, f"/users/{USER}")
    if u:
        out["public_repos"] = u.get("public_repos")
        out["followers"] = u.get("followers")
        out["created_at"] = u.get("created_at")

    repos = all_repos(s)
    if repos:
        own = [r for r in repos if not r.get("fork")]
        out["repo_count"] = len(own)
        out["stars"] = sum(r.get("stargazers_count", 0) for r in own)
        out["languages"] = dict(Counter(r["language"] for r in own if r.get("language")).most_common())
        by_name = {r["name"].lower(): r for r in repos}
    else:
        by_name = {}

    for name, _ in CFG["repos"]:
        r = by_name.get(name.lower()) or get(s, f"/repos/{USER}/{name}")
        if r:
            out["repos"][name] = {k: r.get(k) for k in (
                "description", "language", "stargazers_count", "forks_count", "pushed_at", "topics", "html_url")}

    events = get(s, f"/users/{USER}/events/public", {"per_page": 100})
    if events is not None:
        out["activity"] = activity(events)

    # keep the last good values for anything that failed this time
    path = DATA / "github.json"
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        for k, v in old.items():
            if k == "repos":
                for rk, rv in v.items():
                    out["repos"].setdefault(rk, rv)
            else:
                out.setdefault(k, v)
    DATA.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {path.name}: {len(out.get('languages', {}))} languages, "
          f"{len(out.get('activity', []))} activity rows, {len(out['repos'])} featured repos")


if __name__ == "__main__":
    main()
