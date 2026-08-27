document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("profileModal");
    const openBtn = document.getElementById("openProfileModal");
    const closeBtn = document.getElementById("closeModalBtn");
    const closeOverlay = document.getElementById("closeProfileModal");
    const backBtn = document.getElementById("backBtn");
    const avatarInput = document.getElementById("avatarInput");
    const avatarPreview = document.getElementById("avatarPreview");

    if (!modal) return;

    function openModal() {
        modal.classList.add("show");
    }

    function closeModal() {
        modal.classList.remove("show");
    }

    openBtn?.addEventListener("click", openModal);
    closeBtn?.addEventListener("click", closeModal);
    closeOverlay?.addEventListener("click", closeModal);
    backBtn?.addEventListener("click", closeModal);

    avatarInput?.addEventListener("change", function () {
        if (this.files && this.files[0]) {
            const reader = new FileReader();

            reader.onload = function (e) {
                avatarPreview.src = e.target.result;
            };

            reader.readAsDataURL(this.files[0]);
        }
    });

});