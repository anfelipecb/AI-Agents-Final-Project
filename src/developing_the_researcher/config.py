"""Configuration for It's the Student, Not the Thesis (developing_the_researcher)."""
from pathlib import Path

# Project root (final-project/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
FIGURES_DIR = PROJECT_ROOT / "figures"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_VALIDATION_OUTPUTS = DOCS_DIR / "validation_outputs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)
DOCS_VALIDATION_OUTPUTS.mkdir(parents=True, exist_ok=True)

# Data paths
MACSS_PATH = DATA_DIR / "macs_theses.json"
DIAGNOSTICIAN_VALIDATION_PATH = DATA_DIR / "diagnostician_validation.json"
MACSS_ONLY_PATH = DATA_DIR / "macss_theses_only.json"  # MACSS theses only (by record_appears_in / is_macss) for embeddings/geometry
ABSTRACTS_PATH = DATA_DIR / "abstracts_for_steering.json"
GITHUB_ISSUES_PATH = DATA_DIR / "github_issues.json"
PILOT_RESULTS_PATH = DATA_DIR / "pilot_results.json"
GITHUB_VALIDATION_PATH = DATA_DIR / "github_validation.json"
GITHUB_MEMO_VALIDATION_PATH = DATA_DIR / "github_memo_validation.json"
QUALITATIVE_SAMPLES_PATH = DATA_DIR / "qualitative_samples.json"

# Model names
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# Optional OpenAI backend (for validation runs when USE_OPENAI=true)
USE_OPENAI = False  # Set True or env USE_OPENAI=1 to use GPT-4-mini for selected runs
OPENAI_MODEL = "gpt-4o-mini"  # or "gpt-4-mini"

# Experiment
FAST_MODE = True  # Smaller N for debugging; set False for full runs

# Competency dimensions (6-dimension diagnostician)
COMPETENCY_DIMENSIONS = {
    "argument_construction": "Logical coherence, warrants, claim-evidence alignment",
    "evidence_evaluation": "Distinguishes correlation/causation, source quality, conflicting evidence",
    "methodological_reasoning": "Justifies design choices, identifies validity threats, scope conditions",
    "theoretical_integration": "Connects findings to frameworks, not just pattern description",
    "self_reflexivity": "Awareness of assumptions, positionality, limitations",
    "receptivity_to_critique": "Engages substantively with challenges vs. deflects/capitulates",
}

# Conditions (3 total: C1 single, C2 random, C3 prescribed)
CONDITIONS = ("single_agent", "random_committee", "prescribed_committee")

# Student profiles (3 for MVP)
STUDENT_PROFILES = {
    "passive_accepter": {"revision_style": "copy_paste", "weak_dims": ["self_reflexivity", "receptivity_to_critique"]},
    "methods_weak": {"revision_style": "engage", "weak_dims": ["methodological_reasoning", "evidence_evaluation"]},
    "descriptive_reporter": {"revision_style": "engage", "weak_dims": ["theoretical_integration", "argument_construction"]},
}

# GitHub
GITHUB_OWNER = "KnowledgeLab"
GITHUB_REPO = "AI-Agents-for-Social-Science-and-Society-2026"
GITHUB_API_BASE = "https://api.github.com"

# MACSS / Knowledge UChicago
OAI_URL = "https://knowledge.uchicago.edu/oai2d"
BASE_URL = "https://knowledge.uchicago.edu"
SEARCH_URL = (
    "https://knowledge.uchicago.edu/search"
    "?ln=en&rm=&sf=&so=d&rg=25"
    "&c=Knowledge%20UChicago"
    "&fti=0&fct__4=Computational%20Social%20Sciences%20%28MACSS%29"
    "&fti=0&p=MACSS"
)
INTERMEDIATE_PATH = DATA_DIR / "scrape_intermediate.json"
REQUEST_DELAY = 1.0
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0
