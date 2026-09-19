
document.getElementById("product-form").addEventListener("submit", async function (e) {

 document.querySelectorAll(".media-file-input").forEach(input => {

        if (input.files.length === 0) {
            input.disabled = true;
        } else {
            input.disabled = false;
        }

    });
    let isValid = true;

    // ... your existing code continues here
    document.querySelectorAll(".js-error").forEach(el => el.remove());

   function showError(element, message) {
    const error = document.createElement("small");
    error.className = "field-error js-error";
    error.textContent = message;

    const formGroup = element.closest(".form-group");

    if (formGroup) {
        formGroup.appendChild(error);
    } else {
        element.parentNode.appendChild(error);
    }
}

    const productName =
        document.querySelector('[name="product_name"]');

    const productValue =
        productName.value.trim();

    if (!productValue) {
        showError(productName, "Product name is required");
        isValid = false;
    }
    else if (!/^[A-Za-z ]+$/.test(productValue)) {
        showError(productName,
            "Only letters  are allowed");
        isValid = false;
    }
    else if (productValue.length < 3) {
        showError(productName,
            "Product name must contain at least 3 characters");
        isValid = false;
    }
    

 
    const description =
        document.querySelector('[name="description"]');

    const descValue =
        description.value.trim();

    if (!descValue) {
        showError(description, "Description is required");
        isValid = false;
    }
    else if (descValue.length < 15) {
        showError(description,
            "Description must contain at least 15 characters");
        isValid = false;
    }

 
    const category =
        document.querySelector('[name="category"]');

    if (!category.value) {
        showError(category,
            "Please select a category");
        isValid = false;
    }

    const showOnList =
        document.querySelector('[name="show_on_list"]');

    if (!["yes", "no"].includes(showOnList.value)) {
        showError(showOnList,
            "Please select Yes or No");
        isValid = false;
    }

    const seenVariants = new Set();

    document.querySelectorAll(".variant-item-row")
        .forEach((variantRow) => {

            const price =
                variantRow.querySelector('[name="price[]"]');

            const stock =
                variantRow.querySelector('[name="stock[]"]');

            const size =
                variantRow.querySelector('[name="size[]"]');

            const color =
                variantRow.querySelector('[name="color[]"]');

            const offer =
                variantRow.querySelector('[name="offer[]"]');

            const startDate =
                variantRow.querySelector('[name="start_date[]"]');

            const endDate =
                variantRow.querySelector('[name="end_date[]"]');

            const gallery =
                variantRow.querySelector(".media-gallery-grid");

            const fileInput =
                variantRow.querySelector(".media-file-input");


            if (!price.value.trim()) {
                showError(price,
                    "Price is required");
                isValid = false;
            }
            else if (parseFloat(price.value) <= 0) {
                showError(price,
                    "Price must postive number");
                isValid = false;
            }


            if (!stock.value.trim()) {
                showError(stock,
                    "Stock is required");
                isValid = false;
            }
            else if (parseInt(stock.value) < 0) {
                showError(stock,"Stock must  postive");
                isValid = false;
            }


            if (!size.value.trim()) {
                showError(size,
                    "Size is required");
                isValid = false;
            }


            if (!color.value.trim()) {
                showError(color,
                    "Color is required");
                isValid = false;
            }


            const key =
                `${size.value}_${color.value}`;

            if (seenVariants.has(key)) {
                showError(color,
                    "This size and color combination already exists");
                isValid = false;
            }

            seenVariants.add(key);


            if (
                offer.value &&
                parseFloat(offer.value) > 0
            ) {

                if (!startDate.value) {
                    showError(startDate,
                        "Start date is required");
                    isValid = false;
                }

                if (!endDate.value) {
                    showError(endDate,
                        "End date is required");
                    isValid = false;
                }

                if (
                    startDate.value &&
                    endDate.value &&
                    new Date(startDate.value) >
                    new Date(endDate.value)
                ) {
                    showError(endDate,
                        "End date must be after start date");
                    isValid = false;
                }
            }

         

            const existingImages =
                gallery.querySelectorAll(
                    '.media-item-box img'
                ).length;

            const uploadedImages =
                fileInput.files.length;

            const totalImages =
                existingImages + uploadedImages;

            if (totalImages < 3) {

                showError(
                    gallery,
                    "Upload at least 3 images"
                );

                isValid = false;
            }

        });


    const totalVariants =
        document.querySelectorAll(
            ".variant-item-row"
        ).length;

    if (totalVariants === 0) {

        alert("At least one variant is required");

        isValid = false;
    }


if (!isValid) {
    e.preventDefault();

    showToast("Failed.", "error");

    const firstError = document.querySelector(".js-error");

    if (firstError) {
        firstError.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }

    return;
}



});
document.getElementById("btn-add-variant")
.addEventListener("click", function () {

    const container =
        document.getElementById(
            "variant-items-container"
        );

    const firstVariant =
        container.querySelector(
            ".variant-item-row"
        );

    const newVariant =
        firstVariant.cloneNode(true);

    const variantIndex =
        container.querySelectorAll(
            ".variant-item-row"
        ).length;

    newVariant.querySelectorAll("input")
    .forEach(input => {

        if (input.type === "file") {

            input.value = "";

            input.name =
                `images_${variantIndex}[]`;

        } else {

            input.value = "";
        }

    });

    newVariant.querySelectorAll("select")
    .forEach(select => {

        select.selectedIndex = 0;

    });

    const variantId =
        newVariant.querySelector(
            ".variant-id"
        );

    if (variantId) {
        variantId.value = "";
    }

    const gallery =
        newVariant.querySelector(
            ".media-gallery-grid"
        );

    gallery
        .querySelectorAll(".media-item-box")
        .forEach(item => item.remove());

    const removeBtn =
        newVariant.querySelector(
            ".btn-remove-variant"
        );

    if (removeBtn) {
        removeBtn.style.display = "block";
    }

container.prepend(newVariant);

    updateRemoveButtons();
});

