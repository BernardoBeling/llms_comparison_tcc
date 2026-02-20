document.addEventListener("DOMContentLoaded", () => {
  const confirmButtons = document.querySelectorAll(".js-confirm");
  confirmButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const msg = btn.getAttribute("data-confirm") || "Confirmar ação?";
      const ok = window.confirm(msg);
      if (!ok) {
        e.preventDefault();
      }
    });
  });
});
