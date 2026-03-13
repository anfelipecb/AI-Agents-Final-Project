"""Core utilities for MACSS thesis corpus: shared logic, logging, corpus I/O."""
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import LOGS_DIR, MACSS_PATH


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure logging to file and stdout."""
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / "scrape.log"
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("safe_to_be_challenged")


def extract_year(text: str | None) -> int | None:
    """Extract 4-digit year (1900-2099) from text."""
    if not text:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", str(text))
    return int(m.group(0)) if m else None


def infer_methodology(title: str, abstract: str) -> str:
    """Infer methodology from title/abstract keywords."""
    text = f"{(title or '')} {(abstract or '')}".lower()
    comp_kw = ["network", "algorithm", "machine learning", "nlp", "computational", "simulation", "model"]
    quant_kw = ["regression", "survey", "experiment", "statistical", "causal", "quantitative"]
    qual_kw = ["interview", "ethnograph", "qualitative", "case study", "discourse"]
    if any(k in text for k in comp_kw):
        return "computational"
    if any(k in text for k in quant_kw):
        return "quantitative"
    if any(k in text for k in qual_kw):
        return "qualitative"
    return "unknown"


def save_corpus(
    theses: list[dict[str, Any]],
    path: Path | None = None,
    *,
    source: str = "knowledge.uchicago.edu",
    harvest_method: str | None = None,
) -> Path:
    """Save thesis corpus to JSON."""
    out = path or MACSS_PATH
    data: dict[str, Any] = {
        "source": source,
        "collected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "theses": theses,
    }
    if harvest_method:
        data["harvest_method"] = harvest_method
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return out
