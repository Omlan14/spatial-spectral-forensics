# Stage 7 — Pilot gate report

config `0cbe77dcdb19`; split hash `386ffeaa…e89e89`; run 2026-09-27.

**Pilot subset:** 200 parents per class (400 total), drawn with split seed 2026 from the locked
split (`splits.csv`, `pilot = 1`). It is a subset of the final split and will not change.

**Ran:** E1 (C0) and E3 at quality 75, three arms, all three control checks.

**Timings (this CPU):** Stages 2–5, ~30 s; Stage 6 (12,000 files), 129 s; pilot, 8 s.

## Checks

| Check | Result |
|---|---|
| no group crosses train / val / test; one row per test group | pass (E1, E3_q75) |
| history-only (file actually analysed) AUROC ≈ 0.5 | pass: 0.500 / 0.500 |
| shuffled labels AUROC ≈ 0.5 (pilot tolerance ±0.2, ~80 test images) | pass: 0.619 / 0.552 |
| always-guess baseline | 0.5 (reference) |

**Decision: GO.** No leakage, misalignment, or failed control.

## Oddities recorded (not stop conditions)

1. **Pre-receipt history is a perfect shortcut (exploratory control).** A classifier on the
   *original* file facts (format, width, height) scores AUROC 1.0: every GenImage real is an
   ImageNet JPEG of varying size, and every fake is a fixed-size PNG (BigGAN 128, ADM 256,
   SD v1.4 512). Standard pre-processing removes these facts from the analysed files (history-only
   check = 0.5), but it does not undo their effect on pixels [1], [2]. This is a limitation of the
   data source, carried to `limitations.md`.
2. **Spectral-slope fit is poor for a few images.** Slope R² < 0.8 for 30 of 3,000 C0 images
   (15 SD v1.4, 11 real, 3 BigGAN, 1 ADM). Median R² is 0.93 (BigGAN) to 0.99 (ADM). No image was
   removed (Stage 2 rule: never remove on a feature value); R² is kept in `features.parquet`.
3. **BigGAN fakes are upsampled 2× by the locked resize** (128 → 256, bicubic). This is the only
   generator that is enlarged. Its lower median slope R² is consistent with this; per-generator rows
   will show whether it dominates.
