"""Post-hoc diagnostics (EXPLORATORY, run 2026-09-30 after the locked study concluded).

The locked study (E1-E5) left one open mechanism question: is the near-perfect BigGAN separation
created by the pipeline's own 2x bicubic upsample? These diagnostics answer it without touching
any locked value, split, feature, or classifier:

  D1  resampling-matched condition R: every parent is centre-cropped to 128x128 at NATIVE
      resolution (no resampling), then upsampled 2x bicubic to 256x256. Every image, real or
      fake, now shares one identical resampling history. Same 14 features, same split,
      same classifier recipe, same bootstrap as E1 (all seen) and E4 (SD v1.4 held out).
  D2  fixed-model JPEG transfer: the E1 (C0-trained) models are scored on the C1 test images
      without refitting. Limitation 8 said robustness was measured under refit only.

Note on D1: BigGAN fakes are 128x128, so their R image is pixel-identical to their C0 image
(asserted below). Any BigGAN change between C0 and R therefore comes from the reals' processing.
For SD v1.4, ADM and reals, R also changes the field of view (a 128 crop of a 512 SD image covers
a quarter of its width), so their changes mix resampling and field of view.

Usage: python src/history_diagnostics.py
Writes results/diagnostics/history_diagnostics.csv (and caches features/features_R.parquet).
"""
import numpy as np
import pandas as pd
from PIL import Image, ImageOps

from common import CFG, DATA, ROOT, check
from experiments import ARMS, TRACE, auroc, ci, fit
from features import NAMES, extract, luminance
from prepare import raw_path

OUT = ROOT / "results" / "diagnostics"
CROP = 128
GENS = CFG["generators"]
SUBSETS = ["all"] + GENS


