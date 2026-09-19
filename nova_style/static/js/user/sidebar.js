document.addEventListener("DOMContentLoaded", function () {

    const sidebarLinks = document.querySelectorAll(".sidebar-link");
    const currentPath = window.location.pathname.replace(/\/$/, "");

    // Fallback active menu based on URL
    sidebarLinks.forEach(link => {

        const href = new URL(link.href).pathname.replace(/\/$/, "");

        if (href === currentPath) {

            sidebarLinks.forEach(item => {
                item.classList.remove("active");
            });

            link.classList.add("active");

        }

    });

    // Mobile: scroll active item into view
    const activeLink = document.querySelector(".sidebar-link.active");

    if (activeLink && window.innerWidth <= 768) {

        activeLink.scrollIntoView({
            behavior: "smooth",
            inline: "center",
            block: "nearest"
        });

    }

});