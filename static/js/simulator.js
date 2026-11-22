import { api } from "./api.js";
import { gambarGrafik } from "./chart.js";
import { angka, debounce, deretTile, el, kartuPenjelasan, tahun, titikData } from "./format.js";

export async function mulai() {
  const dataAsli = await api.get("/api/data");
  const form = document.getElementById("sim-form");
  const r0 = parseFloat(form.dataset.r0);
  const kolom = {
    r: document.getElementById("in-r"), K: document.getElementById("in-K"),
    t: document.getElementById("in-t"), metode: document.getElementById("in-metode"),
    h: document.getElementById("in-h"),
  };
  const galat = document.getElementById("sim-error");
  let urutan = 0;
  let terakhir = null;

  const tampilkanNilai = () => {
    document.getElementById("out-r").textContent = angka(parseFloat(kolom.r.value), 4);
    document.getElementById("out-K").textContent = kolom.K.value;
    document.getElementById("out-t").textContent = kolom.t.value;
    document.getElementById("field-h").hidden = kolom.metode.value !== "euler";
  };

  const ambilParameter = () => ({
    r: parseFloat(kolom.r.value), K: parseFloat(kolom.K.value), t_akhir: parseFloat(kolom.t.value),
    metode: kolom.metode.value, h: parseFloat(kolom.h.value),
  });

  const gambarHasil = (hasil) => {
    terakhir = hasil;
    const { metrik, ringkasan, parameter } = hasil;
    deretTile(document.getElementById("sim-tiles"), [
      ["RMSE", `${angka(metrik.rmse)} poin`, ""], ["MAE", `${angka(metrik.mae)} poin`, "cyan"],
      ["R²", angka(metrik.r2, 4), "violet"], ["Nilai 2023", `${angka(ringkasan.p2023)} %`, "orange"],
      [`Nilai ${parameter.t_akhir}`, `${angka(ringkasan.p_akhir)} %`, "green"],
      ["Titik belok", tahun(ringkasan.t_belok), "pink"],
    ]);

    const garisTegak = parameter.t_akhir > 2023 ? 2023 : null;
    gambarGrafik(document.getElementById("chart-sim"), {
      xMin: 2000, xMax: parameter.t_akhir, garisTegak,
      seri: [
        { nama: "Data asli", warna: "var(--c-data)", gaya: "titik", titik: titikData(dataAsli) },
        { nama: `Simulasi (${parameter.metode})`, warna: "var(--c-base)", gaya: "garis", titik: hasil.seri },
      ],
    });
    kartuPenjelasan(document.getElementById("sim-penjelasan"), hasil.penjelasan);

    const puncak = Math.max(...hasil.seri_laju.map((p) => p[1]));
    gambarGrafik(document.getElementById("chart-laju"), {
      xMin: 2000, xMax: parameter.t_akhir, garisTegak, yMax: Math.max(5, Math.ceil((puncak * 1.1) / 5) * 5),
      yJudul: "Pertambahan (poin per tahun)",
      seri: [{ nama: "Laju dP/dt", warna: "var(--c-cepat)", gaya: "garis", titik: hasil.seri_laju }],
    });
    document.getElementById("laju-penjelasan").textContent = hasil.penjelasan_laju;
  };

  const jalankan = async () => {
    const saya = ++urutan;
    try {
      const hasil = await api.post("/api/simulate", ambilParameter());
      if (saya !== urutan) return;
      galat.hidden = true;
      gambarHasil(hasil);
    } catch (e) {
      galat.textContent = e.message;
      galat.hidden = false;
    }
  };
  const jalankanTunda = debounce(jalankan);

  form.addEventListener("input", () => { tampilkanNilai(); jalankanTunda(); });

  document.getElementById("btn-kalibrasi").addEventListener("click", async () => {
    try {
      const hasil = await api.post("/api/calibrate", { K: parseFloat(kolom.K.value) });
      kolom.r.value = hasil.r;
      tampilkanNilai();
      jalankan();
    } catch (e) {
      galat.textContent = e.message;
      galat.hidden = false;
    }
  });

  document.getElementById("btn-reset").addEventListener("click", () => {
    kolom.r.value = r0; kolom.K.value = 100; kolom.t.value = 2035;
    kolom.metode.value = "solve_ivp"; kolom.h.value = 1;
    tampilkanNilai();
    jalankan();
  });

  document.getElementById("btn-csv").addEventListener("click", () => {
    if (!terakhir) return;
    const baris = ["tahun,pengguna_persen,laju_poin_per_tahun", ...terakhir.seri.map(([t, p], i) => `${t},${p},${terakhir.seri_laju[i][1]}`)];
    const tautan = el("a", { href: URL.createObjectURL(new Blob([baris.join("\n")], { type: "text/csv" })), download: "simulasi.csv" });
    tautan.click();
    URL.revokeObjectURL(tautan.href);
  });

  kolom.r.value = r0;
  tampilkanNilai();
  jalankan();
}
