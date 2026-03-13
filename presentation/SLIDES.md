# It's the Student, Not the Thesis — Presentation (5 min, 20 slides)

**All figures:** `docs/validation_outputs/` — See [NARRATIVE.md](NARRATIVE.md) for mappings. [SCRIPT.md](SCRIPT.md) for speaking notes.

---

1. **Title** — It's the Student, Not the Thesis: Personalized Adversarial Committees for Competency Development

2. **Problem** — We want to develop the researcher, not just polish the thesis; reduce mechanical AI use.

3. **Problem (cont.)** — Generic feedback may not target a student's weakest dimensions.

4. **Research question + design** — Do personalized committees (matched to diagnosis) improve development plans and engagement? (committee_assembly_demo.png — diagnosis → committee assignment)

5. **Design: conditions** — Single agent / Random committee / Prescribed committee. (C1=C2=C3 labels)

6. **Design: diagnostician** — Six dimensions, scores 1–5. (radar_by_model.png, radar_by_cluster.png, radar_thesis_13058.png)

7. **Design: committee** — Five personas; prescribe 3 by lowest dimensions. (committee_assembly_demo.png)

8. **Design: digital doubles** — MACSS thesis corpus; embedding clusters; student profiles (passive_accepter, methods_weak, descriptive_reporter); ground-truth weak_dims.

9. **Design: development plan** — Gap map, exercises, trajectory. (development_plan_example.png)

10. **Design: metrics** — Mechanical reliance, trust, quality, plan quality, feedback specificity.

11. **Method** — Load corpus → build doubles → run C1/C2/C3 → compute metrics.

12. **Results: pilot** — Plan quality + feedback specificity by condition. (plan_quality_by_condition.png, feedback_specificity_by_condition.png)

13. **Results: pilot table** — MR, trust, quality by condition (extract from pilot_results.json).

14. **Results: qualitative** — C1 vs C3 feedback; deliberation excerpts. (feedback_comparison_thesis_13058.png, deliberation_thesis_13058.png)

15. **Results: GitHub validation** — 345 memos, 41 authors, Week 2→9. Mean improvement: method 4.15 (highest), argument/theory/evidence 3.5–3.6, reflexivity 2.6, scope 2.0 (lowest). Per-author variation in heatmap. (github_improvement_heatmap.png, github_memo_validation.png)

16. **Data: pilot** — MACSS corpus; 6 embedding clusters; 3 conditions × n per condition; stratified by thesis type.

17. **Data: GitHub retrospective** — 345 memo comments, 49 authors, 8 weeks; 41 with both Week 2 & 9; ~40 memos/week. Course evolution: evidence & method strongest; reflexivity weakest. (github_memo_activity.png, github_course_improvement_heatmap.png, github_competency_evolution.png)

18. **Interpretation** — Pilot: prescribed beats random/single. GitHub: method/argument/theory improve most; reflexivity and scope harder. Per-author variation supports personalized feedback. Qualitative backs quantitative.

19. **Limitations & future** — Simulated students; small N. Scale N; human subjects; Safe to Be Challenged.

20. **Summary + Thank you** — Personalized committees, development plans, pilot + GitHub validation. Repo, report. Reproducibility: memo_w9_integration.ipynb on Colab (GPU, download zip).
