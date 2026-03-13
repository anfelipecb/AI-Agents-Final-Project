"""GitHubIssuesLoader: fetch issues, comments, reactions via httpx + GitHub REST API."""
import json
import os
import re
import time
from pathlib import Path

import httpx

from ..config import GITHUB_API_BASE, GITHUB_ISSUES_PATH, GITHUB_OWNER, GITHUB_REPO, REQUEST_DELAY


class GitHubIssuesLoader:
    """Fetches course repo issues and comments for longitudinal validation."""

    def __init__(self, owner: str = GITHUB_OWNER, repo: str = GITHUB_REPO, cache_path: Path | None = None):
        self.owner = owner
        self.repo = repo
        self.cache_path = cache_path or GITHUB_ISSUES_PATH
        self.token = os.environ.get("GITHUB_TOKEN")
        self._client: httpx.Client | None = None

    def _headers(self) -> dict:
        h = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        """GET with rate-limit handling."""
        if self._client is None:
            self._client = httpx.Client(timeout=30.0, headers=self._headers())
        r = self._client.get(url, params=params or {})
        if r.status_code == 403 and "rate limit" in r.text.lower():
            time.sleep(60)
            return self._get(url, params)
        r.raise_for_status()
        return r.json()

    def fetch_issues(self, state: str = "all") -> list[dict]:
        """Fetch all issues. Filter Week N Memo by title."""
        url = f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}/issues"
        params = {"state": state, "per_page": 100}
        page = 1
        issues: list[dict] = []
        while True:
            params["page"] = page
            data = self._get(url, params)
            if not isinstance(data, list):
                break
            for item in data:
                if "pull_request" in item:
                    continue
                title = item.get("title", "")
                if re.search(r"Week\s+\d+\s+Memo", title, re.I):
                    issues.append(item)
            if len(data) < 100:
                break
            page += 1
            time.sleep(REQUEST_DELAY)
        return issues

    def fetch_comments(self, issue_number: int) -> list[dict]:
        """Fetch all comments for an issue (paginated; GitHub defaults to 30 per page)."""
        url = f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        all_comments: list[dict] = []
        page = 1
        per_page = 100
        while True:
            params = {"per_page": per_page, "page": page}
            data = self._get(url, params)
            if not isinstance(data, list):
                break
            all_comments.extend(data)
            if len(data) < per_page:
                break
            page += 1
            time.sleep(REQUEST_DELAY)
        return all_comments

    def load_github_corpus(self, force_refresh: bool = False) -> list[dict]:
        """Load corpus: issues + comments + reactions. Uses cache if available."""
        if self.cache_path.exists() and not force_refresh:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            return data.get("corpus", [])

        issues = self.fetch_issues()
        corpus: list[dict] = []

        for issue in issues:
            num = issue.get("number")
            title = issue.get("title", "")
            week_match = re.search(r"Week\s+(\d+)", title, re.I)
            week = int(week_match.group(1)) if week_match else 0

            comments = self.fetch_comments(num)
            for c in comments:
                body = c.get("body", "")
                if not body or len(body) < 50:
                    continue
                user = c.get("user", {})
                login = user.get("login", "unknown")
                reactions = c.get("reactions", {})
                thumbs_up = reactions.get("+1", 0)


                corpus.append({
                    "issue_id": num,
                    "week": week,
                    "author": login,
                    "memo_text": body,
                    "created_at": c.get("created_at", ""),
                    "thumbs_up": thumbs_up,
                    "reactions": dict(reactions),
                })

        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps({"corpus": corpus, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=2),
            encoding="utf-8",
        )
        return corpus

    def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
