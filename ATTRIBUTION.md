# Attribution and Third-Party Notices

This repository's own deliverables (the pipeline specification, literature review,
reference list, figure script, and top-level documentation) are released under the
MIT licence in [LICENSE](LICENSE).

It also bundles two third-party research-skill collections under `.roo/`. These keep
their upstream licences, and the top-level MIT licence does **not** apply to them.

## 1. Autoresearch skill — Orchestra Research

- **Source:** <https://github.com/Orchestra-Research/AI-Research-SKILLs>
- **Installed at:** [`.roo/skills/autoresearch/`](.roo/skills/autoresearch/)
- **Purpose here:** the research-orchestration layer used to run this study's
  experimental pipeline (two-loop experiment/synthesis cycle, research-state
  tracking, progress reporting).
- **Licence:** MIT (as published by the upstream project).

## 2. Supervisor-Skills — HKUST (DIAL), Yuyu Luo

- **Source:** <https://github.com/HKUSTDial/Supervisor-Skills>
- **Installed at:**
  - [`.roo/skills/`](.roo/skills/) — twelve paper-lifecycle skills, and
  - [`.roo/supervisor-skills/`](.roo/supervisor-skills/) — the handbook curriculum.
- **Purpose here:** research methodology, paper-writing, figure-design, and
  pre-submission-review guidance across the project lifecycle.
- **Licence:** CC BY-NC-SA 4.0. It is redistributed here non-commercially and under
  the same share-alike terms, consistent with the licence.

## 3. Project data

The image data referenced by the pipeline (GenImage, with AI-GenBench as a fallback)
is **not** redistributed in this repository. It is downloaded at run time from its
original source under that dataset's own terms; see `experimental-pipeline.md`,
Stage 1, and `literature-review.md` references [13] and [14].
