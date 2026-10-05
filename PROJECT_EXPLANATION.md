# Full Project Explanation — workspace + open PR

**Repo:** `Omlan14/spatial-spectral-forensics` · **Local HEAD:** `d883e14` (main, 1 commit ahead of `origin/main`)
**Open PR:** #1 `feat/final-report-resampling-diagnostic` → `main` (+4,515 / −1, 68 files, 9 commits)
**Locked config hash:** `87f5489e9d59` · **Seeds:** split `2026`, bootstrap `20260914` · **Split hash:** `386ffeaa…e89e89`

This file is a reading guide for the whole project. Every number below was read from the raw
tables (`results/*.csv`, `results/diagnostics/history_diagnostics.csv`), from the locked spec, or
from the PR branch — not from memory.

---

## PART 1 — What the project is

### 1.1 One paragraph

This is a **pre-registered measurement study** in image forensics. It asks one question: *with
identical processing applied to both classes and a strict split by image group, which simple,
explainable feature set separates real photographs from AI-generated images best — pixel-pattern
features, frequency (spectrum) features, or both combined — and how much does the answer change
under matched JPEG compression and on a generator the model never saw?*

It is deliberately **not** a new detector, **not** a state-of-the-art comparison, and **not** a
claim about all AI-generated images. The scientific contribution is a *feature-level audit* of how
dataset processing history and generator identity distort the measurement itself.

### 1.2 The one-line answer

The combined 14-feature set wins in every tested setting — **but the pooled numbers are dominated
by a resize artifact the team's own controls exposed.** On the two diffusion families the best
simple set reaches only **0.63–0.76 AUROC**, and on the headline setting (unseen SD v1.4 at JPEG
q75) it reaches **0.629 [0.571, 0.690]** while the pixel arm alone sits at chance (0.465).

### 1.3 The meta-result (the most defensible contribution)

A pipeline that reported only pooled AUROC would have said *"0.793 AUROC, problem solved."*
The controls showed instead that:

| What the pooled number hides | Evidence |
|---|---|
| The dataset itself leaks through file facts | pre-receipt history classifier = **AUROC 1.000** |
| The pipeline's own 2× upsample of BigGAN creates the "spectral evidence" | BigGAN high-band features ≥ 0.97 (reversed); under a matched resample it falls to 0.828 |
| "Which feature family wins" flips with resampling history | pixel − frequency: **−0.088** under C0 → **+0.022** under R |
| Ranking stability ≠ decision stability | fixed model at q50: pixel false positives **98/300 → 157/300** while AUROC moves ≤ 0.027 |

---

## PART 2 — Repository anatomy

### 2.1 Two parallel trees

The workspace is deliberately split in two:

```
(a) THE STUDY (authoritative, pre-registered, immutable)
    src/            spec + pipeline code
    data/           provenance, duplicates, splits, manifests, raw images
    features/       14-feature table + dictionary + extraction report
    models/         fitted logistic regressions + thresholds
    results/        the locked result tables + diagnostics
    figures/        evidence figures
    reports/        final_results.md, limitations.md, deep analysis
    experiments/    e1..e5 {protocol.md, code/, results/, analysis.md}
    paper/          conference + journal manuscript (MD, LaTeX, PDF)
    to_human/       17-slide deck, improvement strategy
    literature/     20-paper verified reference set + novelty check

(b) THE PROJECT MEMORY (autoresearch skill convention)
    research-state.yaml   machine-readable state: hypotheses, verdicts, trajectory
    research-log.md       append-only decision timeline
    findings.md           narrative synthesis + project memory
    config.yaml           the Stage-0 lock + dated deviations
    src/experimental-pipeline.md   THE SPEC (Stages 0-10, v1.0, locked 2026-09-14)
```

### 2.2 Pipeline code (`src/`)

| File | Stage | Role |
|---|---|---|
| `common.py` | — | paths, config load, **config hash**, `check()` — the stop-on-failure primitive |
| `fetch.py` | 1 | stream + provenance recording from the HF mirror |
| `prepare.py` | 2–5 | dedup/near-copy/exclusions, group split + hash, 256² standardisation, C0/C1/C2 variants |
| `features.py` | 6 | **the 14 locked features** + synthetic hand-calculation self-checks |
| `experiments.py` | 7–9 | pilot gate, E1–E5 × 3 arms, controls, group-bootstrap CIs |
| `report.py` | 10 | figures from saved tables |
| `history_diagnostics.py` | **post-hoc** | D1 + D2 (PR branch only) |
| `pipeline-diagram.py` | — | Figure 1 (self-checking) |

### 2.3 The three guards against fooling yourself

1. **`check()` in `common.py` raises `SystemExit` on any failed assertion.** Pipeline rule 2 is
   "stop on a failed check; checks are never edited to make them pass."
