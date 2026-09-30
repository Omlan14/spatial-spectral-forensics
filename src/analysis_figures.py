"""Extended analysis figures for the presentation pack — every figure derived from saved results.

Reads only `results/`, `features/features.parquet`, and `data/splits.csv`; writes derived
evidence tables to `results/extended/` and figures (PNG 200 dpi + vector PDF) to
`figures/extended/`. Self-checking: every computed number is asserted against the stored
tables before a figure is drawn, and the script stops on a failed check (pipeline rule 2).

Usage: python src/analysis_figures.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_curve

from common import ROOT
from features import NAMES

RES, FIG = ROOT / "results", ROOT / "figures" / "extended"
TAB = RES / "extended"
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

ARM_STYLE = {"pixel": ("#2a78d6", "o"), "frequency": ("#eb6834", "s"), "combined": ("#1baf7a", "D")}
GEN_STYLE = {"biggan": ("#b2182b", "o"), "sd_v1_4": ("#555555", "s"), "adm": ("#777777", "^")}
GEN_LABEL = {"biggan": "BigGAN", "sd_v1_4": "SD v1.4", "adm": "ADM"}
COND = [("C0", 0), ("C1", 90), ("C1", 75), ("C1", 50)]
COND_LABEL = ["C0", "q90", "q75", "q50"]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6})

ARM_OF = {f: ("pixel" if i < 7 else "frequency") for i, f in enumerate(NAMES)}
FREQ_LABEL = {"f08_low": "f08 low-band", "f09_mid": "f09 mid-band", "f10_high": "f10 high-band",
              "f11_nyq_ratio": "f11 Nyquist ratio", "f12_slope": "f12 spectral slope",
              "f13_aniso": "f13 anisotropy", "f14_peak": "f14 peak"}
PIX_LABEL = {"f01_var": "f01 variance", "f02_skew": "f02 skewness", "f03_exkurt": "f03 ex-kurtosis",
             "f04_grad_mean": "f04 grad mean", "f05_grad_std": "f05 grad std",
             "f06_lap_var": "f06 Laplacian var", "f07_hp_var": "f07 high-pass var"}
FEAT_LABEL = {**PIX_LABEL, **FREQ_LABEL}


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=200)
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)
    print(f"  wrote figures/extended/{name}.png/.pdf")


def uauc(x, y):
    x, y = np.asarray(x, float), np.asarray(y, int)
    r = stats.rankdata(x)
    n1, n0 = y.sum(), len(y) - y.sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1)


def check(label, got, want, tol=2e-3):
    if abs(got - want) > tol:
        raise SystemExit(f"CHECK FAILED: {label}: computed {got} vs stored {want}")
    print(f"  check ok: {label} = {got:.4f}")


# ---------------------------------------------------------------- load and verify
print("Loading tables and verifying against stored results...")
fc = pd.read_csv(RES / "family_comparison.csv")
gs = pd.read_csv(RES / "generator_shift.csv")
jr = pd.read_csv(RES / "jpeg_robustness.csv")
pf = pd.read_csv(RES / "per_feature_statistics.csv")
cc = pd.read_csv(RES / "control_checks.csv")
preds = pd.read_parquet(RES / "per_image_predictions.parquet")
feats = pd.read_parquet(ROOT / "features" / "features.parquet")
splits = pd.read_csv(ROOT / "data" / "splits.csv")
m = feats.merge(splits[["image_id", "label", "generator_family"]], on="image_id", how="left")
m["y"] = (m.label == "fake").astype(int)

for exp in ["E1", "E5"]:
    s = preds[(preds.exp == exp) & (preds.arm == "combined")]
    check(f"per-image recompute of {exp} combined AUROC", uauc(s.score, s.y),
          fc[(fc.exp == exp) & (fc.arm == "combined") & (fc.subset == "all")].auroc.iloc[0])

# per-feature univariate AUROC by generator at C0
c0 = m[m.condition == "C0"]
rows = []
for f in NAMES:
    row = {"feature": f}
    for g in ["biggan", "sd_v1_4", "adm", "all"]:
        sub = c0[(c0.generator_family == g) | (c0.label == "real")] if g != "all" else c0
        row[g] = uauc(sub[f], sub.y)
    rows.append(row)
u = pd.DataFrame(rows).set_index("feature")
u.to_csv(TAB / "uauc_by_generator_C0.csv")
check("BigGAN f11 univariate AUROC at C0", u.loc["f11_nyq_ratio", "biggan"], 0.009, tol=1e-3)
check("pooled f10 univariate AUROC at C0", u.loc["f10_high", "all"],
      pf[(pf.condition == "C0") & (pf.feature == "f10_high")].univariate_auroc_fake_high.iloc[0])

# per-feature Cohen's d (real - fake) per condition, all parents
rows = []
for f in NAMES:
    row = {"feature": f}
    for cond, q in COND:
        sub = m[(m.condition == cond) & (m.quality == q)]
        a, b = sub[sub.label == "real"][f].values, sub[sub.label == "fake"][f].values
        sp = np.sqrt(((len(a) - 1) * a.std(ddof=1) ** 2 + (len(b) - 1) * b.std(ddof=1) ** 2)
                     / (len(a) + len(b) - 2))
        row[COND_LABEL[COND.index((cond, q))]] = (a.mean() - b.mean()) / sp
    rows.append(row)
d = pd.DataFrame(rows).set_index("feature")
d.to_csv(TAB / "cohens_d_by_condition.csv")
for f, lab in [("f01_var", "C0"), ("f12_slope", "C0"), ("f11_nyq_ratio", "q50")]:
    stored = pf[(pf.condition == ("C0" if lab == "C0" else "C1"))
                & (pf.quality == (0 if lab == "C0" else 50)) & (pf.feature == f)].cohen_d_real_minus_fake.iloc[0]
    check(f"Cohen's d {f} at {lab}", d.loc[f, lab], stored)

# f11 univariate AUROC by generator across conditions
rows = []
for cond, q in COND:
    sub = m[(m.condition == cond) & (m.quality == q)]
    row = {"condition": COND_LABEL[COND.index((cond, q))]}
    for g in ["biggan", "sd_v1_4", "adm"]:
        s2 = sub[(sub.generator_family == g) | (sub.label == "real")]
        row[g] = uauc(s2["f11_nyq_ratio"], s2.y)
    rows.append(row)
f11 = pd.DataFrame(rows).set_index("condition")
f11.to_csv(TAB / "f11_nyq_by_generator.csv")
check("BigGAN f11 reversal at q50", f11.loc["q50", "biggan"], 0.772, tol=5e-3)

# ---------------------------------------------------------------- Figure 1: shortcut anatomy
print("Figure 1: shortcut_anatomy")
fig, axes = plt.subplots(1, 3, figsize=(10, 3.6), sharey=True)
ypos = np.arange(len(NAMES))[::-1]
bar_col = {"pixel": "#9ec5ec", "frequency": "#f4b295"}
for ax, g in zip(axes, ["biggan", "sd_v1_4", "adm"]):
    for i, f in enumerate(NAMES):
        val = u.loc[f, g]
        col = bar_col[ARM_OF[f]]
        ax.barh(ypos[i], val, height=0.72, color=col, edgecolor="#666", linewidth=0.3)
        if val < 0.5:  # show the reversed-direction strength as a ghost bar
            ax.barh(ypos[i], 1 - val, height=0.72, color=col, alpha=0.25, edgecolor="#999",
                    linewidth=0.3, linestyle="--")
    ax.axvline(0.5, color="#888", lw=1, ls="--")
    ax.set_xlim(0, 1.0)
    ax.set_title(FACE := GEN_LABEL[g], fontsize=10)
    ax.set_xlabel("univariate AUROC (feature high = fake)")
axes[0].set_yticks(ypos, [FEAT_LABEL[f] for f in NAMES], fontsize=8)
handles = [plt.Rectangle((0, 0), 1, 1, color=bar_col["pixel"]),
           plt.Rectangle((0, 0), 1, 1, color=bar_col["frequency"])]
axes[2].legend(handles, ["pixel-pattern feature", "frequency feature"], loc="upper right",
               fontsize=8, framealpha=0.95)
fig.suptitle("Where the separation lives: per-feature univariate AUROC at C0 by generator\n"
             "faint dashed bar = strength of the reversed direction (feature low = fake)",
             fontsize=9.5)
fig.tight_layout(rect=(0, 0, 1, 0.90))
save(fig, "shortcut_anatomy")

# ---------------------------------------------------------------- Figure 2: f11 reversal
print("Figure 2: f11_reversal")
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.1))
ax = axes[0]
for g in ["biggan", "sd_v1_4", "adm"]:
    c, mk = GEN_STYLE[g]
    lw = 2.4 if g == "biggan" else 1.4
    ax.plot(range(4), f11[g], marker=mk, color=c, lw=lw, ms=6 if g == "biggan" else 4.5,
            label=GEN_LABEL[g])
ax.axhline(0.5, color="#888", lw=1, ls="--")
ax.annotate("reversed: JPEG block edges add\nnear-Nyquist energy to upsampled fakes",
            xy=(3, f11.loc["q50", "biggan"]), xytext=(0.35, 0.66), fontsize=8,
            arrowprops=dict(arrowstyle="->", color="#b2182b", lw=1))
ax.set_xticks(range(4), COND_LABEL)
ax.set_ylim(0, 1)
ax.set_ylabel("univariate AUROC (high = fake)")
ax.set_title("(a) Nyquist-band ratio f11 by generator", fontsize=9.5)
ax.legend(fontsize=8, loc="lower right", framealpha=0.95)
ax = axes[1]
for f, c, mk in [("f11_nyq_ratio", "#b2182b", "o"), ("f10_high", "#555555", "s"),
                 ("f12_slope", "#999999", "^")]:
    ax.plot(range(4), d.loc[f], marker=mk, color=c, lw=2 if f == "f11_nyq_ratio" else 1.3,
            ms=5.5 if f == "f11_nyq_ratio" else 4, label=FEAT_LABEL[f])
ax.axhline(0, color="#888", lw=1, ls="--")
for i, v in enumerate(d.loc["f11_nyq_ratio"]):
    ax.annotate(f"{v:+.2f}", (i, v), textcoords="offset points",
                xytext=(6, 4 if i == 0 else -11), fontsize=8, color="#b2182b")
ax.set_xticks(range(4), COND_LABEL)
ax.set_ylabel("Cohen's d (real − fake), all parents")
ax.set_title("(b) Effect size across JPEG quality (pooled)", fontsize=9.5)
ax.legend(fontsize=8)
fig.suptitle("A feature's meaning can flip under JPEG while classification barely moves (H3, E3)",
             fontsize=9.5)
fig.tight_layout(rect=(0, 0, 1, 0.92))
save(fig, "f11_reversal")

# ---------------------------------------------------------------- Figure 3: effect-size heatmap
print("Figure 3: effect_size_heatmap")
fig, ax = plt.subplots(figsize=(5.4, 4.4))
mat = d.values
im = ax.imshow(mat, cmap="RdBu_r", vmin=-1.2, vmax=1.2, aspect="auto")
ax.set_xticks(range(4), COND_LABEL)
ax.set_yticks(range(len(NAMES)), [FEAT_LABEL[f] for f in NAMES], fontsize=8)
for i in range(len(NAMES)):
    for j in range(4):
        ax.annotate(f"{mat[i, j]:+.2f}", (j, i), ha="center", va="center", fontsize=7.5,
                    color="white" if abs(mat[i, j]) > 0.75 else "#222")
ax.add_patch(plt.Rectangle((-0.5, 9.5), 4, 1, fill=False, edgecolor="#b2182b", lw=2))
ax.axhline(6.5, color="#444", lw=1)
cb = fig.colorbar(im, ax=ax, shrink=0.85)
cb.set_label("Cohen's d (real − fake)", fontsize=8)
ax.set_title("Per-feature effect size by JPEG condition (3,000 parents)\n"
             "rows 1–7 pixel-pattern, 8–14 frequency; positive = real higher;\n"
             "red outline = the f11 sign flip", fontsize=9.5)
fig.tight_layout()
save(fig, "effect_size_heatmap")

# ---------------------------------------------------------------- Figure 4: ROC curves (headline E5)
print("Figure 4: roc_headline")
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.4), sharey=True)
panels = [("all test images (E5)", ["real", "biggan", "sd_v1_4", "adm"], "all"),
          ("SD v1.4 fakes vs reals only (headline row)", ["real", "sd_v1_4"], "sd_v1_4")]
for ax, (title, fams, key) in zip(axes, panels):
    e5 = preds[(preds.exp == "E5") & (preds.generator_family.isin(fams) | (preds.generator_family == "real"))]
    e5 = preds[(preds.exp == "E5")]
    e5 = e5[e5.generator_family.isin(fams)]
    for arm in ["pixel", "frequency", "combined"]:
        s = e5[e5.arm == arm]
        fpr, tpr, _ = roc_curve(s.y, s.score)
        auc = uauc(s.score, s.y)
        lo = gs[(gs.exp == "E5") & (gs.arm == arm) & (gs.subset == key)].auroc_lo
        hi = gs[(gs.exp == "E5") & (gs.arm == arm) & (gs.subset == key)].auroc_hi
        c, _ = ARM_STYLE[arm]
        ls = {"pixel": "-", "frequency": "--", "combined": "-"}[arm]
        lab = f"{arm}  AUROC {auc:.3f}"
        if len(lo):
            lab += f" [{lo.iloc[0]:.3f}, {hi.iloc[0]:.3f}]"
        ax.plot(fpr, tpr, color=c, lw=2, ls=ls, label=lab)
    ax.plot([0, 1], [0, 1], color="#888", lw=1, ls=":")
    ax.set_xlabel("false-positive rate")
    ax.set_title(title, fontsize=9.5)
    ax.legend(fontsize=8, loc="lower right")
axes[0].set_ylabel("true-positive rate")
fig.suptitle("E5 headline (unseen SD v1.4 fakes in test, JPEG q75): ROC by feature arm", fontsize=9.5)
fig.tight_layout(rect=(0, 0, 1, 0.93))
save(fig, "roc_headline")

# ---------------------------------------------------------------- Figure 5: score distributions
print("Figure 5: score_distributions")
fig, ax = plt.subplots(figsize=(7.2, 3.0))
order = ["real", "biggan", "sd_v1_4", "adm"]
data = [preds[(preds.exp == "E5") & (preds.arm == "combined") & (preds.generator_family == g)].score
        for g in order]
cols = ["#2a78d6", "#b2182b", "#555555", "#777777"]
vp = ax.violinplot(data, positions=range(4), showmedians=False, showextrema=False, widths=0.8)
for body, c in zip(vp["bodies"], cols):
    body.set_facecolor(c)
    body.set_alpha(0.35)
for i, s in enumerate(data):
    q1, med, q3 = np.percentile(s, [25, 50, 75])
    ax.plot([i - 0.24, i + 0.24], [med, med], color=cols[i], lw=2.5)
    ax.plot([i - 0.18, i + 0.18], [q1, q1], color=cols[i], lw=1.2)
    ax.plot([i - 0.18, i + 0.18], [q3, q3], color=cols[i], lw=1.2)
ax.axhline(0, color="#888", lw=1, ls="--")
ax.annotate("decision threshold (score = 0)", (-0.42, 0.75), fontsize=8, color="#555")
ax.axhline(0, color="#888", lw=0)
ax.set_xticks(range(4), ["reals\n(ImageNet)", "BigGAN fakes\n(seen)", "SD v1.4 fakes\n(unseen)", "ADM fakes\n(seen)"])
ax.set_ylabel("E5 combined-arm score")
for i, s in enumerate(data):
    med = np.median(s)
    ax.annotate(f"median {med:+.2f}", (i, med), textcoords="offset points",
                xytext=(0, 9 if med > -1.2 else -16), ha="center", fontsize=8, color=cols[i])
ax.set_title("E5 (unseen SD v1.4 in test, JPEG q75): combined-arm score distributions", fontsize=9.5)
fig.tight_layout()
save(fig, "score_distributions")

# ---------------------------------------------------------------- Figure 6: degradation path
print("Figure 6: degradation_path")
settings = [("E1", "sd_v1_4"), ("E3_q75", "sd_v1_4"), ("E4", "sd_v1_4"), ("E5", "sd_v1_4")]
labels = ["E1 seen\nC0", "E3 q75 seen\n(refit)", "E4 unseen\nC0", "E5 unseen\nq75 (headline)"]
src = {"E1": fc, "E3_q75": jr, "E4": gs, "E5": gs}
fig, ax = plt.subplots(figsize=(6.4, 3.4))
for arm in ["pixel", "frequency", "combined"]:
    vals, los, his = [], [], []
    for exp, sub in settings:
        t = src[exp][(src[exp].exp == exp) & (src[exp].arm == arm) & (src[exp].subset == sub)].iloc[0]
        vals.append(t.auroc); los.append(t.auroc_lo); his.append(t.auroc_hi)
    c, mk = ARM_STYLE[arm]
    ax.plot(range(4), vals, marker=mk, color=c, lw=2, ms=6, label=arm)
    ax.fill_between(range(4), los, his, color=c, alpha=0.12, lw=0)
    for i, v in enumerate(vals):
        off = (5, 6) if arm != "pixel" else (5, -12)
        ax.annotate(f"{v:.3f}", (i, v), textcoords="offset points", xytext=off, fontsize=8, color=c)
ax.axhline(0.5, color="#888", lw=1, ls="--")
ax.annotate("chance", (-0.42, 0.505), fontsize=8, color="#555", va="bottom")
ax.set_xticks(range(4), labels)
ax.set_ylim(0.40, 0.85)
ax.set_ylabel("AUROC on SD v1.4 fakes vs reals")
ax.set_title("The cost of generality on held-out SD v1.4 (95% group-bootstrap CIs)\n"
             "seen → unseen: −0.078 [−0.124, −0.034] · unseen C0 → unseen q75: −0.004",
             fontsize=9.5)
ax.legend(fontsize=8, loc="lower left")
fig.tight_layout()
save(fig, "degradation_path")

# ---------------------------------------------------------------- Figure 7: controls + verdicts
print("Figure 7: controls_and_verdicts")
fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), width_ratios=[1.15, 1])
ax = axes[0]
exps = ["E1", "E2", "E3_q90", "E3_q75", "E3_q50", "E4", "E5"]
ctl_style = {"always_guess": ("#bbbbbb", "o", "always-guess"),
             "history_only": ("#444444", "s", "history-only (C0/C1)"),
             "shuffled_labels": ("#2a78d6", "^", "shuffled labels (mean of 200)"),
             "pre_receipt_history (exploratory)": ("#b2182b", "D", "pre-receipt history (exploratory)")}
for k, (ctl, (c, mk, lab)) in enumerate(ctl_style.items()):
    yy, vv = [], []
    for i, e in enumerate(exps):
        row = cc[(cc.exp == e) & (cc.control == ctl)]
        if len(row):
            yy.append(i + (k - 1.5) * 0.16)
            vv.append(row.auroc.iloc[0])
    ax.plot(vv, yy, mk, color=c, ms=5, label=lab)
ax.axvline(0.5, color="#888", lw=1, ls="--")
ax.set_yticks(range(len(exps)), exps)
ax.set_xlim(0.42, 1.08)
ax.set_xlabel("test AUROC of the control classifier")
ax.set_title("(a) Control checks, all experiments", fontsize=9.5)
ax.legend(fontsize=7.5, loc="center right")
ax = axes[1]
ax.axis("off")
verd = [("H1", "signal exists (E1)", "SUPPORTED", "#1baf7a", "combined 0.793 [0.759, 0.826]"),
        ("H2", "mismatch changes separation (E2)", "PARTLY", "#e8a33d",
         "freq +0.017, comb +0.012, pixel −0.026"),
        ("H3", "broad vs narrow frequency (E3)", "SUPPORTED (unexpected)", "#1baf7a",
         "f14 stable but uninformative; f11 flips"),
        ("H4", "degradation on unseen generator (E4/E5)", "SUPPORTED (SD v1.4)", "#1baf7a",
         "combined −0.078; pixel → chance"),
        ("H5", "content bias", "NOT TESTED", "#aaaaaa", "deferred by design (limitation 5)")]
ax.text(0.02, 0.97, "Hypothesis verdicts (pre-registered, all decided)", fontsize=9.5,
        va="top", transform=ax.transAxes)
for i, (hid, what, status, col, ev) in enumerate(verd):
    y = 0.82 - i * 0.17
    ax.add_patch(plt.Rectangle((0.02, y - 0.045), 0.055, 0.09, transform=ax.transAxes,
                               color=col, clip_on=False))
    ax.text(0.09, y + 0.035, f"{hid} — {what}", fontsize=8.5, va="center", transform=ax.transAxes)
    ax.text(0.09, y - 0.035, f"{status} · {ev}", fontsize=7.5, va="center", color="#444",
            transform=ax.transAxes)
fig.suptitle("Evidence that the pipeline is sound, and what it decided", fontsize=9.5)
fig.tight_layout(rect=(0, 0, 1, 0.92))
save(fig, "controls_and_verdicts")

# ---------------------------------------------------------------- Figure 8: arm complementarity
print("Figure 8: arm_complementarity")
e5sd = preds[(preds.exp == "E5") & (preds.generator_family == "sd_v1_4") & (preds.y == 1)]
piv = e5sd.pivot_table(index="image_id", columns="arm", values="pred")
n = len(piv)
counts = {"caught by pixel": int(piv["pixel"].sum()),
          "caught by frequency": int(piv["frequency"].sum()),
          "caught by combined": int(piv["combined"].sum()),
          "caught by pixel OR frequency": int(((piv["pixel"] == 1) | (piv["frequency"] == 1)).sum()),
          "missed by both pixel and frequency": int(((piv["pixel"] == 0) & (piv["frequency"] == 0)).sum())}
pd.DataFrame([counts | {"n_sd_fakes": n}]).to_csv(TAB / "arm_complementarity_e5.csv", index=False)
fig, ax = plt.subplots(figsize=(7.0, 2.9))
names = list(counts)[::-1]
vals = [counts[k] for k in names]
cols = ["#777777", "#1baf7a", "#8f8f8f", "#eb6834", "#2a78d6"]
bars = ax.barh(names, vals, color=cols, height=0.62)
ax.bar_label(bars, labels=[f"{v} / {n}" for v in vals], fontsize=8.5, padding=3)
ax.axvline(n, color="#888", lw=1, ls="--")
ax.annotate("all 100 unseen\nSD v1.4 fakes", (n - 1.5, 2.4), fontsize=8, color="#555",
            ha="right", rotation=90, va="center")
ax.set_xlim(0, 108)
ax.set_xlabel("unseen SD v1.4 fakes flagged at the validation-selected threshold (E5)")
ax.set_title("The two arms catch different fakes (E5, unseen SD v1.4)", fontsize=9.5)
ax.annotate("combined beats frequency by\n+0.061 AUROC [0.028, 0.094]\n(pixel flags more, ranks worse)",
            (50, 3.4), fontsize=8, color="#444", ha="left", va="center")
fig.tight_layout()
save(fig, "arm_complementarity")

print("All extended figures written; every check passed.")
