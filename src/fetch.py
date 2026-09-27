"""Stage 1 — stream GenImage test shards, keep a content-blind sample, write provenance.csv.

Usage: python src/fetch.py [generator ...]   (default: all; safe to re-run, finished shards are skipped)
"""
import csv
import hashlib
import io
import json
import sys
import urllib.request

import pyarrow as pa
from PIL import Image

from common import CFG, DATA, RAW, sha256

BASE = "https://huggingface.co/datasets/nebula/GenImage-arrow/resolve/main/"
FIELDS = ["image_id", "original_path", "original_sha256", "parent_id", "group_id", "label",
          "generator_family", "generator_checkpoint", "source_dataset", "original_width",
          "original_height", "original_format", "exif_present", "known_jpeg_quality",
          "known_processing_history", "license_note"]


def keep(path: str) -> bool:
    h = int(hashlib.sha1(path.encode()).hexdigest()[:8], 16) / 2**32
    return h < CFG["stream_keep_rate"]


def row(gen, path, label, data):
    im = Image.open(io.BytesIO(data))
    fmt = im.format
    image_id = sha256(path.encode())[:16]
    return {
        "image_id": image_id, "original_path": path, "original_sha256": sha256(data),
        "parent_id": image_id, "group_id": image_id, "label": label,
        "generator_family": gen if label == "fake" else "real",
        "generator_checkpoint": "unknown", "source_dataset": f"GenImage/{CFG['mirror_dirs'][gen]}/val",
        "original_width": im.width, "original_height": im.height, "original_format": fmt,
        "exif_present": int(bool(im.info.get("exif"))),
        "known_jpeg_quality": "unknown",
        "known_processing_history": "jpeg_before_receipt" if fmt == "JPEG" else "unknown",
        "license_note": "GenImage CC-BY-NC-SA-4.0; reals under ImageNet terms",
    }


def fetch(gen):
    manifest = json.load(urllib.request.urlopen(BASE + "manifest.json"))
    out = RAW / gen
    out.mkdir(parents=True, exist_ok=True)
    for shard in manifest["bundles"][CFG["source_split"]][CFG["mirror_dirs"][gen]]["shards"]:
        done = out / (shard["path"].split("/")[-1] + ".csv")
        if done.exists():
            continue
        rows = []
        with urllib.request.urlopen(BASE + shard["path"]) as resp:
            for batch in pa.ipc.open_stream(resp):
                for path, label, data in zip(*(batch[c].to_pylist() for c in ("image_path", "label", "image"))):
                    if keep(path):
                        r = row(gen, path, ["real", "fake"][label], data)
                        (out / (r["image_id"] + "." + r["original_format"].lower())).write_bytes(data)
                        rows.append(r)
        with open(done, "w", newline="") as f:
            w = csv.DictWriter(f, FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(gen, shard["path"], len(rows), flush=True)


def merge():
    rows = [r for g in CFG["generators"] for p in sorted((RAW / g).glob("*.csv"))
            for r in csv.DictReader(open(p))]
    assert all(v not in ("", None) for r in rows for v in r.values()), "empty provenance cell"
    with open(DATA / "provenance.csv", "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("provenance.csv rows:", len(rows))


if __name__ == "__main__":
    for g in sys.argv[1:] or CFG["generators"]:
        fetch(g)
    merge()