2. **Every result row carries `config_hash`, `code_version`, `seed_split`, `seed_bootstrap`.**
3. **A clean rerun (2026-09-27) reproduced every `data/` table byte-for-byte and every
   `results/*.csv` exactly** — only the `code_version` column differed.

---

## PART 3 — The DIP content (what the 14 features actually are)

All features are computed on a 256×256 luminance image `Y = (0.299R + 0.587G + 0.114B)/255` (BT.601, float32, [0,1]). Luminance only — so chroma is deliberately excluded and cannot leak colour shortcuts.

### 3.1 Pixel-pattern arm (spatial, features 1–7)

| # | Name | Definition | What it measures |
|---|---|---|---|
| f01 | `var` | variance of I | global contrast energy |
| f02 | `skew` | skewness of I | asymmetry of the intensity histogram |
| f03 | `exkurt` | excess kurtosis of I | peakedness / spikiness of the histogram |
| f04 | `grad_mean` | mean Sobel \|∇I\| | average edge strength |
| f05 | `grad_std` | std of Sobel \|∇I\| | variation of edge strength |
| f06 | `lap_var` | variance of 4-neighbour Laplacian [[0,1,0],[1,−4,1],[0,1,0]] | second-derivative sharpness / fine detail |
| f07 | `hp_var` | variance of I − binomial3×3(I), kernel [1,2,1]⊗[1,2,1]/16 | high-pass residual energy |

### 3.2 Frequency arm (spectrum, features 8–14)

Computed on the **Hann-windowed power spectrum** after mean removal: `P = |FFT2((I − Ī)·Hann)|²`.
The window prevents edge effects so band energies describe the *image*, not the rectangle.

| # | Name | Definition | What it measures |
|---|---|---|---|
| f08 | `low` | power in (0, 0.05] cyc/px ÷ total | coarse structure |
| f09 | `mid` | power in (0.05, 0.25] ÷ total | texture |
| f10 | `high` | power in (0.25, 0.5] ÷ total | fine detail |
| f11 | `nyq_ratio` | power in (0.375, 0.5] ÷ power in (0.25, 0.5] | energy piled at the **top** of the band — the resize/JPEG tell |
| f12 | `slope` | log–log radial power slope, least squares over r ∈ (0.05, 0.5], 1/256-wide radius bins | overall spectral decay (≈ −2 for natural 1/f) |
| f13 | `aniso` | CV of mid-band power over 12 sectors of 30° | directional bias of texture |
| f14 | `peak` | largest non-DC 3×3 local max ÷ total non-DC power | concentration of power in isolated peaks |

DC (f00) is excluded from every feature. `f12` also reports R²; 30 of 3,000 C0 images had R² < 0.8.

### 3.3 The feature code is verified against hand calculations

`src/features.py::_selfcheck()` runs **before** any real image is touched, on synthetic images with closed-form answers:

| Test image | Closed-form expectation |
|---|---|
| constant 0.5 | f01,f04,f05,f06,f07 = 0 |
| single impulse | f06 = 20/N² |
| impulse band fractions | equal to the **area** of each annular band (flat spectrum) |
| step edge | f04 = 8/N |
| checkerboard | one Nyquist-corner spike → f14 = 0.444 |
| 0.125 cyc/px sinusoid | all power in mid band; f09 > 0.99, f12 > 1.5, f13 = 0.222 |
| 1/f pink noise | f12 = −2 (± 0.15), R² > 0.95 |
| same array twice | bit-identical features (determinism) |

Plus: rename-invariance check (copy a file to a new name → identical features), no NaN/Inf, repeat-run identity.

### 4.2 Conditions

| Condition | Definition | Purpose |
|---|---|---|
| **C0** | canonical 256×256 lossless PNG, both classes, bicubic | the baseline |
| **C1** | both classes JPEG at q90 / q75 / q50, one pinned Pillow encoder, 4:2:0, `optimize=false` | *fair* compression |
| **C2** | reals JPEG q75, fakes PNG — a deliberate mismatch | **control only**, not a detection condition |

### 4.3 Classifier & statistics

* **One L2 logistic regression** for all three arms — the classifier is the *measuring instrument*, kept dumb on purpose.
* `class_weight="balanced"` (needed because E4/E5 remove one generator, unbalancing train/val).
* `C ∈ {0.01, 0.1, 1, 10}` chosen by **validation AUROC** (ties → smaller C).
* Threshold chosen by **validation balanced accuracy**; scorer is `decision_function` (AUROC is ranking-only, so the score must be unbounded — no `predict_proba`).
* `StandardScaler` fitted on **train only**.
* **60/20/20 split by parent image group**, stratified by label × subset. **One locked test set of 600 parents (300 real + 100 per generator) shared by E1–E5** → every cross-experiment comparison is *paired*.
* **Unseen-generator fold:** all SD v1.4 fakes removed from train **and** val for E4/E5.
* **95% CIs from 1,000 rounds of group-level bootstrap** (resample whole groups, never individual JPEG variants). Paired bootstrap for deltas.

