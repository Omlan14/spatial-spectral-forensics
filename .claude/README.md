# `.roo/` — AI research toolchain for this project

This folder holds the AI-agent skills that support the study described in
[`../experimental-pipeline.md`](../experimental-pipeline.md) and
[`../literature-review.md`](../literature-review.md). It contains two independent
collections plus the skill selected to drive the experimental pipeline.

See [`../ATTRIBUTION.md`](../ATTRIBUTION.md) for the licence of each collection.

## Installed skills

| Skill | Role in this project |
|---|---|
| [`skills/autoresearch/`](skills/autoresearch/) | **Selected orchestrator.** Runs the pipeline as a two-loop experiment/synthesis cycle, tracks research state, and routes to domain skills. |
| `skills/deep-research/` | Survey-grade literature investigation (supports the 20-paper reference set). |
| `skills/idea-evaluator/` | Scores the research idea against a five-dimension framework. |
| `skills/tech-paper-template/` | Technical-paper skeleton and logic-chain planning. |
| `skills/benchmark-paper-template/` | Benchmark/evaluation paper structuring. |
| `skills/intro-drafter/` | Introduction drafting. |
| `skills/paper-writer/` | Evidence-gated manuscript drafting. |
| `skills/paper-polish/` | Meaning-preserving polishing. |
| `skills/pre-submission-reviewer/` | Five-dimension pre-submission audit. |
| `skills/rebuttal-guidance/` | Peer-review rebuttal guidance. |
| `skills/figure-designer/` | Figure design for the paper (Figure 1 and results plots). |
| `skills/drawio-reconstruction/` | Rebuild reference figures as editable Draw.io diagrams. |
| `skills/vibe-research-workflow/` | AI-assisted research workflow guidance. |

## The skill selected to run the pipeline

The Orchestra `autoresearch` skill (`.roo/skills/autoresearch/`) is the closest match
for this workspace. The study in `experimental-pipeline.md` is a fixed-protocol
experiment suite (E1–E5 × three feature arms), i.e. exactly the inner-loop
"run experiment → measure → record" pattern the skill orchestrates, with progress
reporting and structured state. Its `templates/` (`research-state.yaml`,
`research-log.md`, `findings.md`) map directly onto the pipeline's traceability rule
(every result records config hash, code version, and seeds).

The upstream library does not contain an image-processing or JPEG-forensics skill, so
no framework-specific skill for this study was available; the orchestration skill plus
the existing paper-lifecycle skills cover the deliverable.

## Where each pipeline stage is supported

- **Stages 0–8 (spec, splits, features, experiments)** — the study's own
  specification and code; `autoresearch` provides the loop, state, and logging.
- **Stage 9–10 (statistics, report, figures)** — `figure-designer` and
  `tech-paper-template` / `pre-submission-reviewer`.
- **Reference set** — `deep-research`.

## Supervisor-Skills handbook

[`supervisor-skills/`](supervisor-skills/) holds the full HKUST (DIAL) handbook
curriculum, with English versions under `supervisor-skills/handbook-en/`.
