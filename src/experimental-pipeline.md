# Experimental Pipeline and Methodology

**Course project:** Interpreting Spatial–Frequency Features for AI-Generated Image Detection Under Generator Shift and JPEG Compression
**Version 1.0, locked 2026-09-14.**

This single document is both the plan and the method: the code follows it stage by stage, and the report's Method section is written from it. The 20 references ([1]–[20]) are listed in `literature-review.md`.

**Main research question (locked):**

> With the same processing applied to both classes and a strict split by image group, which simple feature set separates real photographs from AI-generated images best: pixel-pattern features, frequency (spectrum) features, or both combined? And how much does the answer change when (a) both classes are JPEG-compressed, and (b) the test set uses an image generator the study never trained on?

**What this study is:** careful measurements of simple, explainable image statistics.
**What it is not:** a new detector, a comparison against the best published methods, or a claim about all AI images.

**Companion documents:** `literature-review.md` (the 20-paper reference set; numbers in brackets refer to it), `references.bib`, and the figure files `pipeline-diagram.png` / `.pdf` (Figure 1).

---

## 1. How to run this study (rules)

1. **Stages run in order, 0 to 10.** No stage is skipped. Each stage uses only the previous stage's output as input, with no side paths.
2. **Stop on a failed check.** Every stage lists automatic checks. If one fails, the pipeline stops and the problem is fixed before anything later runs. Checks are never edited to make them pass.
3. **Locked values.** Values marked `LOCK` are decided once, at Stage 0, written into `config.yaml`, and never changed after results are seen. Values marked `SUGGESTED` are this document's proposals; the team may replace them at Stage 0 with a written reason, but not later.
4. **Every change is written down.** Any change to this document after the pilot gate (Stage 7) needs a dated entry in `config.yaml` under `deviations:`, saying what changed and why. Undocumented changes make the affected results invalid.
5. **Every result is traceable.** Every reported number records the config hash, the code version, and the random seeds that produced it.
6. **Claim only what the data shows.** The rules in Section 9 and the conclusion template in Section 10 are required.

**Words we use in this document (plain meanings):**

| Word | Meaning |
|---|---|
| Parent image | One original picture, before any processed copies are made from it |
| Variant | A processed copy of a parent image (standard PNG, a JPEG version, or a deliberate-mismatch version) |
| Arm | One feature set: pixel-pattern only, frequency only, or both combined |
| Condition | How an image was processed: C0, C1, or C2 (defined in Stage 5 below) |
| Group | One parent image together with all its variants and near-copies. Groups must never be split across train/validation/test |
| Locked | Decided in advance, before results, and never changed after |

---

## 2. Stage 0: Lock the configuration

**In plain terms.** Before touching any image, the whole study is written down in one configuration file: which dataset, how many images, which generators, what image size, which features, which classifier settings, which random seeds. This is the promise that later results are judged against. Writing it down first keeps the study honest: after we see results, we cannot quietly turn a knob to get a nicer number.

**Inputs:** none (a decision).
**Outputs:** `config.yaml`, saved to the repository. Its hash is printed in every later stage's log and in the report.

**Locked content:**

```yaml
dataset: GenImage                      # subsets: biggan, sd_v1_4, adm + imagenet reals   [13]
quota: 1500 real / 1500 fake           # 500 fake per generator, 3 generators
pilot: 200 parent images per class
generators: [biggan, sd_v1_4, adm]     # 1 GAN family + 2 diffusion families
image_size: 256                        # shorter side 256, center crop 256x256
resize_kernel: bicubic                 # one kernel, both classes
standard_format: lossless PNG          # JPEG exists only as condition C1/C2
jpeg_qualities: [90, 75, 50]           # 3 qualities, locked before results
jpeg_encoder: LOCK                     # pinned library + version; 4:2:0 subsampling
features: 14 (Section 5)
classifier: L2 logistic regression; C in {0.01, 0.1, 1, 10}
metrics: AUROC; balanced accuracy at the validation-selected threshold
splits: one locked split by image group + one unseen-generator fold
seeds: split 2026; bootstrap 20260914
```

