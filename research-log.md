# Research Log

Chronological record of research decisions and actions. Append-only.

| # | Date | Type | Summary |
|---|------|------|---------|
| 1 | 2026-09-14 | bootstrap | Locked the experimental pipeline (v1.0) and the 20-paper reference set. Main question fixed: which simple feature set (pixel-pattern, frequency, combined) separates real from AI-generated images under matched JPEG compression and an unseen generator. Hypotheses H1-H5 written in advance; H5 deferred. Config (dataset GenImage, quota 1500/1500, generators biggan/sd_v1_4/adm, 14 features, L2 logistic regression, seeds split=2026 / bootstrap=20260914) fixed before any result. |
| 2 | 2026-09-27 | bootstrap | Initialized the autoresearch workspace: moved the accepted proposal and pipeline into the `{project}/` layout, created `research-state.yaml`, `research-log.md`, `findings.md`, and scaffolded `experiments/` for E1-E5 with the H-to-E mapping. No research results yet; pre-registration baseline established. |

<!-- Entry types:
  bootstrap    — initial scoping, literature search, hypothesis formation
  inner-loop   — experiment run and result
  outer-loop   — synthesis, reflection, direction decision
  pivot        — change in research direction
  report       — progress presentation generated
  conclude     — decision to finalize and write paper
-->
