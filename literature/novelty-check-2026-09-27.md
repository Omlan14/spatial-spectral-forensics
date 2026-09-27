# Novelty check after results (2026-09-27)

What was read: full text of Grommelt et al. [1] (arXiv HTML) and Li et al. 2026 (spectral tail, arXiv HTML);
Sato et al. [10] abstract only (VISAPP full text behind SciTePress login, NOT read in full); arXiv abstracts of
the remaining bib entries; one web search for 2025-26 overlap, which found Zhou & Wang 2026 (abstract read).

## Overlap with our findings

| Our finding | Already reported by |
|---|---|
| GenImage reals are JPEG (QF ~96), fakes PNG; fixed per-generator sizes incl. BigGAN 128 px; BigGAN spectrum shows upsampling artifacts | Grommelt et al. [1] (ECCV-W 2024), in detail; B-Free [2] (format/resolution bias) |
| Fixing JPEG/size bias changes cross-generator results | [1]: +11 pts cross-generator for ResNet50/Swin-T after matching QF96 and size-constrained reals |
| Spectral cues separate GANs, weaker for diffusion; detectors trained on one family degrade on another | [5]-[8], [11], [12], Ricker et al. 2024 |
| JPEG weakens high-frequency cues | [9], [11], Li et al. 2026 (App. A.1) |
| Preprocessing choices flip per-generator conclusions; score direction can invert (AUROC < 0.5) | Zhou & Wang, arXiv 2606.20488 (June 2026): controlled audit of training-free detectors on a 1,500-image GenImage subset, JPEG 70/50 |

## Not found in anything read (abstract level for most)

- Per-feature split of "value stability" vs "separation" under matched JPEG for a fixed, explainable feature set, with
  group-bootstrap CIs (f14 stable but uninformative; f11 reverses direction at q50, traced to BigGAN).
- Pixel-pattern features at chance on an unseen diffusion family yet adding +0.061 AUROC to frequency features.
- Removing one diffusion family from training raising another's separation (ADM +0.07..0.12; exploratory).

## Consequence

The study's main caveat is a known result ([1]); the design did not apply [1]'s published correction for size bias
(size-matched reals / no upsampling), so reviewers would read the pooled results as confounded by a documented bias.
Allowed wording remains "no retrieved abstract reports this exact protocol"; "first" is not supportable.
