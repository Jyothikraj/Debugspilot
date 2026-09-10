/**
 * CodeSense Theme Switcher
 * Handles light/dark mode persistence without page flickering.
 */
(function () {
    // 1. Check saved preference or fallback to system preference / default dark
    const savedTheme = localStorage.getItem("theme");
    const systemPrefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
    const initialTheme = savedTheme || (systemPrefersLight ? "light" : "dark");

    // 2. Set attribute on <html> immediately (before DOM loads)
    document.documentElement.setAttribute("data-theme", initialTheme);

    // 3. Bind UI interactions once the DOM is interactive
    document.addEventListener("DOMContentLoaded", () => {
        const themeToggleBtn = document.getElementById("themeToggle");
        if (!themeToggleBtn) return;

        // Function to update the button icon based on the active theme
        function updateToggleIcon(theme) {
            themeToggleBtn.textContent = theme === "light" ? "☀️" : "🌙";
            themeToggleBtn.setAttribute(
                "aria-label",
                theme === "light" ? "Switch to dark mode" : "Switch to light mode"
            );
        }

        // Initialize button icon
        const currentTheme = document.documentElement.getAttribute("data-theme") || initialTheme;
        updateToggleIcon(currentTheme);

        // Click event listener
        themeToggleBtn.addEventListener("click", () => {
            const activeTheme = document.documentElement.getAttribute("data-theme");
            const nextTheme = activeTheme === "light" ? "dark" : "light";

            // Apply to document and save to localStorage
            document.documentElement.setAttribute("data-theme", nextTheme);
            localStorage.setItem("theme", nextTheme);

            // Update button visual
            updateToggleIcon(nextTheme);
        });
    });
})();