# It's the Student, Not the Thesis

**Personalized Adversarial Committees for Competency Development Against Mechanical AI Use**

A final project on personalized committee feedback for thesis development: a six-dimension competency diagnostician, prescribed or random committees, and development plans—with harmlessness monitoring retained as a design feature.

## Motivation

Competency development matters more than the thesis artifact. We study whether **personalized adversarial committees** (matched to a student’s weakest dimensions) improve development plans and engagement compared to a single generic agent or a random committee. The project targets mechanical AI use by emphasizing substantive engagement with feedback.

## What's Done

- **Result 2:** Qwen model comparison (0.5B / 1.5B / 7B) — radar charts in `docs/validation_outputs/`
- **Result 3:** Committee assembly demo
- **Result 4:** C1 vs C3 feedback comparison + deliberation excerpts
- **Result 5:** Development plan example
- **Result 6:** Pilot (plan quality, feedback specificity by condition)
- **Result 7:** GitHub memo retrospective (improvement heatmap, validation)

## Method

- **Three conditions:** single_agent (one helpful reviewer), random_committee (3 agents chosen at random), prescribed_committee (diagnose → assemble committee by lowest dimensions → deliberation → development plan).
- **Six-dimension diagnostician:** argument_construction, evidence_evaluation, methodological_reasoning, theoretical_integration, self_reflexivity, receptivity_to_critique.
- **Student profiles (MVP):** passive_accepter, methods_weak, descriptive_reporter—each with weak_dims for ground-truth diagnostic accuracy.
- **Data:** MACSS theses (OAI-PMH / HTML), abstracts for steering, GitHub course-issue memos for longitudinal validation.
- **Models:** committee (diagnostician, assemble_committee, committee_deliberation), development plan generator, embeddings, safety monitor (design feature only).

## How to Run

**Colab (recommended):** `memo_w9_integration.ipynb` integrates GitHub clone and Colab GPU. Clone from GitHub, run cells; use Colab Secrets for `OPENAI_API_KEY` and `GITHUB_TOKEN`; download `colab_results.zip` before session ends.

**Local (uv):**

```bash
cd final-project
uv sync
uv sync --extra dev   # for pytest
uv run python run.py --pilot
uv run python run.py --pilot --github --fetch-corpus
uv run python run.py --full   # full experiment (3 conditions × 3 students × 5 theses)
uv run python run.py --fetch-github   # fetch GitHub issues only
uv run pytest tests/
```

Note: Result 2 (three Qwen sizes) requires significant GPU memory—Colab T4/A100 recommended.

## Outputs

- `docs/validation_outputs/` — all figures (radar, committee, feedback, deliberation, pilot, GitHub)
- `data/` — pilot_results.json, diagnostician_validation.json, github_memo_validation.json
- The notebook has a download cell that zips results for local use.

## Structure

- `run.py` — main entry: `--pilot`, `--github`, `--fetch-corpus`, `--fetch-github`, `--full`
- `src/developing_the_researcher/` — package: `config`, `data` (corpus, loaders, github_loader), `models` (embeddings, committee, safety, diagnostician, development_plan), `metrics` (core, quality, deliberation), `pipeline` (runner, github_validation)
- `data/` — MACSS corpus, GitHub issues, pilot results, qualitative samples (generated at runtime)
- `figures/` — pilot plots
- `tests/` — unit tests (corpus, loaders, embeddings, metrics, GitHub loader)
- `report.md` — implementation details and rationale

## Requirements

- **Data:** MACSS theses, abstracts for steering, GitHub memo comments (optional).
- **Models:** Committee LLM, embedding model, diagnostician, development plan generator; safety monitor (design feature).
- **Validation:** Pilot metrics (mechanical reliance, trust, quality, plan quality, deliberation metrics); GitHub longitudinal trajectories; qualitative interpretation of feedback–revision pairs.

See [report.md](report.md) for implementation details.