### 4.4 The six non-negotiable rules

1. Check sources and find duplicates **before** splitting.
2. Split by image group; lock the split with a hash.
3. Process both classes exactly the same way.
4. Apply JPEG the same way to both classes, always from the same standard stage.
5. Fit scalers, regularisation and thresholds on train/val only.
6. Resample whole image groups for statistics, never individual variants.

### 4.5 Claim-strength rules (self-imposed, and consistently honoured)

* "The separation **changed after** the controlled change" — never "JPEG **caused** X".
* "No retrieved abstract reports this exact protocol" — never "first".
* Report per-generator and per-quality numbers, never only averages.
* Before stronger novelty wording: full reads of **Grommelt et al. [1]** (done 2026-09-27) and **Sato et al. [10]** (still pending).

---

## PART 4 — The locked methodology

### 4.1 Data

* **Source:** `nebula/GenImage-arrow` (HF mirror of the official GenImage `val` folders) — *fallback step (b), streaming*.
* **Content-blind sampling:** keep row if `sha1(image_path) < 0.12`, then a seeded draw of **500 fake + 500 real per subset** → 1,500 real + 1,500 fake = **3,000 parents**.
* **Generators:** BigGAN (GAN), Stable Diffusion v1.4 (diffusion), ADM (diffusion).

**The critical fact the whole project turns on:**

| Class | Arrives as | Native size | What the locked resize does |
|---|---|---|---|
| Real (ImageNet) | JPEG, varying size | varies | resize to 256² |
| Fake — BigGAN | PNG | **128²** | **enlarged 2×** |
| Fake — ADM | PNG | **256²** | unchanged |
| Fake — SD v1.4 | PNG | **512²** | reduced 0.5× |

So "apply the same processing to both classes" is *nominally* true but *substantively* unequal: every class gets a different resampling factor.

**Stage-2 integrity checks (before splitting):**
* exact / pixel-level duplicate clusters via union-find;
* perceptual-hash near-copies (DCT-64, Hamming ≤ 4) — same rule both classes;
* alpha-channel handling — test *alpha values*, not mode (GenImage ADM PNGs are RGBA but fully opaque, so mode-based exclusion was a bug, fixed in commit `2faf7ea`);
* ICC profile exclusion — ~10% of ImageNet reals carry Camera RGB / Adobe RGB and are dropped.

---

## PART 5 — Experiments and hypotheses

| Exp | Condition | Split | Question | Hypothesis |
|---|---|---|---|---|
| **E1** | C0 | by group | Do any arms separate the classes at all? | H1 |

---

## PART 6 — The locked results

### 6.1 Test AUROC by arm (95% group-bootstrap CI)

| Setting | Pixel (1–7) | Frequency (8–14) | Combined (1–14) |
|---|---|---|---|
| **E1 clean (C0), pooled** | 0.666 [0.622, 0.707] | 0.752 [0.713, 0.792] | **0.793 [0.759, 0.826]** |
| E1 pooled, balanced acc. | 0.612 | 0.685 | 0.700 |
| E2 mismatch (C2) Δ vs E1 | −0.026 [−0.038, −0.015] | +0.017 [0.009, 0.025] | +0.012 [0.007, 0.017] |
| E3 Δ vs E1, q90 | −0.005 | +0.003 | −0.007 |
| E3 Δ vs E1, q75 | −0.016 | +0.005 | −0.003 |
| E3 Δ vs E1, q50 | −0.025 [−0.040, −0.011] | +0.014 [0.002, 0.026] | +0.000 |
| E4 unseen SD v1.4 (C0) | 0.475 [0.422, 0.541] | 0.560 [0.495, 0.627] | 0.634 [0.578, 0.695] |
| **E5 unseen SD + q75 (HEADLINE)** | 0.465 [0.410, 0.527] | 0.568 [0.505, 0.637] | **0.629 [0.571, 0.690]** |
| E5, all test generators | 0.631 | 0.769 | 0.786 [0.753, 0.820] |

### 6.2 Per-generator E1 (the pooled number's anatomy)

| Arm | BigGAN | SD v1.4 | ADM |
|---|---|---|---|
| Pixel | 0.824 | 0.581 | 0.591 |
| Frequency | **0.997** | 0.637 | 0.624 |
| Combined | 0.990 | 0.712 | 0.678 |

Per-generator AUROC = that generator's 100 test fakes vs **all 300** test reals (n = 400).

