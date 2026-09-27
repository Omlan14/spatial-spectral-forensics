# data — Raw Result Data

Structured raw result data: metric CSVs, JSONs, and small outputs used to replot,
reanalyze, and write up the paper. **No code here** (code lives in
[`../src/`](../src) and [`../experiments/`](../experiments)).

## Naming

Name files descriptively, e.g. `trajectory_H1_runs001-010.csv`,
`jpeg_robustness_quality75.csv`.

## Locked pipeline artifacts (from `../src/experimental-pipeline.md`)

These are the Stage 1-8 outputs and are the canonical data this project keeps:

```
data/provenance.csv            # one row per original file (Stage 1)
data/duplicate_clusters.csv    # duplicate / near-copy clusters (Stage 2)
data/canonical_manifest.csv    # SHA-256 per standard image (Stage 4)
data/variant_manifest.csv      # every variant with condition/quality/sha256 (Stage 5)
data/splits.csv                # locked group split (Stage 3)
data/split_hash.txt            # locked split fingerprint (Stage 3)
```

## Not stored here

- **Raw image corpora** (GenImage / AI-GenBench) are downloaded at run time and
  are not redistributed; they are large, licensed separately, and gitignored.
- **Large artifacts** (model checkpoints, feature `.parquet` files) go to a
  separate storage path, not this repository.
- `*.parquet` and `data/raw/` are gitignored (regenerable from the locked config
  and seeds). Small CSV/JSON result tables are tracked.
