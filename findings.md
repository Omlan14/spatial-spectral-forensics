# Research Findings

## Research Question

With the same processing applied to both classes and a strict split by image
group, which simple feature set separates real photographs from AI-generated
images best: pixel-pattern features, frequency (spectrum) features, or both
combined? And how much does the answer change when (a) both classes are
JPEG-compressed, and (b) the test set uses an image generator the study never
trained on?

## Current Understanding

The study is at the pre-registration stage: the design is locked (pipeline v1.0)
and no experiments have been run. The working position from the literature is
that frequency-domain traces are real but weakenable, that local pixel-pattern
statistics transfer across generators, and that JPEG and size differences can
masquerade as detection evidence if processing is not matched. This study does
not aim to build a new detector; it measures which simple, explainable features
carry signal and which survive compression and generator shift.

## Key Results

None yet. Experiment directories (`experiments/e1-first-check` ... `e5-main-result`)
are scaffolded with empty `protocol.md`, `results/`, and `analysis.md`. E5
(unseen generator + JPEG quality 75) is the intended headline result; E1-E4 support it.

## Patterns and Insights

Nothing observed yet. Candidate expectations to confirm or refute once data exists:
- The combined arm should not automatically beat the best single arm (feature
  redundancy between pixel-pattern and frequency statistics).
- Broad-spectrum frequency features are expected to be more robust to JPEG than a
  narrow peak feature (H3), but this is explicitly unsettled in the literature.

## Lessons and Constraints

Pre-registration constraints set in advance (do not relax after seeing results):
- Stages run in order 0-10; no stage is skipped; checks stop the pipeline on failure.
- Locked values (config.yaml) are decided at Stage 0 and never changed after results.
- Splits are by image group; every parent image and all its variants stay in one split.
- Scalers, regularization (`C`), and thresholds are fitted on train/validation data only.
- Statistics resample whole image groups, never individual JPEG variants.
- Claim wording: "the separation changed after the controlled change", never "JPEG caused X";
  "no retrieved abstract reports this exact protocol", never "first".
- Before any stronger novelty wording, two full reads are required: Grommelt et al. [1]
  and Sato et al. [10].

## Open Questions

- Which individual statistics gain or lose separation when processing is matched
  versus mismatched? (The literature reports this only at the detector level.)
- Does the pixel-pattern arm transfer across generator families as well as the
  frequency arm under the matched procedure?
- How much of any E1 separation is content bias (H5), which this study does not test?

## Optimization Trajectory

No runs yet. Metric: AUROC (primary), with balanced accuracy at the
validation-selected threshold. To be populated in `research-state.yaml`
(`experiments.trajectory`) as inner-loop runs complete.