**Why three generators:** BigGAN (one GAN family) plus Stable Diffusion v1.4 and ADM (two diffusion pipelines) is the smallest set that lets us train on two families and test on a third that was never seen. Substitutions (for example GLIDE, Wukong, SD v1.5) are allowed **only** at Stage 0, written into the config before any split is made.

**Values fixed at Stage 0** (all `LOCK`; the suggestions below are the defaults):

| Value | Suggested setting | Why this choice |
|---|---|---|
| FFT window | 2D Hann window applied to the luminance channel; features use the power spectrum | Prevents edge effects, so band energies describe the image, not the rectangle |
| Band edges (features 8–11) | low = (0, 0.05], mid = (0.05, 0.25], high = (0.25, 0.5] cycles/pixel; top band (feature 11) = (0.375, 0.5]; DC excluded | Splits the spectrum into coarse structure, texture, and fine detail |
| Spectral slope fit (feature 12) | log power vs log radius, least squares over the locked mid+high range; DC and r < 2/256 excluded; report R² | The fit range and excluded bins are written down so the number can be reproduced |
| Anisotropy (feature 13) | energy variation across 12 angular sectors of 30° inside the locked mid band | A fixed sector count keeps the number comparable across images |
| Peak concentration (feature 14) | largest non-DC local maximum / total non-DC power | One fixed rule; no per-image tuning |
| High-pass residual (feature 7) | residual after a 3×3 binomial [1,2,1]⊗[1,2,1]/4 blur | One fixed kernel, different from the Laplacian |
| Luminance values | float, range [0, 1] | One numeric convention for all statistics |
| JPEG encoder | one pinned library and version, 4:2:0 stated in the report | "Same compression" is only true if the encoder is fixed |

---

## 3. The strict flow: overview

Every stage is specified in Section 4 with the same six parts: **In plain terms** (why it matters, in everyday words), **Inputs**, **Outputs**, **Locked settings**, **Checks (stop on failure)**, and **Why this stage is here** (which papers support it).

```
Stage 0   Lock the configuration
Stage 1   Download and record   -> source list (where each image came from)
Stage 2   Check the data        -> duplicate and near-copy lists, exclusions
Stage 3   Split by image group  -> split file + hash (plus one unseen-generator fold)
Stage 4   Standard pre-processing -> one standard PNG per parent image + record
Stage 5   Make conditions       -> C0 / C1 (qualities 90, 75, 50) / C2 variant list
Stage 6   Extract features      -> features table + extraction report (unit tests first)
Stage 7   Pilot gate            -> go / no-go on ~200 parent images per class
Stage 8   Run experiments       -> E1–E5 × 3 arms + control checks -> predictions
Stage 9   Statistics            -> effect sizes, confidence intervals, per-feature change
Stage 10  Report                -> figures, tables, careful conclusion, limitations
```

Figure 1 (`pipeline-diagram.png`) shows the data and experiment flow (Stages 1–6 and 8–10, plus the three arms and the classifier). Stage 0 (config lock) and Stage 7 (pilot gate) are process controls described in Sections 2 and 4, and are deliberately not drawn. If the figure and Section 4 ever disagree, Section 4 is correct and the figure is regenerated.

---

## 4. Stage-by-stage specification

### Stage 1: Download and record

**In plain terms.** We download the images exactly as the dataset provides them and record, for every file, where it came from and what is known about it. Nothing is edited yet. If a fact is unknown (for example, whether a file was JPEG-compressed before we got it), we write "unknown". We never guess, because a wrong fact here becomes a wrong conclusion later.

**Inputs:** `config.yaml`.
**Outputs:** raw images on disk; `data/provenance.csv`, one row per original file:

```text
image_id, original_path, original_sha256, parent_id, group_id, label,
generator_family, generator_checkpoint, source_dataset, original_width,
original_height, original_format, exif_present, known_jpeg_quality,
known_processing_history, license_note
```

