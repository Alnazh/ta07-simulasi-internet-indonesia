import unittest

import numpy as np

from app import app
from simulation import data, model


class TestModel(unittest.TestCase):
    def test_data_indonesia_24_tahun(self):
        tahun, y = data.muat()
        self.assertEqual(len(y), 24)
        self.assertEqual((tahun[0], tahun[-1]), (2000, 2023))

    def test_kalibrasi_sesuai_notebook(self):
        r = model.kalibrasi(100.0)
        tahun, y = data.muat()
        m = model.metrik(y, model.selesaikan_ivp(r, 100.0, y[0], tahun))
        self.assertAlmostEqual(r, 0.2385, places=4)
        self.assertAlmostEqual(m["rmse"], 1.9397, places=4)
        self.assertAlmostEqual(m["r2"], 0.9922, places=4)

    def test_ivp_sama_dengan_analitik(self):
        t = np.linspace(2000, 2023, 24)
        selisih = model.selesaikan_ivp(0.24, 100.0, 0.93, t) - model.analitik(t, 0.24, 100.0, 0.93, 2000)
        self.assertLess(np.abs(selisih).max(), 1e-4)

    def test_euler_makin_teliti_bila_h_kecil(self):
        r, P0 = 0.24, 0.93
        acuan = model.analitik(2023, r, 100.0, P0, 2000)
        galat = [abs(model.euler(r, 100.0, P0, 2000, 2023, h)[1][-1] - acuan) for h in (1.0, 0.1)]
        self.assertLess(galat[1], galat[0])

    def test_nilai_tidak_melewati_batas_jenuh(self):
        _, P = model.simulasi(0.5, 90.0, "solve_ivp", 1.0, 2050)
        self.assertLessEqual(P.max(), 90.0 + 1e-6)


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_semua_halaman(self):
        for rute in ("/", "/simulator", "/skenario", "/model", "/data", "/tentang"):
            self.assertEqual(self.client.get(rute).status_code, 200, rute)

    def test_penjelasan_per_grafik(self):
        sim = self.client.post("/api/simulate", json={}).get_json()
        self.assertTrue(sim["penjelasan"] and sim["penjelasan_laju"] and sim["seri_laju"])
        self.assertTrue(self.client.get("/api/data").get_json()["penjelasan"])
        self.assertTrue(self.client.get("/api/scenarios").get_json()["penjelasan"]["grafik"])

    def test_simulasi_baseline(self):
        hasil = self.client.post("/api/simulate", json={}).get_json()
        self.assertAlmostEqual(hasil["metrik"]["rmse"], 1.9397, places=4)
        self.assertAlmostEqual(hasil["ringkasan"]["t_belok"], 2019.6, places=1)

    def test_euler_langkah_satu(self):
        hasil = self.client.post("/api/simulate", json={"metode": "euler", "h": 1}).get_json()
        self.assertAlmostEqual(hasil["metrik"]["rmse"], 5.6761, places=3)

    def test_masukan_tidak_valid_ditolak(self):
        for badan in ({"r": 5}, {"K": 10}, {"metode": "acak"}, {"h": 0.3}, {"r": "abc"}):
            self.assertEqual(self.client.post("/api/simulate", json=badan).status_code, 400, badan)

    def test_kalibrasi_k90(self):
        hasil = self.client.post("/api/calibrate", json={"K": 90}).get_json()
        self.assertAlmostEqual(hasil["r"], 0.2443, places=4)

    def test_skenario(self):
        hasil = self.client.get("/api/scenarios?t_akhir=2035").get_json()
        nama = {s["kunci"]: s for s in hasil["skenario"]}
        self.assertAlmostEqual(nama["cepat"]["ringkasan"]["p2023"], 87.09, places=2)
        self.assertAlmostEqual(nama["k90"]["ringkasan"]["p_akhir"], 87.99, places=2)
        self.assertEqual(len(hasil["sensitivitas"]), 3)


if __name__ == "__main__":
    unittest.main()
