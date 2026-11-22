from flask import Flask, jsonify, render_template, request

from simulation import data, insights, model, scenarios
from simulation.errors import InputError

app = Flask(__name__)

METODE = {"solve_ivp", "euler", "analitik"}
LANGKAH = {0.1, 0.25, 0.5, 1.0, 2.0}


def angka_dalam(payload, kunci, awal, bawah, atas):
    try:
        nilai = float(payload.get(kunci, awal))
    except (TypeError, ValueError):
        raise InputError(f"Nilai {kunci} harus berupa angka")
    if not bawah <= nilai <= atas:
        raise InputError(f"Nilai {kunci} harus di antara {bawah} dan {atas}")
    return nilai


def baca_parameter(payload):
    metode = payload.get("metode", "solve_ivp")
    if metode not in METODE:
        raise InputError("Metode tidak dikenal")
    h = angka_dalam(payload, "h", 1.0, 0.1, 2.0)
    if h not in LANGKAH:
        raise InputError("Langkah h harus 0,1 / 0,25 / 0,5 / 1 / 2")
    return {
        "r": angka_dalam(payload, "r", model.kalibrasi(100.0), 0.01, 1.0),
        "K": angka_dalam(payload, "K", 100.0, 50.0, 100.0),
        "t_akhir": float(round(angka_dalam(payload, "t_akhir", 2023, 2023, 2050))),
        "metode": metode,
        "h": h,
    }


def konteks_dasar():
    r = model.kalibrasi(100.0)
    tahun, y = data.muat()
    waktu, P = model.simulasi(r, 100.0, "solve_ivp", 1.0, 2023.0)
    ukuran = model.metrik(y, model.pada_tahun_data(waktu, P))
    return {"r": r, "p0": float(y[0]), "p2023": float(y[-1]), "ukuran": ukuran, "angka": insights.angka}


@app.errorhandler(InputError)
def galat_masukan(e):
    return jsonify({"galat": str(e)}), 400


@app.errorhandler(404)
def tidak_ditemukan(e):
    if request.path.startswith("/api/"):
        return jsonify({"galat": "Rute tidak ditemukan"}), 404
    return render_template("404.html", halaman="404", **konteks_dasar()), 404


@app.get("/")
def beranda():
    return render_template("beranda.html", halaman="beranda", **konteks_dasar())


@app.get("/simulator")
def simulator():
    return render_template("simulator.html", halaman="simulator", **konteks_dasar())


@app.get("/skenario")
def skenario():
    return render_template("skenario.html", halaman="skenario", **konteks_dasar())


@app.get("/model")
def halaman_model():
    ctx = konteks_dasar()
    waktu, P = model.simulasi(ctx["r"], 100.0, "analitik", 1.0, 2023.0)
    t_belok = model.tahun_capai(waktu, P, 50.0)
    penjelasan = insights.model_halaman(ctx["r"], ctx["p0"], 100.0, t_belok, ctx["p2023"])
    return render_template("model.html", halaman="model", penjelasan=penjelasan, **ctx)


@app.get("/data")
def halaman_data():
    return render_template("data.html", halaman="data", **konteks_dasar())


@app.get("/tentang")
def tentang():
    return render_template("tentang.html", halaman="tentang", **konteks_dasar())


@app.get("/api/data")
def api_data():
    tahun, y = data.muat()
    return jsonify({
        "tahun": tahun.tolist(), "nilai": y.tolist(),
        "statistik": data.statistik(), "penjelasan": insights.data_halaman(),
    })


@app.post("/api/simulate")
def api_simulasi():
    par = baca_parameter(request.get_json(silent=True) or {})
    tahun, y = data.muat()
    waktu, P = model.simulasi(par["r"], par["K"], par["metode"], par["h"], par["t_akhir"])
    hasil = {
        "metrik": model.metrik(y, model.pada_tahun_data(waktu, P)),
        "ringkasan": model.ringkasan(waktu, P, par["K"]),
    }
    langkah = max(1, int(round(0.1 / (waktu[1] - waktu[0])))) if par["metode"] != "euler" else 1
    waktu, P = waktu[::langkah], P[::langkah]
    laju = par["r"] * P * (1 - P / par["K"])
    return jsonify({
        "parameter": par, **hasil,
        "seri": [[float(a), float(b)] for a, b in zip(waktu, P)],
        "seri_laju": [[float(a), float(b)] for a, b in zip(waktu, laju)],
        "penjelasan": insights.susun(par, hasil),
        "penjelasan_laju": insights.laju(par, hasil),
    })


@app.post("/api/calibrate")
def api_kalibrasi():
    K = angka_dalam(request.get_json(silent=True) or {}, "K", 100.0, 50.0, 100.0)
    tahun, y = data.muat()
    r = model.kalibrasi(K)
    return jsonify({"r": r, "K": K, "metrik": model.metrik(y, model.selesaikan_ivp(r, K, y[0], tahun))})


@app.get("/api/scenarios")
def api_skenario():
    t_akhir = round(angka_dalam(request.args, "t_akhir", 2035, 2024, 2050))
    daftar, sens = scenarios.bandingkan(t_akhir), scenarios.sensitivitas_k()
    return jsonify({"skenario": daftar, "sensitivitas": sens,
                    "penjelasan": insights.skenario_halaman(daftar, sens, t_akhir)})


if __name__ == "__main__":
    app.run(debug=True)
