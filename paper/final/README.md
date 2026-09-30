# Final report (6-page IEEE conference format) — current version

Supersedes `paper/submission/` (kept for history). One framing:

> **Same score, different story.** Under the accepted, pre-fixed pipeline the combined feature set
> gives the highest pooled AUROC, but the pooled score hides that the images' resampling history
> decides which generator looks easy and which feature family looks best.

| File | What |
|---|---|
| `main.tex` / `main.pdf` | IEEEtran conference paper (5 pages incl. references; limit 6) |
| `refs.bib` | the verified 20-paper set from `literature/references.bib` + Zhou & Wang 2026 |
| `figures/` | copies of `src/pipeline-diagram.pdf` (unchanged) and `figures/final/*.pdf` |
| `../../presentation/final_presentation.pptx` | 13-slide final deck (3 members x 2 min, section tracker, speaker scripts in notes) |

Build: `pdflatex main && bibtex main && pdflatex main && pdflatex main`.
Regenerate evidence: `cd src && python history_diagnostics.py && python final_figures.py && python deck_figures.py && python build_final_deck.py`.
Author names are placeholders (`Member One/Two/Three`).

## Claim → evidence map (every number in the paper)

| Claim | Evidence | Status |
|---|---|---|
| Combined highest pooled AUROC in every experiment (E1 0.793 [0.759, 0.826]) | `results/family_comparison.csv` | supported (not for BigGAN alone) |
| Matched JPEG moves pooled AUROC ≤ 0.025 refit, ≤ 0.027 fixed model | `results/jpeg_robustness.csv`; `history_diagnostics.csv` D2 | supported |
| Fixed pixel model flags 98 → 157 of 300 reals at q50 | D2 `reals_flagged` | supported (point counts) |
| SD v1.4 held out: −0.078 [−0.124, −0.034]; E5 headline 0.629 [0.571, 0.690] | `results/generator_shift.csv` | supported |
| File facts alone: AUROC 1.000 | `results/control_checks.csv` | supported |
| Resampling-matched R: pooled combined 0.796 → 0.802 (Δ +0.006 [−0.036, 0.045]) | D1 | supported, exploratory |
| R: BigGAN frequency 1.000 → 0.828; E4 SD pixel 0.477 → 0.771 | D1 | supported, exploratory |
| R: pixel − frequency −0.088 [−0.130, −0.045] → +0.022 [−0.015, 0.056] | D1 arm difference | supported, exploratory |
| BigGAN change comes from the reals only | pixel-identity check in `src/history_diagnostics.py` | verified in code |
| SD rise is due to resampling | — | **not claimed** (field of view also changes) |

## Wording rules kept
No "first" / "state of the art"; R is labelled post-hoc and exploratory; claims are bounded to
GenImage val, BigGAN / SD v1.4 / ADM, Pillow 4:2:0 JPEG at q90/75/50, one held-out generator, one split.
