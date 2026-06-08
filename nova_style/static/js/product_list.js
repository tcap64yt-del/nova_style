/**
 * NOVA STYLE - PREMIUM SHOP INTERACTIVITY AND FILTERS ENGINE
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. INITIALIZE LUCIDE ICONS
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // 2. STATE VARIABLES FOR FILTERS
    let activeCategory = 'WOMAN';
    let selectedSize = 'S';
    let currentMinPrice = 500;
    let currentMaxPrice = 3000;
    let activeSort = 'new';
    
    // Cache DOM Elements
    const productGrid = document.querySelector('.products-grid');
    const productCards = Array.from(document.querySelectorAll('.product-card'));
    const priceMinInput = document.getElementById('priceMin');
    const priceMaxInput = document.getElementById('priceMax');
    const priceMinVal = document.getElementById('priceMinVal');
    const priceMaxVal = document.getElementById('priceMaxVal');
    const sliderTrack = document.getElementById('sliderTrack');
    const sizeButtons = document.querySelectorAll('.size-btn');
    const categoryLinks = document.querySelectorAll('.category-link');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');

    // 3. WISHLIST TOGGLE
    document.body.addEventListener('click', (e) => {
        const wishlistBtn = e.target.closest('.wishlist-btn');
        if (wishlistBtn) {
            e.preventDefault();
            wishlistBtn.classList.toggle('active');
            
            // Re-render lucide icon internally if changed state
            const icon = wishlistBtn.querySelector('i');
            if (wishlistBtn.classList.contains('active')) {
                icon.setAttribute('data-lucide', 'heart');
                // Set filled icon logic if preferred, or rely on custom CSS fill
            } else {
                icon.setAttribute('data-lucide', 'heart');
            }
        }
    });

    // 4. ACCORDION (COLLAPSIBLE FILTER GROUPS)
    const accordionHeaders = document.querySelectorAll('.filter-group-header');
    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const isExpanded = header.getAttribute('aria-expanded') === 'true';
            header.setAttribute('aria-expanded', !isExpanded);
        });
    });

    // 5. DOUBLE PRICE SLIDER CONTROLS
    function updatePriceSlider(e) {
        let minVal = parseInt(priceMinInput.value);
        let maxVal = parseInt(priceMaxInput.value);
        const minGap = 200; // Minimum gap between handles

        if (maxVal - minVal < minGap) {
            if (e && e.target.id === 'priceMin') {
                priceMinInput.value = maxVal - minGap;
                minVal = maxVal - minGap;
            } else {
                priceMaxInput.value = minVal + minGap;
                maxVal = minVal + minGap;
            }
        }

        currentMinPrice = minVal;
        currentMaxPrice = maxVal;

        // Visual track fill
        const minPercent = ((minVal - priceMinInput.min) / (priceMinInput.max - priceMinInput.min)) * 100;
        const maxPercent = ((maxVal - priceMaxInput.min) / (priceMaxInput.max - priceMaxInput.min)) * 100;
        
        sliderTrack.style.background = `linear-gradient(to right, var(--color-border) ${minPercent}%, var(--color-text-primary) ${minPercent}%, var(--color-text-primary) ${maxPercent}%, var(--color-border) ${maxPercent}%)`;
        
        priceMinVal.textContent = `₹${minVal}`;
        priceMaxVal.textContent = `₹${maxVal}`;
    }

    priceMinInput.addEventListener('input', updatePriceSlider);
    priceMaxInput.addEventListener('input', updatePriceSlider);
    
    // Initialize slider position
    updatePriceSlider();

    // 6. SIZE FILTER SELECTION
    sizeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            sizeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedSize = btn.dataset.size;
        });
    });

    // 7. CATEGORY FILTER SELECTION
    categoryLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            categoryLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            activeCategory = link.textContent.trim();
        });
    });

    // 8. MOBILE LAYOUT: SIDEPANEL NAVIGATION & FILTERS
    const menuToggle = document.getElementById('menuToggle');
    const mainNav = document.querySelector('.nav');
    const mobileFilterTrigger = document.getElementById('mobileFilterTrigger');
    const filtersSidebar = document.getElementById('filtersSidebar');
    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');

    // Create dark background overlay for drawer
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);

    // Toggle Mobile Main Navigation
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            mainNav.classList.toggle('active');
            const icon = menuToggle.querySelector('i');
            if (mainNav.classList.contains('active')) {
                icon.setAttribute('data-lucide', 'x');
            } else {
                icon.setAttribute('data-lucide', 'menu');
            }
            lucide.createIcons();
        });
    }

    // Toggle Filters Slide-out
    if (mobileFilterTrigger) {
        mobileFilterTrigger.addEventListener('click', () => {
            filtersSidebar.classList.add('active');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Stop page scrolling
        });
    }

    function closeFilterDrawer() {
        filtersSidebar.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (sidebarCloseBtn) sidebarCloseBtn.addEventListener('click', closeFilterDrawer);
    overlay.addEventListener('click', closeFilterDrawer);

    // 9. CORE FILTER ENGINE (Fade anims + Display calculations)
    function applyFiltering() {
        productGrid.style.opacity = '0.3';
        productGrid.style.transition = 'opacity 0.2s ease';
        
        setTimeout(() => {
            let visibleCount = 0;
            
            productCards.forEach(card => {
                const category = card.dataset.category.toLowerCase();
                const price = parseFloat(card.dataset.price);
                const size = card.dataset.size;
                
                // Match criteria
                const categoryMatch = activeCategory.toLowerCase() === 'woman' ? category === 'woman' || category === 'dresses' || category === 'skirts' || category === 'knitwear' || category === 'outerwear' || category === 'trousers'
                                    : activeCategory.toLowerCase() === 'man' ? category === 'man' || category === 'coats' || category === 'outerwear'
                                    : true; // KIDS / others
                                    
                const priceMatch = price >= currentMinPrice && price <= currentMaxPrice;
                const sizeMatch = selectedSize ? size === selectedSize : true;
                
                if (categoryMatch && priceMatch && sizeMatch) {
                    card.style.display = 'flex';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Re-order if sorted
            applySorting();
            
            // Fade-in grid
            productGrid.style.opacity = '1';
            
            // Close mobile panel if open
            closeFilterDrawer();
        }, 250);
    }

    applyFiltersBtn.addEventListener('click', applyFiltering);

    // 10. FILTERS CLEAR ENGINE
    clearFiltersBtn.addEventListener('click', () => {
        // Reset category state
        categoryLinks.forEach(l => l.classList.remove('active'));
        const defaultCategory = Array.from(categoryLinks).find(l => l.textContent.trim() === 'WOMAN');
        if (defaultCategory) defaultCategory.classList.add('active');
        activeCategory = 'WOMAN';

        // Reset sizes state
        sizeButtons.forEach(b => b.classList.remove('active'));
        const defaultSizeBtn = Array.from(sizeButtons).find(b => b.dataset.size === 'S');
        if (defaultSizeBtn) defaultSizeBtn.classList.add('active');
        selectedSize = 'S';

        // Reset prices state
        priceMinInput.value = 500;
        priceMaxInput.value = 3000;
        updatePriceSlider();

        // Perform visual refiltering
        applyFiltering();
    });

    // 11. SORT DROPDOWN AND LOGIC
    const sortDropdownBtn = document.getElementById('sortDropdownBtn');
    const sortDropdown = document.querySelector('.sort-dropdown');
    const sortOptions = document.querySelectorAll('.sort-option');
    const activeSortLabel = document.querySelector('.active-sort');

    sortDropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        sortDropdown.classList.toggle('open');
    });

    // Close sort dropdown when clicking outside
    document.addEventListener('click', () => {
        sortDropdown.classList.remove('open');
    });

    sortOptions.forEach(option => {
        option.addEventListener('click', () => {
            sortOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
            
            const sortType = option.dataset.sort;
            activeSort = sortType;
            activeSortLabel.textContent = option.textContent.trim();
            
            applySorting();
        });
    });

    function applySorting() {
        const visibleCards = productCards.filter(card => card.style.display !== 'none');
        
        visibleCards.sort((a, b) => {
            const priceA = parseFloat(a.dataset.price);
            const priceB = parseFloat(b.dataset.price);
            
            if (activeSort === 'price-low') {
                return priceA - priceB;
            } else if (activeSort === 'price-high') {
                return priceB - priceA;
            } else if (activeSort === 'popular') {
                // Mock popularity via arbitrary sorting metrics
                return b.dataset.price.length - a.dataset.price.length;
            } else {
                // 'new' (default original placement)
                return productCards.indexOf(a) - productCards.indexOf(b);
            }
        });
        
        // Re-append sorted cards into grid
        visibleCards.forEach(card => {
            productGrid.appendChild(card);
        });
    }
});
