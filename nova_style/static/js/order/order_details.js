document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("cancelModal");
    const form = document.getElementById("cancelForm");
    const quantitySelect = document.getElementById("cancelQuantity");

    document.querySelectorAll(".btn-cancel-product").forEach(button => {

        button.addEventListener("click", function (e) {

            e.preventDefault();

            form.action = this.dataset.url;

            const availableQty = Number(this.dataset.quantity);

            quantitySelect.innerHTML = "";

            for (let i = 1; i <= availableQty; i++) {
                quantitySelect.innerHTML += `
                    <option value="${i}">${i}</option>
                `;
            }

            modal.classList.add("show");
        });

    });

    document.querySelector(".close-modal").addEventListener("click", function () {
        modal.classList.remove("show");
    });

    modal.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.classList.remove("show");
        }
    });

});

const orderModal = document.getElementById("orderCancelModal");
const openOrderModal = document.getElementById("openOrderCancelModal");
const closeOrderModal = document.querySelector(".close-order-modal");

if (openOrderModal && orderModal) {
    openOrderModal.addEventListener("click", function (e) {
        e.preventDefault();
        orderModal.classList.add("show");
    });
}

if (closeOrderModal && orderModal) {
    closeOrderModal.addEventListener("click", function () {
        orderModal.classList.remove("show");
    });

    orderModal.addEventListener("click", function (e) {
        if (e.target === orderModal) {
            orderModal.classList.remove("show");
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {

    const returnModal = document.getElementById("returnOrderModal");
    const openReturnBtn = document.getElementById("openReturnOrderModal");
    const closeReturnBtn = document.querySelector(".close-return-modal");

    if (openReturnBtn) {
        openReturnBtn.onclick = function (e) {
            e.preventDefault();
            returnModal.classList.add("show");
        };
    }

    if (closeReturnBtn) {
        closeReturnBtn.onclick = function () {
            returnModal.classList.remove("show");
        };
    }

    if (returnModal) {
        returnModal.onclick = function (e) {
            if (e.target === returnModal) {
                returnModal.classList.remove("show");
            }
        };
    }

});


const returnModal = document.getElementById("returnProductModal");

document.querySelectorAll(".btn-return-product").forEach(btn => {
    btn.addEventListener("click", function(e) {
        e.preventDefault();

        document.getElementById("returnProductForm").action = this.dataset.url;

        document.getElementById("returnProductName").textContent = this.dataset.name;
        document.getElementById("returnProductQty").textContent = this.dataset.qty;
        document.getElementById("returnProductPrice").textContent = this.dataset.price;

        const select = document.getElementById("returnQuantity");
        select.innerHTML = "";

        for (let i = 1; i <= Number(this.dataset.qty); i++) {
            select.innerHTML += `<option value="${i}">${i}</option>`;
        }

        returnModal.style.display = "flex";
    });
});