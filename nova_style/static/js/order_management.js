document.addEventListener("DOMContentLoaded", () => {

    /* ==========================================
       Search Clear Button
    ========================================== */

    const searchInput = document.getElementById("searchInput");
    const clearButton = document.getElementById("clearButton");

    if (searchInput && clearButton) {

        function toggleClearButton() {

            clearButton.classList.toggle(
                "show",
                searchInput.value.trim() !== ""
            );

        }

        toggleClearButton();

        searchInput.addEventListener(
            "input",
            toggleClearButton
        );

        clearButton.addEventListener("click", () => {

            const url = new URL(window.location.href);

            url.searchParams.delete("search");
            url.searchParams.delete("page");

            window.location.href = url.toString();

        });

    }

    /* ==========================================
       Status Dropdown
    ========================================== */

    const statusDropdown = document.getElementById("statusDropdown");
    const statusContainer = document.querySelector(".status-filter-container");
    const selectedStatus = document.getElementById("selected-status");

    if (statusDropdown && statusContainer) {

        statusDropdown.addEventListener("click", function (e) {

            e.stopPropagation();

            statusContainer.classList.toggle("active");

        });

        document.addEventListener("click", () => {

            statusContainer.classList.remove("active");

        });

        document.querySelectorAll(".status-item").forEach(item => {

            item.addEventListener("click", function () {

                if (selectedStatus) {

                    selectedStatus.textContent =
                        this.textContent.trim();

                }

            });

        });

    }

    /* ==========================================
       Edit Order Modal
    ========================================== */

    const modal = document.getElementById("editOrderModal");
    const overlay = modal?.querySelector(".confirm-modal__overlay");

    const cancelBtn = document.getElementById("cancelModalBtn");
    const saveBtn = document.getElementById("confirmSaveBtn");

    const modalOrderId = document.getElementById("modalOrderId");
    const modalCustomerName = document.getElementById("modalCustomerName");
    const modalOrderStatus = document.getElementById("modalOrderStatus");

    let activeRow = null;

    document.querySelectorAll(".edit-order-btn").forEach(button => {

        button.addEventListener("click", () => {

            activeRow = button.closest("tr");

            if (!activeRow) return;

            modalOrderId.value =
                activeRow.querySelector(".order-id-text")?.textContent.trim() || "";

            const customer =
                activeRow.querySelector(".user-first-name");

            modalCustomerName.value =
                customer ? customer.textContent.trim() : "";

            const badge =
                activeRow.querySelector(".status-pill");

            if (badge) {

                modalOrderStatus.value =
                    badge.textContent.trim().toUpperCase();

            }

            modal.classList.add("is-open");
            modal.setAttribute("aria-hidden", "false");

        });

    });

    function closeModal() {

        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");

        activeRow = null;

    }

    cancelBtn?.addEventListener(
        "click",
        closeModal
    );

    overlay?.addEventListener(
        "click",
        closeModal
    );

    document.addEventListener("keydown", e => {

        if (e.key === "Escape") {

            closeModal();

        }

    });

    saveBtn?.addEventListener("click", () => {

        if (!activeRow) return;

        const badge =
            activeRow.querySelector(".status-pill");

        if (badge) {

            badge.textContent =
                modalOrderStatus.value;

            badge.classList.remove(
                "status-placed",
                "status-shipped",
                "status-delivered",
                "status-cancelled"
            );

            switch (modalOrderStatus.value) {

                case "PLACED":
                    badge.classList.add("status-placed");
                    break;

                case "SHIPPED":
                    badge.classList.add("status-shipped");
                    break;

                case "DELIVERED":
                    badge.classList.add("status-delivered");
                    break;

                case "CANCELLED":
                    badge.classList.add("status-cancelled");
                    break;

            }

        }

        closeModal();

    });

    /* ==========================================
       Toast Messages
    ========================================== */

    document.querySelectorAll(".toast").forEach(toast => {

        setTimeout(() => {

            toast.classList.add("fade-out");

            setTimeout(() => {

                toast.remove();

            }, 300);

        }, 3000);

    });

});
document.addEventListener("DOMContentLoaded", function () {

    const dropdown = document.getElementById("statusDropdown");
    const menu = document.getElementById("statusMenu");

    if (!dropdown || !menu) {
        return;
    }

    dropdown.addEventListener("click", function (event) {
        event.stopPropagation();

        menu.classList.toggle("show");
        dropdown.classList.toggle("open");
    });

    document.addEventListener("click", function () {
        menu.classList.remove("show");
        dropdown.classList.remove("open");
    });

});