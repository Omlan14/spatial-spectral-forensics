# E5 — Main result (H4)

**Status:** pending (protocol locked 2026-09-14; not yet run)

## What

Run the three arms on the **held-out generator** under **JPEG quality 75** — the
study's headline: unseen generator and JPEG together.

- **Split:** held-out generator (same locked fold as E4)
- **Condition:** C1 at the middle quality (75)
- **Answer shape:** per-generator and per-quality rows; paired arm differences on
  the same resampled groups

## Why

E5 is the core result the study is built around; E1-E4 support it. It combines
the two stresses this study tests: generator shift and matched JPEG compression.

## Prediction (locked before running)

Separation is lower than E1 (both stresses at once). The combined arm is not
assumed to be the best; the paired arm differences decide (pixel-pattern −
frequency; combined − best single).

## Decision rule (H4)

Per-generator rows only; claims limited to the tested families and qualities.

## Controls that run every time

1. Always-guess baseline.  2. History-only classifier.  3. Shuffled labels.

## Outputs

- Headline metrics, per-generator breakdown -> `results/`
- Interpretation -> `analysis.md`; feeds the conclusion template
  (`../src/experimental-pipeline.md` Section 10).