def resample_matched(path):
    """Native-resolution 128x128 centre crop, then one 2x bicubic upsample (identical for all)."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if min(im.size) < CROP:
        return None
    l, t = (im.width - CROP) // 2, (im.height - CROP) // 2
    im = im.crop((l, t, l + CROP, t + CROP)).resize((2 * CROP, 2 * CROP), Image.BICUBIC)
    return (np.asarray(im, dtype=np.float64) @ [0.299, 0.587, 0.114] / 255.0).astype(np.float32)


def build_R(sp, prov):
    cache = ROOT / "features" / "features_R.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    rows = []
    for r in sp.itertuples():
        p = prov.loc[r.image_id]
        I = resample_matched(raw_path(p.source_dataset, r.image_id, p.original_format))
        if I is not None:
            rows.append([r.image_id, *extract(I)[0]])
    R = pd.DataFrame(rows, columns=["image_id"] + NAMES)
    R.to_parquet(cache, index=False)
    return R


def rounds(y, s, gen, B):
    """Point AUROC and bootstrap rounds per subset (all; each generator vs all reals)."""
    out = {}
    for sub in SUBSETS:
        m = np.ones(len(y), bool) if sub == "all" else (gen == sub) | (gen == "real")
        out[sub] = (auroc(y[m], s[m]), np.array([auroc(y[b][m[b]], s[b][m[b]]) for b in B]))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sp = pd.read_csv(DATA / "splits.csv")
    prov = pd.read_csv(DATA / "provenance.csv", dtype=str, keep_default_na=False).set_index("image_id")
    F = pd.read_parquet(ROOT / "features" / "features.parquet")
    P = pd.read_parquet(ROOT / "results" / "per_image_predictions.parquet")
    info = sp.set_index("image_id")
    rows = []

    # ---------------------------------------------------------------- D1: condition R
    R = build_R(sp, prov).merge(sp, on="image_id")
    R["y"] = (R.label == "fake").astype(int)
    check(np.isfinite(R[NAMES].values).all(), "D1: no NaN/Inf in resampling-matched features")
    c0 = F[F.condition == "C0"].set_index("image_id")
    bg = R[R.generator_family == "biggan"].set_index("image_id")
    check(np.allclose(bg[NAMES].values, c0.loc[bg.index, NAMES].values, rtol=0, atol=1e-6),
          "D1: BigGAN features identical in C0 and R (same pixels; only the reals' processing changes)")
    one = bg.index[0]
    p = prov.loc[one]
    check(np.array_equal(luminance(ROOT / "data" / "images" / "canonical" / f"{one}.png"),
                         resample_matched(raw_path(p.source_dataset, one, p.original_format))),
          "D1: a BigGAN C0 image and its R image are pixel-identical")
    dropped = sorted(set(sp.image_id) - set(R.image_id))
    print(f"D1: {len(R)} parents; {len(dropped)} dropped (native side < {CROP}): {dropped}")

    test_ids = np.sort(R[R.split == "test"].image_id.values)
    B = np.random.default_rng(CFG["seeds"]["bootstrap"]).integers(
        0, len(test_ids), (CFG["bootstrap_rounds"], len(test_ids)))
    gen = info.generator_family.loc[test_ids].values
    y = info.label.loc[test_ids].eq("fake").astype(int).values
    for exp, col in (("E1", "split"), ("E4", "fold_unseen")):
        d = R.sort_values("image_id")
        tr, va, te = (d[d[col] == s] for s in ("train", "val", "test"))
        check(set(te.image_id) == set(test_ids), f"D1 {exp}: test set = all surviving locked test parents")
        te = te.set_index("image_id").loc[test_ids]
        res = {}
        for arm, cols in ARMS.items():
            sc, m, C, thr, _ = fit(tr, va, cols, tr.y)
            res["R", arm] = rounds(y, m.decision_function(sc.transform(te[cols])), gen, B)
            res["C0", arm] = rounds(y, P[(P.exp == exp) & (P.arm == arm)].set_index("image_id")
                                    .score.loc[test_ids].values, gen, B)
        for sub in SUBSETS:
            for arm in ARMS:
                (r, rr), (c, cr) = res["R", arm][sub], res["C0", arm][sub]
                rows.append({"diagnostic": "D1", "exp": exp, "comparison": arm, "subset": sub,
                             "auroc_C0": c, "C0_lo": ci(cr)[0], "C0_hi": ci(cr)[1],
                             "auroc_R": r, "R_lo": ci(rr)[0], "R_hi": ci(rr)[1],
                             "delta": r - c, "delta_lo": ci(rr - cr)[0], "delta_hi": ci(rr - cr)[1],
                             "n_test": len(test_ids)})
            for a, b in (("pixel", "frequency"), ("combined", "frequency")):   # paired arm differences
                for cond in ("C0", "R"):
                    (pa, ra), (pb, rb) = res[cond, a][sub], res[cond, b][sub]
                    rows.append({"diagnostic": "D1 arm difference", "exp": exp, "comparison": f"{a} - {b}",
                                 "subset": sub, "condition": cond, "delta": pa - pb,
                                 "delta_lo": ci(ra - rb)[0], "delta_hi": ci(ra - rb)[1],
                                 "n_test": len(test_ids)})
    Rall = R.set_index("image_id")
    g_all = info.generator_family.loc[Rall.index].values
    for f in NAMES:                                                # univariate AUROC, all surviving parents
        for g in GENS:
            ids = Rall.index[(g_all == g) | (g_all == "real")]
            yy = info.label.loc[ids].eq("fake").astype(int).values
            rows.append({"diagnostic": "D1 univariate", "comparison": f, "subset": g,
                         "auroc_C0": auroc(yy, c0.loc[ids, f].values),
                         "auroc_R": auroc(yy, Rall.loc[ids, f].values)})

    # ---------------------------------------------------------------- D2: fixed-model JPEG transfer
    d0 = F[F.condition == "C0"].merge(sp, on="image_id").sort_values("image_id")
    d0["y"] = (d0.label == "fake").astype(int)
    tr, va = d0[d0.split == "train"], d0[d0.split == "val"]
    for arm, cols in ARMS.items():
        sc, m, C, thr, _ = fit(tr, va, cols, tr.y)
        for q in [0] + CFG["jpeg_qualities"]:
            te = F[(F.condition == ("C0" if q == 0 else "C1")) & (F.quality == q)].merge(sp, on="image_id")
            te = te[te.split == "test"].sort_values("image_id")
            yt, gt = (te.label == "fake").astype(int).values, te.generator_family.values
            s = m.decision_function(sc.transform(te[cols]))
            ref = "E1" if q == 0 else f"E3_q{q}"
            s_refit = P[(P.exp == ref) & (P.arm == arm)].set_index("image_id").score.loc[te.image_id].values
            if q == 0:
                check(np.allclose(s, s_refit), f"D2 {arm}: refitting E1 reproduces the stored E1 scores")
            for sub in SUBSETS:
                mk = np.ones(len(yt), bool) if sub == "all" else (gt == sub) | (gt == "real")
                rows.append({"diagnostic": "D2", "exp": "E1 model on " + ("C0" if q == 0 else f"q{q}"),
                             "comparison": arm, "subset": sub, "quality": q,
                             "auroc_transfer": auroc(yt[mk], s[mk]), "auroc_refit": auroc(yt[mk], s_refit[mk]),
                             "reals_flagged": int((s[yt == 0] >= thr).sum()), "n_reals": int((yt == 0).sum()),
                             "fakes_flagged": int((s[mk & (yt == 1)] >= thr).sum()),
                             "n_fakes": int((mk & (yt == 1)).sum())})

    out = pd.DataFrame(rows).assign(**TRACE, note="EXPLORATORY post-hoc diagnostic (2026-09-30)")
    out.to_csv(OUT / "history_diagnostics.csv", index=False)
    print(f"wrote {OUT / 'history_diagnostics.csv'}: {len(out)} rows")


if __name__ == "__main__":
    main()
