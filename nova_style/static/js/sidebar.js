document.addEventListener("DOMContentLoaded", () => {

    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");

    if (!menuToggle || !sidebar) return;

    const closeSidebar = () => {
        sidebar.classList.remove("mobile-open");
    };

    menuToggle.addEventListener("click", (e) => {

        e.stopPropagation();

        sidebar.classList.toggle("mobile-open");

    });

    document.addEventListener("click", (e) => {

        const isMobile = window.innerWidth < 1025;

        if (
            isMobile &&
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

});