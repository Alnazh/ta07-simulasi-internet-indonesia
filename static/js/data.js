import { api } from "./api.js";
import { gambarGrafik } from "./chart.js";
import { angka, deretTile, el, kartuPenjelasan, titikData } from "./format.js";

export async function mulai() {
  const d = await api.get("/api/data");
  const s = d.statistik;
  deretTile(document.getElementById("data-tiles"), [
    ["Rata-rata", `${angka(s.rata)} %`, ""], ["Simpangan baku", angka(s.std), "cyan"],
    ["Nilai terendah", `${angka(s.min)} %`, "violet"], ["Median", `${angka(s.median)} %`, "orange"],
    ["Nilai tertinggi", `${angka(s.maks)} %`, "green"],
  ]);

  kartuPenjelasan(document.getElementById("data-penjelasan"), d.penjelasan);
  gambarGrafik(document.getElementById("chart-data"), {
    xMin: 2000, xMax: 2023,
    seri: [{ nama: "Pengguna internet", warna: "var(--c-data)", gaya: "garis", titik: titikData(d) }],
  });

  const kepala = el("thead");
  const tr = el("tr");
  for (const h of ["Tahun", "Pengguna (%)", "Kenaikan (poin)"]) tr.appendChild(el("th", { class: h === "Tahun" ? "" : "num" }, h));
  kepala.appendChild(tr);
  const badan = el("tbody");
  d.tahun.forEach((t, i) => {
    const naik = i === 0 ? "-" : angka(d.nilai[i] - d.nilai[i - 1]);
    const baris = el("tr");
    baris.append(el("td", {}, String(t)), el("td", { class: "num" }, angka(d.nilai[i])), el("td", { class: "num" }, naik));
    badan.appendChild(baris);
  });
  document.getElementById("tabel-data").replaceChildren(kepala, badan);
}
