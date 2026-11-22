import { api } from "./api.js";
import { gambarGrafik } from "./chart.js";
import { angka, el, kartuPenjelasan, tahun, titikData } from "./format.js";

const WARNA = { base: "var(--c-base)", cepat: "var(--c-cepat)", lambat: "var(--c-lambat)", k90: "var(--c-k90)" };

function kartuSkenario(s, tAkhir) {
  const kartu = el("article", { class: `scenario scenario--${s.kunci}` });
  kartu.appendChild(el("h4", {}, s.nama));
  const daftar = el("dl");
  const baris = [
    ["Laju r", angka(s.r, 4)], ["Batas K", `${angka(s.K, 0)} %`], ["RMSE vs data", `${angka(s.rmse)} poin`],
    ["Nilai 2023", `${angka(s.ringkasan.p2023)} %`], [`Nilai ${tAkhir}`, `${angka(s.ringkasan.p_akhir)} %`],
    ["Capai 50 %", tahun(s.ringkasan.t50)], ["Capai 80 %", tahun(s.ringkasan.t80)], ["Capai 90 %", tahun(s.ringkasan.t90)],
  ];
  for (const [k, v] of baris) daftar.append(el("dt", {}, k), el("dd", {}, v));
  kartu.appendChild(daftar);
  return kartu;
}

function tabelK(baris) {
  const kepala = el("thead");
  const tr = el("tr");
  for (const h of ["K (%)", "r terkalibrasi", "RMSE", "MAE", "R²"]) tr.appendChild(el("th", { class: "num" }, h));
  kepala.appendChild(tr);
  const badan = el("tbody");
  for (const b of baris) {
    const r = el("tr");
    for (const v of [angka(b.K, 0), angka(b.r, 4), angka(b.rmse, 4), angka(b.mae, 4), angka(b.r2, 4)]) r.appendChild(el("td", { class: "num" }, v));
    badan.appendChild(r);
  }
  document.getElementById("tabel-k").replaceChildren(kepala, badan);
}

export async function mulai() {
  const dataAsli = await api.get("/api/data");
  const pilih = document.getElementById("in-skenario-t");

  const muat = async () => {
    const tAkhir = parseInt(pilih.value, 10);
    const hasil = await api.get(`/api/scenarios?t_akhir=${tAkhir}`);
    kartuPenjelasan(document.getElementById("skenario-penjelasan"), hasil.penjelasan.grafik);
    gambarGrafik(document.getElementById("chart-skenario"), {
      xMin: 2000, xMax: tAkhir, garisTegak: 2023,
      seri: [
        { nama: "Data asli", warna: "var(--c-data)", gaya: "titik", titik: titikData(dataAsli) },
        ...hasil.skenario.map((s) => ({ nama: s.nama, warna: WARNA[s.kunci], gaya: s.kunci === "base" ? "garis" : "putus", titik: s.seri })),
      ],
    });
    document.getElementById("scenario-cards").replaceChildren(...hasil.skenario.map((s) => kartuSkenario(s, tAkhir)));
    tabelK(hasil.sensitivitas);
    kartuPenjelasan(document.getElementById("tabel-penjelasan"), hasil.penjelasan.tabel);
  };

  pilih.addEventListener("change", muat);
  await muat();
}
