import { aktifkanTema } from "./theme.js";

aktifkanTema();

const halaman = { beranda: "./beranda.js", simulator: "./simulator.js", skenario: "./skenario.js", data: "./data.js" };
const modul = halaman[document.body.dataset.halaman];
if (modul) (await import(modul)).mulai();
