"""Stage 6 — the 14 locked features (pipeline Section 5) and their synthetic-image checks.

`python src/features.py` runs the hand-calculation checks; the pipeline calls `extract(I)`.
"""
import numpy as np
from PIL import Image
from scipy import ndimage, stats

N = 256
NAMES = ["f01_var", "f02_skew", "f03_exkurt", "f04_grad_mean", "f05_grad_std", "f06_lap_var",
         "f07_hp_var", "f08_low", "f09_mid", "f10_high", "f11_nyq_ratio", "f12_slope",
         "f13_aniso", "f14_peak"]
PIXEL, FREQ = NAMES[:7], NAMES[7:]

_f = np.fft.fftfreq(N)
FX, FY = np.meshgrid(_f, _f)
R = np.hypot(FX, FY)
THETA = np.degrees(np.arctan2(FY, FX)) % 360
HANN = np.outer(np.hanning(N), np.hanning(N))
LOW, MID, HIGH = (R > 0) & (R <= 0.05), (R > 0.05) & (R <= 0.25), (R > 0.25) & (R <= 0.5)
TOP = (R > 0.375) & (R <= 0.5)
RBIN = np.rint(R * N).astype(int)
SLOPE_BINS = np.arange(N // 2 + 1)[(np.arange(N // 2 + 1) / N > 0.05)]    # r in (0.05, 0.5]
SECTOR = (THETA[MID] // 30).astype(int)
LAP = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], float)
BINOM = np.outer([1, 2, 1], [1, 2, 1]) / 16.0


def luminance(path) -> np.ndarray:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    return (rgb @ [0.299, 0.587, 0.114] / 255.0).astype(np.float32)


