# It's the Student, Not the Thesis — Presentation (5 min, 23 slides)

Use this outline to build the deck (e.g. with MCP pptx tools or Keynote/PowerPoint).

**Figure references (docs/validation_outputs/):** radar_by_model.png, radar_by_cluster.png, radar_thesis_*.png, committee_assembly_demo.png, feedback_comparison_thesis_*.png, deliberation_thesis_*.png, development_plan_example.png, plan_quality_by_condition.png, feedback_specificity_by_condition.png, github_improvement_heatmap.png, github_memo_validation.png. See [NARRATIVE.md](NARRATIVE.md) for slide-by-slide mappings.

---

1. **Title** — It's the Student, Not the Thesis: Personalized Adversarial Committees for Competency Development  
2. **Problem** — We want to develop the researcher, not just polish the thesis; reduce mechanical AI use.  
3. **Problem (cont.)** — Generic feedback may not target a student’s weakest dimensions.  
4. **Research question** — Do personalized committees (matched to diagnosis) improve development plans and engagement?  
5. **Design: three conditions** — Single agent / Random committee / Prescribed committee.  
6. **Design: diagnostician** — Six dimensions (argument, evidence, methodology, theory, self-reflexivity, receptivity); scores 1–5 + justifications. (radar_by_model.png, radar_by_cluster.png, radar_thesis_*.png)  
7. **Design: committee** — Five personas (Methodologist, Theorist, Devil's Advocate, Encourager, Clarity Coach); prescribe 3 by lowest dimensions or pick random 3. (committee_assembly_demo.png)  
8. **Design: digital doubles** — Thesis, condition, student_profile, weak_dims, methodology from MACSS corpus.  
9. **Design: development plan** — Gap map, exercises, trajectory from profile + deliberation feedback. (development_plan_example.png)  
10. **Design: metrics** — Mechanical reliance, trust, quality, plan quality, deliberation metrics.  
11. **Method summary** — Pipeline: load corpus → build doubles → run condition (C1/C2/C3) → compute metrics.  
12. **Results: pilot** — Mean mechanical reliance by condition (chart). (plan_quality_by_condition.png, feedback_specificity_by_condition.png)  
13. **Results: pilot** — Mean trust by condition (chart).  
14. **Results: table** — MR, trust, quality, plan quality by condition (sample sizes).  
15. **Qualitative** — Feedback–revision pairs and development plans in pilot_results / qualitative_samples. (feedback_comparison_thesis_*.png, deliberation_thesis_*.png)  
16. **Interpretation** — Prescribed committee vs. random/single: effect on plan quality and engagement. (plan_quality_by_condition.png, github_improvement_heatmap.png)  
17. **Limitations & future work** — Simulated students; small N; single LLM. Future: scale N; human subjects; Safe to Be Challenged (visible harmlessness label).  
18. **Data: pilot & digital doubles** — MACSS thesis corpus → embedding clusters → sampled theses; 3 conditions × n per condition; ground-truth weak_dims for diagnostic accuracy.  
19. **Data: GitHub retrospective** — 345 memo comments, 49 authors, 8 weeks (2–9); 17 authors with both Week 2 & 9; retrospective pipeline (diagnose → plan → judge Week 9); ecological validation only—no treatment deployed.  
20. **Summary** — It's the student, not the thesis; personalized committees + development plans; pilot + GitHub ecological validation; pipeline in place.  
21. **Thank you / Q&A** — Contact / repo / report.md.  
22. **Reproducibility** — memo_w9_integration.ipynb on Colab (clone from GitHub, GPU T4/A100, download zip).
