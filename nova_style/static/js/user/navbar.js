

document.addEventListener("DOMContentLoaded", function () {

    const searchBtn = document.getElementById("action-search");
    const searchOverlay = document.getElementById("searchOverlay");
    const searchInput = document.getElementById("searchInput");
    const clearSearch = document.getElementById("clearSearch");

    // Open / Close Search
    if (searchBtn && searchOverlay) {

        searchBtn.addEventListener("click", function (e) {

            e.stopPropagation();

            searchOverlay.classList.toggle("active");

            if (searchOverlay.classList.contains("active") && searchInput) {
                searchInput.focus();
            }

        });

    }

    // Clear Search
    if (clearSearch && searchInput) {

        clearSearch.addEventListener("click", function (e) {

            e.preventDefault();

            searchInput.value = "";

            searchInput.focus();

        });

    }

    // Close with ESC
    document.addEventListener("keydown", function (e) {

        if (e.key === "Escape" && searchOverlay) {
            searchOverlay.classList.remove("active");
        }

    });

    // Close when clicking outside
    document.addEventListener("click", function (e) {

        if (!searchOverlay || !searchBtn) return;

        if (
            searchOverlay.classList.contains("active") &&
            !searchOverlay.contains(e.target) &&
            !searchBtn.contains(e.target)
        ) {
            searchOverlay.classList.remove("active");
        }

    });

    // Prevent closing when clicking inside search box
    if (searchOverlay) {

        searchOverlay.addEventListener("click", function (e) {

            e.stopPropagation();

        });

    }

});