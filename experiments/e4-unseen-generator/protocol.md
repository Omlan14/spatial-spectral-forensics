# E4 — Unseen generator (H4)

**Status:** pending (protocol locked 2026-09-14; not yet run)

## What

Run the three arms with one entire **generator family held out** of training and
validation, on the clean condition.

- **Split:** generator held out (locked fold)
- **Condition:** C0 (standard PNG)
- **Answer shape:** separate rows per held-out generator, never only the overall average

## Why

Generator shift is a published, measured phenomenon: GAN-trained detectors get
worse on diffusion outputs. Testing on a generator never seen in training is the
standard procedure in this field.

## Prediction (locked before running)

Detection degrades relative to E1 on the held-out family.

## Decision rule (H4)

Read from the per-generator rows of E4/E5. Conclusions apply **only** to the
tested generator families (BigGAN, SD v1.4, ADM) — no claim of universality.

## Controls that run every time

1. Always-guess baseline.  2. History-only classifier.  3. Shuffled labels.

## Outputs

- Per-generator metrics -> `results/`
- Interpretation -> `analysis.md`
