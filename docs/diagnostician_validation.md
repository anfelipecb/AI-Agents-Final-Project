# Diagnostician Validation

## Purpose

Validate **Step 1** of the causal chain: **Do competency profiles vary by thesis type?**

If the 6-dimension diagnostician produces differentiated profiles across theses (e.g. by embedding cluster), we have evidence that the assessment is sensitive to thesis content. If profiles are flat or undifferentiated, iterate on the diagnostician prompt before proceeding.

## Method

- **Thesis sampling:** 10 theses sampled from the 6 embedding clusters (same clustering as `figures/02_embedding_by_keywords.png`: keyword/abstract embeddings, KMeans, `random_state=42`). This ensures variation across thesis types (not only computational vs qualitative).
- **Models:** Three sizes run locally for comparison:
  - `Qwen/Qwen2.5-0.5B-Instruct`
  - `Qwen/Qwen2.5-1.5B-Instruct`
  - `Qwen/Qwen2.5-7B-Instruct`
- **Assessment:** For each thesis, `diagnose_competencies(thesis_text, generate_fn)` returns scores 1–5 and justifications for each of the six dimensions (argument_construction, evidence_evaluation, methodological_reasoning, theoretical_integration, self_reflexivity, receptivity_to_critique).
- **No student simulation:** The diagnostician assesses thesis text only.

## Outputs

- **Data:** `data/diagnostician_validation.json` — raw results (thesis_id, cluster, model, profile per run).
- **Figures (in `docs/validation_outputs/`):**
  - `radar_thesis_{id}.png` — one radar per thesis with 3 overlaid series (one per model).
  - `radar_by_model.png` — mean competency profile by model (across all 10 theses).
  - `radar_by_cluster.png` — mean competency profile by cluster.

## Results

*(Fill after running validation.)*

### Summary table

| Dimension              | 0.5B mean | 1.5B mean | 7B mean |
|------------------------|-----------|-----------|---------|
| argument_construction  | …         | …         | …       |
| evidence_evaluation    | …         | …         | …       |
| methodological_reasoning | …       | …         | …       |
| theoretical_integration | …        | …         | …       |
| self_reflexivity       | …         | …         | …       |
| receptivity_to_critique | …        | …         | …       |

### By cluster

| Cluster | Mean score (over dimensions) | Notes |
|---------|------------------------------|-------|
| 0       | …                            |       |
| 1       | …                            |       |
| …       | …                            |       |

## Findings

- **Do profiles differentiate?** (e.g. do different clusters or theses get distinct shapes?)
- **Which model differentiates best?** (e.g. does 7B show more variance than 0.5B?)
- **Any cluster showing distinct patterns?**

## Recommendations

- **If profiles are differentiated:** Proceed to next step (e.g. digital doubles, committee conditions).
- **If profiles are flat:** Iterate on the diagnostician prompt (e.g. make dimensions or scoring criteria more explicit), then re-run validation.

## Related validation outputs

- **[Committee assembly](committee_assembly.md)** — Step 2: different profiles trigger different committees. Figure: `validation_outputs/committee_assembly_demo.png`.
- **[Feedback comparison](feedback_comparison.md)** — Result 4: side-by-side C1 vs C3 feedback. Figures: `validation_outputs/feedback_comparison_thesis_*.png`, `deliberation_thesis_*.png`.

## Run summary

*(Optional: add timestamp and key stats after each run, e.g. mean score variance by dimension, by model.)*
