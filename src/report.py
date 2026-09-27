"""Stage 10 — regenerate every figure from the saved result tables (never edited by hand).

Usage: python src/report.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import CFG, ROOT
from features import NAMES

RES, FIG = ROOT / "results", ROOT / "figures"
ARM_STYLE = {"pixel": ("#2a78d6", "o"), "frequency": ("#eb6834", "s"), "combined": ("#1baf7a", "D")}
CLASS_COL = {"real": "#2a78d6", "fake": "#eb6834"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6})


def dots(ax, df, labels):
    """AUROC point + 95% CI per arm, one row per label; arms offset vertically."""
    for k, (arm, (c, m)) in enumerate(ARM_STYLE.items()):
        d = df[df.arm == arm].set_index("exp").loc[labels]
        yy = np.arange(len(labels)) + (k - 1) * 0.22
        ax.errorbar(d.auroc, yy, xerr=[d.auroc - d.auroc_lo, d.auroc_hi - d.auroc], fmt=m, color=c,
                    ms=6, lw=1.5, capsize=0, label=arm)
    ax.set_yticks(range(len(labels)), labels)
    ax.axvline(0.5, color="#888", lw=1, ls="--")
    ax.invert_yaxis()


def family_comparison(fam):
    labels = ["E1", "E3_q90", "E3_q75", "E3_q50", "E4", "E5", "E2"]
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    dots(ax, fam[fam.subset == "all"], labels)
    ax.set_yticklabels(["E1 clean (C0)", "E3 JPEG q90", "E3 JPEG q75", "E3 JPEG q50",
                        "E4 unseen gen., C0", "E5 unseen gen., q75", "E2 mismatch (control)"])
    ax.set_xlabel("Test AUROC (95% group-bootstrap CI); dashed = chance")
    ax.legend(title="feature set", frameon=False, loc="lower left", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "family_comparison.png", dpi=200); plt.close(fig)


def generator_shift(fam):
    gens = CFG["generators"]
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.8), sharex=True, sharey=True)
    labels = ["E1", "E4", "E3_q75", "E5"]
    for ax, g in zip(axes, gens):
        dots(ax, fam[fam.subset == g], labels)
        ax.set_title(f"fakes: {g}" + (" (held out in E4/E5)" if g == CFG["unseen_generator"] else ""), fontsize=9)
        ax.set_yticklabels(["C0, all seen", "C0, SD held out", "q75, all seen", "q75, SD held out"])
        ax.set_xlabel("Test AUROC")
    axes[0].legend(frameon=False, fontsize=7, loc="lower left")
    fig.tight_layout(); fig.savefig(FIG / "generator_shift.png", dpi=200); plt.close(fig)


def robustness_curves(fam):
    subs = ["all"] + CFG["generators"]
    exps, xt = ["E1", "E3_q90", "E3_q75", "E3_q50"], ["PNG", "q90", "q75", "q50"]
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.8), sharey=True)
    for ax, s in zip(axes, subs):
        for arm, (c, m) in ARM_STYLE.items():
            d = fam[(fam.subset == s) & (fam.arm == arm)].set_index("exp").loc[exps]
            ax.fill_between(range(4), d.auroc_lo, d.auroc_hi, color=c, alpha=0.12, lw=0)
            ax.plot(range(4), d.auroc, marker=m, color=c, lw=2, ms=6, label=arm)
        ax.set_xticks(range(4), xt); ax.set_title("all generators" if s == "all" else f"fakes: {s}", fontsize=9)
        ax.axhline(0.5, color="#888", lw=1, ls="--")
    axes[0].set_ylabel("Test AUROC (E1, E3)"); axes[0].legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "robustness_curves.png", dpi=200); plt.close(fig)


def feature_distributions():
    F = pd.read_parquet(ROOT / "features" / "features.parquet").merge(
        pd.read_csv(ROOT / "data" / "splits.csv")[["image_id", "label"]], on="image_id")
    F = F[F.condition == "C0"]
    fig, axes = plt.subplots(2, 7, figsize=(14, 4))
    for ax, f in zip(axes.ravel(), NAMES):
        lo, hi = np.percentile(F[f], [1, 99])
        for lab, c in CLASS_COL.items():
            ax.hist(F.loc[F.label == lab, f].clip(lo, hi), bins=40, range=(lo, hi), color=c, alpha=0.55,
                    label=lab, histtype="stepfilled")
        ax.set_title(f, fontsize=8); ax.tick_params(labelsize=6); ax.set_yticks([])
    axes[0, 0].legend(frameon=False, fontsize=7)
    fig.suptitle("C0 feature distributions (all 3,000 parents; 1st-99th percentile shown)", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "feature_distributions.png", dpi=200); plt.close(fig)


def stability_vs_separation(pf):
    broad, narrow = ["f08_low", "f09_mid", "f10_high", "f11_nyq_ratio", "f13_aniso"], ["f14_peak"]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3), sharex=True, sharey=True)
    for ax, q in zip(axes, CFG["jpeg_qualities"]):
        d = pf[pf.quality == q].set_index("feature")
        sep = (d.univariate_auroc_fake_high - 0.5).abs()
        for grp, c, m, lab in [(broad, "#2a78d6", "o", "broad (8-11, 13)"), (narrow, "#eb6834", "s", "narrow (14)"),
                               ([f for f in NAMES if f not in broad + narrow], "#9a9a94", "^", "other")]:
            ax.scatter(d.loc[grp, "within_parent_median_abs_shift_sd"], sep[grp], color=c, marker=m, s=30, label=lab)
            for f in grp:
                ax.annotate(f[:3], (d.loc[f, "within_parent_median_abs_shift_sd"], sep[f]), fontsize=6,
                            xytext=(3, 2), textcoords="offset points", color="#444")
        ax.set_title(f"JPEG q{q} vs C0", fontsize=9); ax.set_xscale("symlog", linthresh=0.01)
        ax.set_xlabel("stability: median |C1 - C0| (C0 SD units)")
    axes[0].set_ylabel("separation: |univariate AUROC - 0.5|"); axes[0].legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "stability_vs_separation.png", dpi=200); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fam = pd.read_csv(RES / "family_comparison.csv")
    family_comparison(fam)
    generator_shift(fam)
    robustness_curves(fam)
    feature_distributions()
    stability_vs_separation(pd.read_csv(RES / "per_feature_statistics.csv"))
    print("figures written to", FIG)
