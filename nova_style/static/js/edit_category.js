const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
fileInput.value = "";
const previewImage =
    document.getElementById('previewImage');

const cropModal =
    document.getElementById('cropModal');

const cropImage =
    document.getElementById('cropImage');

const applyCrop =
    document.getElementById('applyCrop');

const cancelCrop =
    document.getElementById('cancelCrop');

let cropper = null;
let newImageSelected = false;
/* Show existing category image */

if (
    previewImage &&
    previewImage.getAttribute('src') &&
    previewImage.getAttribute('src').trim() !== ''
) {
    previewImage.style.display = 'block';

    uploadZone.classList.add('has-image');
}

/* Open file picker */

uploadZone.addEventListener('click', () => {
    fileInput.click();
});

uploadZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInput.click();
    }
});

/* Select Image */

fileInput.addEventListener('change', function (e) {

    const file = e.target.files[0];

    if (!file) return;
    newImageSelected = true;

    const reader = new FileReader();

    reader.onload = function (event) {

        cropImage.src = event.target.result;

        cropModal.style.display = 'flex';

        if (cropper) {
            cropper.destroy();
        }

     cropper = new Cropper(cropImage,{
    aspectRatio: 1,
    viewMode: 2,
    dragMode: 'move',
    autoCropArea: 0.9,
    responsive: true,
    restore: false,
    guides: false,
    center: false,
    highlight: false,
    background: false,
    cropBoxMovable: true,
    cropBoxResizable: true,
    movable: true,
    zoomable: true
});
    };

    reader.readAsDataURL(file);
});

/* Apply Crop */

applyCrop.addEventListener('click', function () {

    if (!cropper) return;

    const canvas = cropper.getCroppedCanvas({
        width: 800,
        height: 800,
        imageSmoothingQuality: 'high'
    });

    previewImage.src =
        canvas.toDataURL('image/jpeg', 0.9);

    previewImage.style.display = 'block';

    uploadZone.classList.add('has-image');

  canvas.toBlob(function (blob) {

    const croppedFile = new File(
        [blob],
        'category.jpg',
        {
            type: 'image/jpeg'
        }
    );

    const dataTransfer = new DataTransfer();

    dataTransfer.items.add(croppedFile);

    fileInput.files = dataTransfer.files;

 
}, 'image/jpeg', 0.9);

    cropModal.style.display = 'none';

    cropper.destroy();
    cropper = null;
});

/* Cancel Crop */

cancelCrop.addEventListener('click', function () {

    cropModal.style.display = 'none';

    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
});

/* ==========================================
   DELETE MODAL
========================================== */

const deleteModal =
    document.getElementById('deleteModal');

const deleteForm =
    document.getElementById('deleteForm');

const deleteModalText =
    document.getElementById('deleteModalText');

function openDeleteModal(id, name, url) {

    deleteForm.action = url;

    deleteModalText.textContent =
        `Are you sure you want to delete "${name}"?`;

    deleteModal.style.display = 'flex';
}

function closeDeleteModal() {
    deleteModal.style.display = 'none';
}

window.addEventListener('click', function (e) {

    if (e.target === deleteModal) {
        closeDeleteModal();
    }
});

document.addEventListener('keydown', function (e) {

    if (
        e.key === 'Escape' &&
        deleteModal.style.display === 'flex'
    ) {
        closeDeleteModal();
    }

    if (
        e.key === 'Escape' &&
        cropModal.style.display === 'flex'
    ) {
        cropModal.style.display = 'none';

        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    }
});

/* ==========================================
   CANCEL BUTTON
========================================== */

const btnCancel =
    document.getElementById('btnCancel');

if (btnCancel) {

    btnCancel.addEventListener('click', function () {
        window.history.back();
    });
}

const form = document.getElementById("categoryForm");

const nameInput = document.getElementById("categoryName");
let duplicateName = false;

const offerInput = document.getElementById("offer");


form.addEventListener("submit", async function (e) {
   
    // Clear old errors
    document.getElementById("nameError").textContent = "";
    document.getElementById("offerError").textContent = "";
    document.getElementById("imageError").textContent = "";

    let isValid = true;

    const name = nameInput.value.trim();
    const offer = offerInput.value.trim();

    // Name validation
    if (!name) {
        document.getElementById("nameError").textContent =
            "Category name is required";
        isValid = false;
    }
    else if (!/^[A-Za-z ]+$/.test(name)) {
        document.getElementById("nameError").textContent =
            "Category name must contain only letters";
        isValid = false;
    }

    // Offer validation (optional)
    if (offer !== "") {

        if (isNaN(offer)) {
            document.getElementById("offerError").textContent =
                "Offer must a number";
            isValid = false;
        }
        else {
            const offerValue = Number(offer);

            if (offerValue < 0 || offerValue > 100) {
                document.getElementById("offerError").textContent =
                    "Offer must be between 0 and 100";
                isValid = false;
            }
        }
    }

    // Image validation
    // For edit page: allow existing image
    const hasExistingImage =
        previewImage.src &&
        !previewImage.src.endsWith("/") &&
        previewImage.src !== window.location.href;

    if (!fileInput.files.length && !hasExistingImage) {
        document.getElementById("imageError").textContent =
            "Category image is required";
        isValid = false;
    }
 if (!isValid) {
    e.preventDefault();
    return;
}



});


fileInput.addEventListener("change", () => {
    document.getElementById("imageError").textContent = "";
});

document.addEventListener("DOMContentLoaded", () => {

    const toasts = document.querySelectorAll(".toast");

    toasts.forEach((toast) => {

        const closeBtn = toast.querySelector(".toast-close");

        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                toast.classList.add("hide");
                setTimeout(() => toast.remove(), 400);
            });
        }

        setTimeout(() => {
            toast.classList.add("hide");
            setTimeout(() => toast.remove(), 400);
        }, 3000);

    });

});

