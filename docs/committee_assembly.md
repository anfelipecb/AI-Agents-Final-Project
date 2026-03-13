# Committee Assembly Validation (Step 2)

**Different profiles trigger different committees.**

This document describes the Step 2 validation: given a thesis, we run the 6-dimension diagnostician to obtain a competency profile, then assemble a committee of 3 agents from the persona pool based on the lowest-scoring dimensions. Different theses produce different profiles, which in turn yield different committee compositions.

## Figure

See `validation_outputs/committee_assembly_demo.png` for the committee assembly demo figure.

The figure shows 2–3 theses side by side:

- **Left panel (per thesis):** Bar chart of the 6 competency scores (argument_construction, evidence_evaluation, methodological_reasoning, theoretical_integration, self_reflexivity, receptivity_to_critique).
- **Right panel (per thesis):** The assembled committee—3 agent names selected to cover the weakest dimensions.

## Example Theses

When we sample theses by embedding cluster (e.g., from the MACSS corpus), we observe:

1. **Thesis A** (e.g., methods-heavy): Low scores on theoretical_integration and self_reflexivity → Committee: Theorist, Encourager, plus one other.
2. **Thesis B** (e.g., theory-heavy): Low scores on methodological_reasoning and evidence_evaluation → Committee: Methodologist, Devil's Advocate, Clarity Coach.
3. **Thesis C** (e.g., descriptive): Low scores on argument_construction and receptivity_to_critique → Committee: Clarity Coach, Devil's Advocate, Theorist.

This validates that the committee assembly logic correctly maps competency gaps to targeted agent personas.

## How to Generate

```bash
uv run python run.py --committee-assembly-demo
```

Or from the Colab notebook: run the "Result 3: Committee assembly demo" cell.
