# E1 — analysis (CONFIRMATORY)

**H1 supported.** C0, group split, 600 test parents. AUROC: pixel 0.666 [0.622, 0.707], frequency 0.752
[0.713, 0.792], combined 0.793 [0.759, 0.826]; all CIs exclude 0.5. Combined beats the best single arm
(frequency, chosen by validation AUROC) by +0.041 [0.018, 0.064].

Why: most of the pooled signal comes from BigGAN (combined 0.990), whose 128 px fakes are upsampled 2x
by the locked resize and lose high-band energy. SD v1.4 0.712 and ADM 0.678. The single strongest feature
is the spectral slope (f12, univariate AUROC 0.254, Cohen's d 1.07).

Controls: history-only 0.500; shuffled-label mean 0.507 (200 rounds); pre-receipt history 1.000
(exploratory, limitation 2). Tables: results/family_comparison.csv, results/per_feature_statistics.csv.
