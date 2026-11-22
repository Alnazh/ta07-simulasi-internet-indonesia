"""Pembaca data pengguna internet Indonesia."""
import csv
from functools import lru_cache
from pathlib import Path

import numpy as np

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "internet_indonesia.csv"


@lru_cache(maxsize=1)
def muat():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        baris = list(csv.DictReader(f))
    tahun = np.array([float(b["Tahun"]) for b in baris])
    nilai = np.array([float(b["Pengguna"]) for b in baris])
    return tahun, nilai


def statistik():
    _, y = muat()
    q1, median, q3 = np.percentile(y, [25, 50, 75])
    return {
        "jumlah": int(y.size), "rata": float(y.mean()), "std": float(y.std(ddof=1)),
        "min": float(y.min()), "q1": float(q1), "median": float(median),
        "q3": float(q3), "maks": float(y.max()),
    }


def kenaikan_tahunan():
    t, y = muat()
    return [{"tahun": int(t[i]), "naik": float(y[i] - y[i - 1])} for i in range(1, len(y))]
