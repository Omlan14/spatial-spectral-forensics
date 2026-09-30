"""Explanatory figures for the final deck (2026-09-30). Reads data/, features/, results/ only.

  classes_at_native_scale   one test image per class drawn at its true native size + its resize factor
  feature_anatomy           what the 14 features look at: luminance, gradients, Laplacian, residual, spectrum bands
  jpeg_strip                one zoomed patch at C0 / q90 / q75 / q50 (condition C1)
  auroc_matrix              test AUROC matrix: E1 and E5, arms x (pooled, BigGAN, SD v1.4, ADM)
  radial_spectra            mean radial power spectrum per class, accepted resize (C0) vs matched resampling (R)

Usage: python src/deck_figures.py   (writes figures/deck/*.png and results/diagnostics/radial_spectra.csv)
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle, Rectangle
from PIL import Image
from scipy import ndimage

from common import DATA, ROOT
from features import BINOM, HANN, LAP, N, RBIN, luminance
from history_diagnostics import resample_matched
from prepare import raw_path

FIG = ROOT / "figures" / "deck"
FIG.mkdir(parents=True, exist_ok=True)
GEN = {"biggan": ("BigGAN", "#b2182b"), "sd_v1_4": ("SD v1.4", "#7b3fb5"), "adm": ("ADM", "#a87200")}
plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False})

sp = pd.read_csv(DATA / "splits.csv")
prov = pd.read_csv(DATA / "provenance.csv", dtype=str, keep_default_na=False).set_index("image_id")
man = pd.read_csv(DATA / "canonical_manifest.csv").set_index("image_id")


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=220, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)


def pick(gen, w=None, h=None):
    ids = sp[(sp.generator_family == gen) & (sp.split == "test")].image_id.sort_values()
    if w:
        ids = [i for i in ids if int(prov.loc[i].original_width) == w and int(prov.loc[i].original_height) == h]
    return list(ids)[0]


def raw(i):
    p = prov.loc[i]
    return Image.open(raw_path(p.source_dataset, i, p.original_format)).convert("RGB")


# ------------------------------------------------------------------ classes at native scale
cls = [("real", pick("real", 500, 375), "Real photo", "#222222"),
       ("biggan", pick("biggan"), "BigGAN", GEN["biggan"][1]),
       ("adm", pick("adm"), "ADM", GEN["adm"][1]),
       ("sd_v1_4", pick("sd_v1_4"), "SD v1.4", GEN["sd_v1_4"][1])]
fig, ax = plt.subplots(figsize=(11, 4.2))
x = 0
for g, i, lab, c in cls:
    im = raw(i)
    w, h = im.size
    ax.imshow(im, extent=(x, x + w, 0, h))
    ax.add_patch(Rectangle((x, 0), w, h, fill=False, ec=c, lw=2))
    f = man.loc[i].resize_factor
    verb = "enlarged" if f > 1 else ("unchanged" if f == 1 else "shrunk")
    ax.text(x + w / 2, h + 18, lab, ha="center", va="bottom", fontsize=13, fontweight="bold", color=c)
    ax.text(x + w / 2, -18, f"{prov.loc[i].original_format}  {w}×{h}\n{verb} {f:.2g}×",
            ha="center", va="top", fontsize=11, color="#333", linespacing=1.4)
    x += max(w, 190) + 60
ax.set_xlim(-10, x - 35)
ax.set_ylim(-110, 560)
ax.set_aspect("equal")
ax.axis("off")
save(fig, "classes_at_native_scale")

# ------------------------------------------------------------------ feature anatomy
i = cls[0][1]
I = luminance(ROOT / man.loc[i].path).astype(np.float64)
g = np.hypot(ndimage.sobel(I, 1, mode="reflect"), ndimage.sobel(I, 0, mode="reflect"))
lap = ndimage.convolve(I, LAP, mode="reflect")
res = I - ndimage.convolve(I, BINOM, mode="reflect")
P = np.fft.fftshift(np.abs(np.fft.fft2((I - I.mean()) * HANN)) ** 2)
fig, axs = plt.subplots(1, 5, figsize=(13, 3.3))
panels = [(I, "gray", "Luminance I", "f01–f03\nvariance, skew, kurtosis"),
          (g, "magma", "Sobel gradient |∇I|", "f04–f05\ngradient mean, std"),
          (np.abs(lap), "magma", "Laplacian", "f06\nLaplacian variance"),
          (np.abs(res), "magma", "High-pass residual", "f07\nresidual variance")]
for a, (img, cm, t, sub) in zip(axs, panels):
    v = img if cm == "gray" else np.clip(img / np.percentile(img, 99), 0, 1)
    a.imshow(v, cmap=cm)
    a.set_title(t, fontsize=11, color="#2a78d6", fontweight="bold")
    a.set_xlabel(sub, fontsize=9.5)
    a.set_xticks([]); a.set_yticks([])
a = axs[4]
a.imshow(np.log10(P + 1e-12), cmap="viridis", extent=(-0.5, 0.5, -0.5, 0.5))
for r, lab in ((0.05, "low"), (0.25, "mid"), (0.375, ""), (0.5, "high")):
    a.add_patch(Circle((0, 0), r, fill=False, ec="white", lw=1.1, ls="-" if r != 0.375 else "--"))
a.text(0.0, 0.14, "mid", color="white", ha="center", fontsize=8)
a.text(0.0, 0.3, "high", color="white", ha="center", fontsize=8)
a.text(0.0, 0.43, "top", color="white", ha="center", fontsize=8)
a.set_title("Power spectrum (Hann)", fontsize=11, color="#eb6834", fontweight="bold")
a.set_xlabel("f08–f14  band fractions, Nyquist\nratio, slope, anisotropy, peak", fontsize=9.5)
a.set_xticks([]); a.set_yticks([])
b0, b3, b4 = axs[0].get_position(), axs[3].get_position(), axs[4].get_position()
fig.text((b0.x0 + b3.x1) / 2, b0.y1 + 0.13, "Pixel arm: 7 features", ha="center", fontsize=13,
         color="#2a78d6", fontweight="bold")
fig.text((b4.x0 + b4.x1) / 2, b0.y1 + 0.13, "Frequency arm: 7 features", ha="center", fontsize=13,
         color="#eb6834", fontweight="bold")
save(fig, "feature_anatomy")

# ------------------------------------------------------------------ JPEG strip
fig, axs = plt.subplots(1, 4, figsize=(9, 2.6))
for a, (lab, path) in zip(axs, [("C0 (PNG)", man.loc[i].path)] +
                          [(f"JPEG q{q}", f"data/images/variants/{i}_q{q}.jpg") for q in (90, 75, 50)]):
    L = luminance(ROOT / path)
    a.imshow(L[112:144, 112:144], cmap="gray", interpolation="nearest", vmin=0, vmax=1)
    a.set_title(lab, fontsize=11)
    a.set_xticks([]); a.set_yticks([])
    a.axis("off")
fig.suptitle("Same 32×32 patch (zoomed 8×); both classes compressed identically (Pillow, 4:2:0)", fontsize=10,
             y=0.1, color="#444")
save(fig, "jpeg_strip")

# ------------------------------------------------------------------ AUROC matrix
fam = pd.read_csv(ROOT / "results" / "family_comparison.csv")
rows = [("E1", a) for a in ("pixel", "frequency", "combined")] + [("E5", a) for a in ("pixel", "frequency", "combined")]
cols = ["all", "biggan", "sd_v1_4", "adm"]
M = np.array([[fam[(fam.exp == e) & (fam.arm == a) & (fam.subset == c)].auroc.iloc[0] for c in cols] for e, a in rows])
assert abs(M[2, 0] - 0.793) < 5e-4 and abs(M[5, 2] - 0.629) < 5e-4, "matrix does not match reported values"
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.imshow(M, cmap="Blues", vmin=0.4, vmax=1.05, aspect="auto")
for r in range(M.shape[0]):
    for c in range(M.shape[1]):
        bold = (r, c) in ((2, 0), (5, 2))
        ax.text(c, r, f"{M[r, c]:.3f}", ha="center", va="center", fontsize=13 if bold else 12,
                fontweight="bold" if bold else "normal", color="white" if M[r, c] > 0.8 else "#1c2833")
ax.set_xticks(range(4), ["Pooled", "BigGAN", "SD v1.4", "ADM"], fontsize=11.5)
ax.set_yticks(range(6), [f"{e}  {a}" for e, a in rows], fontsize=11.5)
ax.xaxis.tick_top()
ax.axhline(2.5, color="white", lw=5)
ax.add_patch(Rectangle((1.5, 2.5), 1, 3, fill=False, ec="#b2182b", lw=2.2))
ax.text(2, 5.75, "unseen in E5", ha="center", va="top", fontsize=10, color="#b2182b")
for s in ax.spines.values():
    s.set_visible(False)
ax.tick_params(length=0)
save(fig, "auroc_matrix")

# ------------------------------------------------------------------ radial spectra, C0 vs R
cache = ROOT / "results" / "diagnostics" / "radial_spectra.csv"
if not cache.exists():
    nb = np.bincount(RBIN.ravel())
    out = []
    for r in sp.itertuples():
        p = prov.loc[r.image_id]
        for cond, L in (("C0", luminance(ROOT / man.loc[r.image_id].path)),
                        ("R", resample_matched(raw_path(p.source_dataset, r.image_id, p.original_format)))):
            if L is None:
                continue
            L = L.astype(np.float64)
            Pw = np.abs(np.fft.fft2((L - L.mean()) * HANN)) ** 2
            rad = np.bincount(RBIN.ravel(), Pw.ravel()) / nb
            out.append((cond, r.generator_family, np.log10(rad[1:N // 2 + 1] / Pw.sum())))
    arr = pd.DataFrame([(c, g, k, v) for c, g, s in out for k, v in enumerate(s, start=1)],
                       columns=["condition", "class", "radius_bin", "log10_rel_power"])
    arr.groupby(["condition", "class", "radius_bin"]).log10_rel_power.mean().reset_index().to_csv(cache, index=False)
S = pd.read_csv(cache)
fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
for a, cond, title in ((axs[0], "C0", "Accepted resize (C0)"), (axs[1], "R", "Same resampling for every image (R)")):
    a.axvspan(0.25, 0.5, color="#f2f2f2", zorder=0)
    a.text(0.375, 0.97, "high band", transform=a.get_xaxis_transform(), ha="center", va="top", fontsize=9.5, color="#666")
    for g, (lab, c) in [("real", ("Real", "#222222"))] + list(GEN.items()):
        d = S[(S.condition == cond) & (S["class"] == g)]
        f = d.radius_bin.values / N
        a.plot(f, d.log10_rel_power.values, color=c, lw=2 if g != "real" else 1.8, ls="--" if g == "real" else "-",
               label=lab)
    a.set_title(title, fontsize=11.5, loc="left")
    a.set_xlabel("spatial frequency (cycles / pixel)")
    a.set_xlim(0, 0.5)
    a.grid(color="#e6e6e6", lw=0.6)
axs[0].set_ylabel("mean log10 relative power")
axs[0].legend(loc="lower left", frameon=False, fontsize=10)
save(fig, "radial_spectra")
print("deck figures written to", FIG)
