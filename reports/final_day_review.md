# Final-day project review

Date: 2026-10-05. Presentation: 2026-10-06, six minutes, three presenters.

## Recommended backbone

I think the strongest framing is **Same score, different story: how image-processing history changes the interpretation of spatial-frequency features**.

The study compares explainable image statistics, rather than claiming a universal AI-image detector. JPEG remains a useful stress test. The more coherent contribution connects three observations: original dataset history can separate the classes; the evaluation pipeline introduces unequal resizing; similar ranking scores can conceal different generator results and different threshold decisions.

The defensible conclusion is: **In this sample, simple features separate real and generated images, but their scores depend on processing and generator composition. Report processing history, generator-specific results, and threshold behavior alongside pooled AUROC.**

## Branch and artifact inventory

Checked local branches, live remote heads, branch reflogs and detached worktree history.

| Reference | Verified head | Meaning |
|---|---|---|
| local main | d883e14 | Completed locked study plus literature novelty check |
| dev/native-biggan-256 | d883e14 | Same commit as main; no unique experiment or result |
| origin/main | 0a2a215 | One commit behind local main |
| feat/final-report-resampling-diagnostic | b8d64c9 | Seven commits beyond local main; analysis, D1/D2, final paper and deck |
| origin/feat/final-report-resampling-diagnostic | b8d64c9 | Matches current branch |

The remote has two branch heads. Detached sore-sink is clean at origin/main. Missing/prunable bald-saltopus refers to ancestor 39e8eb1, with no unique experimental history found. No branch merge is needed to assemble this evidence.

Authoritative paper: paper/final/main.tex and main.pdf. Latest existing presentation: presentation/final_presentation.pptx, **14 slides**, despite stale README references to 13. Older decks in to_human contain 17, 16 and 10 slides. The older improvement_strategy.md incorrectly says the paper and slides do not exist and proposes a JPEG transfer test that D2 has since completed; use it only as historical planning.

## What was implemented and measured

The locked pipeline uses 3,000 GenImage parents: 1,500 real and 500 generated each by BigGAN, SD v1.4 and ADM. It uses content-blind mirror sampling, image validity and duplicate checks, group splits, 256-square standardisation, 14 named features, and three feature arms. Spatial features include moments, Sobel gradients, Laplacian variance and high-pass residual variance. Frequency features include band powers, near-Nyquist ratio, radial spectral slope, anisotropy and peak strength.

All arms use L2 logistic regression, training-only standardisation, validation-based model selection and threshold selection. Planned tests share 600 test parents. Confidence intervals use 1,000 group-bootstrap rounds. The shuffled-label gate was amended, with a documented approval, from a single shuffle to a 200-shuffle mean. This is a recorded deviation, not a claim that every original control passed unchanged.

Use “locked” or “pre-specified.” The repository records advance specification, but this review did not verify an external preregistration registry.

| Experiment | Question | Outcome |
|---|---|---|
| E1 | Do any feature arms separate these samples? | All above chance; combined highest pooled |
| E2 | Does deliberate JPEG mismatch change separation? | Small frequency/combined increases; spatial decreases; H2 partly supported |
| E3 | What changes under matched JPEG q90/q75/q50? | Small pooled changes after refitting; individual features behave differently |
| E4 | What happens when SD v1.4 is absent from training? | Its separation falls; spatial arm reaches chance |
| E5 | Holdout plus matched JPEG q75 | Combined strongest on unseen SD, with limited discrimination |
| D1 / R | Later native crop plus shared enlargement | Similar pooled AUROC; substantial generator-specific changes |
| D2 | Later clean-model JPEG transfer, no refit | Small pooled AUROC changes, larger spatial false-positive drift |
| H5 | Content bias | Not tested |

## Evidence to carry into the talk

Locked results from results/family_comparison.csv, generator_shift.csv and jpeg_robustness.csv:

| Setting | Spatial | Frequency | Combined |
|---|---|---|---|
| E1 pooled | 0.666 | 0.752 | 0.793 |
| E4 unseen SD, C0 | 0.475 | 0.560 | 0.634 |
| E5 unseen SD, JPEG q75 | 0.465 | 0.568 | 0.629 |

