# E1 — First check (H1)

**Status:** pending (protocol locked 2026-09-14; not yet run)

## What

Run all three feature arms (pixel-pattern, frequency, combined) with the single
locked classifier (L2 logistic regression) on the clean condition, split by
image group.

- **Split:** by image group (locked, hashed)
- **Condition:** C0 (standard PNG)
- **Arms:** pixel-pattern (features 1-7), frequency (8-14), combined
- **Answer shape:** one comparison table (three arms x AUROC / balanced accuracy)

## Why

This is the first check: does any signal exist at all before we interpret
anything else. No paper retrieved establishes a universal winner between simple
feature sets under one fair procedure, so this is a measurement, not a novelty claim.

## Prediction (locked before running)

At least one arm shows a confidence interval (group-based bootstrap) excluding
chance (AUROC 0.5). The combined arm is **not** assumed to beat the best single
arm; feature redundancy between the arms would make that possible.

## Decision rule (H1)

H1 is **supported** if at least one arm shows clear separation in E1 (CI
excluding chance). Reported as one table.

## Controls that run every time

1. Always-guess baseline (must be beaten).
2. History-only classifier (must be near-random after standard pre-processing).
3. Shuffled-labels (test AUROC approx 0.5).

## Outputs

- Per-image predictions, per-arm metrics, thresholds -> `results/`
- Interpretation -> `analysis.md`
