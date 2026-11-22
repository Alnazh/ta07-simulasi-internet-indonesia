const pemformat = {};

export function angka(x, nd = 2) {
  if (!pemformat[nd]) {
    pemformat[nd] = new Intl.NumberFormat("id-ID", { minimumFractionDigits: nd, maximumFractionDigits: nd });
  }
  return pemformat[nd].format(x);
}

export function tahun(x) {
  return x === null || x === undefined ? "belum tercapai" : angka(x, 1).replace(".", "");
}

export function el(tag, atribut = {}, isi = "") {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(atribut)) node.setAttribute(k, v);
  node.textContent = isi;
  return node;
}

export function debounce(fn, tunda = 160) {
  let waktu;
  return (...arg) => {
    clearTimeout(waktu);
    waktu = setTimeout(() => fn(...arg), tunda);
  };
}

export function kartuPenjelasan(wadah, daftar) {
  wadah.replaceChildren(...daftar.map((p) => {
    const kotak = el("article", { class: `insight insight--${p.jenis}` });
    kotak.append(el("h4", {}, p.judul), el("p", {}, p.teks));
    return kotak;
  }));
}

export function deretTile(wadah, daftar) {
  wadah.replaceChildren(...daftar.map(([nama, nilai, warna]) => {
    const t = el("article", { class: `tile ${warna ? `tile--${warna}` : ""}` });
    t.append(el("span", {}, nama), el("strong", {}, nilai));
    return t;
  }));
}

export const titikData = (d) => d.tahun.map((t, i) => [t, d.nilai[i]]);