E5 combined unseen-SD interval: [0.571, 0.690]. These numbers are AUROC, **not percent accuracy**. The pooled E5 combined score is 0.786. Combined has the highest pooled score across locked experiments; frequency can beat combined on BigGAN. Removing SD from training costs combined about 0.078 on SD at C0. Under refitted matched JPEG, pooled changes are at most 0.025 across arms and qualities.

On unseen SD at q75, combined beats frequency by +0.061 [0.028, 0.094], although spatial alone is at chance. This is evidence of useful joint information in the tested classifier. It does not prove that every spatial feature helps or establish which feature causes the gain.

The original file-format/size control reaches AUROC 1.000. Processed-file facts reach 0.500 in matched conditions, but the deliberate mismatch E2 reaches 1.000 by design. Removing explicit file facts does not remove prior JPEG traces from pixels.

BigGAN is enlarged from 128 to 256; ADM starts at 256 and SD at 512. BigGAN's unusually low high-band energy is consistent with its enlargement, and many high-frequency features almost perfectly separate it from reals. This strongly affects pooled interpretation.

## What the exploratory diagnostics add

Source: results/diagnostics/history_diagnostics.csv and src/history_diagnostics.py.

D1 uses a native 128-square centre crop followed by 2x bicubic enlargement for every surviving parent. Six undersized real images are excluded, leaving 2,994 parents and 599 test parents. Compare the D1 C0 and R rows on those same surviving test parents; do not mix the D1 0.796 baseline with the locked 600-parent 0.793 baseline.

| D1 comparison | C0 | R | Paired change and 95% interval |
|---|---|---|---|
| Pooled combined, E1 | 0.796 | 0.802 | +0.006 [-0.036, 0.045] |
| BigGAN frequency, E1 | 1.000 | 0.828 | -0.172 [-0.225, -0.125] |
| Unseen SD spatial, E4 | 0.477 | 0.771 | +0.295 [0.235, 0.358] |
| Pooled spatial minus frequency, E1 | -0.088 | +0.022 | C0 [-0.130, -0.045]; R [-0.015, 0.056] |

The supported frequency advantage disappears in R; the R interval does **not** establish spatial superiority. The pooled interval includes zero, so say “similar pooled scores” or “no detectable pooled change,” not “equal” or “proved unchanged.”

All 500 BigGAN parents have identical saved feature values between C0 and R, checked independently this turn. The diagnostic code also asserts pixel identity for one BigGAN image. However, classifiers are refitted, and other generators' training features change. Therefore unchanged BigGAN inputs do **not** prove its classifier-AUROC change comes only from the reals. For univariate BigGAN-versus-real feature AUROCs, unchanged BigGAN feature values localise the change to the real comparison distribution. That is a narrower and defensible statement.

R shares a final crop/enlargement operation; it does not equalise complete acquisition/compression history. It changes field of view for other images, and training-data representation also changes. It is exploratory evidence of processing sensitivity, not a pure causal resize experiment. BigGAN still separates reasonably under R, so enlargement does not explain all its separation.

D2 holds the clean model and threshold fixed. Spatial false positives move from 98/300 (32.7%) to 157/300 (52.3%) at q50: 59 more real images flagged, or +19.7 percentage points. Frequency moves 14 to 16; combined 37 to 42. Pooled AUROC changes by at most 0.027. This is the clearest practical connection between JPEG and the broader backbone: ranking stability and decision stability are different measurements.

## Further findings, best used in Q&A

- f11, the near-Nyquist/high-band ratio, reverses univariate separation under JPEG: pooled 0.299 to 0.581; BigGAN 0.009 to 0.772 at q50. The JPEG-block explanation is consistent with the observation, not causally established by this experiment.
- f14, peak strength, is very stable but uninformative here: univariate AUROC approximately 0.497. Stable feature values alone do not establish useful detection.
- ADM combined separation rises by about 0.071 when SD is removed from training. This is exploratory and does not establish a general rule about diffusion families.
- High-band, Laplacian and high-pass statistics connect the course's spatial filters and Fourier analysis to observed processing effects. This is a useful DIP contribution even without a high-performing detector.

