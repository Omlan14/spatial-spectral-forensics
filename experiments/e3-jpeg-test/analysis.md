# E3 — analysis (CONFIRMATORY)

Matched JPEG, both classes, refit per condition. Change from E1 (all generators): combined −0.007 / −0.003 /
+0.000 at q90 / q75 / q50; frequency +0.003 / +0.005 / +0.014; pixel −0.005 / −0.016 / −0.025 (CI excludes 0).

**H3 supported, in an unexpected form** (two separate verdicts):
- (a) stability: narrow f14 is the most stable frequency feature (median |Δ| 0.003 SD at q50); broad
  f08/f09/f10/f13 are stable (≤ 0.031 SD); broad f11 (Nyquist ratio) is the least stable of all 14 (0.393 SD).
- (b) separation: f14 never separates (0.497); broad f10/f08/f13 separate at every quality; f11 reverses
  direction (0.299 → 0.581 at q50), driven by BigGAN (0.009 → 0.772, exploratory).

Tables: results/jpeg_robustness.csv, results/per_feature_statistics.csv; figures/robustness_curves.png,
figures/stability_vs_separation.png.
