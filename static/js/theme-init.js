(function () {
  try {
    var saved = localStorage.getItem("tema");
    document.documentElement.setAttribute("data-theme", saved || "light");
  } catch (e) {}
})();