def extract(I: np.ndarray):
    """Return (14 features, slope R^2) for a 256x256 luminance image in [0, 1]."""
    I = I.astype(np.float64)
    v = I.ravel()
    g = np.hypot(ndimage.sobel(I, 1, mode="reflect"), ndimage.sobel(I, 0, mode="reflect"))
    pixel = [v.var(), np.nan_to_num(stats.skew(v)), np.nan_to_num(stats.kurtosis(v)),
             g.mean(), g.std(), ndimage.convolve(I, LAP, mode="reflect").var(),
             (I - ndimage.convolve(I, BINOM, mode="reflect")).var()]

    P = np.abs(np.fft.fft2((I - I.mean()) * HANN)) ** 2
    s = P[LOW | MID | HIGH].sum()
    radial = np.bincount(RBIN.ravel(), P.ravel()) / np.bincount(RBIN.ravel())
    x, y = np.log(SLOPE_BINS / N), np.log(radial[SLOPE_BINS] + 1e-30)
    slope, icpt = np.polyfit(x, y, 1)
    r2 = 1 - ((y - slope * x - icpt) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    sec = np.bincount(SECTOR, P[MID], 12) / np.bincount(SECTOR, minlength=12)
    is_max = (P == ndimage.maximum_filter(P, size=3, mode="wrap")) & (R > 0)
    freq = [P[LOW].sum() / s, P[MID].sum() / s, P[HIGH].sum() / s, P[TOP].sum() / P[HIGH].sum(),
            slope, sec.std() / sec.mean(), P[is_max].max() / (P.sum() - P[0, 0])]
    return np.array(pixel + freq), r2


def _selfcheck():
    x = np.arange(N)
    X, Y = np.meshgrid(x, x)
    near = lambda a, b, tol: abs(a - b) <= tol

    f, _ = extract(np.full((N, N), 0.5))                        # constant: no edges, no detail
    assert np.allclose(f[[0, 3, 4, 5, 6]], 0), "constant"

    imp = np.zeros((N, N)); imp[N // 2, N // 2] = 1             # impulse: Laplacian var = 20/N^2
    f, _ = extract(imp)
    assert near(f[5], 20 / N**2 - (0 / N**2) ** 2, 1e-12), "impulse laplacian"
    area = np.pi * np.array([0.05**2, 0.25**2 - 0.05**2, 0.5**2 - 0.25**2]) / (np.pi * 0.25)
    assert np.allclose(f[7:10], area, atol=0.02), f"impulse bands {f[7:10]} vs {area}"   # flat spectrum

    edge = (X >= N // 2).astype(float)                          # step edge: Sobel |g| = 4 on 2 columns
    f, _ = extract(edge)
    assert near(f[3], 8 / N, 1e-12), "edge gradient mean"

    chk = ((X + Y) % 2).astype(float)                           # checkerboard: one Nyquist-corner spike,
    f, _ = extract(chk)                                          # Hann spreads it over 3x3 -> 0.0625/0.1406
    assert near(f[13], 0.444, 0.01), f"checkerboard peak {f[13]}"

    f, _ = extract(0.5 + 0.5 * np.cos(2 * np.pi * 32 / N * X))   # 0.125 cyc/px sinusoid: all mid band
    assert f[8] > 0.99 and f[12] > 1.5 and near(f[13], 0.222, 0.01), f"mid sinusoid {f[8]} {f[12]} {f[13]}"
    f, _ = extract(0.5 + 0.5 * np.cos(2 * np.pi * 112 / N * X))  # 0.4375 cyc/px: high band, top band
    assert f[9] > 0.99 and f[10] > 0.99, f"high sinusoid {f[9]} {f[10]}"

    rng = np.random.default_rng(0)                              # 1/f amplitude noise: power slope -2
    amp = np.where(R > 0, 1 / np.maximum(R, 1e-9), 0)
    pink = np.real(np.fft.ifft2(amp * np.exp(2j * np.pi * rng.random((N, N)))))
    f, r2 = extract((pink - pink.min()) / np.ptp(pink))
    assert near(f[11], -2, 0.15) and r2 > 0.95, f"slope {f[11]} r2 {r2}"

    img = rng.random((N, N))
    assert np.array_equal(extract(img)[0], extract(img.copy())[0]), "repeat run"
    print("features self-check: all hand calculations match")


def run():
    """Extract features for every variant in data/variant_manifest.csv (C2 rows reuse C0/C1 files)."""
    import shutil
    import time

    import pandas as pd
    from common import CONFIG_HASH, DATA, ROOT, check

    out = ROOT / "features"
    out.mkdir(exist_ok=True)
    vm = pd.read_csv(DATA / "variant_manifest.csv")
    paths = vm.path.unique()
    t = time.time()
    res = {p: extract(luminance(ROOT / p)) for p in paths}
    secs = time.time() - t
    F = pd.DataFrame([np.r_[res[p][0], res[p][1]] for p in vm.path], columns=NAMES + ["slope_r2"])
    table = pd.concat([vm[["image_id", "condition", "quality", "path", "sha256"]].reset_index(drop=True), F], axis=1)

    check(np.isfinite(F.values).all(), "no NaN or Inf anywhere in the table")
    tmp = out / "_renamed_copy.png"
    shutil.copy(ROOT / paths[0], tmp)
    check(np.array_equal(extract(luminance(tmp))[0], res[paths[0]][0]), "renaming a file does not change its features")
    tmp.unlink()
    check(all(np.array_equal(extract(luminance(ROOT / p))[0], res[p][0]) for p in paths[:20]),
          "repeating a run produces identical values")

    table.to_parquet(out / "features.parquet", index=False)
    pd.DataFrame({"feature": NAMES, "arm": ["pixel"] * 7 + ["frequency"] * 7,
                  "definition": ["variance of I", "skewness of I", "excess kurtosis of I", "mean Sobel |grad|",
                                 "std Sobel |grad|", "variance of 4-neighbour Laplacian", "variance of I - binomial3x3(I)",
                                 "low-band power fraction (0,0.05]", "mid-band power fraction (0.05,0.25]",
                                 "high-band power fraction (0.25,0.5]", "power (0.375,0.5] / power (0.25,0.5]",
                                 "log-log radial power slope over (0.05,0.5]", "CV of mid-band power over 12 x 30deg sectors",
                                 "largest non-DC local max / non-DC power"]}).to_csv(out / "feature_dictionary.csv", index=False)
    (out / "extraction_report.md").write_text(
        f"# Extraction report\n\nconfig `{CONFIG_HASH}`; {len(paths)} unique files, {len(table)} variant rows; "
        f"{secs:.0f} s.\n\nChecks passed: synthetic hand calculations, no NaN/Inf, rename invariance, repeat identity.\n\n"
        f"Spectral slope fit R^2: median {F.slope_r2.median():.3f}, min {F.slope_r2.min():.3f}.\n\n"
        + table.groupby(["condition", "quality"]).size().rename("rows").to_frame().to_markdown() + "\n")
    print(f"  features.parquet: {len(table)} rows, {secs:.0f} s")


if __name__ == "__main__":
    _selfcheck()
    run()
