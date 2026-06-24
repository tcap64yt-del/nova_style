const categoryForm = document.getElementById('categoryForm');

categoryForm.addEventListener('submit', function (e) {

    const categoryName =
        document.getElementById('categoryName').value.trim();

    const offer =
        document.getElementById('offer').value.trim();

    // Category name validation
    if (categoryName === '') {
        e.preventDefault();
        alert('Category name is required');
        return;
    }

    if (categoryName.length < 3) {
        e.preventDefault();
        alert('Category name must contain at least 3 characters');
        return;
    }

    // Only letters and spaces
    const nameRegex = /^[A-Za-z\s]+$/;

    if (!nameRegex.test(categoryName)) {
        e.preventDefault();
        alert('Category name can contain only letters and spaces');
        return;
    }

    // Offer validation
    if (offer !== '') {

        const offerValue = Number(offer);

        if (isNaN(offerValue)) {
            e.preventDefault();
            alert('Offer must be a number');
            return;
        }

        if (offerValue < 0 || offerValue > 100) {
            e.preventDefault();
            alert('Offer must be between 0 and 100');
            return;
        }
    }

    // Image validation (optional)
    const imageFile = fileInput.files[0];

    if (imageFile) {

        const allowedTypes = [
            'image/jpeg',
            'image/png',
            'image/webp'
        ];

        if (!allowedTypes.includes(imageFile.type)) {
            e.preventDefault();
            alert('Only JPG, PNG and WEBP images are allowed');
            return;
        }

        const maxSize = 2 * 1024 * 1024; // 2 MB

        if (imageFile.size > maxSize) {
            e.preventDefault();
            alert('Image size must be less than 2 MB');
            return;
        }
    }
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