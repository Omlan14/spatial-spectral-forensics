# Experiments

Per-hypothesis / per-experiment work following the autoresearch convention.

## Layout

```
experiments/
└── {slug}/
    ├── protocol.md     # What, why, and the prediction (locked BEFORE running)
    ├── code/           # Experiment-specific code
    ├── results/        # Raw outputs, metrics, logs
    └── analysis.md     # What we learned
```

Shared, reusable code belongs in [`../src/`](../src); raw result data belongs in
[`../data/`](../data). Do not duplicate those here.

## Hypothesis to experiment map

The locked pipeline (`../src/experimental-pipeline.md`, Sections 7-8) uses
experiment IDs **E1-E5**, each the operational test of one hypothesis.

| Experiment | Slug | Hypothesis | Split | Condition | Question it answers |
|---|---|---|---|---|---|
| E1 | `e1-first-check` | H1 | by image group | C0 | Do the features separate the classes at all? |
| E2 | `e2-shortcut-control` | H2 | by image group | C2 | Does a deliberately unfair pipeline "detect" the shortcut? (control) |
| E3 | `e3-jpeg-test` | H3 | by image group | C1 (90/75/50) | What happens under fair compression? |
| E4 | `e4-unseen-generator` | H4 | generator held out | C0 | Does it transfer to an unseen generator family? |
| E5 | `e5-main-result` | H4 | held-out generator | C1 (75) | Unseen generator **and** JPEG together: the headline result |

H5 (content bias) is **not tested** by design; it is documented in the limitations.

## Protocol discipline

- `protocol.md` is committed to git **before** the experiment runs (pre-registration).
- Results matching the locked protocol are **confirmatory**; anything else is
  **exploratory** and is labelled as such in `analysis.md`.
- Protocol commits and result commits are never combined.