**Locked settings:** dataset and quota from Section 2.
**Checks (stop on failure):**
- Missing values are written as `unknown`. Empty cells are a bug and stop the stage.
- **Fallback plan if the download is blocked or too large** (choose at Stage 0 and write down which step was used): (a) authorized GenImage download; (b) partial download or streaming, to get the needed number of images without storing the full archives; (c) switch to the fallback dataset AI-GenBench [14]; (d) only if (a)–(c) cannot supply enough images, reduce to two generators (one for training, one unseen for testing) and record the smaller claim in the report's limitations.
**Why this stage is here:** results go wrong when nobody checks where images came from and how they were processed before [1], [2].

### Stage 2: Check the data (sources, duplicates, exclusions)

**In plain terms.** Before trusting any measurement, we check what each file actually is and whether the same picture (or a near-copy) appears more than once. This matters because if a copy of the same image ends up in both training and test data, the classifier can simply recognise the copy, and the score looks great for the wrong reason.

**Inputs:** `provenance.csv`, raw images.
**Outputs:** `data/duplicate_clusters.csv`; exclusion list with reasons; updated `parent_id` / `group_id`.
**Locked settings:** one perceptual hash (a fingerprint of how an image looks) with one threshold, locked during the pilot, applied the same way to both classes.
**Checks (stop on failure):**
- Exact copies: SHA-256 over original bytes.
- Pixel-level copies: hash of the decoded pixel array (catches the same picture saved in a different format).
- Near-copies: one fixed perceptual hash; threshold locked on the pilot; a sample is inspected by hand.
- Exclusion rules are applied **before** looking at how well classes separate: remove unreadable files, images with transparency or strange profiles, and duplicates. An image is **never** removed because its feature value looks unusual.
**Why this stage is here:** duplicate and history-related leakage inflate results; this is a documented failure mode of generated-image benchmarks [1], [2].

### Stage 3: Split by image group (locked and hashed)

**In plain terms.** We divide the images into training, validation, and test sets so that everything made from one picture stays on one side of the wall. Then we lock the division and take its fingerprint (a hash), so it cannot quietly change later. A separate fold also holds out an entire generator family: that is how we test whether a classifier trained on BigGAN and ADM recognises SD v1.4 images it has never seen.

**Inputs:** checked data list with `parent_id` / `group_id`.
**Outputs:** `data/splits.csv`; `data/split_hash.txt`; both locked.
**Locked settings:** split seed 2026; equal label counts in every split; one unseen-generator fold.
**Checks (stop on failure):**

```text
every parent image appears in exactly one split
the unseen generator appears in neither training nor validation data
no parent image and none of its variants crosses a split boundary
both classes appear in every split
```

**Why this stage is here:** testing on an unseen generator is only meaningful when groups and generators are kept strictly separate [1], [2], [11]; benchmark designers treat unseen-generator testing as the standard [13], [14].

### Stage 4: Standard pre-processing

**In plain terms.** All images are brought into exactly the same form: same colour handling, same brightness channel, same size, same lossless format, by one script. The aim is that nothing about the *file* tells the classifier which class an image belongs to. Without this step, a classifier can cheat by reading the file format or the image size instead of the picture content.

**Inputs:** split list.
**Outputs:** one standard PNG per parent image; `data/canonical_manifest.csv` (SHA-256 per file, so we can prove every later step used these exact images).
**Locked settings:** one pinned decoding library; EXIF orientation applied exactly once; sRGB; float32 luminance Y; resize shorter side to 256 (bicubic); center crop 256×256; metadata removed; lossless PNG.
**Checks (stop on failure):**
- This script is the **only** path to feature extraction. Extracting features from any other image version is forbidden.
- Settings are exactly the same for both classes; a log records library versions.
- Every file is tagged `final_transform` or `known_prior_history`. **Caveat for the report:** processing the files the same way now does not erase what happened to them earlier. A photograph that was JPEG-compressed before we received it is still damaged after we save it as PNG [1], [2].
**Why this stage is here:** format, size, and compression differences are measurable shortcuts a classifier can exploit [1]; matching the final format is not the same as matching the full history [2].

### Stage 5: Conditions (C0, C1, C2)

