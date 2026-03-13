# Speaking Script — It's the Student, Not the Thesis (~5 min, 20 slides)

*Slide numbers in [brackets]. Pause briefly on transitions.*

---

## [1] Title

**It's the student, not the thesis.** When we use AI for feedback, we're shaping a researcher—not just polishing text. The risk: mechanical AI use. Generic feedback that misses where students are actually weak.

---

## [2–3] Problem

**Slide 2:** We want to develop the researcher, not just polish the thesis. Reduce mechanical AI use.

**Slide 3:** Generic feedback may not target a student's weakest dimensions. A thesis weak on methodology might get comments spread evenly across argument, evidence, theory—missing the main gap entirely.

---

## [4] Research Question + Design

**Research question:** Do personalized committees—matched to diagnosis—improve development plans and engagement? *[Show committee_assembly_demo]* This figure shows the design: we diagnose each thesis on six dimensions, then assign a committee based on the lowest scores. Different profiles trigger different committees.

---

## [5–10] Design

**Conditions.** Single, random, prescribed. C3 is where diagnosis drives committee assembly.

**Diagnostician.** Six dimensions—argument, evidence, methodology, theory, self-reflexivity, receptivity. Scores one to five. We validated across Qwen 0.5B, 1.5B, 7B—larger models produce more differentiated profiles. The radar charts show it.

**Committee.** Five personas. We prescribe three based on the lowest-scoring dimensions. Different profiles trigger different committees—the demo shows that.

**Digital doubles.** MACSS thesis corpus. We cluster by embeddings, sample across clusters so we're not just computational vs qualitative. Three student profiles with ground-truth weak dimensions for diagnostic validation.

**Development plan.** Gap map, exercises, trajectory—from profile and deliberation. One figure shows what that looks like.

**Metrics.** Mechanical reliance, trust, quality, plan quality, feedback specificity.

---

## [11] Method

Corpus, digital doubles, run each condition, compute metrics.

---

## [12–15] Results

**Pilot.** Prescribed committee yields higher plan quality and more specific feedback than random or single agent. The charts show it.

**Pilot table.** Mechanical reliance, trust, quality by condition—the numbers behind the charts.

**Qualitative.** Side by side, C3 feedback is dimension-targeted. C1 is generic. The deliberation figure makes that clear.

**GitHub.** Real course memos—345 comments, 41 authors, week two to week nine. We run the pipeline retrospectively: diagnose week two, generate a hypothetical plan, judge week nine on those targets. Students never received the plans. This is ecological validation: do our dimensions map onto observable growth? Mean improvement runs 3.2 to 4.2 by dimension. The heatmap shows per-author variation.

---

## [16–17] Data

**Pilot data.** MACSS corpus, six embedding clusters, stratified sampling, three conditions.

**GitHub data.** 345 memo comments, 49 authors, eight weeks. Forty-one had memos in both week two and week nine. The activity chart shows participation; the course heatmap shows competency evolution by week across the quarter.

---

## [18] Interpretation

Pilot says prescribed beats random and single. GitHub says our dimensions map onto real growth. Qualitative backs quantitative. The story holds together.

---

## [19–20] Close

**Limitations.** Simulated students. Small N. Future: scale up, human subjects, Safe to Be Challenged label.

**Summary.** It's the student, not the thesis. Personalized committees. Development plans. Pilot plus GitHub validation. Pipeline in place.

**Thank you.** Repo and report in the deck. Reproducibility: one Colab notebook—clone, GPU, run, download the zip.

**[Pause. Open for questions.]**
