document.addEventListener("DOMContentLoaded", () => {

    // -----------------------------
    // Mobile Sidebar Toggle
    // -----------------------------
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");

    if (menuToggle && sidebar) {

        const closeSidebar = () => {
            sidebar.classList.remove("mobile-open");
        };

        menuToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            sidebar.classList.toggle("mobile-open");
        });

        document.addEventListener("click", (e) => {
            if (
                window.innerWidth < 1025 &&
                sidebar.classList.contains("mobile-open") &&
                !sidebar.contains(e.target) &&
                !menuToggle.contains(e.target)
            ) {
                closeSidebar();
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth >= 1025) {
                closeSidebar();
            }
        });
    }

    // -----------------------------
    // Search & Clear (Same as User Management)
    // -----------------------------
    const searchInput = document.getElementById("searchInput");
    const clearButton = document.getElementById("clearButton");

    if (searchInput && clearButton) {

        const toggleClearButton = () => {
            clearButton.classList.toggle(
                "show",
                searchInput.value.trim() !== ""
            );
        };

        toggleClearButton();

        searchInput.addEventListener("input", toggleClearButton);

        clearButton.addEventListener("click", () => {
            window.location.href = window.location.pathname;
        });
    }

    // -----------------------------
    // Status / Sort Dropdown
    // -----------------------------
    const statusDropdown = document.getElementById("statusDropdown");
    const statusContainer = document.querySelector(".status-filter-container");

    if (statusDropdown && statusContainer) {

        statusDropdown.addEventListener("click", (e) => {
            e.stopPropagation();
            statusContainer.classList.toggle("active");
        });

        document.addEventListener("click", () => {
            statusContainer.classList.remove("active");
        });
    }

});