**In plain terms.** From each standard image we make the different versions the study compares. C0 is the clean copy. C1 is the same image saved as JPEG at three fixed qualities. In the real world almost every image has been through JPEG at some point, so C1 asks a simple question: do our features survive it? C2 is a deliberately unfair version, where the two classes get *different* treatment. It exists only to show how easily a careless pipeline can "detect" processing instead of content. C2 is a control, never a result.

**Inputs:** standard PNGs.
**Outputs:** `data/variant_manifest.csv`: every variant tagged with `parent_id`, `condition`, `encoder`, `quality`, `sha256`.

| ID | Definition | Role |
|---|---|---|
| C0 | the standard PNG image | main condition |
| C1 | both classes re-saved as JPEG at quality 90, 75, and 50, same encoder and settings | the JPEG test (E3, E5) |
| C2 | deliberate mismatch: one class gets a different format/quality, on purpose | control only, to show the shortcut; never reported as a detection result |

**Locked settings:** the three JPEG qualities; the pinned encoder and version; 4:2:0 stated.
**Checks (stop on failure):** every variant comes from the standard image, never from another variant (no re-saving a JPEG of a JPEG).
**Why this stage is here:** JPEG and size differences alone can look like detection evidence [1]; JPEG compression measurably lowers how well artifact-based detectors work [11]. C1 makes the compression test fair (same treatment for both classes) instead of accidental.

### Stage 6: Features (14 numbers per image)

**In plain terms.** Each image is reduced to fourteen numbers that describe simple, explainable properties. Seven describe the picture itself: how spread out the light and dark values are, how strong and how even the edges are, how much fine detail exists. Seven describe its frequency content: how energy is spread from coarse shapes to fine detail, the slope of that falloff, whether it leans in some direction, and whether one single frequency stands out. Using fourteen explainable numbers instead of a black-box network is what lets the study say *which kind* of property carries the signal, and which properties survive compression.

**Inputs:** variant list (C0 and C1 rows; C2 only for the control experiment).
**Outputs:** `features/features.parquet`; `features/feature_dictionary.csv`; `features/extraction_report.md`.
**Locked settings:** the 14 features as defined in Section 5, with the Stage 0 lock table applied; fixed Hann window; power spectrum stated.
**Checks (stop on failure), run on synthetic test images before any real data:**

```text
constant, impulse, edge, checkerboard, and sinusoid images -> verify gradient /
Laplacian / FFT / band behaviour matches hand calculations
renaming a file does not change its features
repeating a run produces identical values
no NaN or Inf anywhere in the table
```

**Why this stage is here:** simple frequency statistics separate generated from camera images [5], [6], [7], [8], and this family of methods is still competitive in recent work [10]; pixel-pattern statistics carry related signals [15], [16]; but spectral traces can be deliberately weakened, so every spectral claim is measured under stress, never assumed [9].

### Stage 7: Pilot gate

**In plain terms.** Before the full run, a small slice (200 images per class) goes through the whole pipeline from start to finish. It is a rehearsal: if there is a leakage bug or a crash, we want to find it here, cheaply, before the full experiment.

**Inputs:** all previous stages, restricted to the pilot subset.
**Outputs:** pilot report: E1 plus one JPEG quality on the pilot, the check log, timings, and any oddities found.
**Locked settings:** 200 parent images per class; the pilot subset is drawn with the locked split seed and is a subset of the final split (never extra data).
**Checks (stop on failure):** the pilot is **stop-and-repair**. Any leakage, misalignment, or strange control-check result (Section 6) stops the pipeline and is fixed before Stage 8. The pilot subset never changes after this gate.
**Why this stage is here:** a strict split is only as good as its enforcement [1], [2]; the pilot is where we verify the enforcement works.

### Stage 8: Experiments (E1–E5, three arms each)

**In plain terms.** This is the actual study: five experiments, decided in advance, each run with the same three feature sets and the same simple classifier. Because nothing else changes between runs, any difference in the results comes from the features and the condition, not from switching methods halfway.

**Inputs:** locked features and splits.
**Outputs:** `models/` (one artifact per arm × condition × fold), `results/per_image_predictions.parquet`, `models/thresholds.csv`.

**Classifier procedure (identical for all three arms):**

