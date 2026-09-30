# Research Findings

## Research Question

With the same processing applied to both classes and a strict split by image
group, which simple feature set separates real photographs from AI-generated
images best: pixel-pattern features, frequency (spectrum) features, or both
combined? And how much does the answer change when (a) both classes are
JPEG-compressed, and (b) the test set uses an image generator the study never
trained on?

## Current Understanding

All five pre-registered experiments ran under the locked pipeline (config `87f5489e9d59`, one
owner-approved deviation to the shuffled-label control). All control checks pass. On GenImage
(BigGAN, ADM, SD v1.4; 3,000 parents), simple features separate real from generated images
(H1), and the combined 14-feature set is best in every setting, including the headline (E5: unseen
SD v1.4 + JPEG q75, AUROC 0.629 [0.571, 0.690]; pixel-pattern alone is at chance there). But the
pooled separation is dominated by one shortcut: BigGAN fakes are 128 px and the locked resize
upsamples them 2x, which empties the high band, so every high-frequency feature finds them almost
perfectly. On the two diffusion families the best simple set reaches only 0.63-0.76 AUROC.

## Key Results

| | pixel | frequency | combined |
|---|---|---|---|
| E1 all (C0) | 0.666 | 0.752 | 0.793 |
| E1 SD v1.4 / ADM / BigGAN | 0.581 / 0.591 / 0.824 | 0.637 / 0.624 / 0.997 | 0.712 / 0.678 / 0.990 |
| E3 q50 - E1 (all) | -0.025* | +0.014* | +0.000 |
| E4 SD v1.4 held out | 0.475 | 0.560 | 0.634 |
| E5 SD v1.4 held out, q75 (headline) | 0.465 | 0.568 | 0.629 |
| E4 - E1, SD v1.4 | -0.106* | -0.077* | -0.078* |

(* CI excludes 0.) Hypotheses: H1 supported; H2 partly supported (small change, mixed direction);
H3 supported in an unexpected form; H4 supported for SD v1.4; H5 not tested.
Full numbers: `reports/final_results.md`.

## Patterns and Insights

1. **Resizing history beats generation as a signal.** High-band features separate BigGAN at AUROC
   >= 0.97 (reversed direction) and ADM / SD v1.4 only at 0.33-0.59. Whatever the pipeline does to
   one family's pixel grid (here: 2x bicubic upsampling) becomes the dominant "detection" cue.
2. **Matched JPEG hardly matters once the classifier is refit.** Changes of <= 0.025 AUROC across
   q90-q50; the reals already carry JPEG history, so extra matched compression adds little.
3. **Feature meaning can flip under JPEG while the classifier score stays put.** The Nyquist-band
   ratio f11 reverses direction (0.299 -> 0.581 at q50) because JPEG block edges add near-Nyquist
   energy to the upsampled BigGAN images. "Value changed" and "classification changed" are indeed
   different findings (H3's two verdicts).
4. **Stable is not useful.** The narrow peak feature f14 is the most stable frequency feature and
   carries no signal at all (0.497).
5. **Arms are complementary on an unseen generator.** Pixel-pattern alone is at chance on held-out
   SD v1.4, yet adding it to the frequency set raises AUROC by +0.061 [0.028, 0.094].
6. **Training on more generators can hurt a seen one** (exploratory): removing SD v1.4 from
   training raised ADM AUROC by +0.071 (combined), +0.115 (frequency).

## Lessons and Constraints

Pre-registration constraints (unchanged): stages in order; locked values never changed after
results; group splits; scalers/C/thresholds fit on train/val only; group bootstrap; claim wording
rules ("the separation changed after the controlled change"; "no retrieved abstract reports this
exact protocol").

Learned during execution:
- A single shuffled-label run is not a usable gate when features are informative (SD ~0.09 AUROC);
  use the mean of many shuffles (deviation 1).
- GenImage ADM PNGs are RGBA with fully opaque alpha; "transparency" must test alpha values, not mode.
- ~10% of ImageNet reals carry non-sRGB ICC profiles (Camera RGB, Adobe RGB); they are excluded.
- GenImage's real/fake file facts (JPEG vs PNG, sizes) separate the classes perfectly; any
  GenImage study must report per-generator rows and pre-receipt history.
- On Windows, always pass encoding="utf-8" when scripts write text files.

## Exploratory post-hoc diagnostic (2026-09-30) — the final framing

Giving every image the same resampling history (native 128 crop + one shared 2x bicubic; BigGAN
pixels identical to C0) leaves pooled combined AUROC unchanged (0.796 -> 0.802, delta +0.006
[-0.036, 0.045]) but moves per-generator AUROC from -0.17 (BigGAN, frequency) to +0.30 (unseen SD,
pixel: 0.477 -> 0.771) and removes the frequency arm's advantage (pixel - frequency -0.088 -> +0.022).
Fixed C0 models on JPEG test images: pooled AUROC change <= 0.027, but the pixel model's false
positives on reals go 98 -> 157 of 300 at q50. Framing: *same score, different story* — resampling
history is part of the result. Caveat: for non-BigGAN classes R also narrows the field of view.
Evidence: `results/diagnostics/history_diagnostics.csv`; paper `paper/final/`.

## Open Questions

- How much of the diffusion-family separation (0.63-0.76) survives content matching (H5)?
- Would a resize policy that never enlarges (e.g. crop-only at native resolution) remove the BigGAN
  shortcut? (Would change a locked value; not run.)
- Does the ADM/SD interference hold with other held-out folds (rotation was cut)?
- Before stronger novelty wording: full reads of Grommelt et al. [1] and Sato et al. [10] are required.

## Optimization Trajectory

Not an optimization study: one pre-registered run per experiment (E1-E5 x 3 arms), no tuning
beyond the locked C grid. Trajectory entries are in `research-state.yaml`.
