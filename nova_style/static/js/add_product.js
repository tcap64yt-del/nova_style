document.addEventListener("DOMContentLoaded", () => {

    let cropper = null;
    let currentGallery = null;
    let currentInput = null;

    let selectedFiles = [];
    let currentFileIndex = 0;

    // -------------------------
    // Hide first remove button
    // -------------------------
    const firstRemoveBtn =
        document.querySelector(".variant-item-row .btn-remove-variant");

    if (firstRemoveBtn) {
        firstRemoveBtn.style.display = "none";
    }

    // -------------------------
    // Open upload box
    // -------------------------
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

    // -------------------------
    // Open cropper
    // -------------------------
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
                aspectRatio: 1,
                viewMode: 2,
                dragMode: "move",
                autoCropArea: 1,
                responsive: true,
                cropBoxMovable: true,
                cropBoxResizable: true,
                movable: true,
                zoomable: true
            });

        };

        reader.readAsDataURL(file);
    }

    // -------------------------
    // File selected
    // -------------------------
    document.addEventListener("change", function(e){

        const input = e.target;

        if(
            input.type !== "file" ||
            !input.closest(".media-gallery-section")
        ){
            return;
        }

        if(!input.files.length) return;

        currentInput = input;

        currentGallery = input
            .closest(".media-gallery-section")
            .querySelector(".media-gallery-grid");

        selectedFiles = Array.from(input.files);

        currentFileIndex = 0;

        openCropper(selectedFiles[currentFileIndex]);

    });

    // -------------------------
    // Save cropped image
    // -------------------------
    document
        .getElementById("cropBtn")
        .addEventListener("click", function(){

        if(!cropper) return;

        const canvas = cropper.getCroppedCanvas({
            width: 800,
            height: 800
        });

        canvas.toBlob(function(blob){

            const croppedFile = new File(
                [blob],
                `cropped_${Date.now()}.jpg`,
                {
                    type: "image/jpeg"
                }
            );

            const imageBox =
                document.createElement("div");

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

            currentGallery.appendChild(imageBox);

            currentFileIndex++;

            if(currentFileIndex < selectedFiles.length){

                cropper.destroy();

                openCropper(
                    selectedFiles[currentFileIndex]
                );

            }else{

                const dataTransfer =
                    new DataTransfer();

                currentGallery
                    .querySelectorAll(".media-item-box")
                    .forEach(box => {

                    if(box.croppedFile){
                        dataTransfer.items.add(
                            box.croppedFile
                        );
                    }

                });

                currentInput.files =
                    dataTransfer.files;

                closeCropModal();
            }

        }, "image/jpeg", 0.95);

    });

    // -------------------------
    // Close crop modal
    // -------------------------
    function closeCropModal(){

        document
            .getElementById("cropModal")
            .style.display = "none";

        selectedFiles = [];
        currentFileIndex = 0;

        if(cropper){
            cropper.destroy();
            cropper = null;
        }

    }

    document
        .getElementById("cancelCropBtn")
        .addEventListener("click", function(){

        if(currentInput){
            currentInput.value = "";
        }

        closeCropModal();

    });

    document
        .getElementById("cancelCropBtn2")
        .addEventListener("click", function(){

        if(currentInput){
            currentInput.value = "";
        }

        closeCropModal();

    });

    // -------------------------
    // Delete image
    // -------------------------
    document.addEventListener("click", function(e){

        const btn =
            e.target.closest(".btn-delete-image");

        if(!btn) return;

        const imageBox =
            btn.closest(".media-item-box");

        const gallery =
            imageBox.closest(".media-gallery-grid");

        imageBox.remove();

        const fileInput =
            gallery.querySelector(".media-file-input");

        const dataTransfer =
            new DataTransfer();

        gallery
            .querySelectorAll(".media-item-box")
            .forEach(box => {

            if(box.croppedFile){
                dataTransfer.items.add(
                    box.croppedFile
                );
            }

        });

        fileInput.files =
            dataTransfer.files;

    });

    // -------------------------
    // Add Variant
    // -------------------------
    document
        .getElementById("btn-add-variant")
        .addEventListener("click", function(){

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

        newVariant
            .querySelectorAll("input")
            .forEach(input => {

            if(input.type === "file"){

                input.value = "";

                input.name =
                    `images_${variantIndex}[]`;

            }else if(
                input.type === "text" ||
                input.type === "number" ||
                input.type === "date"
            ){

                input.value = "";

            }

        });

        newVariant
            .querySelectorAll("select")
            .forEach(select => {

            select.selectedIndex = 0;

        });

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

        removeBtn.style.display = "block";

        container.appendChild(newVariant);

    });

    // -------------------------
    // Remove Variant
    // -------------------------
    document.addEventListener("click", function(e){

        const btn =
            e.target.closest(
                ".btn-remove-variant"
            );

        if(!btn) return;

        const container =
            document.getElementById(
                "variant-items-container"
            );

        if(
            container.querySelectorAll(
                ".variant-item-row"
            ).length === 1
        ){
            return;
        }

        btn
            .closest(".variant-item-row")
            .remove();

    });

    // -------------------------
    // Sort images
    // -------------------------
    document
        .querySelectorAll(".media-gallery-grid")
        .forEach(gallery => {

        new Sortable(gallery,{
            animation:150
        });

    });

});

