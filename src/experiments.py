"""Stages 7-9 — pilot gate, experiments E1-E5 x 3 arms + control checks, group-bootstrap statistics.

Usage: python src/experiments.py --pilot    (Stage 7: pilot subset, E1 + E3 q75)
       python src/experiments.py            (Stages 8-9: full run)
Positive class = generated (fake). E1-E5 share one locked test set, so all comparisons are paired.
"""
import json
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from common import CFG, CONFIG_HASH, DATA, ROOT, check
from features import FREQ, NAMES, PIXEL

PILOT = "--pilot" in sys.argv
OUT = ROOT / "results" / ("pilot" if PILOT else "")
ARMS = {"pixel": PIXEL, "frequency": FREQ, "combined": PIXEL + FREQ}
EXPS = [("E1", "C0", 0, "split"), ("E2", "C2", None, "split"), ("E3_q90", "C1", 90, "split"),
        ("E3_q75", "C1", 75, "split"), ("E3_q50", "C1", 50, "split"),
        ("E4", "C0", 0, "fold_unseen"), ("E5", "C1", 75, "fold_unseen")]
if PILOT:
    EXPS = [e for e in EXPS if e[0] in ("E1", "E3_q75")]
GIT = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
TRACE = {"config_hash": CONFIG_HASH, "code_version": GIT, "seed_split": CFG["seeds"]["split"],
         "seed_bootstrap": CFG["seeds"]["bootstrap"]}


