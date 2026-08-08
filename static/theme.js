(() => {
    const storageKey = "moksha-theme";
    const root = document.documentElement;

    const applyTheme = (isDark) => {
        root.classList.toggle("dark-mode", isDark);
        document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
            button.setAttribute("aria-pressed", String(isDark));
            button.querySelector("[data-theme-label]").textContent = isDark ? "Light mode" : "Dark mode";
        });
    };

    const isDark = () => root.classList.contains("dark-mode");

    document.addEventListener("DOMContentLoaded", () => {
        applyTheme(isDark());

        document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
            button.addEventListener("click", () => {
                const nextThemeIsDark = !isDark();
                applyTheme(nextThemeIsDark);
                try {
                    localStorage.setItem(storageKey, nextThemeIsDark ? "dark" : "light");
                } catch (error) {}
            });
        });
    });
})();
