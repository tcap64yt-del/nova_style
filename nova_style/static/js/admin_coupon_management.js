document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    const clearButton = document.getElementById("clearButton");

    if (searchInput && clearButton) {

        clearButton.addEventListener("click", (e) => {
            e.preventDefault();

            const url = new URL(window.location.href);

            // Remove search
            url.searchParams.delete("search");

            // Go back to first page
            url.searchParams.delete("page");

            window.location.href = url.toString();
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {

    const deleteModal = document.getElementById("deleteModal");
    const deleteModalText = document.getElementById("deleteModalText");
    const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
    const deleteCouponForm = document.getElementById("deleteCouponForm");

    const deleteButtons = document.querySelectorAll(".btn-delete");

    deleteButtons.forEach(button => {

        button.addEventListener("click", () => {

            const deleteUrl = button.dataset.deleteUrl;
            const couponCode = button.dataset.couponCode;

            deleteCouponForm.action = deleteUrl;

            deleteModalText.textContent =
                `Are you sure you want to delete coupon "${couponCode}"?`;

            deleteModal.classList.add("is-open");
            deleteModal.setAttribute("aria-hidden", "false");
        });

    });

    cancelDeleteBtn.addEventListener("click", () => {

        deleteModal.classList.remove("is-open");
        deleteModal.setAttribute("aria-hidden", "true");

    });

});