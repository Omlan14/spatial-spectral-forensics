# Final results

config `87f5489e9d59`; code `git log` at the `research(results)` commit; seeds split 2026, bootstrap
20260914 (1,000 group-resampling rounds). One locked test set of 600 parents (300 real, 100 per
generator) is shared by E1–E5, so every difference below is paired on the same image groups.
Read `limitations.md` first. Tables: `results/*.csv`; figures: `figures/*.png`.

AUROC treats generated as the positive class; brackets are 95% group-bootstrap CIs.

## Control checks (all pass)

| Experiment | always-guess | history-only | shuffled labels (mean of 200) | pre-receipt history (exploratory) |
|---|---|---|---|---|
| E1, E3 (×3), E4, E5 | 0.500 | 0.500 | 0.503–0.521 | 1.000 |
| E2 (mismatch) | 0.500 | **1.000** (the mismatch is visible, as designed) | 0.517 | 1.000 |

## E1 — first check (H1)

| Arm | AUROC | Balanced acc. |
|---|---|---|
| pixel-pattern (1–7) | 0.666 [0.622, 0.707] | 0.612 |
| frequency (8–14) | 0.752 [0.713, 0.792] | 0.685 |
| combined | 0.793 [0.759, 0.826] | 0.700 |

Paired: pixel − frequency −0.087 [−0.130, −0.046]; combined − frequency +0.041 [0.018, 0.064].
Per generator (combined): BigGAN 0.990, SD v1.4 0.712, ADM 0.678.

**H1: supported.** All three arms have CIs excluding 0.5. The pooled numbers are driven heavily by
BigGAN (limitation 3).

## E2 — shortcut control (H2; control, not a detection result)

Paired change E2 − E1: frequency +0.017 [0.009, 0.025], combined +0.012 [0.007, 0.017], pixel
−0.026 [−0.038, −0.015]. E2 − E3 q75: frequency +0.012 [−0.001, 0.023], combined +0.015
[0.008, 0.023], pixel −0.011 [−0.021, −0.000].

**H2: partly supported.** For the frequency and combined arms the separation changed after the
controlled change in the predicted (inflating) direction, but by ≤ 0.017 AUROC; for the pixel arm it
changed in the opposite direction. The file-history classifier sees the mismatch perfectly (1.000),
yet the 14 content features barely exploit it, most plausibly because the reals already carry JPEG
history before the mismatch is applied (limitation 2).

## E3 — matched JPEG (H3 and robustness)

Paired change from E1, all generators:

| Quality | pixel | frequency | combined |
|---|---|---|---|
| q90 | −0.005 [−0.007, −0.002] | +0.003 [−0.001, 0.007] | −0.007 [−0.014, −0.000] |
| q75 | −0.016 [−0.025, −0.007] | +0.005 [−0.004, 0.015] | −0.003 [−0.012, 0.006] |
| q50 | −0.025 [−0.040, −0.011] | +0.014 [0.002, 0.026] | +0.000 [−0.011, 0.011] |

The pixel arm lost a little separation as quality fell; the frequency and combined arms did not lose
separation (the classifier is refit on each condition, limitation 8).

**H3 — two separate verdicts (broad = 8–11, 13; narrow = 14):**

- *(a) Stability of feature values* (median |C1 − C0| within parent, C0 SD units, q50):
  broad f08 0.010, f09 0.006, f10 0.031, f13 0.009, but **f11 0.393**; narrow f14 **0.003**.
  The narrow peak feature is the most stable frequency feature; the broad group is stable except the
  Nyquist-band ratio f11, which is the least stable of all 14 features.
- *(b) Separation* (univariate AUROC, all parents): the narrow f14 does **not** separate at any
  quality (0.497 [0.48, 0.52] at C0 and at every quality). Broad features do: f10 0.291 → 0.301
  (q50), f08 0.563, f13 0.552, stable across quality. f11 **reverses direction** under compression:
  0.299 (C0) → 0.326 (q90) → 0.425 (q75) → 0.581 (q50). Exploratory: the reversal comes from BigGAN
  (0.009 → 0.772), consistent with JPEG 8×8 block edges adding near-Nyquist energy to upsampled images
  that had almost none.

**H3: supported, in a form not predicted.** Broad and narrow features behave differently on both
verdicts, but not as "broad more robust than narrow": the narrow feature is stable because it carries
no signal here, and the broad group's one unstable member (f11) changes its meaning under JPEG.

## E4 / E5 — unseen generator (H4); E5 is the headline

SD v1.4 fakes held out of training; per-generator test rows:

| | SD v1.4 (unseen) | ADM (seen) | BigGAN (seen) | all |
|---|---|---|---|---|
| E4 combined (C0) | 0.634 [0.578, 0.695] | 0.749 | 0.984 | 0.789 [0.755, 0.823] |
| E4 frequency | 0.560 [0.495, 0.627] | 0.738 | 0.995 | 0.765 |
| E4 pixel | 0.475 [0.422, 0.541] | 0.566 | 0.919 | 0.653 |
| **E5 combined (q75)** | **0.629 [0.571, 0.690]** | 0.761 | 0.969 | **0.786 [0.753, 0.820]** |
| E5 frequency | 0.568 [0.505, 0.637] | 0.757 | 0.981 | 0.769 |
| E5 pixel | 0.465 [0.410, 0.527] | 0.540 | 0.888 | 0.631 |

Paired change for SD v1.4 when it is held out (E4 − E1): combined −0.078 [−0.124, −0.034],
frequency −0.077 [−0.132, −0.026], pixel −0.106 [−0.149, −0.065]; at q75 (E5 − E3 q75): combined
−0.075 [−0.116, −0.034]. On the unseen SD v1.4 fakes, combined beats frequency by +0.061
[0.028, 0.094] (E5), although the pixel arm alone is at chance.

**H4: supported for SD v1.4.** Separation of SD v1.4 fakes fell when that family was not in training,
for all three arms; the pixel arm fell to chance. Exploratory: ADM separation *rose* when SD v1.4 was
removed from training (combined +0.071 [0.038, 0.104]; frequency +0.115), suggesting the two diffusion
families pull the linear boundary in different directions. Claims apply only to the tested families.

## H5 — not tested (limitation 5).

## Conclusion (template, Section 10)

> For the tested generator families (BigGAN, SD v1.4, ADM) and JPEG conditions (quality 90, 75, 50),
> the combined feature set gave the best separation on unseen data (E5, unseen SD v1.4 at JPEG q75:
> AUROC 0.629, 95% CI 0.571–0.690; all test generators: 0.786, 0.753–0.820), ahead of the frequency
> set (0.568, 0.505–0.637) and the pixel-pattern set (0.465, 0.410–0.527, not above chance). Its
> performance changed as follows under compression: by at most −0.007 AUROC (all generators, q90–q50,
> refit per condition) and −0.004 on the held-out generator (E5 − E4); and on the unseen generator:
> −0.075 (−0.116 to −0.034) relative to training with that family. These results apply only to the
> sampled images and processing conditions.

Because of limitations 2 and 3, the strong pooled separation should not be read as evidence that
these features detect generation itself: on the two diffusion families without resizing artifacts,
the best simple feature set reaches only 0.63–0.76 AUROC in the headline setting (E5), and
0.68–0.71 when every family is seen in training (E1).
