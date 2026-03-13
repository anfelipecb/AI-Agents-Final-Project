"""Configuration for Safe to Be Challenged project."""
from pathlib import Path

# Project root (final-project/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
FIGURES_DIR = PROJECT_ROOT / "figures"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# Data paths
MACSS_PATH = DATA_DIR / "macs_theses.json"
ABSTRACTS_PATH = DATA_DIR / "abstracts_for_steering.json"
GITHUB_ISSUES_PATH = DATA_DIR / "github_issues.json"
PILOT_RESULTS_PATH = DATA_DIR / "pilot_results.json"
GITHUB_VALIDATION_PATH = DATA_DIR / "github_validation.json"
QUALITATIVE_SAMPLES_PATH = DATA_DIR / "qualitative_samples.json"

# Model names
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# Experiment
FAST_MODE = True  # Smaller N for debugging; set False for full runs
CONDITIONS = ("committee_only", "silent_monitor", "visible_label")

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