### 6.3 Key paired effects

| Effect | Δ AUROC | 95% CI |
|---|---|---|
| E1: combined − frequency | +0.041 | [0.018, 0.064] |
| E1: pixel − frequency | −0.087 | [−0.130, −0.046] |
| E4 − E1 (combined, SD held out) | −0.078 | [−0.124, −0.034] |
| E5 − E4 (unseen + JPEG vs unseen clean) | −0.004 | small |
| E5: combined − frequency on unseen SD | **+0.061** | [0.028, 0.094] |
| *Exploratory:* ADM when SD leaves training | +0.071 | [0.038, 0.104] |

### 6.4 H3's two verdicts — the part most people get wrong

**(a) Value stability** (median |C1 − C0| within parent, in C0 SD units, at q50):

| f08 low | f09 mid | f10 high | f13 aniso | **f11 nyq** | **f14 peak** |

---

## PART 7 — Controls: the real scientific work

| Control | What it does | Result | Verdict |
|---|---|---|---|
| 1. **Always-guess** | predicts majority class | 0.500 | pass (chance) |
| 2. **History-only** | classifier on the *analysed* files' format/size | 0.500 in C0/C1; **1.000 in E2** | pass — the E2 mismatch is visible by design |
| 3. **Shuffled labels** | training labels permuted | mean of 200 = **0.503–0.521** (SD ≈ 0.09) | pass **under deviation 1** |
| 4. **Pre-receipt history** (exploratory) | classifier on the *original* file facts | **1.000 everywhere** | the dataset-level shortcut, exposed |

### The deviation-1 story (important for any examiner question)

Stage 8 **stopped** on the single-shuffle gate: E1 gave 0.623, E2 gave 0.268. Investigation
(`results/diagnostics/shuffle_control.md`) confirmed features and labels were correctly aligned.
Over 200 shuffles the means were 0.512 / 0.514 with SD ≈ 0.09 — i.e. a *single shuffle is one random
direction in a high-dimensional space*, not a usable gate when the features are informative.
Deviation 1 (200 shuffles, gate on the mean within 0.5 ± 0.03, SD reported) was **diagnosed,
dated and owner-approved before the rerun**, and changed *no* feature, split, classifier or metric.

The lesson, stated in `findings.md`: **a single shuffled-label run is not a usable gate.**

---

## PART 8 — The five findings, each with its evidence chain

1. **Resizing history beats generation as a signal.** High-band features separate BigGAN at
   AUROC ≥ 0.97 (in the reversed direction: f06 0.015, f07 0.020, f10 0.030, f11 0.009, f12 0.004)
   while ADM/SD reach only 0.33–0.62. Whatever the pipeline does to one family's pixel grid becomes
   the dominant "detection" cue.
2. **Matched JPEG hardly matters once the classifier is refit** — ≤ 0.025 AUROC across q90–q50 —
   because the reals already carry JPEG history before our compression.
3. **Feature meaning can flip under JPEG while the classifier score stays put** (f11, above).
4. **Stable is not useful** (f14: most stable, zero signal).

---

## PART 9 — The nine limitations

1. **Scope** — 3 families, one dataset split, one encoder, three qualities, one unseen fold.
2. **Pre-receipt history is a perfect shortcut (1.000).** Standardisation removes the *file facts*
   from the analysed files (history-only → 0.500) but **not their effect on the pixels**.
3. **BigGAN's 2× upsample inflates all pooled numbers.**
4. **One unseen-generator fold only** (SD v1.4). "Generator shift costs X" is not a general law.
5. **Content bias (H5) not tested** — reals and fakes are not content-matched.
6. **Deviation 1** on the shuffled-label control (documented, owner-approved).
7. **Feature-definition details locked at Stage 0** — other reasonable choices may give different numbers.
8. **Matched JPEG is train-and-test matched** — "robustness" = *the recipe still works after refitting*,
   not *a C0 model transfers*. (This is exactly what PR diagnostic **D2** addresses.)
9. **Sampled from a mirror**, not the official archive; fidelity verified only for format and size.

|---|---|---|---|---|---|
| 0.010 | 0.006 | 0.031 | 0.009 | **0.393** | **0.003** ← most stable of all 14 |

**(b) Separation** (univariate AUROC, fake-high, C0 → q50):

| feature | C0 | q90 | q75 | q50 |
|---|---|---|---|---|
| f14 peak | 0.497 | 0.497 | 0.497 | 0.497 → **never separates** |
| f10 high | 0.291 | — | — | 0.301 |
| f08 low | 0.563 | — | — | stable |
| f13 aniso | 0.552 | — | — | stable |
| **f11 nyq_ratio** | **0.299** | 0.326 | 0.425 | **0.581** ← reverses direction |

