async function kirim(url, opsi) {
  const res = await fetch(url, opsi);
  const isi = await res.json();
  if (!res.ok) throw new Error(isi.galat || "Terjadi kesalahan pada server");
  return isi;
}

export const api = {
  get: (url) => kirim(url),
  post: (url, badan) => kirim(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(badan),
  }),
};
