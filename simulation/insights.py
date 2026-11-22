"""Teks penjelasan grafik yang dihitung dari angka."""
from . import data


def angka(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def tahun(x):
    return f"{x:.1f}".replace(".", ",")


def capaian(x, akhir):
    return f"pada tahun {tahun(x)}" if x is not None else f"belum tercapai sampai {int(akhir)}"


def kualitas(rmse):
    if rmse < 2.5:
        return "sangat dekat dengan data"
    if rmse < 6:
        return "cukup dekat dengan data"
    return "masih jauh dari data"


def susun(par, hasil):
    _, y = data.muat()
    m, s = hasil["metrik"], hasil["ringkasan"]
    r, K = par["r"], par["K"]
    daftar = [{
        "jenis": "biru", "judul": "Kecocokan dengan data",
        "teks": f"RMSE {angka(m['rmse'])} poin dan R² {angka(m['r2'], 4)}. Kurva simulasi {kualitas(m['rmse'])}. "
                f"Pada 2023 simulasi bernilai {angka(s['p2023'])} % dan data asli {angka(y[-1])} %.",
    }, {
        "jenis": "cyan", "judul": "Titik belok",
        "teks": f"Pertumbuhan paling cepat terjadi saat P mencapai K/2 = {angka(K / 2)} %, sekitar tahun "
                f"{tahun(s['t_belok'])}. Saat itu pengguna bertambah {angka(r * K / 4)} poin per tahun.",
    }, {
        "jenis": "violet", "judul": "Masa depan model",
        "teks": f"Pada {int(par['t_akhir'])} nilai simulasi {angka(s['p_akhir'])} %. Batas 80 % "
                f"{capaian(s['t80'], par['t_akhir'])}, sedangkan batas 90 % {capaian(s['t90'], par['t_akhir'])}. "
                "Ini hasil simulasi dengan asumsi, bukan prediksi.",
    }]
    if K < y.max():
        daftar.append({"jenis": "oranye", "judul": "Batas jenuh terlalu rendah",
                       "teks": f"K = {angka(K)} % lebih kecil dari nilai data tertinggi ({angka(y.max())} %). "
                               "Kurva tidak akan pernah menyentuh titik data terakhir."})
    if par["metode"] == "euler" and par["h"] >= 1:
        daftar.append({"jenis": "oranye", "judul": "Langkah Euler besar",
                       "teks": f"Dengan h = {angka(par['h'], 2)} tahun, Euler cenderung tertinggal dari solusi sebenarnya. "
                               "Perkecil h atau pilih solve_ivp untuk hasil yang lebih teliti."})
    return daftar


def laju(par, hasil):
    """Penjelasan grafik laju pertambahan pengguna (dP/dt)."""
    r, K, s = par["r"], par["K"], hasil["ringkasan"]
    return (f"Laju pertambahan berbentuk lonceng. Puncaknya {angka(r * K / 4)} poin per tahun "
            f"(r × K / 4) saat P mencapai {angka(K / 2)} %, sekitar tahun {tahun(s['t_belok'])}. "
            "Sebelum puncak, pertambahan makin cepat karena pengguna lama mengajak pengguna baru. "
            "Sesudahnya melambat karena sisa penduduk yang belum memakai internet makin sedikit.")


def data_halaman():
    t, y = data.muat()
    naik = y[1:] - y[:-1]
    i = int(naik.argmax())
    s = data.statistik()
    daftar = [{
        "jenis": "biru", "judul": "Tren naik",
        "teks": f"Pengguna naik dari {angka(y[0])} % pada {int(t[0])} menjadi {angka(y[-1])} % pada {int(t[-1])}, "
                f"bertambah {angka(y[-1] - y[0])} poin dalam {int(t[-1] - t[0])} tahun.",
    }, {
        "jenis": "cyan", "judul": "Lonjakan terbesar",
        "teks": f"Kenaikan tahunan terbesar terjadi pada {int(t[i + 1])}, yaitu {angka(naik[i])} poin "
                f"(dari {angka(y[i])} % menjadi {angka(y[i + 1])} %).",
    }, {
        "jenis": "violet", "judul": "Data condong ke kanan",
        "teks": f"Median {angka(s['median'])} % jauh di bawah rata-rata {angka(s['rata'])} %. "
                "Artinya sebagian besar tahun bernilai rendah dan lonjakan baru terjadi di tahun-tahun akhir.",
    }]
    turun = [int(t[j + 1]) for j in range(len(naik)) if naik[j] < 0]
    if turun:
        daftar.append({"jenis": "oranye", "judul": "Penurunan kecil",
                       "teks": f"Nilai sempat turun pada {', '.join(map(str, turun))}. Model logistik yang mulus tidak bisa meniru penurunan ini."})
    return daftar


def skenario_halaman(daftar, sens, t_akhir):
    k = {x["kunci"]: x for x in daftar}
    b, c, l, k90 = k["base"], k["cepat"], k["lambat"], k["k90"]
    _, y = data.muat()
    t50 = lambda x: x["ringkasan"]["t50"]
    p23 = lambda x: x["ringkasan"]["p2023"]
    grafik = [{
        "jenis": "biru", "judul": "Baseline",
        "teks": f"Dengan r = {angka(b['r'], 4)} dan K = 100 %, simulasi memberi {angka(p23(b))} % pada 2023 "
                f"(data {angka(y[-1])} %) dan RMSE {angka(b['rmse'])} poin. Separuh penduduk memakai internet sekitar tahun {tahun(t50(b))}.",
    }, {
        "jenis": "cyan", "judul": "Laju naik 20 %",
        "teks": f"Kurva naik terlalu cepat. Pada 2023 nilainya {angka(p23(c))} %, lebih tinggi {angka(p23(c) - y[-1])} poin "
                f"dari data. RMSE melonjak ke {angka(c['rmse'])} poin dan batas 50 % tercapai {angka(t50(b) - t50(c), 1)} tahun lebih awal.",
    }, {
        "jenis": "violet", "judul": "Laju turun 20 %",
        "teks": f"Kurva tertinggal. Pada 2023 nilainya {angka(p23(l))} %, kurang {angka(y[-1] - p23(l))} poin dari data. "
                f"RMSE {angka(l['rmse'])} poin dan batas 50 % baru tercapai {angka(t50(l) - t50(b), 1)} tahun setelah baseline.",
    }, {
        "jenis": "oranye", "judul": "Batas jenuh K = 90",
        "teks": f"Kurva melambat lebih awal dan tidak pernah melewati 90 %. Pada {t_akhir} nilainya {angka(k90['ringkasan']['p_akhir'])} %. "
                f"RMSE naik {angka(k90['rmse'] - b['rmse'])} poin menjadi {angka(k90['rmse'])}.",
    }, {
        "jenis": "biru", "judul": "Mana yang lebih peka?",
        "teks": f"Perubahan r sebesar 20 % membuat RMSE sampai {angka(max(c['rmse'], l['rmse']) / b['rmse'], 1)} kali lipat, "
                f"sedangkan K turun ke 90 % hanya {angka(k90['rmse'] / b['rmse'], 1)} kali lipat. Model jauh lebih peka terhadap laju r.",
    }]
    a, z = sens[0], sens[-1]
    tabel = [{
        "jenis": "violet", "judul": "Membaca tabel K",
        "teks": f"Saat K naik dari {angka(a['K'], 0)} % ke {angka(z['K'], 0)} %, RMSE turun dari {angka(a['rmse'], 4)} ke {angka(z['rmse'], 4)} "
                f"dan R² naik dari {angka(a['r2'], 4)} ke {angka(z['r2'], 4)}. Nilai r ikut berubah ({angka(a['r'], 4)} ke {angka(z['r'], 4)}) "
                "karena r dan K saling mengimbangi. Data belum jenuh, jadi K = 100 % tetap sebuah asumsi.",
    }]
    return {"grafik": grafik, "tabel": tabel}


def model_halaman(r, p0, K, t_belok, p2023):
    aliran = lambda P: r * P * (1 - P / K)
    return [{
        "jenis": "biru", "judul": "Awal pertumbuhan",
        "teks": f"Pada 2000, P = {angka(p0, 4)} %, sehingga pertambahannya hanya {angka(aliran(p0), 4)} poin per tahun. "
                "Loop penguat R masih lemah karena pengguna lamanya sedikit.",
    }, {
        "jenis": "cyan", "judul": "Puncak pertumbuhan",
        "teks": f"Saat P = K/2 = {angka(K / 2)} % (sekitar tahun {tahun(t_belok)}), faktor (1 − P/K) bernilai 0,5 dan "
                f"pertambahan mencapai maksimum {angka(r * K / 4)} poin per tahun.",
    }, {
        "jenis": "oranye", "judul": "Menuju jenuh",
        "teks": f"Pada 2023, P = {angka(p2023)} %, pertambahannya turun menjadi {angka(aliran(p2023))} poin per tahun. "
                "Loop penyeimbang B mulai mendominasi karena ruang tumbuh (1 − P/K) tinggal sedikit.",
    }]