document.addEventListener(
    "click",
    function (e) {

        const btn =
            e.target.closest(
                ".btn-remove-variant"
            );

        if (!btn) return;

        const variant =
            btn.closest(
                ".variant-item-row"
            );

        const variantId =
            variant.querySelector(
                ".variant-id"
            );

        if (
            variantId &&
            variantId.value
        ) {

            const hidden =
                document.getElementById(
                    "deleted_variant_ids"
                );

            if (hidden.value) {
    hidden.value += "," + variantId.value;
} else {
    hidden.value = variantId.value;
}
        }

        variant.remove();

        updateRemoveButtons();
    }
);

document.addEventListener(
    "click",
    function (e) {

        const btn =
            e.target.closest(
                ".btn-delete-image"
            );

        if (!btn) return;

        const imageId =
            btn.dataset.imageId;

        if (imageId) {

            const hidden =
                document.getElementById(
                    "deleted_image_ids"
                );

            if (hidden.value) {
    hidden.value += "," + imageId;
} else {
    hidden.value = imageId;
}
        }

        btn.closest(
            ".media-item-box"
        ).remove();
    }
);
let cropper = null;
let currentGallery = null;
let currentInput = null;
let selectedFiles = [];
let currentFileIndex = 0;

document.addEventListener("click", function(e){

    const uploadBox =
        e.target.closest(".media-upload-box");

    if(!uploadBox) return;

    const input =
        uploadBox.querySelector(".media-file-input");

    if(input){
        input.click();
    }

});
function openCropper(file){

    const reader = new FileReader();

    reader.onload = function(event){

        const modal =
            document.getElementById("cropModal");

        const image =
            document.getElementById("cropImage");

        image.src = event.target.result;

        modal.style.display = "flex";

        if(cropper){
            cropper.destroy();
        }

        cropper = new Cropper(image,{
            aspectRatio:1,
            viewMode:2
        });
    };

    reader.readAsDataURL(file);
}



document.addEventListener("change", function(e) {

    const input = e.target;

    if (!input.classList.contains("media-file-input")) {
        return;
    }

    if (!input.files.length) {
        return;
    }

    // Only NEWLY selected files are stored here
    currentInput = input;

    currentGallery = input
        .closest(".media-gallery-section")
        .querySelector(".media-gallery-grid");

    selectedFiles = Array.from(input.files);

    currentFileIndex = 0;

    openCropper(selectedFiles[currentFileIndex]);
});


document
.getElementById("cropBtn")
.addEventListener("click", function () {

    if (!cropper) return;

    const canvas = cropper.getCroppedCanvas({
        width: 800,
        height: 800
    });

    canvas.toBlob(function (blob) {

        const croppedFile = new File(
            [blob],
            `cropped_${Date.now()}.jpg`,
            {
                type: "image/jpeg"
            }
        );

        // Create image box
        const imageBox = document.createElement("div");

        imageBox.className = "media-item-box";

        imageBox.innerHTML = `
            <img
                src="${URL.createObjectURL(croppedFile)}"
                class="preview-image"
            >

            <button
                type="button"
                class="btn-delete-image">
                ✕
            </button>
        `;

        imageBox.croppedFile = croppedFile;

        // Add cropped image to gallery
        currentGallery.appendChild(imageBox);

        // IMPORTANT:
        // Move to next selected image
        currentFileIndex++;

        if (currentFileIndex < selectedFiles.length) {

            // Destroy current cropper
            cropper.destroy();
            cropper = null;

            // Open next image
            openCropper(
                selectedFiles[currentFileIndex]
            );

        } else {

            // All selected images are finished
            const dt = new DataTransfer();

            currentGallery
                .querySelectorAll(".media-item-box")
                .forEach(box => {

                    if (box.croppedFile) {
                        dt.items.add(box.croppedFile);
                    }

                });

            // Put all cropped files into input
            currentInput.files = dt.files;

            currentInput.dataset.newImages = "true";
            currentInput.disabled = false;

            // Close modal
            document
                .getElementById("cropModal")
                .style.display = "none";

            cropper.destroy();
            cropper = null;

            // Reset
            selectedFiles = [];
            currentFileIndex = 0;
        }

    }, "image/jpeg");

});

function updateRemoveButtons() {
    const variants = document.querySelectorAll(".variant-item-row");
    const removeBtns = document.querySelectorAll(".btn-remove-variant");

    if (variants.length <= 1) {
        removeBtns.forEach(btn => {
            btn.style.display = "none";
        });
    } else {
        removeBtns.forEach(btn => {
            btn.style.display = "block";
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateRemoveButtons();
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
/* =========================================================
   CROP CANCEL
========================================================= */

function closeCropper() {

    const modal = document.getElementById("cropModal");

    if (cropper) {
        cropper.destroy();
        cropper = null;
    }

    if (modal) {
        modal.style.display = "none";
    }

    // Reset current crop state
    currentGallery = null;
    currentInput = null;
    selectedFiles = [];
    currentFileIndex = 0;
}


/* Top X button */
document
    .getElementById("cancelCropBtn")
    ?.addEventListener("click", function () {

        closeCropper();

    });


/* Bottom Cancel button */
document
    .getElementById("cancelCropBtn2")
    ?.addEventListener("click", function () {

        closeCropper();

    });