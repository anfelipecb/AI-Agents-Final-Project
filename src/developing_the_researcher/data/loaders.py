"""Pipeline loaders: CorpusLoader, DoublesLoader."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from ..config import ABSTRACTS_PATH, CONDITIONS, FAST_MODE, MACSS_PATH, MACSS_ONLY_PATH, STUDENT_PROFILES
from .corpus import infer_methodology
from .harvest import harvest_theses, run_harvest
from .scraper import run_scrape


def filter_macss(theses: list[dict]) -> list[dict]:
    """Return only theses where record_appears_in indicates MACSS (Computational Social Sciences)."""
    out = []
    for t in theses:
        appears = t.get("record_appears_in") or []
        if isinstance(appears, str):
            appears = [appears]
        combined = " ".join(appears).lower()
        if "computational social sciences" in combined or "macss" in combined:
            out.append(t)
        elif t.get("is_macss") is True:
            out.append(t)
    return out

SAMPLE_ABSTRACTS = [
    {
        "id": "sample_1",
        "url": "",
        "title": "We study Twitter effects on political polarization using network analysis.",
        "abstract": "We study Twitter effects on political polarization using network analysis. Using a large-scale dataset of retweets and replies, we model ideological clustering and echo chambers.",
        "author": "Sample Author",
        "year": 2023,
        "methodology": "computational",
    },
    {
        "id": "sample_2",
        "url": "",
        "title": "This thesis examines algorithmic bias in hiring systems using case studies.",
        "abstract": "This thesis examines algorithmic bias in hiring systems using case studies. We conduct qualitative interviews with HR professionals and analyze resume screening tools.",
        "author": "Sample Author",
        "year": 2024,
        "methodology": "qualitative",
    },
    {
        "id": "sample_3",
        "url": "",
        "title": "Causal inference in survey experiments for policy evaluation.",
        "abstract": "Causal inference in survey experiments for policy evaluation. We use regression discontinuity and instrumental variables to estimate treatment effects.",
        "author": "Sample Author",
        "year": 2022,
        "methodology": "quantitative",
    },
]


class CorpusLoader:
    """Loads MACSS thesis corpus via OAI-PMH harvest or HTML scraper."""

    def __init__(self, path: Path | None = None):
        self.path = path or MACSS_PATH

    def load(self) -> list[dict]:
        """Load corpus from JSON. Returns sample data if file missing/empty. Preserves all fields (keywords, record_appears_in, primary_category, is_macss, etc.)."""
        if not self.path.exists():
            return SAMPLE_ABSTRACTS
        data = json.loads(self.path.read_text(encoding="utf-8"))
        theses = data.get("theses", [])
        if not theses:
            return SAMPLE_ABSTRACTS
        return theses

    def load_macss_only(self) -> list[dict]:
        """Load corpus and return only MACSS theses (record_appears_in contains Computational Social Sciences / MACSS)."""
        return filter_macss(self.load())

    def fetch_via_harvest(self, max_records: int = 50) -> Path:
        """Fetch via OAI-PMH and save. Returns path."""
        return run_harvest(max_records=max_records)

    def fetch_via_scrape(self, max_records: int = 50) -> Path:
        """Fetch via HTML scraper and save. Returns path."""
        return run_scrape(max_records=max_records)

    def save_abstracts_for_steering(self, path: Path | None = None) -> Path:
        """Save abstracts as list for steering (simplified format)."""
        out = path or ABSTRACTS_PATH
        theses = self.load()
        abstracts = [
            {"id": t.get("id", ""), "abstract": t.get("abstract", ""), "methodology": t.get("methodology", "unknown")}
            for t in theses
        ]
        out.write_text(json.dumps(abstracts, indent=2, ensure_ascii=False), encoding="utf-8")
        return out

    def export_macss_only(self, path: Path | None = None) -> Path:
        """Write a separate JSON with only MACSS theses (record_appears_in / is_macss). Same structure as main corpus for embeddings/geometry."""
        out = path or MACSS_ONLY_PATH
        theses = self.load()
        macss_only = filter_macss(theses)
        data = {
            "source": "knowledge.uchicago.edu",
            "subset": "macss_only",
            "collected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "theses": macss_only,
        }
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return out


class DoublesLoader:
    """Builds digital doubles from corpus for the three-condition experiment."""

    def __init__(self, corpus_loader: CorpusLoader | None = None):
        self.corpus = corpus_loader or CorpusLoader()

    def load_doubles_from_corpus(
        self,
        n_per_condition: int = 6,
        stratify_by_methodology: bool = True,
        override_fast_mode: bool = False,
    ) -> list[dict]:
        """Build doubles: thesis, condition, student_profile, weak_dims, methodology."""
        theses = self.corpus.load()
        if FAST_MODE and not override_fast_mode:
            n_per_condition = min(n_per_condition, 2)

        doubles: list[dict] = []
        abstracts = [t.get("abstract", t.get("title", "")) for t in theses if t.get("abstract") or t.get("title")]
        if not abstracts:
            abstracts = [s["abstract"] for s in SAMPLE_ABSTRACTS]
        if not theses:
            theses = SAMPLE_ABSTRACTS

        profile_names = list(STUDENT_PROFILES)
        idx = 0
        for cond in CONDITIONS:
            for _ in range(n_per_condition):
                thesis = abstracts[idx % len(abstracts)]
                student_profile = profile_names[idx % len(profile_names)]
                profile_spec = STUDENT_PROFILES.get(student_profile, {})
                weak_dims = list(profile_spec.get("weak_dims", []))
                doubles.append({
                    "thesis": thesis,
                    "condition": cond,
                    "student_profile": student_profile,
                    "weak_dims": weak_dims,
                    "methodology": theses[idx % len(theses)].get("methodology", "unknown"),
                })
                idx += 1

        return doubles
