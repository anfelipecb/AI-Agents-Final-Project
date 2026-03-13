# GitHub Memo Retrospective Validation

## Purpose

Validate whether students who received a **development plan** (based on their Week 2 memo diagnosis and committee feedback) show **improvement** in their Week 9 memos, as judged by GPT-4-mini on the plan’s target dimensions.

## Method

1. **Data:** Fetch all "Week N Memo" issues and comments from [KnowledgeLab/AI-Agents-for-Social-Science-and-Society-2026](https://github.com/KnowledgeLab/AI-Agents-for-Social-Science-and-Society-2026/issues).
2. **Panel:** Memos with body ≥ 100 chars; authors with memos in both early week (2) and late week (9).
3. **Per author pipeline:**
   - **Diagnose** Week 2 memo on 6 competency dimensions (GPT-4-mini).
   - **Assemble** committee from lowest-scoring dimensions.
   - **Generate** development plan (gap map + exercises).
   - **Judge** Week 9 memo against plan targets (GPT-4-mini).

## Results (Latest Run)

### Data Summary

| Metric | Value |
|--------|-------|
| Corpus size | 345 memo comments (with pagination) |
| Authors | 49 |
| Weeks present | 2, 3, 4, 5, 6, 7, 8, 9 |
| Authors with both Week 2 & 9 | 17 |

*Pagination fix: GitHub API returns 30 comments/page by default. The loader now paginates (per_page=100) to fetch all comments. Before fix: 240 memos, 46 authors; anfelipecb missing weeks 2, 4, 5, 6. After: 345 memos, 49 authors; anfelipecb in all 8 weeks. Re-run validation with `--fetch-github` to use updated corpus.*

### Mean Improvement by Dimension (1–5 scale)

| Dimension | Mean improvement |
|-----------|------------------|
| methodological_reasoning | 4.22 |
| theoretical_integration | 4.08 |
| argument_construction | 4.00 |
| receptivity_to_critique | 3.36 |
| self_reflexivity | 3.18 |
| evidence_evaluation | 3.29 |

### Outputs

- **Data:** `data/github_memo_validation.json` — profiles, plans, improvement scores per author.
- **Figures (in `docs/validation_outputs/`):**
  - `github_memo_validation.png` — improvement bar chart.
  - `github_improvement_heatmap.png` — top 20 authors × dimension heatmap (inferno palette).
  - `github_course_improvement_heatmap.png` — week × dimension mean competency scores (inferno palette).

## Example: yangyuwang

- **Week 2 profile:** argument 4, evidence 3, method 4, theory 3, reflexivity 2, receptivity 3.
- **Plan targets:** evidence, theory, reflexivity, receptivity.
- **Week 9 improvement scores:** evidence 4, theory 4, reflexivity 3, receptivity 4.

## Run

```bash
uv run python run.py --no-pilot --fetch-github --github-memo-validation
```

Use `--fetch-github` to refresh GitHub data; omit to use cached `data/github_issues.json`.

## Note on Pagination

The GitHub API returns 30 comments per page by default. The loader now paginates (`per_page=100`) to fetch all comments for each issue, so authors whose memos appear after the first page (e.g. "Load more" on the web UI) are included.
