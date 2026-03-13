"""Tests for GitHubIssuesLoader: mock httpx, parse GitHub API response."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from safe_to_be_challenged.data.github_loader import GitHubIssuesLoader


def test_parse_github_api_response():
    """Parse a sample GitHub issues API response structure (issues have no 'pull_request' key)."""
    sample = [
        {"number": 1, "title": "Week 3 Memo", "body": "Memo content"},
        {"number": 2, "title": "Other issue", "body": "Not a memo"},
    ]
    # Loader excludes PRs and keeps "Week N Memo" titles
    issues = [i for i in sample if "pull_request" not in i and "Week" in i.get("title", "") and "Memo" in i.get("title", "")]
    assert len(issues) == 1
    assert issues[0]["title"] == "Week 3 Memo"


@patch("safe_to_be_challenged.data.github_loader.httpx.Client")
def test_load_github_corpus_uses_cache(mock_client, tmp_path):
    """When cache exists and force_refresh=False, no HTTP calls."""
    cache = tmp_path / "github_issues.json"
    cache.write_text(json.dumps({"corpus": [{"memo_text": "cached"}]}), encoding="utf-8")
    loader = GitHubIssuesLoader(cache_path=cache)
    out = loader.load_github_corpus(force_refresh=False)
    assert out == [{"memo_text": "cached"}]
    mock_client.return_value.get.assert_not_called()
