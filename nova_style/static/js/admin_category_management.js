document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // Lucide Icons
    // ==========================

    if (window.lucide) {
        lucide.createIcons();
    }

    // ==========================
    // Search Clear Button
    // ==========================

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

        searchInput.addEventListener(
            "input",
            toggleClearButton
        );

        clearButton.addEventListener("click", (e) => {

            e.preventDefault();

            searchInput.value = "";

            toggleClearButton();

            const url = new URL(window.location.href);

            url.searchParams.delete("search");

            window.location.href = url.toString();

        });

    }

    // ==========================
    // Sort Dropdown
    // ==========================

    const sortDropdown = document.getElementById("sortDropdown");

    if (sortDropdown) {

        sortDropdown.addEventListener("click", function (e) {

            e.stopPropagation();

            this.classList.toggle("active");

        });

        document.addEventListener("click", () => {

            sortDropdown.classList.remove("active");

        });

    }

    // ==========================
    // Status Modal
    // ==========================

    const statusModal = document.getElementById("statusModal");
    const confirmBtn = document.getElementById("confirmStatusBtn");
    const cancelBtn = document.getElementById("cancelStatusBtn");

    let selectedToggle = null;

    document
        .querySelectorAll(".status-toggle-checkbox")
        .forEach(toggle => {

            toggle.addEventListener("click", function (e) {

                e.preventDefault();

                selectedToggle = this;

                const willDeactivate = this.checked;

                const modalText =
                    document.getElementById("statusModalText");

                modalText.textContent = willDeactivate
                    ? "Are you sure you want to deactivate this category?"
                    : "Are you sure you want to activate this category?";

                statusModal.classList.add("is-open");

            });

        });

    function closeModal() {

        if (!statusModal) return;

        statusModal.classList.remove("is-open");

        selectedToggle = null;

    }

    if (cancelBtn) {

        cancelBtn.addEventListener(
            "click",
            closeModal
        );

    }

    if (confirmBtn) {

        confirmBtn.addEventListener("click", () => {

            if (!selectedToggle) return;

            window.location.href =
                selectedToggle.dataset.url;

        });

    }

    const overlay = document.querySelector(
        "#statusModal .confirm-modal__overlay"
    );

    if (overlay) {

        overlay.addEventListener(
            "click",
            closeModal
        );

    }

    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") {

            closeModal();

        }

    });

    // ==========================
    // Toast
    // ==========================

    document.querySelectorAll(".toast").forEach((toast) => {

        setTimeout(() => {

            toast.classList.add("hide");

            setTimeout(() => {

                toast.remove();

            }, 400);

        }, 3000);

    });

});