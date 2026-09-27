# E2 — Shortcut control (H2)

**Status:** pending (protocol locked 2026-09-14; not yet run)

## What

Run the three arms on condition **C2** — the deliberate mismatch where the two
classes receive *different* processing — and compare the separation against the
matched conditions E1 (C0) and E3 (C1).

- **Split:** by image group (locked)
- **Condition:** C2 (control only)
- **Comparison:** E2 vs E1 vs E3, confidence intervals on the same image groups

## Why

C2 exists to demonstrate that a careless pipeline can "detect" processing instead
of content. It is a **control, never a reported detection result**. It is never
entered into E5's headline or the conclusion template.

## Prediction (locked before running)

The deliberate mismatch **changes** the separation relative to the matched
conditions, in the direction predicted in advance (mismatch inflates apparent
detection).

## Decision rule (H2)

H2 is supported only if the separation changes in the predicted direction, with a
confidence interval computed on the same image groups.

**Wording rule:** "the separation changed after the controlled change" — never
"JPEG caused X".

## Controls that run every time

1. Always-guess baseline.  2. History-only classifier.  3. Shuffled labels.

## Outputs

- Control table only -> `results/`
- Interpretation -> `analysis.md` (flagged: C2 is a control, not a result)