- L2 logistic regression. The value `C` is chosen on validation data only, from {0.01, 0.1, 1, 10}.
- Standardization is fitted on training images only.
- The decision threshold is chosen on validation data only (balanced accuracy).
- One artifact per arm × condition × fold. The combined arm simply joins the standardized pixel-pattern and frequency features (scaler fitted on training data only).

**Experiment table (the whole study):**

| # | Experiment | Split | Condition | Question it answers |
|---|---|---|---|---|
| E1 | First check | by image group | C0 | Do the features separate the classes at all? (one table) |
| E2 | Shortcut control | by image group | C2 | Does a deliberately unfair pipeline "detect" the shortcut? (control) |
| E3 | JPEG test | by image group | C1, three qualities | What happens under fair compression? |
| E4 | Unseen generator | generator held out | C0 | Does it transfer to a generator family never trained on? |
| E5 | **Main result** | held-out generator | C1, middle quality (75) | Unseen generator and JPEG together: the study's headline |

E5 is the core result; E1–E4 support it.

**Checks (stop on failure):** arm comparisons use the *same* resampled images (paired); C2 is reported only in its own control table.
**Why this stage is here:** using fixed features and a simple classifier is the honest way to measure feature quality, as done in [17].

### Stage 9: Statistics

**In plain terms.** A single number per experiment is not enough to trust. We need to know how uncertain each number is, and we must not let near-copies of the same picture create false confidence. So every comparison resamples whole image groups, keeping all copies of one picture together.