// =====================================
// FRONTEND VALIDATION
// =====================================

document.getElementById("product-form").addEventListener("submit", function(e){

    let isValid = true;

    // remove old frontend errors
    document.querySelectorAll(".js-error").forEach(el => el.remove());

    function showError(element, message){
        const error = document.createElement("small");
        error.className = "field-error js-error";
        error.textContent = message;
        element.parentNode.appendChild(error);
    }

    // Product Name
    const productName =
        document.querySelector('[name="product_name"]');

    const productValue =
        productName.value.trim();

    if(!productValue){
        showError(productName,"Product name is required");
        isValid = false;
    }
    else if(!/^[A-Za-z ]+$/.test(productValue)){
        showError(productName,
            "Only letters are allowed");
        isValid = false;
    }
    else if(productValue.length < 3){
        showError(productName,
            "Product name must contain at least 3 characters");
        isValid = false;
    }
    

    const description =
        document.querySelector('[name="description"]');

    if(!description.value.trim()){
        showError(description,"Description is required");
        isValid = false;
    }
    else if(description.value.trim().length < 15){
        showError(description,
            "Description must contain at least 15 characters");
        isValid = false;
    }

    const category =
        document.querySelector('[name="category"]');

    if(!category.value){
        showError(category,"Please select a category");
        isValid = false;
    }

    const showOnList =
        document.querySelector('[name="show_on_list"]');

    if(!["yes","no"].includes(showOnList.value)){
        showError(showOnList,"Please select Yes or No");
        isValid = false;
    }


    document.querySelectorAll(".variant-item-row")
    .forEach((variant)=>{

        const price =
            variant.querySelector('[name="price[]"]');

        const stock =
            variant.querySelector('[name="stock[]"]');

        const size =
            variant.querySelector('[name="size[]"]');

        const color =
            variant.querySelector('[name="color[]"]');

        const offer =
            variant.querySelector('[name="offer[]"]');

        const startDate =
            variant.querySelector('[name="start_date[]"]');

        const endDate =
            variant.querySelector('[name="end_date[]"]');

        const images =
            variant.querySelector('input[type="file"]');

        if(!price.value.trim()){
            showError(price,"Price is required");
            isValid = false;
        }

        if(!stock.value.trim()){
            showError(stock,"Stock is required");
            isValid = false;
        }

        if(!size.value.trim()){
            showError(size,"Size is required");
            isValid = false;
        }

        if(!color.value.trim()){
            showError(color,"Color is required");
            isValid = false;
        }

        if(offer.value &&
           parseFloat(offer.value) > 0){

            if(!startDate.value){
                showError(startDate,
                    "Start date is required");
                isValid = false;
            }

            if(!endDate.value){
                showError(endDate,
                    "End date is required");
                isValid = false;
            }

            if(startDate.value &&
               endDate.value &&
               new Date(startDate.value) >
               new Date(endDate.value)){

                showError(endDate,
                    "End date must be after start date");
                isValid = false;
            }
        }

        if(images.files.length < 3){
            showError(images.closest(".media-gallery-section"),
                "Upload at least 3 images");
            isValid = false;
        }
    });

    if(!isValid){
        e.preventDefault();

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }

});