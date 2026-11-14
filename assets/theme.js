(() => {
  const root = document.documentElement;
  let theme = "dark";

  try {
    if (localStorage.getItem("portfolio-theme") === "light") {
      theme = "light";
    }
  } catch {
    // Keep the default when browser storage is unavailable.
  }

  // Apply the saved theme before the stylesheet and page are rendered.
  root.dataset.theme = theme;

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("dark-mode");
    if (!toggle) return;

    toggle.checked = theme === "dark";
    toggle.addEventListener("change", () => {
      theme = toggle.checked ? "dark" : "light";
      root.dataset.theme = theme;
      try {
        localStorage.setItem("portfolio-theme", theme);
      } catch {
        // The switch still works when the preference cannot be saved.
      }
    });
  });
})();
