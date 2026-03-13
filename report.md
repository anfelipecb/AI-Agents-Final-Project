# Implementation Report: It's the Student, Not the Thesis

## What Was Implemented and Why

This document summarizes the implementation of the final project: **It's the Student, Not the Thesis** — Personalized Adversarial Committees for Competency Development Against Mechanical AI Use.

---

## Phase 0: Project Skills

**Implemented:** Three Cursor skills in `.cursor/skills/`:

| Skill | Purpose | Why |
|-------|---------|-----|
| `ml-llm-expert` | Model selection, embeddings, evaluation, RepE, safety | Guides the agent when implementing LLM components, choosing models (Qwen2.5-7B, sentence-transformers), and defining metrics (mechanical reliance, trust, quality). |
| `pipeline-orchestration` | Loader patterns, pipeline flow, MACSS refactor, error handling | Ensures consistent structure across loaders, paths in `config.py`, and graceful fallbacks when corpus is empty. |
| `web-scraping` | httpx, API vs HTML, rate limiting | Guides HTTP fetching (httpx preferred over requests), API-first for GitHub, BeautifulSoup for HTML when no API exists. |

**Rationale:** Skills are created first so the agent can apply them end-to-end when building the rest of the project. They encode domain knowledge and conventions that would otherwise be repeated or forgotten.

---

## Phase 1: Self-Contained Project Setup

**Implemented:**

- **`config.py`** — Centralized paths (`DATA_DIR`, `LOGS_DIR`, `FIGURES_DIR`), model names, `FAST_MODE`, GitHub API base, MACSS OAI/URL config.
- **`data/corpus.py`** — `extract_year`, `infer_methodology`, `save_corpus`, `setup_logging`. Refactored from week6 `core.py`; uses project config paths.
- **`data/harvest.py`** — OAI-PMH harvester for Knowledge UChicago. Refactored from week6 `oai_harvest.py`.
- **`data/scraper.py`** — HTML scraper fallback (httpx + BeautifulSoup). Refactored from week6 `scraper.py`.

**Why:** The project is self-contained. No runtime imports from `week6` or `week9`. All MACSS logic lives in `src/developing_the_researcher/data/`.

---

## Phase 2: Pipeline Loaders

**Implemented:**

| Loader | File | Purpose |
|--------|------|---------|
| `CorpusLoader` | `data/loaders.py` | Loads MACSS corpus from JSON; `fetch_via_harvest()`, `fetch_via_scrape()`, `save_abstracts_for_steering()`. Falls back to `SAMPLE_ABSTRACTS` if empty. |
| `DoublesLoader` | `data/loaders.py` | `load_doubles_from_corpus()` — builds `(thesis, condition, student_profile, weak_dims, methodology)` for three conditions (single_agent, random_committee, prescribed_committee). Uses `STUDENT_PROFILES` from config. |
| `GitHubIssuesLoader` | `data/github_loader.py` | Fetches issues + comments via httpx + GitHub REST API. Filters "Week N Memo" issues; extracts `(issue_id, week, author, memo_text, created_at, thumbs_up, reactions)`. Caches to `github_issues.json`. |
| `EmbeddingLoader` | `models/embeddings.py` | Lazy-loads sentence-transformers; `get_embeddings()`, `cosine_sim()`. |
| `CommitteeLoader` | `models/committee.py` | Lazy-loads Qwen2.5-7B (4-bit); `generate()`, `skill_diagnostician()`, `adversarial_critic()`. |
| `SafetyLoader` | `models/safety.py` | `judge_safety_llm()`, `harmlessness_monitor()`. Uses CommitteeLoader for generation. |

**Rationale:**

- **httpx** — Chosen for HTTP (faster than requests, async support). Used for GitHub API and MACSS scraper.
- **GitHub API** — Preferred over HTML scraping; returns structured JSON with reactions. No BeautifulSoup needed.
- **Lazy loading** — Models load on first use to avoid loading Qwen when only running corpus or GitHub fetch.
- **FAST_MODE** — Reduces `n_per_condition` for quick debugging.

---

## Phase 2: Pipeline Runner and Notebook

**Implemented:**

- **`pipeline/runner.py`** — `run_pilot()`: loads corpus → doubles → runs committee (Skill Diagnostician → Adversarial Critic → harmlessness monitor) → simulates student revision → computes mechanical reliance, trust, quality → saves results and figures.
- **`metrics.py`** — `mechanical_reliance`, `trust_rating`, `quality_rating` (LLM-as-judge).
- **`memo_w9_integration.ipynb`** — Minimal notebook that imports and runs `run_pilot()`.

