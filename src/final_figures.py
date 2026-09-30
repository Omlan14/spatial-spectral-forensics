"""Figures for the final report and deck (2026-09-30). Reads only saved result tables.

  fig_resampling_swap   the key figure: same pooled AUROC, different per-generator story (C0 vs R)
  fig_effect_sizes      how far each manipulation moves AUROC (JPEG refit, JPEG fixed model,
                        generator held out, resampling matched)

Encoding is fixed across both figures: colour = feature arm, marker = generator.
Usage: python src/final_figures.py   (writes figures/final/*.pdf and *.png)
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from common import ROOT

RES, FIG = ROOT / "results", ROOT / "figures" / "final"
FIG.mkdir(parents=True, exist_ok=True)
ARMS = ["pixel", "frequency", "combined"]
COL = {"pixel": "#2a78d6", "frequency": "#eb6834", "combined": "#1baf7a"}
GENS = ["biggan", "sd_v1_4", "adm"]
GL = {"biggan": "BigGAN", "sd_v1_4": "SD v1.4", "adm": "ADM", "all": "Pooled"}
MK = {"biggan": "o", "sd_v1_4": "s", "adm": "^"}
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e6e6",
                     "grid.linewidth": 0.5, "axes.axisbelow": True, "legend.frameon": False,
                     "pdf.fonttype": 42})

D = pd.read_csv(RES / "diagnostics" / "history_diagnostics.csv")
d1 = D[D.diagnostic == "D1"]
uni = D[D.diagnostic == "D1 univariate"]
d2 = D[D.diagnostic == "D2"]
jpeg = pd.read_csv(RES / "jpeg_robustness.csv")
shift = pd.read_csv(RES / "generator_shift.csv")


def val(df, **kw):
    m = np.ones(len(df), bool)
    for k, v in kw.items():
        m &= df[k].values == v
    assert m.sum() == 1, (kw, m.sum())
    return df[m].iloc[0]


def check(label, got, want, tol=1.5e-3):
    assert abs(got - want) <= tol, f"{label}: {got:.4f} != {want:.4f}"


# self-checks against numbers quoted in the paper
check("E1 combined pooled C0", val(d1, exp="E1", comparison="combined", subset="all").auroc_C0, 0.796)
check("E1 frequency BigGAN R", val(d1, exp="E1", comparison="frequency", subset="biggan").auroc_R, 0.828)
check("E4 pixel SD R", val(d1, exp="E4", comparison="pixel", subset="sd_v1_4").auroc_R, 0.771)
check("f11 BigGAN C0", val(uni, comparison="f11_nyq_ratio", subset="biggan").auroc_C0, 0.006)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# ------------------------------------------------------------------ Figure: resampling swap
rows_spec = [("E1", "all", "Pooled (E1)"), ("E1", "biggan", "BigGAN (E1)"), ("E1", "sd_v1_4", "SD v1.4 (E1)"),
             ("E1", "adm", "ADM (E1)"), ("E4", "sd_v1_4", "SD v1.4 unseen (E4)")]
fig, (a, b) = plt.subplots(1, 2, figsize=(7.16, 2.7), gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.62})
off = {"pixel": 0.22, "frequency": 0, "combined": -0.22}
for i, (exp, sub, lab) in enumerate(rows_spec):
    yc = len(rows_spec) - 1 - i
    if i == 0:
        a.axhspan(yc - 0.45, yc + 0.45, color="#f2f4f6", zorder=0, lw=0)
    for arm in ARMS:
        r = val(d1, exp=exp, comparison=arm, subset=sub)
        y = yc + off[arm]
        a.annotate("", xy=(r.auroc_R, y), xytext=(r.auroc_C0, y),
                   arrowprops=dict(arrowstyle="-|>", color=COL[arm], lw=1.1, mutation_scale=7,
                                   shrinkA=2.5, shrinkB=2.5))
        a.plot(r.auroc_C0, y, "o", mfc="white", mec=COL[arm], mew=1.1, ms=4.2, zorder=3)
        a.plot(r.auroc_R, y, "o", color=COL[arm], ms=4.2, zorder=3)
a.axvline(0.5, color="#888", ls="--", lw=0.8)
a.set_yticks(range(len(rows_spec)))
a.set_yticklabels([r[2] for r in rows_spec][::-1])
a.set_xlim(0.42, 1.02)
a.set_xlabel("Test AUROC")
a.set_title("(a) Classifier AUROC per test subset", fontsize=8, loc="left")
hs = [Line2D([], [], color=COL[k], marker="o", lw=1.1, ms=4, label=k) for k in ARMS]
hs += [Line2D([], [], color="#333", marker="o", mfc="white", ls="", ms=4, label="C0 (accepted resize)"),
       Line2D([], [], color="#333", marker="o", ls="", ms=4, label="R (matched resampling)")]
fig.legend(handles=hs, ncol=5, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 0.97),
           handlelength=1.4, columnspacing=1.0)

feats = [("f06_lap_var", "f06 Laplacian var"), ("f07_hp_var", "f07 high-pass var"),
         ("f10_high", "f10 high-band"), ("f11_nyq_ratio", "f11 Nyquist ratio"), ("f12_slope", "f12 spectral slope")]
for j, (f, lab) in enumerate(feats):
    r = val(uni, comparison=f, subset="biggan")
    y = len(feats) - 1 - j
    b.annotate("", xy=(r.auroc_R, y), xytext=(r.auroc_C0, y),
               arrowprops=dict(arrowstyle="-|>", color=COL["frequency" if j >= 2 else "pixel"], lw=1.1,
                               mutation_scale=7, shrinkA=2.5, shrinkB=2.5))
    b.plot(r.auroc_C0, y, "o", mfc="white", mec="#333", mew=1.0, ms=4.2, zorder=3)
    b.plot(r.auroc_R, y, "o", color="#333", ms=4.2, zorder=3)
    b.text(r.auroc_R + 0.03, y, f"{r.auroc_R:.2f}", fontsize=6.5, va="center", color="#333")
    b.text(r.auroc_C0 + 0.01, y + 0.3, f"{r.auroc_C0:.3f}", fontsize=6.5, ha="left", color="#666")
b.axvline(0.5, color="#888", ls="--", lw=0.8)
b.set_yticks(range(len(feats)))
b.set_yticklabels([f[1] for f in feats][::-1])
b.set_xlim(-0.03, 1.0)
b.set_ylim(-0.6, len(feats) - 0.3)
b.set_xlabel("Univariate AUROC, BigGAN vs reals")
b.set_title("(b) BigGAN high-frequency features, C0 → R", fontsize=8, loc="left")
save(fig, "fig_resampling_swap")

# ------------------------------------------------------------------ Figure: effect sizes
man = ["Matched JPEG q50\n(refit, E3−E1)", "JPEG q50, fixed\nC0 model (transfer)",
       "SD v1.4 held out\n(E4−E1, C0)", "Resampling matched\n(R−C0, E1)"]
pts = {m: [] for m in man}
for arm in ARMS:
    for sub in GENS + ["all"]:
        pts[man[0]].append((arm, sub, val(jpeg, exp="E3_q50 - E1", arm=arm, subset=sub).auroc))
        t, c = (val(d2, exp=e, comparison=arm, subset=sub).auroc_transfer for e in ("E1 model on q50", "E1 model on C0"))
        pts[man[1]].append((arm, sub, t - c))
        pts[man[2]].append((arm, sub, val(shift, exp="E4 - E1 (held out vs seen, C0)", arm=arm, subset=sub).auroc))
        pts[man[3]].append((arm, sub, val(d1, exp="E1", comparison=arm, subset=sub).delta))
check("E4-E1 combined SD", [v for a_, s, v in pts[man[2]] if a_ == "combined" and s == "sd_v1_4"][0], -0.078)

fig, ax = plt.subplots(figsize=(3.45, 2.75))
aoff = {"pixel": 0.2, "frequency": 0.0, "combined": -0.2}
for i, m in enumerate(man):
    y0 = len(man) - 1 - i
    vals = [v for _, s, v in pts[m] if s != "all"]
    ax.plot([min(vals), max(vals)], [y0 - 0.34] * 2, color="#999", lw=0.8)
    ax.text(max(vals) + 0.012, y0 - 0.34, f"range {max(vals) - min(vals):.2f}", va="center", fontsize=6.3, color="#555")
    for arm, sub, v in pts[m]:
        y = y0 + aoff[arm]
        if sub == "all":
            ax.plot(v, y, marker="|", color="black", ms=8, mew=1.4, zorder=4)
        else:
            ax.plot(v, y, marker=MK[sub], color=COL[arm], ms=4, mec="white", mew=0.4, ls="", zorder=3)
ax.axvline(0, color="#888", lw=0.8)
ax.set_yticks(range(len(man)))
ax.set_yticklabels(man[::-1], fontsize=7)
ax.set_xlabel("Change in test AUROC (per generator; | = pooled)")
ax.set_xlim(-0.24, 0.40)
h_arm = [Line2D([], [], color=COL[k], marker="o", ls="", ms=4, label=k) for k in ARMS]
h_gen = [Line2D([], [], color="#555", marker=MK[g], ls="", ms=4, label=GL[g]) for g in GENS]
h_gen.append(Line2D([], [], color="black", marker="|", ls="", ms=7, mew=1.4, label="pooled"))
ax.legend(handles=h_arm + h_gen, ncol=4, fontsize=6.3, loc="lower center", bbox_to_anchor=(0.42, 1.0),
          handletextpad=0.2, columnspacing=0.7)
save(fig, "fig_effect_sizes")
print("figures written to", FIG)