**Inputs:** per-image predictions and splits.
**Outputs:** `results/per_feature_statistics.csv`, `family_comparison.csv`, `generator_shift.csv`, `jpeg_robustness.csv`.
**Locked settings:** 95% confidence intervals from group-based bootstrap (resampling), 1,000 rounds, bootstrap seed 20260914.
**Required reporting for every experiment:**
- AUROC (how well classes are ranked apart) and balanced accuracy at the validation-chosen threshold.
- Separate rows per generator for E4/E5, never just the overall average.
- 95% confidence intervals from the group-based resampling.
- Paired arm differences (pixel-pattern − frequency; combined − best single) on the same resampled groups.
- Per-feature statistics (E1, E3): mean / median / interquartile range per class; effect size (Cohen's d, real − generated, with pooled standard deviation stated) plus bootstrap confidence interval; within-parent change from C0 to C1 for each JPEG quality.

**Checks (stop on failure):** resampling always uses whole image groups, never individual JPEG variants, because variants share a parent and counting them separately would fake confidence.
**Why this stage is here:** "the feature value changed" and "the classifier got worse" are different findings and are reported as different outcomes.

### Stage 10: Report and careful conclusion

**In plain terms.** The final stage turns numbers into the report. Limitations are written *before* conclusions, figures are regenerated from saved tables, and the headline sentence says exactly what was tested: three generator families, three JPEG qualities. Nothing in the report claims more than the experiment did.

**Inputs:** all result tables.
**Outputs:** `figures/` (feature distributions, robustness curves, family comparison, pipeline diagram); `reports/final_results.md`; `reports/limitations.md`; `README.md` (environment, library versions, seeds, config hash, exact rerun steps).
**Checks (stop on failure):**
- A clean rerun from scratch reproduces the saved tables.
- Figures are regenerated from saved tables and never edited by hand.
- Limitations are written before conclusions.
- The headline result uses the conclusion template at the end of this section.

---

## 5. The 14 features

Every feature is computed from the standard luminance image `I` (float, [0, 1]). Frequency features use the FFT with the locked Hann window; features 8–11 use the power spectrum. Each row gives the plain meaning first, then the exact definition.

**Pixel-pattern features (7):**

| # | Feature | In plain terms | Exact definition |
|---|---|---|---|
| 1 | Intensity variance | How spread out the light and dark values are | Variance of `I` |
| 2 | Intensity skewness | Whether the brightness histogram leans to one side | Third standardized moment of `I` |
| 3 | Intensity excess kurtosis | How heavy the histogram's tails are compared to a normal shape | Fourth standardized moment − 3 |
| 4 | Gradient-magnitude mean | How strong the edges are on average | Mean of Sobel gradient magnitude |
| 5 | Gradient-magnitude std | How uneven the edge strength is | Standard deviation of Sobel gradient magnitude |
| 6 | Laplacian variance | How much fine, pixel-level detail exists | Variance of the Laplacian response |
| 7 | High-pass residual variance | How much energy remains above the blur level | Variance of `I` minus its 3×3 binomial-blurred version (locked kernel) |

**Frequency features (7):**

| # | Feature | In plain terms | Exact definition |
|---|---|---|---|
| 8 | Low-band energy fraction | Share of energy in coarse shapes | Σ power in locked low band / Σ power in all non-DC bands |
| 9 | Mid-band energy fraction | Share of energy in mid-scale texture | Σ power in locked mid band / Σ power in all non-DC bands |
| 10 | High-band energy fraction | Share of energy in the finest detail | Σ power in locked high band / Σ power in all non-DC bands |
| 11 | Nyquist-band energy ratio | How much of the fine detail sits at the very top of the spectrum, where upsampling and aliasing leave their mark | Σ power in the locked top band (0.375, 0.5] / Σ power in the locked high band |
| 12 | Spectral slope | How quickly energy falls off from coarse to fine detail (generator upsampling changes this falloff) | Slope of log power vs log radius, least squares over the locked range; DC and r < 2/256 excluded; R² reported |
| 13 | Directional anisotropy | Whether energy is uneven around the compass, a sign of a periodic upsampling fingerprint | Variation of mean energy across 12 angular sectors of 30° inside the locked mid band |
| 14 | Peak concentration | How much one single frequency spike stands out above the rest | Largest non-DC local maximum / total non-DC power |

**Combined arm.** The standardized pixel-pattern features joined with the standardized frequency features (scaler fitted on training images only). Feature counts are reported.

**Removed features and why (kept in the report):** total spectral energy (it duplicates intensity energy by Parseval's theorem, so it was audit-only); generic Fourier symmetry (true for all real images); unspecified peak statistics (not reproducible); autocorrelation (a Fourier twin of the spectrum arm); LBP and colour features (removed in the scope reduction).

---

## 6. Classifier and control checks

Every experiment uses one classifier: L2 logistic regression, fitted the same way for all three arms. Alongside it, three cheap control checks run every time. They do not improve results; they are there to catch mistakes.

**Control check 1: always-guess baseline.** Always predicts the more common class. A real result must beat it; if it does not, the features carry no usable signal on that condition.

**Control check 2: history-only classifier.** Trained only on file information from the source list (format, size, known quality), never on the image content. In plain terms: if this can tell the classes apart, then our pipeline is leaking processing information and the results are suspect. After standard pre-processing, the expected score is close to random.

**Control check 3: shuffled labels.** The training labels are shuffled on purpose; the test AUROC must be about 0.5. This catches indexing mistakes, where one image's features are accidentally paired with another image's label.

All three are required. They diagnose the pipeline; they never "fix" a result.

---

## 7. Hypotheses and decision rules (decided in advance)

Written before results and applied as written.

- **H1 (first check).** Supported if at least one arm shows clear separation in E1 (confidence interval excluding chance). Reported as one table.
- **H2 (shortcut check).** Compare E2 with E1 and E3. Supported only if the separation changes in the direction we predicted, with a confidence interval computed on the same image groups. Wording rule: "the separation changed after the controlled change" — never "JPEG caused it".
- **H3 (broad vs narrow frequency features).** Broad = features 8–11 and 13; narrow = feature 14. **Two separate verdicts:** (a) how much the feature values change (stability), and (b) whether classification still works (separation). The two are never merged: H3 can hold for one and not the other.
- **H4 (generator dependence).** Read from the per-generator rows of E4 and E5. Conclusions apply only to the tested generator families.
- **H5 (content dependence).** Not tested. One limitations paragraph, citing the content-bias literature [3] and the bias-free training framework [2].

---

## 8. Six non-negotiable rules

These are one-time scripts; none of them grows with the number of experiments. Removing any of them makes the results invalid.

1. Check sources and find duplicates **before** splitting.
2. Split by image group; every parent image and all its variants stay in one split; lock the split with a hash.
3. Process both classes exactly the same way.
4. Apply JPEG the same way to both classes, always from the same standard stage.
5. Fit scalers, regularization, and thresholds on training/validation data only.
6. Resample whole image groups for statistics, never individual JPEG variants.

---

## 9. Claim-strength rules

- "The separation changed after the controlled change" — not "JPEG caused X".
- "No retrieved abstract reports this exact protocol" — not "first".
- Report per-generator and per-quality numbers, never only averages.
- A negative or mixed result written with the template below is a valid outcome.
- Before any stronger novelty wording in a paper submission, two papers must be read in full: Grommelt et al. [1] (closest JPEG-bias study) and Sato et al. [10] (closest radial-spectrum method). No other full-text reads are required by this plan.

---

## 10. Deliverables and the final conclusion template

```text
data/      provenance.csv, duplicate_clusters.csv, canonical_manifest.csv,
           variant_manifest.csv, splits.csv, split_hash.txt
features/  feature_dictionary.csv, features.parquet, extraction_report.md
models/    per-experiment artifacts, thresholds.csv
results/   per_image_predictions.parquet, per_feature_statistics.csv,
           family_comparison.csv, generator_shift.csv, jpeg_robustness.csv
figures/   feature_distributions.png, robustness_curves.png, family_comparison.png,
           pipeline-diagram.png / .pdf
reports/   final_results.md, limitations.md
README.md  environment, library versions, seeds, config hash, exact rerun steps
```

**Conclusion template (fill in only after results):**

> "For the tested generator families (BigGAN, SD v1.4, ADM) and JPEG conditions (quality 90, 75, 50), feature set X gave the best separation on unseen data (AUROC …, 95% CI …). Its performance changed as follows under compression (…) and on the unseen generator (…). These results apply only to the sampled images and processing conditions."

---

## 11. What was cut, and why it stays cut

| Removed | Reason |
|---|---|
| Resize / blur / sharpen / noise / screenshot conditions | Outside the two chosen topics (JPEG and unseen generator); JPEG is the most common real-world transform |
| Linear SVM as a second classifier | Logistic regression alone answers the feature-set question; a second classifier adds settings to tune, not information |
| Content-matched generation track (H5) | Needs TwinSynths-style controlled construction, which is out of scope; deferred to limitations with citations [2], [3] |
| Learned detectors (DIRE / AEROBLADE / FIRE / CLIP) | A different cost class; cited as context only [18], [19], [20] |
| 4th generator (Midjourney); 4,000-image quota | 3 generators and a 3,000-image quota (1,500 real + 1,500 generated) suffice for the planned experiments |
| Multiple-testing (FDR) corrections | Not needed with 14 features chosen in advance |
| Rotating all unseen-generator folds | One locked fold is committed; rotation stays out |
| LBP as a 15th feature; colour features; phase features | Removed in the scope reduction |
| Equal-size sensitivity check (top-k features) | Does not change the feature-set conclusion; stays out |
| Rank correlation C0 vs C1 | The within-parent change already answers the stability question |
| Separate reproducibility document | Folded into `README.md` (environment, seeds, rerun steps) |
| Downloading PDFs of secondary citations | Citing at abstract level is enough for context-only papers |

---

## 12. Where each design decision comes from

| Design decision | Supporting papers (review numbers) |
|---|---|
| Source and history record; JPEG applied the same way to both classes; C1/C2 | [1], [2] |
| Split by image group; careful handling across generators | [1], [2], [11] |
| Same processing for both classes | [1], [2] |
| Frequency features 8–14 and their interpretation | [5], [6], [7], [8], [10] |
| Stress tests are required (spectral traces can be weakened) | [9] |
| Pixel-pattern arm (local pixel statistics) | [15], [16] |
| Fixed features + simple classifier as the measurement method | [17] |
| Unseen-generator testing as the standard | [11], [12], [13], [14] |
| Caution with hard examples; careful claims | [4] |
| Why H5 is not tested | [2], [3] |
| Reconstruction methods cited as context, not implemented | [18], [19], [20] |
| Data source and fallback dataset | [13], [14] |
