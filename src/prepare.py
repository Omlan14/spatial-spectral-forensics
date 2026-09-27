"""Stages 2-5 — check data, split by group, standard pre-processing, conditions C0/C1/C2.

Usage: python src/prepare.py   (reads data/provenance.csv, writes the locked data/ tables)
"""
import io

import numpy as np
import pandas as pd
import PIL
from PIL import Image, ImageCms, ImageOps
from scipy.fft import dctn

from common import CFG, DATA, ROOT, RAW, check, sha256

IMG = DATA / "images"
S = CFG["image_size"]


def raw_path(source_dataset, image_id, fmt):
    gen = {v: k for k, v in CFG["mirror_dirs"].items()}[source_dataset.split("/")[1]]
    return RAW / gen / f"{image_id}.{fmt.lower()}"


def phash(im):
    a = np.asarray(im.convert("L").resize((32, 32), Image.BICUBIC), float)
    d = dctn(a, norm="ortho")[:8, :8].ravel()
    return int("".join("1" if x > np.median(d) else "0" for x in d), 2)


def exclusion_reason(im):
    if im.mode not in ("RGB", "L") or "transparency" in im.info:
        return f"mode_{im.mode}_or_transparency"
    icc = im.info.get("icc_profile")
    if icc and "srgb" not in ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(io.BytesIO(icc))).lower():
        return "non_srgb_profile"
    return ""


