# Research Log

Chronological record of research decisions and actions. Append-only.

| # | Date | Type | Summary |
|---|------|------|---------|
| 1 | 2026-09-14 | bootstrap | Locked the experimental pipeline (v1.0) and the 20-paper reference set. Main question fixed: which simple feature set (pixel-pattern, frequency, combined) separates real from AI-generated images under matched JPEG compression and an unseen generator. Hypotheses H1-H5 written in advance; H5 deferred. Config (dataset GenImage, quota 1500/1500, generators biggan/sd_v1_4/adm, 14 features, L2 logistic regression, seeds split=2026 / bootstrap=20260914) fixed before any result. |
| 2 | 2026-09-27 | bootstrap | Initialized the autoresearch workspace: moved the accepted proposal and pipeline into the `{project}/` layout, created `research-state.yaml`, `research-log.md`, `findings.md`, and scaffolded `experiments/` for E1-E5 with the H-to-E mapping. No research results yet; pre-registration baseline established. |
| 3 | 2026-09-27 | bootstrap | Stage 0 locked in `config.yaml` before any download: data from the `nebula/GenImage-arrow` mirror of GenImage `val` (fallback step b, streaming); content-blind sampling rule sha1(path) < 0.12, then a seeded 500 real + 500 fake draw per subset; split 60/20/20 stratified by label x subset; SD v1.4 = unseen generator; C2 = reals JPEG q75 vs fakes PNG; Pillow JPEG 4:2:0; pHash DCT-64 with Hamming <= 4; class_weight balanced (needed for E4/E5 imbalance). Feature definitions pinned where the spec left detail open (mean removal before Hann, radial-average slope fit, CV for anisotropy, 3x3 local max for the peak). Stage 6 synthetic checks pass against hand calculations. |
| 4 | 2026-09-27 | inner-loop | Stages 6-7 done (features 129 s; pilot GO). Stage 8 stopped on the shuffled-label control (single shuffle E1 0.623, E2 0.268). Diagnosis: alignment verified; over 200 shuffles mean 0.512 / 0.514, SD 0.09 — a single shuffle is a random direction, not a usable gate. Held pending the owner's decision on the check (see results/diagnostics/shuffle_control.md). |
| 5 | 2026-09-27 | inner-loop | Deviation 1 approved (200 shuffles, mean within 0.5 +/- 0.03) and committed before the rerun. Stages 8-9: all controls pass. E1 combined 0.793; E3 changes <= 0.025; E4/E5 SD v1.4 held out drops ~0.08 (combined 0.634 / 0.629). |
| 6 | 2026-09-27 | outer-loop | Per-generator and per-feature analysis: BigGAN (2x upsampled by the locked resize) is separated near-perfectly by high-band features, diffusion families only 0.63-0.76; f11 reverses under q50 (BigGAN-driven); f14 stable but uninformative; pixel+frequency complementary on the unseen family; exploratory ADM gain when SD leaves training. |
| 7 | 2026-09-27 | conclude | All pre-registered hypotheses decided (H1 supported, H2 partly, H3 supported in unexpected form, H4 supported for SD v1.4, H5 not tested). Further experiments (no-upsampling resize, fold rotation, content matching) would change locked values; left as open questions. Stage 10 report, limitations, figures written. |

<!-- Entry types:
  bootstrap    — initial scoping, literature search, hypothesis formation
  inner-loop   — experiment run and result
  outer-loop   — synthesis, reflection, direction decision
  pivot        — change in research direction
  report       — progress presentation generated
  conclude     — decision to finalize and write paper
-->