Cohen's d for f11 goes **+0.797 → −0.263**. The reversal traces to BigGAN (0.009 → 0.089 → 0.367 → 0.772); SD and ADM stay 0.37–0.55. Mechanism: JPEG 8×8 block edges add near-Nyquist energy to the 2×-upsampled BigGAN images, which had almost none.

**H3 verdict:** broad and narrow features differ on *both* verdicts — but **not** as "broad is more robust". The narrow feature is stable because it carries no signal at all ("stable is not useful"), and the broad group's one unstable member changes *meaning* under JPEG. **"The feature value changed" and "the classification changed" are different findings** — H3 was designed so they could never be merged.

### 6.5 Threshold-level complementarity (E5, 100 unseen SD fakes)

pixel flags **34**, frequency flags **19**, union **41**, **59 missed by both** → the arms flag *different images*, which is why combined beats frequency by +0.061 even though pixel alone is at chance.

| **E2** | C2 mismatch | by group | Does a deliberately unfair pipeline "detect" the shortcut? | H2 |
| **E3** | C1 q90/75/50 | by group | What does *fair* compression change? | H3 |
| **E4** | C0 | SD v1.4 held out | Does it transfer to an unseen generator family? | H4 |
| **E5** | C1 q75 | SD v1.4 held out | Unseen generator **and** JPEG together → **headline** | H4 |
| **H5** | — | — | Content bias | **not tested by design** |

21 runs total (E1, E2, E3×3, E4, E5 × 3 arms).

### Verdict table

| H | Statement | Verdict | Decisive number |
|---|---|---|---|
| **H1** | ≥1 arm separates on clean data | **Supported** | combined 0.793 [0.759, 0.826] |
| **H2** | A deliberate mismatch changes separation | **Partly supported** | freq +0.017, combined +0.012, pixel **−0.026** vs E1 |
| **H3** | Broad vs narrow frequency features differ | **Supported, in an unexpected form** | f14 stable (0.003) but uninformative (0.497); f11 reverses, Cohen's d **+0.797 → −0.263** |
| **H4** | Detection degrades on an unseen generator | **Supported for SD v1.4** | combined −0.078 [−0.124, −0.034]; pixel → chance |
| **H5** | Detection depends on image content | **Not tested** | needs TwinSynths-style content-matched construction |


---

## PART 10 — The open PR (#1)

**Title:** *Prepare final DIP report and six-minute team presentation*
**Branch:** `feat/final-report-resampling-diagnostic` → `main` · **+4,515 / −1** across **68 files** · **9 commits** · **OPEN**

### 10.1 Branch inventory (from the PR's own review)

| Reference | Head | Meaning |
|---|---|---|
| local `main` | `d883e14` | completed locked study + literature novelty check |
| `dev/native-biggan-256` | `d883e14` | **same commit as main — no unique experiment.** The name is misleading. |
| `origin/main` | `0a2a215` | one commit behind local main |
| `feat/final-report-resampling-diagnostic` | `b8d64c9` + `7902769` | analysis, D1/D2, final paper, deck |

### 10.2 The nine commits

| Commit | Purpose |
|---|---|
| `f4354a0` | ignore scratch/superseded drafts/agent tooling; record rerun extraction report |
| `f3153df` | 2026-09-28 presentation analysis pack |
| `648ed38` | **research(diagnostic): resampling-matched condition + fixed-model JPEG transfer** ← the science |
| `b37fd59` | final 6-page IEEE conference report (`paper/final/main.tex` + PDF) |
| `720b207` | final 13-slide deck for three presenters (speaker scripts in notes) |
| `d45e806` | style polish — flat shapes, no hero-metric cards, WCAG AA contrast, typography |
| `b8d64c9` | two dedicated novelty slides (positioning diagram + diverging bar chart) → deck becomes 14 slides |
| `7902769` | team rehearsal handoff: review doc, rehearsal deck, scripts, numeric verification, rendered PDFs |

### 10.3 What D1 and D2 add (clearly labelled EXPLORATORY, post-hoc)

#### D1 — resampling-matched condition **R**

Every parent is centre-cropped to **128² at native resolution** (no resampling), then upsampled 2× bicubic to 256². **Every** image — real or fake — now shares one identical resampling operation. Same 14 features, same split, same classifier recipe, same bootstrap, as E1 (all seen) and E4 (SD held out).

*Six undersized reals are excluded → 2,994 parents, 599 test parents.* **Do not mix the D1 baseline 0.796 with the locked 600-parent 0.793.**