def stage2(prov):
    print("Stage 2: check data")
    prov["subset"] = [s.split("/")[1] for s in prov.source_dataset]
    reasons, pix, ph = [], [], []
    for r in prov.itertuples():
        try:
            im = Image.open(raw_path(r.source_dataset, r.image_id, r.original_format)); im.load()
            reasons.append(exclusion_reason(im))
            pix.append(sha256(np.asarray(im).tobytes() + str(im.size).encode()))
            ph.append(phash(im))
        except Exception as e:
            reasons.append(f"unreadable_{type(e).__name__}"); pix.append(""); ph.append(0)
    prov["reason"], prov["pixel_sha"], prov["phash"] = reasons, pix, ph

    # union-find over exact, pixel-level, and near-copy links (same rule for both classes)
    parent = list(range(len(prov)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    links = []
    for key in ("original_sha256", "pixel_sha"):
        for _, idx in prov[prov[key] != ""].groupby(key).groups.items():
            links += [(idx[0], j, key) for j in idx[1:]]
    h = np.array(ph, dtype=np.uint64)
    for i in range(len(h)):
        d = np.unpackbits((h[i + 1:] ^ h[i]).view(np.uint8).reshape(-1, 8), axis=1).sum(1)
        links += [(i, i + 1 + j, "phash") for j in np.flatnonzero(d <= CFG["phash"]["max_hamming"])]
    for a, b, _ in links:
        parent[find(a)] = find(b)
    prov["cluster"] = [find(i) for i in range(len(prov))]
    sizes = prov.cluster.map(prov.cluster.value_counts())
    dup = prov[sizes > 1].sort_values(["cluster", "image_id"])
    kinds = {}
    for a, b, k in links:
        kinds.setdefault(prov.cluster[a], set()).add(k)
    dup.assign(link_kinds=[";".join(sorted(kinds[c])) for c in dup.cluster])[
        ["cluster", "image_id", "label", "subset", "link_kinds"]].to_csv(DATA / "duplicate_clusters.csv", index=False)
    keeper = prov.sort_values("image_id").groupby("cluster").image_id.first()
    is_dup = prov.image_id != prov.cluster.map(keeper)
    prov.loc[is_dup & (prov.reason == ""), "reason"] = "duplicate_of_" + prov.cluster.map(keeper)
    prov[prov.reason != ""][["image_id", "label", "subset", "reason"]].to_csv(DATA / "exclusions.csv", index=False)
    print(f"  {len(dup)} images in {dup.cluster.nunique()} duplicate clusters; {int((prov.reason != '').sum())} excluded")
    return prov[prov.reason == ""]


def stage3(ok):
    print("Stage 3: quota draw and split by image group")
    rng = np.random.default_rng(CFG["seeds"]["split"])
    q, fr = CFG["quota_per_generator"], CFG["split"]["fractions"]
    n_tr, n_va = int(q * fr["train"]), int(q * fr["val"])
    parts = []
    for (subset, label), g in ok.sort_values("image_id").groupby(["subset", "label"]):
        check(len(g) >= q, f"{subset}/{label}: {len(g)} available >= quota {q}")
        g = g.iloc[rng.permutation(len(g))[:q]].copy()
        g["split"] = ["train"] * n_tr + ["val"] * n_va + ["test"] * (q - n_tr - n_va)
        parts.append(g)
    sp = pd.concat(parts)
    sp["group_id"] = sp.image_id                                   # duplicates removed -> one parent per group
    uns = CFG["unseen_generator"]
    sp["fold_unseen"] = np.where((sp.generator_family == uns) & (sp.split != "test"), "unused", sp.split)
    order = rng.permutation(len(sp))                               # pilot: first 200 per class, subset of split
    sp = sp.iloc[order]
    sp["pilot"] = (sp.groupby("label").cumcount() < CFG["pilot_per_class"]).astype(int)
    sp = sp.sort_values("image_id")[["image_id", "group_id", "label", "generator_family", "subset",
                                     "split", "fold_unseen", "pilot"]]
    check(sp.image_id.is_unique, "every parent image appears in exactly one split")
    check(not ((sp.generator_family == uns) & sp.fold_unseen.isin(["train", "val"])).any(),
          "the unseen generator appears in neither training nor validation data")
    check(all(sp[sp.split == s].label.value_counts().nunique() == 1 and sp[sp.split == s].label.nunique() == 2
              for s in ("train", "val", "test")), "both classes, equal counts, in every split")
    check(sp[sp.pilot == 1].split.nunique() == 3, "pilot covers train/val/test")
    sp.to_csv(DATA / "splits.csv", index=False)
    (DATA / "split_hash.txt").write_text(sha256((DATA / "splits.csv").read_bytes()) + "\n")
    print("  split counts:\n", sp.groupby(["split", "label"]).size().to_string())
    return sp


def stage4(sp, prov):
    print("Stage 4: standard pre-processing")
    (IMG / "canonical").mkdir(parents=True, exist_ok=True)
    prov = prov.set_index("image_id")
    rows = []
    for r in sp.itertuples():
        p = prov.loc[r.image_id]
        im = ImageOps.exif_transpose(Image.open(raw_path(p.source_dataset, r.image_id, p.original_format)))
        im = im.convert("RGB")                                      # L -> RGB; profiles already checked in Stage 2
        k = S / min(im.size)
        im = im.resize((max(S, round(im.width * k)), max(S, round(im.height * k))), Image.BICUBIC)
        l, t = (im.width - S) // 2, (im.height - S) // 2
        im = im.crop((l, t, l + S, t + S))
        out = IMG / "canonical" / f"{r.image_id}.png"
        im.save(out, format="PNG")                                  # fresh image: no EXIF/ICC/text chunks
        rows.append({"image_id": r.image_id, "path": out.relative_to(ROOT).as_posix(),
                     "sha256": sha256(out.read_bytes()),
                     "history_tag": "known_prior_history" if p.original_format == "JPEG" else "final_transform",
                     "resize_factor": round(k, 4), "pillow": PIL.__version__})
    man = pd.DataFrame(rows)
    check(all(Image.open(ROOT / p).size == (S, S) for p in man.path), f"all standard images are {S}x{S}")
    man.to_csv(DATA / "canonical_manifest.csv", index=False)
    return man


def stage5(sp, man):
    print("Stage 5: conditions C0 / C1 / C2")
    (IMG / "variants").mkdir(parents=True, exist_ok=True)
    enc = CFG["jpeg_encoder"]
    label = sp.set_index("image_id").label
    rows = []
    for r in man.itertuples():
        base = dict(image_id=r.image_id, parent_id=r.image_id, source_sha256=r.sha256)
        rows.append({**base, "condition": "C0", "quality": 0, "encoder": "none", "path": r.path, "sha256": r.sha256})
        im = Image.open(ROOT / r.path)
        for q in CFG["jpeg_qualities"]:
            out = IMG / "variants" / f"{r.image_id}_q{q}.jpg"
            im.save(out, format="JPEG", quality=q, subsampling=2, optimize=enc["optimize"])
            rows.append({**base, "condition": "C1", "quality": q, "encoder": f"Pillow {PIL.__version__} 4:2:0",
                         "path": out.relative_to(ROOT).as_posix(), "sha256": sha256(out.read_bytes())})
    vm = pd.DataFrame(rows)
    c2 = vm[((vm.condition == "C1") & (vm.quality == 75) & (vm.image_id.map(label) == "real")) |
            ((vm.condition == "C0") & (vm.image_id.map(label) == "fake"))].assign(condition="C2")
    vm = pd.concat([vm, c2], ignore_index=True)
    check((vm.source_sha256 == vm.image_id.map(man.set_index("image_id").sha256)).all(),
          "every variant comes from the standard image")
    vm.to_csv(DATA / "variant_manifest.csv", index=False)
    print("  variants:", vm.groupby(["condition", "quality"]).size().to_dict())


if __name__ == "__main__":
    prov = pd.read_csv(DATA / "provenance.csv", dtype=str, keep_default_na=False)
    check((prov != "").all().all(), "no empty provenance cells")
    ok = stage2(prov)
    sp = stage3(ok)
    man = stage4(sp, prov)
    stage5(sp, man)
