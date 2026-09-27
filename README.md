# Interpreting Spatial-Frequency Features for AI-Generated Image Detection Under Generator Shift and JPEG Compression

A feature-level study that asks one question: with the same processing applied to
both classes and a strict split by image group, which simple feature set
separates real photographs from AI-generated images best — pixel-pattern
features, frequency (spectrum) features, or both combined — and how much the
answer changes under matched JPEG compression and on an unseen generator.

**What this study is:** careful measurements of simple, explainable image statistics.
**What it is not:** a new detector, a comparison against the best published
methods, or a claim about all AI images.

The study is organized in the autoresearch project layout and driven by a locked,
pre-registered pipeline. The full workspace follows this structure:

```
DIP Project (Final)/
├── research-state.yaml       # Central state tracking (project, hypotheses, experiments)
├── research-log.md           # Decision timeline (append-only)
├── findings.md               # Evolving narrative synthesis (project memory)
├── literature/               # Reference library and survey notes
│   ├── literature-review.md        # The 20-paper reference set, by job in the study
│   ├── references.bib              # BibTeX (20 cited + archived extras)
│   ├── survey.md                   # Running survey notes
│   └── README.md
├── src/                      # Reusable code and the method specification
│   ├── experimental-pipeline.md    # THE SPECIFICATION (Stages 0-10, locked v1.0)
│   ├── pipeline-diagram.py         # Figure 1 script (self-checking)
│   ├── pipeline-diagram.png / .pdf # Figure 1 output
│   └── README.md
├── data/                     # Raw result data (CSVs, JSONs); no code, no large artifacts
│   └── README.md
├── experiments/              # Per-hypothesis / per-experiment work
│   ├── e1-first-check/             # H1 - do the features separate the classes? (C0)
│   ├── e2-shortcut-control/        # H2 - deliberate mismatch control (C2)
│   ├── e3-jpeg-test/               # H3 - fair JPEG compression (C1, 90/75/50)
│   ├── e4-unseen-generator/        # H4 - generator held out (C0)
│   ├── e5-main-result/             # H4 - unseen generator + JPEG 75 (headline)
│   └── README.md                   # Hypothesis-to-experiment map + protocol discipline
├── to_human/                 # Progress presentations for human review
├── paper/                    # Final manuscript (paper-lifecycle skills)
│   └── figures/
└── .roo/                     # Bundled AI research skills (autoresearch + supervisor skills)
```

Each `experiments/{slug}/` directory contains `protocol.md` (locked before
running), `code/`, `results/`, and `analysis.md`.

## Start here

| To understand... | Read |
|---|---|
| The method and every locked decision | [`src/experimental-pipeline.md`](src/experimental-pipeline.md) |
| Why the design is the way it is | [`literature/literature-review.md`](literature/literature-review.md) |
| Current research state | [`research-state.yaml`](research-state.yaml) |
| What we know so far | [`findings.md`](findings.md) |
| The decision timeline | [`research-log.md`](research-log.md) |
| How experiments map to hypotheses | [`experiments/README.md`](experiments/README.md) |
| **Results and conclusion** | [`reports/final_results.md`](reports/final_results.md) (read [`reports/limitations.md`](reports/limitations.md) first) |

## Reproduce (Stage 10)

Environment used: Windows 11, CPU only; Python 3.13.2, numpy 2.2.4, scipy 1.16.2, scikit-learn 1.7.2,
pandas 2.3.3, Pillow 11.1.0 (decoder and JPEG encoder), pyarrow 25.0.1, matplotlib 3.10.1, PyYAML 6.0.3.
Config hash `87f5489e9d59` (Stage 0 lock + deviation 1); split hash in `data/split_hash.txt`;
seeds split 2026, bootstrap 20260914.

```bash
pip install numpy scipy scikit-learn pandas pillow pyarrow matplotlib pyyaml
cd src
python fetch.py                  # Stage 1: streams ~5.8 GB, stores ~0.5 GB sample in data/raw/ (~40 min)
python prepare.py                # Stages 2-5: checks, split, standard PNGs, C0/C1/C2 (~1 min)
python features.py               # Stage 6: synthetic checks, then 14 features (~2 min)
python experiments.py --pilot    # Stage 7: pilot gate
python experiments.py            # Stages 8-9: E1-E5 x 3 arms, controls, bootstrap (~2 min)
python report.py                 # Stage 10: figures/ from results/
```

Every script stops on a failed check. Result tables carry the config hash, code version, and seeds.

**Rerun check (2026-09-27):** Stages 2-9 rerun from the stored raw sample reproduced every `data/` table
byte-for-byte and every `results/*.csv` table exactly (only the `code_version` column differs).

## What the study does in one line

Compare three simple feature sets (pixel-pattern, frequency, and both combined)
for telling real photographs from AI-generated images apart, with JPEG
compression and an unseen generator as the two tests. H1 is the first check
(does any signal exist), and H5 (content bias) is not tested, which is stated in
the limitations.

## The 20-paper reference set

- **How it was chosen:** by job, not by count. It is the 17 papers that directly
  shape the design (Tier 1 and Tier 2 of the earlier ranking) plus the 3 context
  papers with stated roles: DIRE, FIRE (reconstruction-based methods, cited but
  not implemented) and AI-GenBench (the fallback data source).
- **Verification (2026-09-14):** all 20 records were checked against primary
  sources (arXiv pages, CVF Open Access, publisher DOI pages, the OpenReview API,
  and OpenAlex). This pass fixed **eight wrong author lists**, completed **three
  incomplete author lists**, and corrected two venues (Corvi et al. = ICASSP 2023,
  not AVSS; Durall et al. = CVPR Workshops 2020, not 2019). The full correction
  table is in `literature/literature-review.md` Section 2.
- **Rule going forward:** nothing is cited until its details are checked against a
  primary source.

## Honesty rules kept in these deliverables

- No invented references, no unverified details, and no claims beyond what was checked.
- Novelty is written as "no retrieved abstract reports this exact protocol", never "first".
- No numbers are quoted from the cited papers (their result tables were not
  audited); they are cited for their role in the design.
- Two full reads remain required **before any stronger novelty wording in a paper
  submission**: Grommelt et al. (closest JPEG-bias study) and Sato et al. (closest
  radial-spectrum method). No other full reads are needed.

## AI research toolchain

The study is driven by an AI-agent skill selected from the Orchestra Research
library: [`autoresearch`](.roo/skills/autoresearch/) (installed under
`.roo/skills/`). It runs the pipeline as a two-loop experiment/synthesis cycle and
keeps structured research state, matching the traceability rule in
[`src/experimental-pipeline.md`](src/experimental-pipeline.md) Section 1. The
paper-lifecycle skills and the full HKUST (DIAL) Supervisor-Skills handbook are
bundled alongside it. See [`.roo/README.md`](.roo/README.md) for the full
inventory and stage mapping.

Note: the Orchestra library has no image-processing or JPEG-forensics skill, so no
framework-specific skill for this study exists; the study's own specification and
code implement the measurement.

## Citation, licence, and attribution

- **Cite this project:** [`CITATION.cff`](CITATION.cff).
- **Licence:** MIT for this project's deliverables (see [`LICENSE`](LICENSE)).
- **Third-party content:** the bundled skills under `.roo/` are `autoresearch`
  (Orchestra Research, MIT) and Supervisor-Skills (HKUST DIAL, CC BY-NC-SA 4.0).
  They keep their upstream licences; see [`ATTRIBUTION.md`](ATTRIBUTION.md).
- **Data:** the image data (GenImage, with AI-GenBench as fallback) is not
  redistributed here; it is downloaded at run time under its own terms.
