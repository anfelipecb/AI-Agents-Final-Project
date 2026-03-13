#!/usr/bin/env python3
"""Main pipeline entry point. Usage: uv run python run.py [--pilot] [--github] [--fetch-corpus] [--fetch-github]"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from safe_to_be_challenged.config import MACSS_PATH, GITHUB_ISSUES_PATH
from safe_to_be_challenged.data import CorpusLoader, GitHubIssuesLoader
from safe_to_be_challenged.pipeline import run_pilot
from safe_to_be_challenged.pipeline.github_validation import run_github_validation


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe to Be Challenged: main pipeline")
    parser.add_argument("--pilot", action="store_true", default=True, help="Run experiment (default)")
    parser.add_argument("--no-pilot", action="store_false", dest="pilot", help="Skip experiment")
    parser.add_argument("--github", action="store_true", help="Run GitHub longitudinal validation")
    parser.add_argument("--fetch-corpus", action="store_true", help="Fetch MACSS via OAI-PMH before running")
    parser.add_argument("--fetch-github", action="store_true", help="Fetch GitHub issues before validation")
    parser.add_argument("--n-per-condition", type=int, default=2, help="Doubles per condition (default 2)")
    args = parser.parse_args()

    if args.fetch_corpus and not MACSS_PATH.exists():
        print("Fetching MACSS corpus via OAI-PMH...")
        corpus = CorpusLoader()
        corpus.fetch_via_harvest(max_records=50)
        corpus.save_abstracts_for_steering()
        print("Corpus saved to", MACSS_PATH)

    if args.fetch_github:
        print("Fetching GitHub issues...")
        gh = GitHubIssuesLoader()
        corpus = gh.load_github_corpus(force_refresh=True)
        print(f"Fetched {len(corpus)} memo comments to", GITHUB_ISSUES_PATH)
        gh.close()

    if args.pilot:
        print("Running pilot experiment...")
        results = run_pilot(n_per_condition=args.n_per_condition, save_figures=True)
        print(f"Pilot complete. {len(results)} results saved.")

    if args.github:
        print("Running GitHub validation...")
        run_github_validation()
        print("GitHub validation complete.")


if __name__ == "__main__":
    main()
