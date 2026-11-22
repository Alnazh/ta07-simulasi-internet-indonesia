"""Skenario What-If untuk r dan K."""
import numpy as np

from . import data, model


def _satu(nama, kunci, r, K, t_akhir):
    tahun, y = data.muat()
    waktu, P = model.simulasi(r, K, "solve_ivp", 0.1, t_akhir)
    ringkas = model.ringkasan(waktu, P, K)
    galat = model.metrik(y, model.pada_tahun_data(waktu, P))["rmse"]
    return {
        "kunci": kunci, "nama": nama, "r": r, "K": K, "rmse": galat, "ringkasan": ringkas,
        "seri": [[float(a), float(b)] for a, b in zip(waktu[::5], P[::5])],
    }


def bandingkan(t_akhir=2035.0):
    r0 = model.kalibrasi(100.0)
    return [
        _satu("Baseline", "base", r0, 100.0, t_akhir),
        _satu("Laju +20 %", "cepat", r0 * 1.2, 100.0, t_akhir),
        _satu("Laju −20 %", "lambat", r0 * 0.8, 100.0, t_akhir),
        _satu("Batas jenuh K = 90", "k90", r0, 90.0, t_akhir),
    ]


def sensitivitas_k():
    tahun, y = data.muat()
    baris = []
    for K in (80.0, 90.0, 100.0):
        r = model.kalibrasi(K)
        m = model.metrik(y, model.selesaikan_ivp(r, K, y[0], tahun))
        baris.append({"K": K, "r": r, **m})
    return baris
