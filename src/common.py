"""Shared paths and the locked config. Every script prints the config hash."""
import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
CONFIG_PATH = ROOT / "config.yaml"
CFG = yaml.safe_load(CONFIG_PATH.read_text())
CONFIG_HASH = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()[:12]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def check(cond, msg):
    """Stop-on-failure check (pipeline rule 2)."""
    if not cond:
        raise SystemExit(f"CHECK FAILED: {msg}")
    print(f"  ok  {msg}")


print(f"[config {CONFIG_HASH}]")