| D1 comparison | C0 | R | Paired Δ [95% CI] |
|---|---|---|---|
| Pooled **pixel**, E1 | 0.667 | **0.777** | **+0.110 [0.066, 0.154]** |
| Pooled **frequency**, E1 | 0.755 | 0.755 | +0.000 [−0.045, 0.047] |
| Pooled **combined**, E1 | 0.796 | 0.802 | +0.006 [−0.036, 0.045] |
| BigGAN **frequency**, E1 | 1.000 | **0.828** | **−0.172 [−0.225, −0.125]** |
| BigGAN **combined**, E1 | 0.993 | 0.890 | −0.104 [−0.135, −0.070] |

### 10.4 The final IEEE paper

`paper/final/main.tex` — **title: *"Same Score, Different Story: How Resampling History Shapes What
Spatial–Frequency Features Detect in AI-Generated Images"***, IEEEtran conference, 6 pages,
author block "Member One/Two/Three", Department of CSE, United International University, Dhaka —
CSE 4883: Digital Image Processing, Summer 2026. Two new self-checking figures
(`fig_effect_sizes`, `fig_resampling_swap`) plus `pipeline-diagram`. Verified bibliography.
The abstract's punchline: *"For simple features, which generator is 'easy' and which feature
family 'wins' depends on resampling history, and pooled AUROC cannot show it."*

The **practical rule** stated in the Discussion: *report per-generator results, record each class's
native size and resampling factor, and state the resampling policy as part of the method.*

### 10.5 Presentation assets

| File | What |
|---|---|
| `presentation/final_presentation.pptx` | the original 14-slide deck (notes total 383 s: 118/135/130 by member) |
| `presentation/final_presentation_rehearsal.pptx` | **11 speaking slides + 3 Q&A backups**; corrected causal wording |
| `presentation/rehearsal_script.md` | full speaking scripts (also embedded in PPTX notes) |
| `presentation/rehearsal_manifest.json` | slide-by-slide manifest |
| `presentation/review-render/*.pdf`, `*.png` | LibreOffice-rendered previews + contact sheets |
| `figures/deck/*.png` | 6 explanatory figures: classes at native scale, feature anatomy, JPEG strip, AUROC matrix, radial spectra, novelty positioning |

**Timing arithmetic (checked):** 3 × 110 s speaking = 330 s, + 3 × 10 s transitions = **360 s = 6:00
exactly.** That leaves *zero* slack for hesitations, so the scripts are written tight and an aloud
rehearsal is still required.

| Presenter | Slides | Job |
|---|---|---|
| Member 1 | 1–3 | Problem, dataset history, contribution |
| Member 2 | 4–7 | Pipeline, DIP features, experiments, locked results |
| Member 3 | 8–11 | Exploratory diagnostic, JPEG decisions, limits, conclusion |

### 10.6 Independent numeric verification (PR)

---

## PART 11 — Timeline

| Date | Event |
|---|---|
| 2026-09-14 | pipeline v1.0 locked; 20-paper reference set verified |
| 2026-09-27 | `config.yaml` locked **before any download**; Stages 1–5 (provenance, exclusions, split+hash, manifests) |
| 2026-09-27 | Stage 6 features (129 s, all synthetic checks pass); Stage 7 pilot gate **GO** |
| 2026-09-27 | **Stage 8 stopped** on single-shuffle control → diagnosis → deviation 1 → rerun |
| 2026-09-27 | Stages 8–9: all controls pass; E1–E5 × 3 arms + group-bootstrap CIs |
| 2026-09-27 | Stage 10 figures, limitations (written *before* conclusions), final results |
| 2026-09-28 | findings synthesis; presentation analysis pack |
| 2026-09-28 | literature novelty check against the reference set |
| 2026-09-27/29 | clean rerun reproduces every table byte-for-byte; README reproducibility section |
| 2026-09-30 | **D1 + D2 diagnostics** (`648ed38`); 6-page IEEE paper; 13→14-slide deck |
| 2026-10-05 | team rehearsal handoff (`7902769`) |
| 2026-10-06 | **presentation, 6 minutes, 3 presenters** |

| SD v1.4 **pixel**, E1 | 0.583 | 0.815 | +0.232 [0.162, 0.301] |
| **Unseen SD pixel**, E4 | 0.477 | **0.771** | **+0.295 [0.235, 0.358]** |
| pooled pixel − frequency, E1 | **−0.088** [−0.130, −0.045] | **+0.022** [−0.015, 0.056] | the *ranking flips* |

**The honest causal statement** (this is where the PR is deliberately careful):

