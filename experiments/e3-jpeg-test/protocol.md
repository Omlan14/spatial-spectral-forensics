# E3 — JPEG test (H3)

**Status:** pending (protocol locked 2026-09-14; not yet run)

## What

Run the three arms on condition **C1**: both classes re-saved as JPEG at the
three locked qualities (90, 75, 50), from the same standard stage, with the same
pinned encoder and 4:2:0 subsampling.

- **Split:** by image group (locked)
- **Condition:** C1 at qualities 90, 75, 50
- **Answer shape:** per-quality rows, never only averages

## Why

In the real world almost every image has been through JPEG at some point. C1
makes the compression test **fair** (same treatment for both classes) instead of
accidental, and measures whether the features survive it.

## Prediction (locked before running)

Separation changes under compression. Broad-spectrum frequency features
(8-11, 13) are expected to be more **stable** than the narrow peak feature (14),
but the literature marks this as unsettled, so it is tested, not assumed.

## Decision rule (H3)

**Two separate verdicts, never merged:**
- (a) how much the feature values change (stability);
- (b) whether classification still works (separation).

H3 can hold for one and not the other. Broad = features 8-11 and 13; narrow = feature 14.

## Controls that run every time

1. Always-guess baseline.  2. History-only classifier.  3. Shuffled labels.

## Outputs

- Per-quality metrics, per-feature C0->C1 within-parent change -> `results/`
- Interpretation -> `analysis.md`
