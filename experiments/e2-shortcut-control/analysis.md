# E2 — analysis (CONTROL, not a detection result)

**H2 partly supported.** The separation changed after the controlled change (reals JPEG q75, fakes PNG):
E2 − E1 frequency +0.017 [0.009, 0.025], combined +0.012 [0.007, 0.017] (predicted direction), pixel
−0.026 [−0.038, −0.015] (opposite direction). The file-history classifier separates E2 perfectly (1.000),
yet the content features gain at most 0.017: the reals already carry JPEG history before the mismatch is
applied, so the extra compression adds little new difference.

Lesson: in this data the shortcut is already present at C0 (pre-receipt history AUROC 1.000), so C2 is a
weak lever. Table: results/family_comparison.csv (rows 'E2 - E1', 'E2 - E3_q75').
