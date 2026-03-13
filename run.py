#!/usr/bin/env python3
"""Main pipeline entry point. Usage: uv run python run.py [--pilot] [--github] [--fetch-corpus] [--fetch-github]"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from developing_the_researcher.config import (
    MACSS_PATH,
    MACSS_ONLY_PATH,
    DIAGNOSTICIAN_VALIDATION_PATH,
    DOCS_VALIDATION_OUTPUTS,
    GITHUB_ISSUES_PATH,
)
from developing_the_researcher.data import CorpusLoader, GitHubIssuesLoader
from developing_the_researcher.pipeline import run_pilot
from developing_the_researcher.pipeline.github_validation import run_github_validation


def main() -> None:
    parser = argparse.ArgumentParser(description="It's the Student, Not the Thesis: main pipeline")
    parser.add_argument("--pilot", action="store_true", default=True, help="Run experiment (default)")
    parser.add_argument("--no-pilot", action="store_false", dest="pilot", help="Skip experiment")
    parser.add_argument("--github", action="store_true", help="Run GitHub longitudinal validation")
    parser.add_argument("--fetch-corpus", action="store_true", help="Fetch MACSS via OAI-PMH before running")
    parser.add_argument("--fetch-github", action="store_true", help="Fetch GitHub issues before validation")
    parser.add_argument("--n-per-condition", type=int, default=2, help="Doubles per condition (default 2)")
    parser.add_argument("--full", action="store_true", help="Full experiment (3 conditions × 3 students × 5 theses)")
    parser.add_argument("--max-records", type=int, default=50, help="Max theses to fetch via OAI-PMH (default 50); use 0 for all")
    parser.add_argument("--enrich", action="store_true", help="Enrich corpus by fetching record pages for keywords, record_appears_in, degree_type")
    parser.add_argument("--figures", action="store_true", help="Generate corpus figures (Warm Research palette) and save to figures/")
    parser.add_argument("--export-macss", action="store_true", help="Write MACSS-only theses to macss_theses_only.json (by record_appears_in / is_macss)")
    parser.add_argument("--diagnostician-validation", action="store_true", help="Run 6-dim diagnostician on 10 cluster-sampled theses with 3 models; save radar charts to docs/validation_outputs")
    parser.add_argument("--committee-assembly-demo", action="store_true", help="Plot committee assembly for 2–3 cluster-sampled theses; save to docs/validation_outputs/committee_assembly_demo.png")
    parser.add_argument("--side-by-side", action="store_true", help="Run C1 vs C3 feedback comparison for 2–3 theses; save side-by-side and deliberation figures")
    parser.add_argument("--development-plan-example", action="store_true", help="Generate development plan example figure for 1 thesis")
    parser.add_argument("--full-experiment", action="store_true", help="Run full experiment (3×3×5) and save bar charts")
    args = parser.parse_args()

    if args.fetch_corpus:
        print("Fetching thesis corpus via OAI-PMH...")
        corpus = CorpusLoader()
        corpus.fetch_via_harvest(max_records=args.max_records)
        corpus.save_abstracts_for_steering()
        print("Corpus saved to", MACSS_PATH)

    if args.enrich:
        print("Enriching corpus (fetching record pages for Details)...")
        from developing_the_researcher.data.scraper import enrich_corpus_from_file
        enrich_corpus_from_file()
        corpus = CorpusLoader()
        corpus.export_macss_only()
        print("Enrichment complete. MACSS-only corpus written to", MACSS_ONLY_PATH)

    if args.export_macss:
        print("Exporting MACSS-only theses...")
        corpus = CorpusLoader()
        corpus.export_macss_only()
        print("MACSS-only corpus written to", MACSS_ONLY_PATH)

    if args.figures:
        print("Generating corpus figures...")
        from developing_the_researcher.analysis import generate_corpus_figures
        paths = generate_corpus_figures()
        print(f"Saved {len(paths)} figures to figures/")

    if args.diagnostician_validation:
        print("Running diagnostician validation (10 theses, 3 models)...")
        from developing_the_researcher.analysis.diagnostician_validation import run_validation
        results = run_validation(
            n_theses=10,
            out_json_path=DIAGNOSTICIAN_VALIDATION_PATH,
            out_figures_dir=DOCS_VALIDATION_OUTPUTS,
        )
        print(f"Validation complete. {len(results)} results saved to {DIAGNOSTICIAN_VALIDATION_PATH}")
        print(f"Radar charts saved to {DOCS_VALIDATION_OUTPUTS}")

    if args.committee_assembly_demo:
        print("Generating committee assembly demo figure...")
        from developing_the_researcher.analysis.committee_assembly_figure import plot_committee_assembly_demo
        from developing_the_researcher.analysis.diagnostician_validation import sample_theses_by_cluster
        from developing_the_researcher.models import CommitteeLoader, EmbeddingLoader
        corpus = CorpusLoader()
        theses = corpus.load()
        embed_loader = EmbeddingLoader()
        sampled = sample_theses_by_cluster(theses, embed_loader, n_total=3, n_clusters=6)
        committee = CommitteeLoader()
        out = plot_committee_assembly_demo(sampled, committee)
        print(f"Saved to {out}")

    if args.side_by_side:
        print("Running side-by-side feedback comparison (C1 vs C3)...")
        from developing_the_researcher.analysis.feedback_comparison import run_side_by_side_comparison
        from developing_the_researcher.analysis.diagnostician_validation import sample_theses_by_cluster
        from developing_the_researcher.models import CommitteeLoader, EmbeddingLoader
        corpus = CorpusLoader()
        theses = corpus.load()
        embed_loader = EmbeddingLoader()
        sampled = sample_theses_by_cluster(theses, embed_loader, n_total=3, n_clusters=6)
        committee = CommitteeLoader()
        paths = run_side_by_side_comparison(sampled, committee, embed_loader, DOCS_VALIDATION_OUTPUTS)
        print(f"Saved {len(paths)} figures to {DOCS_VALIDATION_OUTPUTS}")

    if args.fetch_github:
        print("Fetching GitHub issues...")
        gh = GitHubIssuesLoader()
        corpus = gh.load_github_corpus(force_refresh=True)
        print(f"Fetched {len(corpus)} memo comments to", GITHUB_ISSUES_PATH)
        gh.close()

    if args.development_plan_example:
        print("Generating development plan example figure...")
        from developing_the_researcher.analysis.development_plan_figure import plot_development_plan_example
        from developing_the_researcher.analysis.diagnostician_validation import sample_theses_by_cluster
        from developing_the_researcher.models import CommitteeLoader, EmbeddingLoader
        from developing_the_researcher.models.development_plan import development_plan
        from developing_the_researcher.models.diagnostician import diagnose_competencies
        corpus = CorpusLoader()
        theses = corpus.load()
        embed_loader = EmbeddingLoader()
        sampled = sample_theses_by_cluster(theses, embed_loader, n_total=1, n_clusters=6)
        if sampled:
            t = sampled[0]
            text = f"{(t.get('title') or '')}. {(t.get('abstract') or '')}"[:800]
            committee = CommitteeLoader()
            def _gen(p, s, m): return committee.generate(p, s, m)
            profile = diagnose_competencies(text, _gen)
            agents = committee.assemble_committee(profile)
            consolidated = committee.committee_deliberation(text, agents)
            plan = development_plan(profile, consolidated, _gen)
            out = plot_development_plan_example(plan, t.get("title", "Example"), DOCS_VALIDATION_OUTPUTS / "development_plan_example.png")
            print(f"Saved to {out}")

    if args.full_experiment:
        print("Running full experiment (3×3×5)...")
        results = run_pilot(n_per_condition=5, save_figures=True, full_experiment=True)
        print(f"Full experiment complete. {len(results)} results saved. Figures in {DOCS_VALIDATION_OUTPUTS}")

    if args.pilot and not args.full_experiment:
        print("Running pilot experiment...")
        results = run_pilot(n_per_condition=args.n_per_condition, save_figures=True)
        print(f"Pilot complete. {len(results)} results saved.")

    if args.github:
        print("Running GitHub validation...")
        run_github_validation()
        print("GitHub validation complete.")


if __name__ == "__main__":
    main()
