# Limitations (written before the conclusions)

config `87f5489e9d59` (Stage 0 lock + deviation 1); split hash `386ffeaa…e89e89`.

1. **Scope of the sample.** 3,000 parents (500 real + 500 generated per GenImage subset: BigGAN,
   ADM, SD v1.4), GenImage `val` folder only, three JPEG qualities (90, 75, 50), one Pillow encoder
   (4:2:0). Nothing is claimed about other generators, datasets, encoders, or processing.

2. **Pre-receipt history is a perfect shortcut in this data.** Every real is an ImageNet JPEG of
   varying size; every fake is a fixed-size PNG (BigGAN 128², ADM 256², SD v1.4 512²). A classifier
   on these original file facts alone reaches AUROC 1.0 in every experiment (exploratory control in
   `results/control_checks.csv`). Standard pre-processing removes the facts from the analysed files
   (history-only check = 0.500), but not their effect on pixels [1], [2]. Every separation reported
   here may partly measure prior JPEG compression of the reals and resizing of the fakes, not
   generation.

3. **BigGAN is enlarged 2× by the locked resize, the other fakes are not.** Bicubic 128 → 256 leaves
   almost no energy above 0.25 cycles/pixel. BigGAN fakes are near-perfectly separated by every
   high-frequency feature at C0 (univariate AUROC 0.004–0.03, i.e. ≥ 0.97 in the reversed
   direction) while ADM and SD v1.4 are not (0.33–0.59). Pooled ("all generators") numbers
   are therefore inflated by BigGAN; per-generator rows are the ones to read.

4. **One unseen-generator fold.** Only SD v1.4 is held out (locked; fold rotation was cut, pipeline
   Section 11). "Generator shift" results describe one family, not a general law.

5. **Content bias (H5) is not tested.** Reals and fakes are not content-matched (ImageNet classes are
   shared, but not individual scenes); part of any separation may be content [3], [2].

6. **Control-check deviation.** The shuffled-label control was changed after the first full run
   stopped on it (deviation 1, owner-approved): 200 shuffles judged on the mean instead of one
   shuffle. The diagnosis showed no indexing error (`results/diagnostics/shuffle_control.md`).
   The pilot used a single shuffle. No feature, split, classifier, or metric was changed.

7. **Feature-definition details fixed at Stage 0.** Where the specification left freedom (mean
   removal before the Hann window, radial-average slope fit, coefficient of variation for anisotropy,
   3×3 local maximum for the peak), one choice was locked before data. Other reasonable choices may
   give different numbers. The slope fit is poor (R² < 0.8) for 30 of 3,000 C0 images.

8. **Matched JPEG is train-and-test matched.** In E3/E5 the classifier is refit on the compressed
   condition, so "robustness" means *the recipe still works after refitting*, not that a C0 model
   transfers to compressed images.

9. **Sampling from a mirror.** Images were streamed from the `nebula/GenImage-arrow` Hugging Face
   mirror (fallback step b) with a content-blind hash rule, not downloaded from the official archive;
   the mirror's fidelity to the original files was not independently verified beyond format and size.