**Why:** The runner orchestrates the full flow: load → run experiment → save. The notebook provides a single entry point for Colab or local execution.

---

## Four Forms of Data

| # | Data Form | Source | Implementation |
|---|-----------|--------|----------------|
| 1 | Thesis abstracts | MACSS corpus | `CorpusLoader`, `macs_theses.json`, `abstracts_for_steering.json` |
| 2 | Interaction logs | Pilot experiment | `pilot_results.json` (feedback, revisions, metrics per double) |
| 3 | Embedding/similarity scores | sentence-transformers | `get_embeddings()`, `cosine_sim()` for mechanical reliance |
| 4 | GitHub issue corpus | Course repo issues | `GitHubIssuesLoader`, `github_issues.json` |

---

## Three Model Types from Three Weeks

| Week | Model | Use |
|------|-------|-----|
| Week 6 | sentence-transformers | Embeddings, cosine similarity, mechanical reliance |
| Week 8 | Skill-diagnostic advisor (ReAct-style) | Skill Diagnostician, Adversarial Critic |
| Week 9 | Qwen2.5-7B + safety judge | Committee generation, `judge_safety_llm`, harmlessness monitor |

---

## Project Structure (Final)

```
final-project/
  .cursor/skills/
    ml-llm-expert/SKILL.md
    pipeline-orchestration/SKILL.md
    web-scraping/SKILL.md
  src/developing_the_researcher/
    config.py
    metrics/
      core.py, quality.py, deliberation.py
    data/
      corpus.py, harvest.py, scraper.py
      loaders.py, github_loader.py
    models/
      embeddings.py, committee.py, safety.py, diagnostician.py, development_plan.py
    pipeline/
      runner.py
      github_validation.py
  run.py
  tests/
  data/
  logs/
  figures/
  memo_w9_integration.ipynb
  blog_post.md
  presentation/
  report.md
  README.md
  pyproject.toml
```

---

## Dependencies

- `httpx` — HTTP client (GitHub API, MACSS scraper)
- `beautifulsoup4` — HTML parsing for MACSS scraper
- `sentence-transformers` — Embeddings
- `transformers`, `accelerate`, `bitsandbytes` — Qwen2.5-7B
- `numpy`, `scikit-learn`, `matplotlib`, `seaborn` — Metrics and plots

---

## Phase 3: GitHub Validation and Qualitative Analysis

**Implemented:**

- **`pipeline/github_validation.py`** — `run_github_validation()`: loads or fetches GitHub memo corpus, embeds memo texts, computes per-week trajectories (mean similarity to first memo in week), saves `data/github_validation.json`. Invoked via `run.py --github`.
- **Qualitative samples** — `run_pilot()` now records `thesis`, `feedback`, and `revision` per run and writes up to 10 feedback–revision pairs to `data/qualitative_samples.json` for manual interpretation.

### Qualitative Interpretation

Qualitative validation uses the saved feedback–revision pairs in `qualitative_samples.json`. Interpreters can:

- **Engagement:** Whether revisions reflect the feedback (e.g., addressing specific critiques vs. generic improvements).
- **Harmlessness:** In `visible_label` and `silent_monitor`, whether the monitor’s interventions (e.g., softening tone, adding caveats) appear in the feedback and whether revisions stay on-topic and non-harmful.
- **Mechanical reliance:** Whether revisions are overly similar to a generic baseline (high cosine similarity) vs. meaningfully incorporating the committee’s critique.

These interpretations support the quantitative metrics (mechanical reliance, trust, quality) and inform the blog post and presentation.

---

## What Remains (Phase 4)

- **Phase 4:** Draft blog post (3600 words + 13 figures), presentation (5 min / 20 slides).

### Future Work: Safe to Be Challenged

The **visible harmlessness label** as a trust intervention (committee_only vs. silent_monitor vs. visible_label) is retained as a design feature in the safety monitor but is no longer an experimental condition in the main study. It can be revisited as future work: e.g., A/B tests on whether labeling feedback as “checked for harmlessness” changes engagement or over-reliance.

---

## Summary

The implementation is complete for Phases 0–3. The project is self-contained, uses pipeline loaders for all data sources, and includes project skills for ML/LLM expertise, pipeline orchestration, and web scraping. MACSS thesis fetching is refactored into the project; GitHub issues are fetched via httpx + REST API. The pilot can be run via `run.py`, `run_pilot()`, or the notebook. GitHub validation and qualitative samples support longitudinal and qualitative interpretation.
