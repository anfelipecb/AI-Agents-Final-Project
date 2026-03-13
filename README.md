# Safe to Be Challenged

**Trust and Harmlessness in Adversarial AI Advising**

A final project on how AI advising can remain trustworthy and harmless when students are explicitly challenged—using a skill-diagnostic committee, a harmlessness monitor, and three experimental conditions (committee-only, silent monitor, visible label).

## Motivation

When students receive adversarial or critical feedback from an AI, trust and visible feedback matter: users need to know when the system is monitoring for harm and how it is steering advice. This project studies whether making harmlessness monitoring visible (vs. silent or absent) changes reliance and engagement.

## Method

- **Three conditions:** committee-only (no monitor), silent_monitor (monitor present but not shown), visible_label (monitor and label shown to the user).
- **Digital doubles:** synthetic “students” with thesis abstracts, trust sensitivity, and methodology, driven by the MACSS thesis corpus.
- **Data:** MACSS theses (OAI-PMH / HTML), abstracts for steering, and GitHub course-issue memos for longitudinal validation.
- **Models:** committee (skill diagnostician + adversarial critic), embedding model (sentence-transformers), safety monitor (condition-dependent labeling).

## How to Run

**Local (uv):**

```bash
cd final-project
uv sync
uv sync --extra dev   # for pytest
uv run python run.py --pilot
uv run python run.py --pilot --github --fetch-corpus
uv run python run.py --fetch-github   # fetch GitHub issues only
uv run pytest tests/
```

**Colab:** Use `pip` in notebook cells (e.g. `!pip install -q ...` or `!pip install -e .`). See `memo_w9_integration.ipynb`.

## Structure

- `run.py` — main entry: `--pilot`, `--github`, `--fetch-corpus`, `--fetch-github`
- `src/safe_to_be_challenged/` — package: `config`, `data` (corpus, loaders, github_loader), `models` (embeddings, committee, safety), `metrics`, `pipeline` (runner, github_validation)
- `data/` — MACSS corpus, GitHub issues, pilot results, qualitative samples (generated at runtime)
- `figures/` — pilot plots
- `tests/` — unit tests (corpus, loaders, embeddings, metrics, GitHub loader)
- `report.md` — implementation details and rationale

## Requirements

- **Data:** Three forms—MACSS theses, abstracts for steering, GitHub memo comments (optional).
- **Models:** Committee LLM, embedding model, safety/condition logic.
- **Validation:** Pilot metrics (mechanical reliance, trust, quality); GitHub longitudinal trajectories; qualitative interpretation of feedback–revision pairs.

See [report.md](report.md) for implementation details and qualitative interpretation.