* All **500** BigGAN parents have **identical saved feature values** between C0 and R (verified independently; the code also asserts pixel identity). But **classifiers are refitted** and other generators' training features change. So unchanged BigGAN inputs do **not** prove its classifier-AUROC change came only from the reals.
* What the unchanged BigGAN features *do* support is a **narrower** claim: for **univariate** BigGAN-vs-real feature AUROC, the change localises to the **real comparison distribution**.
* R shares a final crop/enlargement; it does **not** equalise complete acquisition/compression history, and it changes **field of view** for SD/ADM/reals (a 128 crop of a 512 SD image covers a quarter of its width).
* **BigGAN still separates under R** (combined 0.890, spectral slope univariate 0.147) → enlargement explains the *near-perfect* result but not all of it.
* The pooled interval includes zero → say "**similar pooled scores**" or "**no detectable pooled change**", never "equal" or "proved unchanged". The R pixel−frequency interval also spans zero → it does **not** prove spatial superiority.

#### D2 — fixed-model JPEG transfer (closes limitation 8)

The E1 (C0-trained) models and thresholds are scored on the C1 test images **without refitting**.
The code asserts that refitting reproduces the stored E1 scores exactly.

| Arm | reals flagged (C0 → q50) | fakes flagged (C0 → q50) | pooled AUROC transfer | refit |
|---|---|---|---|---|
| **pixel** | **98/300 (32.7%) → 157/300 (52.3%)** | 165 → 203 | 0.666 → 0.639 | 0.641 |
| frequency | 14 → 16 | 125 → 129 | 0.753 → 0.745 | 0.766 |
| combined | 37 → 42 | 157 → 155 | 0.793 → 0.774 | 0.794 |

Pixel false positives rise **+19.7 percentage points** while pooled AUROC moves ≤ 0.027. This is the
clearest practical link between JPEG and the paper's backbone: **ranking stability and decision
stability are different measurements.** A detector deployed at a clean-data threshold would drift.

5. **Arms are complementary on an unseen generator** (+0.061 [0.028, 0.094]).
6. *(Exploratory)* **Training on more generators can hurt a seen one**: removing SD v1.4 from
   training *raised* ADM AUROC (+0.071 combined, +0.115 frequency) → the two diffusion families pull
   the linear boundary in different directions.

---

## PART 12 — What you can and cannot say

### Can say (every one CI-backed)
* Combined is best in every tested setting.
* Headline 0.629 [0.571, 0.690] with the pixel arm at chance.
* Pooled 0.793 is dominated by a resize artifact.
* Matched JPEG **with refit** changed at most 0.025 AUROC; **without refit** (D2) ranking moves ≤ 0.027 but pixel false positives rise 33% → 52%.
* A feature can reverse direction while classification holds.
* Arms are complementary on the unseen family.
* Verdicts: H1 supported · H2 partly · H3 supported in unexpected form · H4 supported for SD v1.4 · H5 not tested.
* "No retrieved abstract reports this exact protocol" (never "first").

### Cannot say
* Not "these features detect AI images" — pre-receipt history and the resize artifact confound separation.
* Not "robust to JPEG" in the transfer sense for E3 (refit); D2 is the transfer test.
* Not "generator shift always costs X" — one held-out family.
* Not "first", "state of the art", "universal detector".
* Nothing about generators, datasets, encoders or qualities outside
  **{BigGAN, SD v1.4, ADM} × {GenImage val} × {Pillow 4:2:0} × {q90, q75, q50}**.
* Not "R proves resizing *caused* BigGAN's score" — crop and fitted models also changed.
* Not "spatial beats frequency under R" — the interval spans zero.

---

## PART 13 — Deliberate scope cuts (and why they stay cut)

| Removed | Reason |
|---|---|
| Resize/blur/sharpen/noise/screenshot conditions | outside the two chosen topics (JPEG, unseen generator) |
| Linear SVM as a second classifier | LR alone answers the feature-set question |
| Content-matched generation track (H5) | needs TwinSynths-style construction |
| Learned detectors (DIRE / AEROBLADE / FIRE / CLIP) | a different cost class; cited as context only |
| 4th generator (Midjourney); 4,000-image quota | 3 × 1,000 suffices |
| Multiple-testing (FDR) corrections | not needed for 14 features chosen in advance |
| Rotating all unseen-generator folds | one fold locked; rotation stayed out |
| LBP as a 15th feature; colour; phase features | removed in scope reduction |
| Rank correlation C0 vs C1 | within-parent change already answers stability |
| A never-enlarge resize policy | would change a locked v1 value → T2.1 pre-registered appendix |

The stated **anti-strategy**: *no SOTA/deep baselines (out of scope, buries the contribution); no
more generators or bigger quotas (worst cost, marginal gain); no H5 content matching (a project of
its own); no feature tuning toward better AUROC — it would destroy the pre-registration guarantee.
The 0.465/0.629 numbers are findings, not a scoreboard.*


---

## PART 14 — Glossary

