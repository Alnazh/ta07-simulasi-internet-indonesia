import { angka } from "./format.js";

const NS = "http://www.w3.org/2000/svg";
const L = 720, M = { kiri: 54, kanan: 18, atas: 16, bawah: 46 };

function svg(tag, atribut, induk) {
  const node = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(atribut)) node.setAttribute(k, v);
  induk.appendChild(node);
  return node;
}

function terdekat(titik, x) {
  return titik.reduce((a, p) => (Math.abs(p[0] - x) < Math.abs(a[0] - x) ? p : a), titik[0]);
}

// Tinggi grafik menyesuaikan kolom penjelasan di sebelahnya (tampilan lebar)
function tinggiSelaras(wadah) {
  const panel = wadah.closest(".panel");
  const sisi = panel && !panel.classList.contains("panel--tumpuk") && panel.querySelector(".insights");
  if (!sisi || window.innerWidth <= 960 || !wadah.clientWidth) return 340;
  return Math.min(520, Math.max(260, Math.round((L * (sisi.offsetHeight - 40)) / wadah.clientWidth)));
}

// seri: [{nama, warna, titik: [[x, y]], gaya: "garis" | "titik" | "putus"}]
export function gambarGrafik(wadah, { seri, xMin, xMax, yMin = 0, yMax = 100, yJudul = "Pengguna internet (%)", garisTegak = null }) {
  wadah.replaceChildren();
  const T = tinggiSelaras(wadah);
  const lebar = L - M.kiri - M.kanan, tinggi = T - M.atas - M.bawah;
  const px = (x) => M.kiri + ((x - xMin) / (xMax - xMin)) * lebar;
  const py = (y) => M.atas + (1 - (y - yMin) / (yMax - yMin)) * tinggi;

  const kanvas = svg("svg", { viewBox: `0 0 ${L} ${T}` }, wadah);
  for (let i = 0; i <= 5; i++) {
    const y = yMin + (i * (yMax - yMin)) / 5;
    svg("line", { class: "grid-line", x1: M.kiri, x2: L - M.kanan, y1: py(y), y2: py(y) }, kanvas);
    svg("text", { class: "axis-text", x: M.kiri - 8, y: py(y) + 4, "text-anchor": "end" }, kanvas).textContent = angka(y, 0);
  }
  const langkahX = xMax - xMin > 30 ? 10 : 5;
  for (let x = Math.ceil(xMin / langkahX) * langkahX; x <= xMax; x += langkahX) {
    svg("text", { class: "axis-text", x: px(x), y: T - M.bawah + 20, "text-anchor": "middle" }, kanvas).textContent = x;
  }
  svg("line", { class: "axis-line", x1: M.kiri, x2: M.kiri, y1: M.atas, y2: M.atas + tinggi }, kanvas);
  svg("line", { class: "axis-line", x1: M.kiri, x2: L - M.kanan, y1: M.atas + tinggi, y2: M.atas + tinggi }, kanvas);
  svg("text", { class: "axis-title", x: 14, y: M.atas + tinggi / 2, transform: `rotate(-90 14 ${M.atas + tinggi / 2})`, "text-anchor": "middle" }, kanvas).textContent = yJudul;
  svg("text", { class: "axis-title", x: M.kiri + lebar / 2, y: T - 6, "text-anchor": "middle" }, kanvas).textContent = "Tahun";

  if (garisTegak) {
    svg("line", { class: "vline", x1: px(garisTegak), x2: px(garisTegak), y1: M.atas, y2: M.atas + tinggi }, kanvas);
  }

  for (const s of seri) {
    if (s.gaya === "titik") {
      for (const [x, y] of s.titik) svg("circle", { cx: px(x), cy: py(y), r: 5.5, fill: s.warna, stroke: "var(--ink)", "stroke-width": 2 }, kanvas);
      continue;
    }
    const d = s.titik.map(([x, y], i) => `${i ? "L" : "M"}${px(x).toFixed(1)} ${py(y).toFixed(1)}`).join("");
    const garis = svg("path", { d, fill: "none", stroke: s.warna, "stroke-width": 4.5, "stroke-linejoin": "round", "stroke-linecap": "round" }, kanvas);
    if (s.gaya === "putus") garis.setAttribute("stroke-dasharray", "9 6");
  }

  const legenda = document.createElement("div");
  legenda.className = "legend";
  for (const s of seri) {
    const item = document.createElement("span");
    const kotak = document.createElement("i");
    kotak.style.background = s.warna;
    item.append(kotak, s.nama);
    legenda.appendChild(item);
  }
  const tip = document.createElement("div");
  tip.className = "tooltip";
  tip.hidden = true;
  wadah.append(tip, legenda);

  const lapisan = svg("rect", { x: M.kiri, y: M.atas, width: lebar, height: tinggi, fill: "transparent" }, kanvas);
  lapisan.addEventListener("pointermove", (e) => {
    const kotak = kanvas.getBoundingClientRect();
    const x = xMin + (((e.clientX - kotak.left) * (L / kotak.width) - M.kiri) / lebar) * (xMax - xMin);
    const baris = [];
    let acuan = null;
    for (const s of seri) {
      const p = s.titik.length ? terdekat(s.titik, x) : null;
      if (!p || Math.abs(p[0] - x) > (xMax - xMin) / 30) continue;
      baris.push(`${s.nama}: ${angka(p[1])}`);
      acuan = acuan || p;
    }
    if (!acuan) { tip.hidden = true; return; }
    tip.replaceChildren(...[`Tahun ${angka(acuan[0], 1).replace(".", "")}`, ...baris].flatMap((t, i) => (i ? [document.createElement("br"), t] : [t])));
    tip.style.left = `${(px(acuan[0]) / L) * 100}%`;
    tip.style.top = `${(py(acuan[1]) / T) * kotak.height}px`;
    tip.hidden = false;
  });
  lapisan.addEventListener("pointerleave", () => { tip.hidden = true; });
}
