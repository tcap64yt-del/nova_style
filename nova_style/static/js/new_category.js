document.getElementById("categoryForm")
.addEventListener("submit", async function (e) {

    let isValid = true;

    document
        .querySelectorAll(".js-error")
        .forEach(el => el.remove());
    document.getElementById("image-error-container").innerHTML = "";

    function showError(element, message) {

    const error = document.createElement("small");

    error.className = "field-error js-error";

    error.textContent = message;

    if (element.id === "file-input") {

        document
            .getElementById("image-error-container")
            .appendChild(error);

        return;
    }

    const formGroup = element.closest(".form-group");

    if (formGroup) {
        formGroup.appendChild(error);
    } else {
        element.parentNode.appendChild(error);
    }
}

    const categoryName =
        document.getElementById("category-name");

    const imageInput =
        document.getElementById("file-input");

    const offer =
        document.getElementById("offer");

    const value = categoryName.value.trim();

if (!value) {

    showError(categoryName,
        "Category name is required");

    isValid = false;

}
else if (!/^[A-Za-z ]+$/.test(value)) {

    showError(categoryName,
        "Only letters and spaces are allowed");

    isValid = false;

}
else if (value.length < 3) {

    showError(categoryName,
        "Category name must contain at least 3 characters");

    isValid = false;
}
    

    // Offer

    if (offer.value.trim()) {

        const offerValue =
            parseFloat(offer.value);

        if (offerValue < 0) {

            showError(
                offer,
                "Offer cannot be negative"
            );

            isValid = false;
        }

        else if (offerValue > 100) {

            showError(
                offer,
                "Offer must be between 0 and 100"
            );

            isValid = false;
        }
    }

    // Image

    if (!imageInput.files.length) {

        showError(
            imageInput,
            "Category image is required"
        );

        isValid = false;
    }

 if (!isValid) {

    e.preventDefault();

    showToast("Failed.", "error");

    return;
}

// Stop the normal submit
e.preventDefault();

// Check duplicate name
const response = await fetch(
    `${CHECK_CATEGORY_URL}?name=${encodeURIComponent(value)}`
);

const data = await response.json();

console.log(data);

if (data.exists) {

    console.log("Duplicate category");

    showError(categoryName, "Category already exists.");

    showToast("Failed", "error");

    return;
}

console.log("Submitting form");
this.submit();

// No duplicate -> submit form
this.submit();


});
document.addEventListener("DOMContentLoaded", function () {

    const uploadBox = document.getElementById("upload-box");
    const fileInput = document.getElementById("file-input");

    const previewContainer =
        document.getElementById("preview-container");

    const previewImage =
        document.getElementById("preview-image");

    const changeImageBtn =
        document.getElementById("change-image");

    const cropModal =
        document.getElementById("crop-modal");

    const cropImage =
        document.getElementById("crop-image");

    const cropBtn =
        document.getElementById("crop-btn");

    const cancelBtn =
        document.getElementById("cancel-crop");

    let cropper = null;

    /* --------------------------
       OPEN FILE PICKER
    -------------------------- */

    uploadBox.addEventListener("click", function (e) {

        if (e.target.id === "change-image") {
            return;
        }

        fileInput.click();
    });

    changeImageBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        fileInput.click();
    });

    /* --------------------------
       FILE SELECT
    -------------------------- */

    fileInput.addEventListener("change", function (e) {

        const file = e.target.files[0];

        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (event) {

            cropImage.src = event.target.result;

            cropModal.style.display = "flex";

            if (cropper) {
                cropper.destroy();
            }

            cropper = new Cropper(cropImage, {
                aspectRatio: 1,
                viewMode: 1,
                autoCropArea: 1,
                responsive: true,
                movable: true,
                zoomable: true,
                scalable: true,
                rotatable: false
            });
        };

        reader.readAsDataURL(file);
    });

    /* --------------------------
       APPLY CROP
    -------------------------- */

    cropBtn.addEventListener("click", function () {

        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas({
            width: 800,
            height: 800,
            imageSmoothingQuality: "high"
        });

        const previewUrl =
            canvas.toDataURL("image/jpeg", 0.9);

        previewImage.src = previewUrl;

        previewContainer.style.display = "block";

        uploadBox.classList.add("has-image");

        canvas.toBlob(function(blob) {

            const croppedFile = new File(
                [blob],
                "category.jpg",
                {
                    type: "image/jpeg"
                }
            );

            const dataTransfer =
                new DataTransfer();

            dataTransfer.items.add(croppedFile);

            fileInput.files =
                dataTransfer.files;

        }, "image/jpeg", 0.9);

        cropModal.style.display = "none";

        cropper.destroy();
        cropper = null;
    });

    /* --------------------------
       CANCEL CROP
    -------------------------- */

    cancelBtn.addEventListener("click", function () {

    cropModal.style.display = "none";

    fileInput.value = "";

    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
});

    /* --------------------------
       DRAG & DROP
    -------------------------- */

    uploadBox.addEventListener("dragover", function (e) {
        e.preventDefault();
        uploadBox.classList.add("dragover");
    });

    uploadBox.addEventListener("dragleave", function () {
        uploadBox.classList.remove("dragover");
    });

    uploadBox.addEventListener("drop", function (e) {

        e.preventDefault();

        uploadBox.classList.remove("dragover");

        const files = e.dataTransfer.files;

        if (!files.length) return;

        fileInput.files = files;

        fileInput.dispatchEvent(
            new Event("change")
        );
    });

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

function showToast(message, type) {

    let container = document.getElementById("toast-container");

    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    toast.innerHTML = `
        <span>${message}</span>
        <button class="toast-close">&times;</button>
    `;

    container.appendChild(toast);

    toast.querySelector(".toast-close").onclick = () => {
        toast.remove();
    };

    setTimeout(() => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}