# Development Plan Examples (Result 5)

This document shows example development plans produced by the pipeline: gap map, exercises, and trajectory for 1–2 theses.

## Structure

Each development plan has three sections:

1. **Gap map** — List of competency gaps: dimension, current state, target state, priority.
2. **Exercises** — 2–4 concrete exercises (title, description, dimension) to address the gaps.
3. **Trajectory** — A short narrative (2–4 sentences) describing the recommended development path.

## Figure

See `validation_outputs/development_plan_example.png` for a full example.

## Interpretation

- The gap map is derived from the 6-dimension diagnostician output (scores and justifications).
- Exercises are generated to be actionable and dimension-specific (e.g., "Practice identifying scope conditions" for methodological_reasoning).
- The trajectory ties the exercises together into a coherent developmental arc.

## Example (abbreviated)

**Thesis:** A computational study of social media effects on polarization.

**Gap map:**
- methodological_reasoning: current "design choices under-specified" → target "explicit validity threats"
- theoretical_integration: current "pattern description" → target "connect to frameworks"

**Exercises:**
1. Scope conditions exercise — List 3 scope conditions for your design.
2. Theory mapping — Map your findings to one established framework.

**Trajectory:** Begin with methodological clarity, then integrate theoretical framing. Revisit evidence-claim alignment after each revision.

## How to Generate

```bash
uv run python run.py --development-plan-example
```

Or from the Colab notebook: run the "Result 5: Development plan example" cell.
