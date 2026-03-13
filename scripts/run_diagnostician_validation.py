#!/usr/bin/env python3
"""Run diagnostician validation: sample 10 theses by cluster, run 3 models, save JSON and radar charts."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from developing_the_researcher.analysis.diagnostician_validation import run_validation
from developing_the_researcher.config import DIAGNOSTICIAN_VALIDATION_PATH, DOCS_VALIDATION_OUTPUTS


def main() -> None:
    print("Diagnostician validation: sampling 10 theses by cluster, running 3 models...")
    results = run_validation(
        n_theses=10,
        out_json_path=DIAGNOSTICIAN_VALIDATION_PATH,
        out_figures_dir=DOCS_VALIDATION_OUTPUTS,
    )
    print(f"Done. {len(results)} results saved to {DIAGNOSTICIAN_VALIDATION_PATH}")
    print(f"Figures saved to {DOCS_VALIDATION_OUTPUTS}")


if __name__ == "__main__":
    main()
