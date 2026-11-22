import { api } from "./api.js";
import { gambarGrafik } from "./chart.js";
import { kartuPenjelasan, titikData } from "./format.js";

export async function mulai() {
  const [data, hasil] = await Promise.all([api.get("/api/data"), api.post("/api/simulate", { t_akhir: 2023 })]);
  kartuPenjelasan(document.getElementById("beranda-penjelasan"), hasil.penjelasan.slice(0, 3));
  gambarGrafik(document.getElementById("chart-beranda"), {
    xMin: 2000, xMax: 2023,
    seri: [
      { nama: "Data asli", warna: "var(--c-data)", gaya: "titik", titik: titikData(data) },
      { nama: "Simulasi baseline", warna: "var(--c-base)", gaya: "garis", titik: hasil.seri },
    ],
  });
}
