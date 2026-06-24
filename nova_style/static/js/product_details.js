document.addEventListener("DOMContentLoaded", function () {

    // Description toggle
    const trigger = document.querySelector(".accordion-trigger");
    const content = document.querySelector(".accordion-content");

    if (trigger && content) {
        trigger.addEventListener("click", function () {
            if (content.style.display === "none" || content.style.display === "") {
                content.style.display = "block";
            } else {
                content.style.display = "none";
            }
        });
    }

    // Main image + thumbnails
    const mainImage = document.getElementById("mainProductImage");
    const thumbnails = document.querySelectorAll(".thumbnail-btn");

    // Zoom preview
    const zoomContainer = document.querySelector(".main-image-container");
    const zoomPreview = document.getElementById("zoomPreview");

    if (zoomContainer && zoomPreview && mainImage) {

        zoomContainer.addEventListener("mouseenter", () => {

            zoomPreview.style.display = "block";
            zoomPreview.style.backgroundImage = `url(${mainImage.src})`;
            zoomPreview.style.backgroundSize = "250%";
        });

        zoomContainer.addEventListener("mousemove", (e) => {

            const rect = zoomContainer.getBoundingClientRect();

            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;

            zoomPreview.style.backgroundPosition = `${x}% ${y}%`;
        });

        zoomContainer.addEventListener("mouseleave", () => {
            zoomPreview.style.display = "none";
        });
    }

    // Thumbnail click
    thumbnails.forEach((thumb) => {

        thumb.addEventListener("click", function () {

            const img = this.querySelector("img");

            if (img && mainImage) {

                mainImage.src = img.src;

                if (zoomPreview) {
                    zoomPreview.style.backgroundImage = `url(${img.src})`;
                }
            }

            thumbnails.forEach(t => t.classList.remove("active"));
            this.classList.add("active");
        });

    });

});

document.addEventListener("DOMContentLoaded", () => {

    const grid = document.getElementById("relatedGrid");
    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");

    if (grid && nextBtn && prevBtn) {

        nextBtn.addEventListener("click", () => {
            grid.scrollBy({
                left: 280,
                behavior: "smooth"
            });
        });

        prevBtn.addEventListener("click", () => {
            grid.scrollBy({
                left: -280,
                behavior: "smooth"
            });
        });

    }
});


document.addEventListener("DOMContentLoaded", () => {

    const reviewBtn = document.querySelector(".btn-write-review");
    const reviewModal = document.getElementById("reviewModal");
    const cancelBtn = document.querySelector(".review-cancel-btn");

    const stars = document.querySelectorAll(".rating-star");
    const ratingInput = document.getElementById("ratingInput");

    if (reviewBtn) {

        reviewBtn.addEventListener("click", () => {
            reviewModal.classList.add("active");
        });

    }

    if (cancelBtn) {

        cancelBtn.addEventListener("click", () => {
            reviewModal.classList.remove("active");
        });

    }

    if (reviewModal) {

        reviewModal.addEventListener("click", (e) => {

            if (e.target === reviewModal) {
                reviewModal.classList.remove("active");
            }

        });

    }

    stars.forEach((star) => {

        star.addEventListener("click", () => {

            const rating = parseInt(star.dataset.rating);

            ratingInput.value = rating;

            stars.forEach((s) => {
                s.classList.remove("active");
            });

            stars.forEach((s) => {

                if (parseInt(s.dataset.rating) <= rating) {
                    s.classList.add("active");
                }

            });

        });

    });

});