# src — Reusable Code and Method

Shared code used across experiments. Experiment-specific code belongs in
`../experiments/{slug}/code/`; do not duplicate here.

## Contents

| File | What it is |
|---|---|
| `experimental-pipeline.md` | **The specification and method.** Stages 0-10 as a strict step-by-step flow: locked settings, stop-on-failure checks, and supporting papers. The code implements this stage by stage, and the report's Method section is written from it. |
| `pipeline-diagram.py` | Generates Figure 1 (`pipeline-diagram.png` / `.pdf`) from Section 4 of the pipeline. Self-checks layout and refuses to save if text overlaps or does not fit. Writes output next to the script. |
| `pipeline-diagram.png` / `.pdf` | Figure 1 output (regenerated from `pipeline-diagram.py`). |

## Planned shared modules

As the pipeline is implemented (Stages 1-10), reusable pieces land here so all
experiments import one implementation:

- data loading / provenance helpers
- the 14 feature extractors (Stage 6)
- classifier fitting and threshold selection (Stage 8)
- group-based bootstrap and effect-size statistics (Stage 9)
- plotting helpers for the report figures (Stage 10)

## Rule

One implementation, imported everywhere. If two experiments need the same
function, it lives here, not copied in each experiment directory.
