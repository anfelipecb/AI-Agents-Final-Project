# Feedback Comparison (Result 4)

**C3 feedback is more targeted than C1.**

This document summarizes Result 4: a side-by-side comparison of feedback from Condition 1 (single agent) vs Condition 3 (prescribed committee).

## Setup

For 2–3 theses sampled by embedding cluster:

- **C1 (single agent):** One generic advisor reviews the thesis and produces feedback.
- **C3 (prescribed committee):** The thesis is diagnosed on 6 competency dimensions; a committee of 3 agents is assembled to cover the weakest dimensions; each agent reviews independently; feedback is synthesized.

## Findings

- **C1 feedback** tends to be generic and evenly distributed across dimensions (methodology, theory, clarity, etc.).
- **C3 feedback** is more targeted: the Methodologist focuses on design and validity, the Theorist on conceptual integration, the Devil's Advocate on challenges, etc. The deliberation excerpt shows distinct, persona-specific perspectives before synthesis.

## Figures

- `validation_outputs/feedback_comparison_thesis_{id}.png` — Side-by-side C1 vs C3 feedback text.
- `validation_outputs/deliberation_thesis_{id}.png` — Deliberation excerpt (agent names + truncated reviews) showing that the committee produces distinct, persona-specific feedback.

## How to Generate

```bash
uv run python run.py --side-by-side
```

Or from the Colab notebook: run the "Result 4: Side-by-side feedback (C1 vs C3)" cell.
