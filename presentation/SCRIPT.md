# Lighting Script — It's the Student, Not the Thesis

*TED-talk style script (~5 min). Slide numbers in brackets. Pause briefly on transitions.*

---

## Opening [Slide 1]

**It's the student, not the thesis.**

That’s the idea at the heart of this project. When we use AI to give feedback on theses and memos, we’re not just polishing a document. We’re shaping a researcher. And the risk? Mechanical AI use. Students pressing "regenerate" instead of thinking. Generic feedback that misses where they’re actually weak.

So we asked: *What if the feedback was personalized—matched to a diagnosis of the student’s weakest dimensions?*

---

## Problem [Slides 2–3]

Here’s the thing. Right now, AI feedback tends to be generic. A thesis weak on methodology might get comments spread evenly across argument, evidence, theory—missing the main gap entirely. We want to target that gap. We want to develop the researcher, not just touch up the text.

---

## Research Question [Slide 4]

Our research question: **Do personalized committees—matched to a competency diagnosis—improve development plans and engagement?**

We compare three conditions: a single generic agent, a random committee, and a prescribed committee driven by diagnosis. That gives us a clean comparison.

---

## Design [Slides 5–9]

**Conditions.** Single agent, random committee, prescribed committee. C1 is baseline. C2 gets a committee but no diagnosis. C3: diagnosis drives committee assembly.

**Diagnostician.** Six dimensions—argument, evidence, methodology, theory, self-reflexivity, receptivity. Scores one to five, plus justifications. We validated across three Qwen model sizes: 0.5B, 1.5B, 7B. Larger models produce more differentiated profiles. And profiles vary by thesis type—we see that in the radar charts.

**Committee.** Five personas: Methodologist, Theorist, Devil’s Advocate, Encourager, Clarity Coach. We prescribe three based on the lowest-scoring dimensions. Different profiles trigger different committees—that’s what the committee assembly demo shows.

**Development plan.** Gap map, exercises, trajectory—all from the profile and deliberation feedback. One figure shows exactly what that looks like for a single thesis.

---

## Method & Results [Slides 10–16]

**Pipeline.** Load corpus, build digital doubles, run each condition, compute metrics. Mechanical reliance, trust, quality, plan quality.

**Pilot results.** The prescribed committee yields higher plan quality and more specific feedback than random or single agent. And qualitatively, you can see it: C3 feedback is dimension-targeted. C1 is generic. Side by side, it’s clear.

**Interpretation.** Prescribed beats random and single. And we have ecological validation too—real course memos, week two to week nine. More on that in a moment.

---

## Limitations & Future [Slide 17]

We use simulated students. Small N. Single LLM. Those are real limitations. Future work: scale up, run with human subjects, and revisit the visible harmlessness label—“Safe to Be Challenged”—as a trust intervention.

---

## Data Process [Slides 18–19]

*For anyone running experiments—here’s the data side.*

**Pilot.** MACSS thesis corpus. We cluster by embeddings, sample theses across clusters, so we’re not just computational vs qualitative. Three conditions, n per condition. Ground-truth weak dimensions for diagnostic accuracy.

**GitHub retrospective.** Three hundred forty-five memo comments. Forty-nine authors. Eight weeks. Seventeen authors had memos in both week two and week nine. We run our pipeline *retrospectively*—diagnose week two, generate a hypothetical plan, then an LLM judge rates week nine on those plan targets. The students never received the plans. This is ecological validation: does our competency framework map onto real growth in a real course? Mean improvement runs 3.2 to 4.2 by dimension. The heatmap shows per-author variation.

---

## Summary [Slide 20]

So: **It’s the student, not the thesis.** Personalized committees. Development plans. Pilot evidence that prescribed beats random. GitHub evidence that our dimensions align with observable improvement. Pipeline in place, ready to scale.

---

## Close [Slides 21–22]

Thank you. Repo, report, contact—all in the deck. And reproducibility: one notebook on Colab. Clone from GitHub, enable GPU, run the cells, download the zip before you disconnect. Everything’s there.

**[Pause. Smile. Open for questions.]**
