#!/usr/bin/env python3
"""Test GitHub fetch for one week. Run from final-project/: uv run python scripts/test_github_one_week.py"""
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from developing_the_researcher.config import GITHUB_OWNER, GITHUB_REPO
from developing_the_researcher.data import GitHubIssuesLoader


def main():
    print("=" * 60)
    print("GitHub Memo Fetch Test (one week)")
    print("=" * 60)
    print(f"Repo: {GITHUB_OWNER}/{GITHUB_REPO}")
    print(f"URL: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues")
    print()

    gh = GitHubIssuesLoader()
    issues = gh.fetch_issues(state="all")
    print(f"Found {len(issues)} issues matching 'Week N Memo'")
    for i in issues:
        print(f"  #{i['number']}: {i['title']} (state={i.get('state', '?')})")
    print()

    # Pick one week (e.g. Week 9)
    target_week = 9
    target_issue = next((i for i in issues if "Week 9" in i.get("title", "")), None)
    if not target_issue:
        target_issue = issues[0] if issues else None
    if target_issue:
        m = re.search(r"Week\s+(\d+)", target_issue.get("title", ""), re.I)
        target_week = int(m.group(1)) if m else 0

    if not target_issue:
        print("No issues found.")
        gh.close()
        return

    print(f"Testing Week {target_week} issue #{target_issue['number']}: {target_issue['title']}")
    comments = gh.fetch_comments(target_issue["number"])
    print(f"  Total comments: {len(comments)}")

    # Apply same filters as load_github_corpus
    kept = [c for c in comments if (c.get("body") or "").strip() and len((c.get("body") or "").strip()) >= 50]
    print(f"  kept (body >= 50 chars): {len(kept)}")

    kept_100 = [c for c in kept if len((c.get("body") or "").strip()) >= 100]
    print(f"  kept (body >= 100 chars, for panel): {len(kept_100)}")

    print()
    print("Sample memos (first 3):")
    for i, c in enumerate(kept[:3]):
        body = (c.get("body") or "").strip()
        user = c.get("user", {}) or {}
        print(f"  [{i+1}] {user.get('login', 'unknown')}: {body[:80]}...")
    print()
    print("Sample full memo (first one):")
    if kept:
        print("-" * 40)
        print((kept[0].get("body") or "").strip()[:500])
        print("-" * 40)

    gh.close()
    print("\nDone. If data looks correct, run: uv run python run.py --no-pilot --fetch-github --github-memo-validation")


if __name__ == "__main__":
    main()
