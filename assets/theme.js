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

  const backgrounds = __BACKGROUND_IMAGES__;
  if (backgrounds.length) {
    let previous = null;
    try {
      previous = sessionStorage.getItem("portfolio-background");
    } catch {
      // Random selection also works when browser storage is blocked.
    }
    const choices = backgrounds.length > 1
      ? backgrounds.filter((image) => image !== previous)
      : backgrounds;
    const selected = choices[Math.floor(Math.random() * choices.length)];
    root.style.setProperty("--sidebar-image", `url("${selected}")`);
    try {
      sessionStorage.setItem("portfolio-background", selected);
    } catch {
      // Remembering the last image is optional.
    }
  }

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
