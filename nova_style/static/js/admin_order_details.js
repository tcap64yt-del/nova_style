const modal = document.getElementById("editOrderModal");

document.getElementById("detailsEditOrderBtn").onclick = function () {
    modal.classList.add("is-open");
};

document.getElementById("cancelModalBtn").onclick = function () {
    modal.classList.remove("is-open");
};

document.getElementById("confirmSaveBtn").onclick = function () {
    modal.classList.remove("is-open");
};

document.querySelector(".confirm-modal__overlay").onclick = function () {
    modal.classList.remove("is-open");
};