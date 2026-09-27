# Stage 8 stop — shuffled-label control (2026-09-27)

The full run stopped: single-shuffle test AUROC was E1 0.623, E2 0.268 (tolerance ±0.1).

Diagnosis (`shuffle_diag.py`, run from `src/`):
- Features for 10 random test rows recomputed from their files: identical. Labels match `splits.csv`.
- 200 shuffles, E1: mean AUROC 0.512, SD 0.092; 33% of single shuffles fall outside ±0.1.
- 200 shuffles, E2: mean 0.514, SD 0.091. Random untrained directions: mean ~0.507, SD ~0.10.

Cause: a classifier fit on shuffled labels is a random direction; with informative features a single
random direction has AUROC far from 0.5 in either sign. The control is unbiased on average but a
single draw cannot gate. Not an indexing error. Pipeline held at Stage 8 pending a decision.