| Term | Meaning in this project |
|---|---|
| **Parent image** | one original picture, before any processed copies |
| **Variant** | a processed copy (standard PNG, a JPEG version, or a mismatch version) |
| **Arm** | one feature set: pixel / frequency / combined |
| **Condition** | how an image was processed: C0, C1, C2 |
| **Group** | one parent + all its variants and near-copies — never split across train/val/test |
| **Locked** | decided before results, never changed after |
| **AUROC** | ranking quality; 0.5 = chance. **Not accuracy.** Positive class = generated |
| **Balanced accuracy** | mean of the two per-class recalls at the validation threshold |
| **Group bootstrap** | resample whole parent groups, 1,000 rounds |
| **Paired delta** | difference between experiments on the *same* 600 test parents |
| **Univariate AUROC** | AUROC of one raw feature, no fitting — a "does this single number separate?" check |
| **Cohen's d** | standardised mean difference, real − fake |


`reports/final_day_numeric_verification.json` recomputes AUROC from the saved per-image predictions
with no retraining. All 12 headline numbers reproduce exactly (e.g. E1 combined pooled 0.79347,
E5 combined unseen-SD 0.62930), and `biggan_R_C0_feature_identity: true` for all 500 parents.
Bootstrap intervals were **cross-checked against saved tables, not regenerated.**

---

## PART 15 — Q&A starter bank (from the PR, with the reasoning)

**Q: Why not claim AI-image detection?**
A. Prior JPEG and resizing differ between classes, and content is unmatched. Our measured
separation can include those effects.

**Q: Why is AUROC 0.629 worth presenting?**
A. It is an honest held-out-generator result for explainable features. The contribution is
understanding what the scores measure, not claiming a deployable detector.

**Q: Is JPEG robustness proved?**
A. E3 refits at each quality. D2 separately tests fixed clean models. Ranking changes little, but
the spatial model's false positives increase substantially.

**Q: Did you prove resizing causes all of BigGAN's score?**
A. No. R changes crop and fitted models. Unchanged BigGAN feature values give a narrower univariate
reference-distribution check; the classifier results show broader sensitivity.

**Q: Why can combined help if spatial alone is at chance?**
A. Joint features can support a different fitted boundary. The observed +0.061 supports
complementarity in this setup, without identifying its causal feature driver. At threshold level,
pixel flags 34 of 100 unseen SD fakes and frequency flags 19 — different images, 41 in the union.

**Q: What is new here?**
A. A project-specific feature-level audit linking controlled processing, generator-specific
statistics and actual decisions. No first or state-of-the-art claim.

**Q: What would you do next?**
A. Pre-specify a matched-field-of-view processing comparison, then rotate the generator holdouts,
then address content matching. These are future tests, not completed results.

**Q: The shuffled-label control was changed after it failed. Isn't that p-hacking?**
A. No. The diagnosis showed no indexing error — features and labels were aligned. A single shuffle
is one random direction in 14-dimensional space (SD ≈ 0.09 AUROC across 200 shuffles), so it is not
a usable gate. The change (200 shuffles, gate on the mean, SD reported) was dated, reasoned and
approved *before* the rerun, and touched no feature, split, classifier or metric. It is logged as
deviation 1 in `config.yaml`.

**Q: `dev/native-biggan-256` sounds like a never-enlarge experiment. Can you present it?**
A. No. That branch's head is `d883e14` — identical to `main`. It contains no unique experiment.
The never-enlarge/native-256 comparison is a pre-registered Tier-2 proposal (T2.1), not a result.

---

## PART 16 — File map (quick reference)

| Artifact | Path |
|---|---|
| Locked specification | `src/experimental-pipeline.md` |
| Locked config + deviation 1 | `config.yaml` |
| Central state / findings / log | `research-state.yaml`, `findings.md`, `research-log.md` |
| Literature (20 verified refs, novelty check) | `literature/literature-review.md`, `literature/novelty-check-2026-09-27.md` |
| Final results + limitations | `reports/final_results.md`, `reports/limitations.md` |
| Deep verified analysis | `reports/results_deep_analysis.md` |
| **PR: final-day review** | `reports/final_day_review.md` |
| **PR: numeric verification** | `reports/final_day_numeric_verification.json` |
| **PR: D1/D2 code** | `src/history_diagnostics.py` |
| **PR: D1/D2 results** | `results/diagnostics/history_diagnostics.csv` |
| **PR: IEEE paper** | `paper/final/main.tex` + `main.pdf` |
| **PR: decks & scripts** | `presentation/final_presentation*.pptx`, `rehearsal_script.md` |
| Result tables | `results/*.csv`, `results/extended/*.csv` |
| Figures | `figures/`, `figures/extended/`, `figures/deck/` |
| Shuffle-control diagnosis | `results/diagnostics/shuffle_control.md` |

---
