document.addEventListener("DOMContentLoaded", () => {

    /* ============================
       Sort Dropdown
    ============================ */

    const sortContainer = document.querySelector(".sort-container");
    const sortButton = document.querySelector(".sort-dropdown");
    const selectedSort = document.getElementById("selected-sort");

    if (sortContainer && sortButton) {

        sortButton.addEventListener("click", (e) => {

            e.stopPropagation();

            const open = sortContainer.classList.toggle("active");

            sortButton.setAttribute(
                "aria-expanded",
                open
            );

        });

        document.addEventListener("click", () => {

            sortContainer.classList.remove("active");

            sortButton.setAttribute(
                "aria-expanded",
                false
            );

        });

    }

    document.querySelectorAll(".sort-menu a").forEach(link => {

        link.addEventListener("click", () => {

            if (selectedSort) {

                selectedSort.textContent =
                    "SORT BY: " + link.dataset.label;

            }

        });

    });



    /* ============================
       Search Clear Button
    ============================ */

    const searchInput = document.getElementById("searchInput");

    const clearButton = document.getElementById("clearButton");

    if (searchInput && clearButton) {

        function toggleClear() {

            clearButton.classList.toggle(
                "show",
                searchInput.value.trim() !== ""
            );

        }

        toggleClear();

        searchInput.addEventListener(
            "input",
            toggleClear
        );

        clearButton.addEventListener("click", () => {

            searchInput.value = "";

            toggleClear();

            const url = new URL(window.location);

            url.searchParams.delete("search");

            window.location = url;

        });

    }



    /* ============================
       Block Modal
    ============================ */

    const modal = document.getElementById("blockModal");

    const overlay = document.querySelector(
        ".confirm-modal__overlay"
    );

    const cancel = document.querySelector(
        ".cancel-modal"
    );

    const confirm = document.getElementById(
        "confirmAction"
    );

    const modalTitle = document.getElementById(
        "modalTitle"
    );

    const modalText = document.getElementById(
        "modalText"
    );

    let activeForm = null;

    document
        .querySelectorAll(".user-status-btn")
        .forEach(button => {

            button.addEventListener("click", () => {

                activeForm = button.closest("form");

                if (
                    button.textContent.trim().toLowerCase()
                    === "block"
                ) {

                    modalTitle.textContent =
                        "Block User";

                    modalText.textContent =
                        "Are you sure you want to block this user?";

                } else {

                    modalTitle.textContent =
                        "Unblock User";

                    modalText.textContent =
                        "Are you sure you want to unblock this user?";

                }

                modal.classList.add("is-open");

            });

        });


    function closeModal() {

        modal.classList.remove("is-open");

        activeForm = null;

    }

    if (overlay)
        overlay.addEventListener(
            "click",
            closeModal
        );

    if (cancel)
        cancel.addEventListener(
            "click",
            closeModal
        );

    if (confirm)
        confirm.addEventListener("click", () => {

            if (activeForm) {

                activeForm.requestSubmit();

            }

        });

    document.addEventListener("keydown", e => {

        if (e.key === "Escape") {

            closeModal();

        }

    });



    /* ============================
       Toast Messages
    ============================ */

    const toasts = document.querySelectorAll(".toast");

    toasts.forEach(toast => {

        setTimeout(() => {

            toast.style.opacity = "0";

            toast.style.transform =
                "translateY(-10px)";

            setTimeout(() => {

                toast.remove();

            }, 300);

        }, 3000);

    });

});