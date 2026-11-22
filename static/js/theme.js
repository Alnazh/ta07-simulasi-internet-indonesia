export function aktifkanTema() {
  const tombol = document.getElementById("theme-toggle");
  tombol.addEventListener("click", () => {
    const root = document.documentElement;
    const baru = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", baru);
    try { localStorage.setItem("tema", baru); } catch (e) { /* penyimpanan diblokir */ }
  });
}
