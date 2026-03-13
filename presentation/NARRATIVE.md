# Presentation Narrative (20 slides, 5 min)

**Figures:** `docs/validation_outputs/` | **Script:** [SCRIPT.md](SCRIPT.md)

---

## Figure → Slide Mapping

| Slide | Figure | Use |
|-------|--------|-----|
| 4 | committee_assembly_demo.png | Research design: diagnosis → committee assignment |
| 6 | radar_by_model.png, radar_by_cluster.png, radar_thesis_13058.png | 0.5B/1.5B/7B; profiles by cluster |
| 7 | committee_assembly_demo.png | Profile → committee mapping |
| 9 | development_plan_example.png | Gap map, exercises, trajectory |
| 12 | plan_quality_by_condition.png, feedback_specificity_by_condition.png | Pilot: prescribed > random > single |
| 14 | feedback_comparison_thesis_13058.png, deliberation_thesis_13058.png | C1 vs C3 side-by-side |
| 15 | github_improvement_heatmap.png, github_memo_validation.png | Mean improvement by dim: method 4.15, scope 2.0; per-author variation |
| 17 | github_memo_activity.png, github_course_improvement_heatmap.png, github_competency_evolution.png | Memos/week; week × dimension; reflexivity weakest |

---

## Slides 1–4: Problem, Question, Design

**1. Title** — Core claim.

**2. Problem** — Develop the researcher, not polish the thesis; reduce mechanical AI use.

**3. Problem (cont.)** — Generic feedback may not target a student's weakest dimensions.

**4. Research question + design** — Do personalized committees (matched to diagnosis) improve plans and engagement? *Show:* committee_assembly_demo.png — diagnosis (6-dim scores) → committee assignment; different profiles → different committees.

---

## Slides 5–11: Design & Method

**5. Conditions** — C1 single, C2 random, C3 prescribed.

**6. Diagnostician** — Six dimensions, 1–5. Qwen 0.5B/1.5B/7B; profiles by cluster. *Show:* radar_by_model, radar_by_cluster, radar_thesis_13058.

**7. Committee** — Five personas; prescribe 3 by lowest dimensions. *Show:* committee_assembly_demo.png.

**8. Digital doubles** — MACSS corpus; embedding clusters (KMeans); student profiles (passive_accepter, methods_weak, descriptive_reporter); ground-truth weak_dims for diagnostic validation.

**9. Development plan** — Gap map, exercises, trajectory. *Show:* development_plan_example.png.

**10. Metrics** — Mechanical reliance, trust, quality, plan quality, feedback specificity.

**11. Method** — Corpus → doubles → C1/C2/C3 → metrics.

---

## Slides 12–15: Results

**12. Pilot** — Prescribed yields higher plan quality and feedback specificity. *Show:* plan_quality_by_condition.png, feedback_specificity_by_condition.png.

**13. Pilot table** — MR, trust, quality by condition. *Data:* pilot_results.json. Table can be built from aggregated means per condition.

**14. Qualitative** — C3 feedback dimension-targeted; C1 generic. *Show:* feedback_comparison_thesis_13058.png, deliberation_thesis_13058.png. Quotes: deliberation_thesis_13058.txt.

**15. GitHub validation** — 345 memos, 41 authors, 8 weeks. Retrospective: diagnose Week 2 → plan → judge Week 9. *Key stats:* methodological reasoning 4.15 (highest), argument/theory/evidence 3.5–3.6, self-reflexivity 2.6, scope_of_research 2.0 (lowest). Heatmap: per-author variation; scope is bottleneck. *Show:* github_improvement_heatmap.png, github_memo_validation.png.

---

## Slides 16–18: Data & Interpretation

**16. Data: pilot** — MACSS corpus; 6 embedding clusters; stratified sampling; 3 conditions × n per condition.

**17. Data: GitHub retrospective** — 345 memo comments, 49 authors, 8 weeks; 41 with both Week 2 & 9; ~40 memos/week. Course evolution: evidence & method strongest; reflexivity consistently weakest. *Show:* github_memo_activity.png, github_course_improvement_heatmap.png, github_competency_evolution.png.

**18. Interpretation** — Pilot: prescribed beats random/single. GitHub: method, argument, theory improve most; reflexivity and scope harder. Per-author variation supports personalized feedback. Qualitative backs quantitative.

---

## Slides 19–20: Close

**19. Limitations & future** — Simulated students; small N. Future: scale N; human subjects; Safe to Be Challenged.

**20. Summary + Thank you** — Personalized committees, development plans, pilot + GitHub validation, pipeline ready. Repo, report. Reproducibility: Colab notebook, GPU, download zip.