def auroc(y, s):
    n1 = y.sum(); n0 = len(y) - n1
    return (rankdata(s)[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def bacc(y, p):
    return 0.5 * ((p[y == 1] == 1).mean() + (p[y == 0] == 0).mean())


def fit(tr, va, cols, ytr):
    sc = StandardScaler().fit(tr[cols])
    Xtr, Xva = sc.transform(tr[cols]), sc.transform(va[cols])
    fits = [(C, LogisticRegression(C=C, class_weight=CFG["classifier"]["class_weight"],
                                   max_iter=CFG["classifier"]["max_iter"]).fit(Xtr, ytr))
            for C in CFG["classifier"]["C_grid"]]
    C, m = max(fits, key=lambda f: (auroc(va.y.values, f[1].decision_function(Xva)), -f[0]))
    sva = m.decision_function(Xva)
    thr = max(np.unique(sva), key=lambda t: bacc(va.y.values, (sva >= t).astype(int)))
    return sc, m, C, thr, auroc(va.y.values, sva)


def load():
    F = pd.read_parquet(ROOT / "features" / "features.parquet")
    sp = pd.read_csv(DATA / "splits.csv")
    prov = pd.read_csv(DATA / "provenance.csv", dtype=str).set_index("image_id")
    D = F.merge(sp, on="image_id")
    D["y"] = (D.label == "fake").astype(int)
    D["h_is_jpeg"] = D.path.str.endswith(".jpg").astype(int)       # history of the file actually analysed
    D["h_quality"], D["h_w"], D["h_h"] = D.quality, 256, 256
    D["o_is_jpeg"] = (D.image_id.map(prov.original_format) == "JPEG").astype(int)   # history before receipt
    D["o_w"] = D.image_id.map(prov.original_width).astype(int)
    D["o_h"] = D.image_id.map(prov.original_height).astype(int)
    return D[D.pilot == 1] if PILOT else D


def run_experiments(D):
    preds, models, controls = [], [], []
    rng = np.random.default_rng(CFG["seeds"]["split"])
    for exp, cond, q, col in EXPS:
        d = D[(D.condition == cond) & ((D.quality == q) if q is not None else True)].sort_values("image_id")
        tr, va, te = (d[d[col] == s] for s in ("train", "val", "test"))
        check(not set(tr.image_id) & set(te.image_id) and not set(va.image_id) & set(te.image_id)
              and te.image_id.is_unique, f"{exp}: no group crosses train/val/test; one row per test group")
        for arm, cols in ARMS.items():
            sc, m, C, thr, va_auc = fit(tr, va, cols, tr.y)
            s = m.decision_function(sc.transform(te[cols]))
            preds.append(te[["image_id", "y", "generator_family"]].assign(exp=exp, arm=arm, score=s,
                                                                          pred=(s >= thr).astype(int)))
            models.append({"exp": exp, "arm": arm, "C": C, "threshold": thr, "val_auroc": va_auc,
                           "n_train": len(tr), "n_val": len(va), "n_test": len(te),
                           "coef": dict(zip(cols, m.coef_[0].round(6))), "scaler_mean": list(sc.mean_),
                           "scaler_scale": list(sc.scale_), **TRACE})
        # control checks (Section 6): they diagnose, never fix
        runs = [("always_guess", None, None)]
        runs += [("history_only", ["h_is_jpeg", "h_quality", "h_w", "h_h"], tr.y)]
        runs += [("shuffled_labels", PIXEL + FREQ, rng.permutation(tr.y.values))   # deviation 1: many shuffles,
                 for _ in range(CFG["shuffle_rounds"])]                              # judged on the mean
        runs += [("pre_receipt_history (exploratory)", ["o_is_jpeg", "o_w", "o_h"], tr.y)]
        res = {}
        for name, cols, ytr in runs:
            if cols is None:
                s, p = np.zeros(len(te)), np.zeros(len(te), int)
            else:
                sc, m, C, thr, _ = fit(tr, va, cols, ytr)
                s = m.decision_function(sc.transform(te[cols]))
                p = (s >= thr).astype(int)
            res.setdefault(name, []).append((auroc(te.y.values, s), bacc(te.y.values, p)))
        for name, r in res.items():
            r = np.array(r)
            controls.append({"exp": exp, "control": name, "auroc": r[:, 0].mean(), "auroc_sd": r[:, 0].std(),
                             "balanced_accuracy": r[:, 1].mean(), "rounds": len(r), **TRACE})
    return pd.concat(preds, ignore_index=True), models, pd.DataFrame(controls)


def gate(controls):
    tol = CFG["shuffle_mean_tolerance"]
    c = controls.set_index(["exp", "control"]).auroc
    for exp in controls.exp.unique():
        check(abs(c[exp, "shuffled_labels"] - 0.5) < tol,
              f"{exp}: mean shuffled-label AUROC {c[exp, 'shuffled_labels']:.3f} within 0.5 +/- {tol}")
        if exp != "E2":   # E2 is the deliberate mismatch; the history classifier is meant to see it
            check(abs(c[exp, "history_only"] - 0.5) < 0.02, f"{exp}: history-only AUROC {c[exp, 'history_only']:.3f} ~ 0.5")


def ci(v):
    return np.percentile(v, [2.5, 97.5])


def statistics(P, models):
    ids = np.sort(P.image_id.unique())                              # the shared test groups
    rng = np.random.default_rng(CFG["seeds"]["bootstrap"])
    B = rng.integers(0, len(ids), (CFG["bootstrap_rounds"], len(ids)))
    val = {(m["exp"], m["arm"]): m["val_auroc"] for m in models}
    first = P[(P.exp == P.exp.iloc[0]) & (P.arm == "pixel")].set_index("image_id").loc[ids]
    y, gen = first.y.values, first.generator_family.values
    subsets = {"all": np.ones(len(ids), bool), **{g: (gen == g) | (gen == "real") for g in CFG["generators"]}}

    boot = {}                                                       # (exp, arm, subset) -> (point, rounds) for AUROC, BA
    for (exp, arm), g in P.groupby(["exp", "arm"]):
        g = g.set_index("image_id").loc[ids]
        s, p = g.score.values, g.pred.values
        for sub, mask in subsets.items():
            rounds = [(auroc(y[b][mask[b]], s[b][mask[b]]), bacc(y[b][mask[b]], p[b][mask[b]])) for b in B]
            boot[exp, arm, sub] = (np.array([auroc(y[mask], s[mask]), bacc(y[mask], p[mask])]), np.array(rounds))

    def row(label_exp, arm, sub, point, rounds, **kw):
        (a_lo, a_hi), (b_lo, b_hi) = ci(rounds[:, 0]), ci(rounds[:, 1])
        return {"exp": label_exp, "arm": arm, "subset": sub, "auroc": point[0], "auroc_lo": a_lo, "auroc_hi": a_hi,
                "balanced_accuracy": point[1], "bacc_lo": b_lo, "bacc_hi": b_hi, **kw, **TRACE}

    fam = []
    exps = list(dict.fromkeys(P.exp))
    for exp in exps:
        for sub in subsets:
            for arm in ARMS:
                fam.append(row(exp, arm, sub, *boot[exp, arm, sub]))
            diff = lambda a, b: (boot[exp, a, sub][0] - boot[exp, b, sub][0], boot[exp, a, sub][1] - boot[exp, b, sub][1])
            fam.append(row(exp, "pixel - frequency", sub, *diff("pixel", "frequency")))
            best = max(("pixel", "frequency"), key=lambda a: val[exp, a])
            fam.append(row(exp, f"combined - best single ({best}, by val AUROC)", sub, *diff("combined", best)))
    fam = pd.DataFrame(fam)

    def paired(a, b, name, subs):
        return [row(name, arm, sub, boot[a, arm, sub][0] - boot[b, arm, sub][0],
                    boot[a, arm, sub][1] - boot[b, arm, sub][1]) for sub in subs for arm in ARMS]
    shift, jpeg = [], []
    if "E4" in exps:
        shift = fam[fam.exp.isin(["E4", "E5"])].to_dict("records")
        shift += paired("E4", "E1", "E4 - E1 (held out vs seen, C0)", subsets)
        shift += paired("E5", "E3_q75", "E5 - E3_q75 (held out vs seen, q75)", subsets)
        shift += paired("E5", "E4", "E5 - E4 (q75 vs C0, held out)", subsets)
    if "E2" in exps:
        fam = pd.concat([fam, pd.DataFrame(paired("E2", "E1", "E2 - E1 (control)", ["all"])
                                           + paired("E2", "E3_q75", "E2 - E3_q75 (control)", ["all"]))])
    for e in [x for x in exps if x.startswith("E3")]:
        jpeg += fam[fam.exp.isin([e])].to_dict("records") + paired(e, "E1", f"{e} - E1", subsets)
    return fam, pd.DataFrame(shift), pd.DataFrame(jpeg)


def per_feature(D):
    """E1/E3 feature-level statistics over all sampled parents (no fitting involved)."""
    rng = np.random.default_rng(CFG["seeds"]["bootstrap"])
    c0 = D[D.condition == "C0"].sort_values("image_id").set_index("image_id")
    B = rng.integers(0, len(c0), (CFG["bootstrap_rounds"], len(c0)))
    y = c0.y.values
    rows = []
    for q in [0] + CFG["jpeg_qualities"]:
        d = c0 if q == 0 else D[(D.condition == "C1") & (D.quality == q)].set_index("image_id").loc[c0.index]
        for f in NAMES:
            x = d[f].values
            def dval(xx, yy):
                r, g = xx[yy == 0], xx[yy == 1]
                sp = np.sqrt(((len(r) - 1) * r.var(ddof=1) + (len(g) - 1) * g.var(ddof=1)) / (len(r) + len(g) - 2))
                return (r.mean() - g.mean()) / sp
            dr = np.array([dval(x[b], y[b]) for b in B])
            ar = np.array([auroc(y[b], x[b]) for b in B])
            delta = (x - c0[f].values) / c0[f].std()
            dd = np.array([np.median(np.abs(delta[b])) for b in B])
            r_ = {"quality": q, "condition": "C0" if q == 0 else "C1", "feature": f,
                  "arm": "pixel" if f in PIXEL else "frequency",
                  "cohen_d_real_minus_fake": dval(x, y), "d_lo": ci(dr)[0], "d_hi": ci(dr)[1],
                  "pooled_sd": "sample-size-weighted pooled SD of both classes",
                  "univariate_auroc_fake_high": auroc(y, x), "uauc_lo": ci(ar)[0], "uauc_hi": ci(ar)[1],
                  "within_parent_median_shift_sd": np.median(delta),
                  "within_parent_median_abs_shift_sd": np.median(np.abs(delta)), "abs_shift_lo": ci(dd)[0],
                  "abs_shift_hi": ci(dd)[1], **TRACE}
            for lab, k in (("real", 0), ("fake", 1)):
                v = x[y == k]
                r_ |= {f"{lab}_mean": v.mean(), f"{lab}_median": np.median(v),
                       f"{lab}_iqr": np.subtract(*np.percentile(v, [75, 25]))}
            rows.append(r_)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT / "models").mkdir(exist_ok=True)
    D = load()
    print(f"{'Stage 7 pilot' if PILOT else 'Stage 8'}: {D.image_id.nunique()} parents, {len(D)} rows")
    P, models, controls = run_experiments(D)
    controls.to_csv(OUT / "control_checks.csv", index=False)
    print(controls.pivot(index="exp", columns="control", values="auroc").round(3).to_string())
    gate(controls)
    P.to_parquet(OUT / "per_image_predictions.parquet", index=False)
    (ROOT / "models" / f"models{'_pilot' if PILOT else ''}.json").write_text(json.dumps(models, indent=1))
    thr = pd.DataFrame(models).drop(columns=["coef", "scaler_mean", "scaler_scale"])
    thr.to_csv(ROOT / "models" / f"thresholds{'_pilot' if PILOT else ''}.csv", index=False)
    thr.to_csv(OUT / "thresholds.csv", index=False)                 # tracked copy (models/ is gitignored)
    print("Stage 9: statistics")
    fam, shift, jpeg = statistics(P, models)
    fam.to_csv(OUT / "family_comparison.csv", index=False)
    if len(shift):
        shift.to_csv(OUT / "generator_shift.csv", index=False)
    jpeg.to_csv(OUT / "jpeg_robustness.csv", index=False)
    if not PILOT:
        per_feature(D).to_csv(OUT / "per_feature_statistics.csv", index=False)
    print(fam[fam.subset == "all"][["exp", "arm", "auroc", "auroc_lo", "auroc_hi", "balanced_accuracy"]].round(3).to_string())
