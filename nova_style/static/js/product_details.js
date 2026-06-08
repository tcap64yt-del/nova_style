document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // 2. Vertical Image Gallery and Thumbnail Tracking
    const thumbBtns = document.querySelectorAll('.thumb-btn');
    const galleryImgs = document.querySelectorAll('.gallery-img');

    // Clicking a thumbnail scrolls the corresponding main image into view
    thumbBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = btn.getAttribute('data-target');
            const targetImg = document.getElementById(targetId);
            
            if (targetImg) {
                // Remove active class from all thumbnails
                thumbBtns.forEach(b => b.classList.remove('active'));
                // Add active class to clicked thumbnail
                btn.classList.add('active');
                
                // Scroll to target image
                targetImg.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        });
    });

    // Intersection Observer to update active thumbnail as the user scrolls
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -40% 0px', // Trigger when image is in the center area
        threshold: 0.2
    };

    const galleryObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetId = entry.target.id;
                thumbBtns.forEach(btn => {
                    if (btn.getAttribute('data-target') === targetId) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
            }
        });
    }, observerOptions);

    galleryImgs.forEach(img => {
        galleryObserver.observe(img);
    });

    // 3. Size Selection
    const sizeBtns = document.querySelectorAll('.size-option-btn');
    sizeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            sizeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // 4. Color Selection
    const colorBtns = document.querySelectorAll('.color-option-btn');
    colorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            colorBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Premium micro-interaction: update gallery images based on selected color if mock assets are set up
            // Here, we just highlight selected swatch
        });
    });

    // 5. Save to Wishlist Toggle (Main Product)
    const wishlistBtn = document.getElementById('wishlist-toggle-btn');
    if (wishlistBtn) {
        wishlistBtn.addEventListener('click', () => {
            wishlistBtn.classList.toggle('active');
            const icon = wishlistBtn.querySelector('.heart-icon');
            const text = wishlistBtn.querySelector('span');
            
            if (wishlistBtn.classList.contains('active')) {
                text.textContent = 'Saved to Wishlist';
                if (icon) {
                    icon.setAttribute('fill', 'var(--color-brand-red)');
                    icon.setAttribute('stroke', 'var(--color-brand-red)');
                }
            } else {
                text.textContent = 'Save to Wishlist';
                if (icon) {
                    icon.setAttribute('fill', 'transparent');
                    icon.setAttribute('stroke', 'currentColor');
                }
            }
        });
    }

    // 6. Card Wishlist Toggles (Related Products)
    const cardWishlistBtns = document.querySelectorAll('.card-wishlist-btn');
    cardWishlistBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            btn.classList.toggle('active');
            const svg = btn.querySelector('svg');
            
            if (btn.classList.contains('active')) {
                svg.setAttribute('fill', 'var(--color-brand-red)');
                svg.setAttribute('stroke', 'var(--color-brand-red)');
            } else {
                svg.setAttribute('fill', 'transparent');
                svg.setAttribute('stroke', 'currentColor');
            }
        });
    });

    // 7. Collapsible Description Accordion
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const item = header.closest('.accordion-item');
            const isOpen = item.classList.contains('active');
            
            // Toggle active state
            item.classList.toggle('active');
            header.setAttribute('aria-expanded', !isOpen);
        });
    });

    // 8. Related Products Slider Horizontal Scroll
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const relatedGrid = document.querySelector('.related-grid');

    if (prevBtn && nextBtn && relatedGrid) {
        // Scroll horizontal distance of one card width + gap
        const scrollAmount = 300; 

        prevBtn.addEventListener('click', () => {
            relatedGrid.scrollBy({
                left: -scrollAmount,
                behavior: 'smooth'
            });
        });

        nextBtn.addEventListener('click', () => {
            relatedGrid.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        });

        // Hide/show buttons based on scroll position (optional premium polish)
        relatedGrid.addEventListener('scroll', () => {
            const maxScroll = relatedGrid.scrollWidth - relatedGrid.clientWidth;
            
            // Subtle button opacity feedback
            if (relatedGrid.scrollLeft <= 5) {
                prevBtn.style.opacity = '0.5';
            } else {
                prevBtn.style.opacity = '1';
            }

            if (relatedGrid.scrollLeft >= maxScroll - 5) {
                nextBtn.style.opacity = '0.5';
            } else {
                nextBtn.style.opacity = '1';
            }
        });
        
        // Trigger scroll event once to set initial opacity
        relatedGrid.dispatchEvent(new Event('scroll'));
    }
});
