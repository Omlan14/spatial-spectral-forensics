# research-final — Final deliverables (AI-generated image detection project)

**Project:** Interpreting Spatial–Frequency Features for AI-Generated Image Detection Under Generator Shift and JPEG Compression

This folder is the complete, final deliverable set for the course project. It replaces the earlier draft versions, which were reorganized in the workspace and are not needed to read or run anything here. The team-facing project plan is `../../PROJECT_HANDOFF.md`.

## Contents

| File | What it is |
|---|---|
| `experimental-pipeline.md` | **The specification.** Stages 0–10 as a strict step-by-step flow. Every stage explains in plain words what it does and why, lists the exact settings locked in advance, the checks that stop the pipeline on failure, and the papers that support it. This document is both the plan and the method. |
| `literature-review.md` | The 20-paper reference set, organized by the job each paper does in the study. Each entry says what the authors did, what they found, why it is in our study, and how far we can use its result. Also includes the hypothesis-by-hypothesis summary, the careful novelty statement, and the full verification record. |
| `references.bib` | BibTeX for the 20 cited references (all details verified 2026-09-14) plus an **archived section** holding 17 papers from the earlier corpus for future expansion. Those are not cited by anything. |
| `pipeline-diagram.png` / `.pdf` | Figure 1: the pipeline flow, drawn from `experimental-pipeline.md` Section 4. |
| `pipeline-diagram.py` | The script that draws the figure. Rerun it to regenerate the PNG and PDF; it checks its own layout and refuses to save if any text overlaps or does not fit. |

## What the study does in one line

Compare three simple feature sets (pixel-pattern, frequency, and both combined) for telling real photographs from AI-generated images apart, with JPEG compression and an unseen generator as the two tests. H1 is the first check (does any signal exist), and H5 (content bias) is not tested, which is stated in the limitations.

## The 20-paper reference set

- **How it was chosen:** by job, not by count. It is the 17 papers that directly shape the design (Tier 1 and Tier 2 of the earlier ranking) plus the 3 context papers with stated roles: DIRE, FIRE (reconstruction-based methods, cited but not implemented) and AI-GenBench (the fallback data source).
- **Verification (2026-09-14):** all 20 records were checked against primary sources (arXiv pages, CVF Open Access, publisher DOI pages, the OpenReview API, and OpenAlex). This pass fixed **eight wrong author lists**, completed **three incomplete author lists**, and corrected two venues (Corvi et al. = ICASSP 2023, not AVSS; Durall et al. = CVPR Workshops 2020, not 2019). The full correction table is in `literature-review.md` Section 2.
- **Rule going forward:** nothing is cited until its details are checked against a primary source.

## Honesty rules kept in these deliverables

- No invented references, no unverified details, and no claims beyond what was checked.
- Novelty is written as "no retrieved abstract reports this exact protocol", never "first".
- No numbers are quoted from the cited papers (their result tables were not audited); they are cited for their role in the design.
- Two full reads remain required **before any stronger novelty wording in a paper submission**: Grommelt et al. (closest JPEG-bias study) and Sato et al. (closest radial-spectrum method). No other full reads are needed.

## AI research toolchain

The study is driven by an AI-agent skill selected from the Orchestra Research library:
[`autoresearch`](.roo/skills/autoresearch/) (installed under `.roo/skills/`). It runs the
pipeline as a two-loop experiment/synthesis cycle and keeps structured research state,
matching the traceability rule in `experimental-pipeline.md` Section 1. The
paper-lifecycle skills and the full HKUST (DIAL) Supervisor-Skills handbook are bundled
alongside it. See [`.roo/README.md`](.roo/README.md) for the full inventory and stage
mapping.

Note: the Orchestra library has no image-processing or JPEG-forensics skill, so no
framework-specific skill for this study exists; the study's own specification and code
implement the measurement.

## Citation, licence, and attribution

- **Cite this project:** [`CITATION.cff`](CITATION.cff).
- **Licence:** MIT for this project's deliverables (see [`LICENSE`](LICENSE)).
- **Third-party content:** the bundled skills under `.roo/` are
  `autoresearch` (Orchestra Research, MIT) and Supervisor-Skills
  (HKUST DIAL, CC BY-NC-SA 4.0). They keep their upstream licences; see
  [`ATTRIBUTION.md`](ATTRIBUTION.md).
- **Data:** the image data (GenImage, with AI-GenBench as fallback) is not
  redistributed here; it is downloaded at run time under its own terms.
