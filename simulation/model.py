"""Model logistik dP/dt = r P (1 - P/K)."""
from functools import lru_cache

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from . import data

LANGKAH_GRAFIK = 0.1


def turunan(t, P, r, K):
    return r * P * (1 - P / K)


def analitik(t, r, K, P0, t0):
    return K / (1 + ((K - P0) / P0) * np.exp(-r * (np.asarray(t) - t0)))


def selesaikan_ivp(r, K, P0, t_eval):
    hasil = solve_ivp(turunan, (t_eval[0], t_eval[-1]), [P0], args=(r, K),
                      t_eval=t_eval, rtol=1e-8, atol=1e-10)
    return hasil.y[0]


def euler(r, K, P0, t0, t1, h):
    n = int(round((t1 - t0) / h))
    waktu = t0 + h * np.arange(n + 1)
    P = np.empty(n + 1)
    P[0] = P0
    for i in range(n):
        P[i + 1] = P[i] + h * r * P[i] * (1 - P[i] / K)
    return waktu, P


def simulasi(r, K, metode="solve_ivp", h=1.0, t_akhir=2023.0, P0=None):
    tahun, y = data.muat()
    t0 = float(tahun[0])
    P0 = float(y[0]) if P0 is None else P0
    if metode == "euler":
        return euler(r, K, P0, t0, t_akhir, h)
    n = int(round((t_akhir - t0) / LANGKAH_GRAFIK))
    waktu = np.linspace(t0, t_akhir, n + 1)
    if metode == "analitik":
        return waktu, analitik(waktu, r, K, P0, t0)
    return waktu, selesaikan_ivp(r, K, P0, waktu)


def metrik(aktual, prediksi):
    selisih = prediksi - aktual
    rmse = float(np.sqrt(np.mean(selisih ** 2)))
    mae = float(np.mean(np.abs(selisih)))
    r2 = float(1 - np.sum(selisih ** 2) / np.sum((aktual - aktual.mean()) ** 2))
    return {"rmse": rmse, "mae": mae, "r2": r2}


def pada_tahun_data(waktu, P):
    tahun, _ = data.muat()
    return np.interp(tahun, waktu, P)


@lru_cache(maxsize=64)
def kalibrasi(K):
    """Cari r dengan RMSE terkecil."""
    tahun, y = data.muat()

    def galat(r):
        return metrik(y, selesaikan_ivp(r, K, y[0], tahun))["rmse"]

    hasil = minimize_scalar(galat, bounds=(0.01, 1.0), method="bounded")
    return float(hasil.x)


def tahun_capai(waktu, P, ambang):
    """Tahun pertama P mencapai ambang, None bila tidak tercapai."""
    ada = np.nonzero(P >= ambang)[0]
    if ada.size == 0:
        return None
    i = int(ada[0])
    if i == 0:
        return float(waktu[0])
    frac = (ambang - P[i - 1]) / (P[i] - P[i - 1])
    return float(waktu[i - 1] + frac * (waktu[i] - waktu[i - 1]))


def ringkasan(waktu, P, K):
    nilai_di = lambda th: float(np.interp(th, waktu, P))
    return {
        "p2023": nilai_di(2023.0),
        "p_akhir": float(P[-1]),
        "t50": tahun_capai(waktu, P, 50.0),
        "t80": tahun_capai(waktu, P, 80.0),
        "t90": tahun_capai(waktu, P, 90.0),
        "t_belok": tahun_capai(waktu, P, K / 2),
    }