## Strategy for the final day

Present the pipeline and modest held-out result first, then show the processing diagnostic and JPEG decision drift. This connects the experiments into one argument without adding a new detection claim.

The strongest addition is a reporting rule, grounded in existing evidence: record native size and resize factor, show each generator separately, and evaluate fixed-threshold false positives alongside AUROC. This is a synthesis, not a newly validated algorithm.

The next most informative experiment would hold field of view fixed while changing resampling, and separate fixed-model effects from retraining effects. Further held-out folds and content-matched pairs are worthwhile future work. A never-enlarge/native-256 experiment is not present merely because a branch has that name. Do not present proposals as completed results.

I recommend using the remaining time for rehearsal and Q&A rather than tuning features, adding deep-model baselines or expanding the data. Such work would add interpretive and validation obligations before tomorrow.

## Presentation review and rehearsal copy

The current deck is visual and already follows the required Introduction, Novelty, Methodology, Experiments, Results, Limitations and Future structure. Its declared notes total 383 seconds: 118, 135 and 130 by member. Those are planned durations, not observed speech timings. Two members exceed their two-minute allocation before transitions.

The rehearsal copy uses 11 speaking slides plus three backups after the closing slide. It preserves the original deck and accepted pipeline. Duplicate preview and spectral-detail material move to backup, novelty wording becomes a project contribution, and causal/control wording is qualified. Each member has a 110-second speaking allocation, leaving ten seconds per member for transitions.

| Presenter | Main slides | Job |
|---|---|---|
| Member 1 | 1-3 | Problem, data history and contribution |
| Member 2 | 4-7 | Pipeline, DIP features, experiments and locked results |
| Member 3 | 8-11 | Exploratory diagnostic, JPEG decisions, limits and conclusion |

Use presentation/rehearsal_script.md or the PPTX notes. Stop at slide 11 for the timed talk; slides 12-14 are Q&A backups. Names remain Member 1/2/3 until supplied. The pipeline overview is too dense to read every box in six minutes; point out split integrity and matched processing, then use the feature visual for the DIP explanation.

## Short Q&A answers

**Why not claim AI detection?** Prior JPEG and resizing differ between classes, and content is unmatched. Our measured separation can include those effects.

**Why is AUROC 0.629 worth presenting?** It is an honest held-out-generator result for explainable features. The contribution is understanding what the scores measure, not claiming a deployable detector.

**Is JPEG robustness proved?** E3 refits at each quality. D2 separately tests fixed clean models. Ranking changes little, but the spatial model's false positives increase substantially.

**Did you prove resizing causes all of BigGAN's score?** No. R changes crop and fitted models. Unchanged BigGAN feature values give a narrower univariate reference-distribution check; the classifier results show broader sensitivity.

**Why can combined help if spatial alone is at chance?** Joint features can support a different fitted boundary. The observed +0.061 gain supports complementarity in this setup, without identifying its causal feature driver.

**What is new?** A project-specific feature-level audit linking controlled processing, generator-specific statistics and decisions. We make no first or state-of-the-art claim.

**What would you do next?** Pre-specify a matched-field-of-view processing comparison, then rotate generator holdouts and address content matching.

## Validation and limits of this review

Recomputed E1/E5 AUROCs independently from saved per-image predictions and checked BigGAN C0/R feature identity for all 500 parents. Source: reports/final_day_numeric_verification.json. The original and rehearsal PPTX files were rendered through LibreOffice; PDF pages and slide images were inspected. Bootstrap intervals were cross-checked against saved tables, not regenerated. No new training, full pipeline rerun, paid service, or literature verification was performed. Actual spoken timing still requires an aloud rehearsal.

Original paper/deck wording remains available and includes causal overstatements described above. Use the qualified rehearsal copy and this evidence map for tomorrow. No original experimental result was changed.
