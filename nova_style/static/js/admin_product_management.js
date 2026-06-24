document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // MOBILE SIDEBAR
    // ==========================================

    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {

        const closeSidebar = () => {
            sidebar.classList.remove('mobile-open');
        };

        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('mobile-open');
        });

        document.addEventListener('click', (e) => {

            const isMobile = window.innerWidth < 1025;

            if (
                isMobile &&
                sidebar.classList.contains('mobile-open') &&
                !sidebar.contains(e.target) &&
                !menuToggle.contains(e.target)
            ) {
                closeSidebar();
            }
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1025) {
                closeSidebar();
            }
        });
    }

    // ==========================================
    // SEARCH
    // ==========================================

    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearButton');

    if (searchInput && clearButton) {

        const toggleClearButton = () => {

            if (searchInput.value.trim()) {
                clearButton.classList.add('show');
            } else {
                clearButton.classList.remove('show');
            }
        };

        searchInput.addEventListener('input', toggleClearButton);

        clearButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = window.location.pathname;
        });

        toggleClearButton();
    }

    // ==========================================
    // SORT DROPDOWN
    // ==========================================

    const sortDropdown = document.getElementById('sortDropdown');

    if (sortDropdown) {

        sortDropdown.addEventListener('click', function (e) {
            e.stopPropagation();
            this.classList.toggle('active');
        });

        document.addEventListener('click', () => {
            sortDropdown.classList.remove('active');
        });
    }

    // ==========================================
    // DELETE MODAL
    // ==========================================

    const deleteModal = document.getElementById('deleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    let rowToDelete = null;

    document.querySelectorAll('.btn-delete').forEach(btn => {

        btn.addEventListener('click', () => {

            rowToDelete = btn.closest('tr');

            if (deleteModal) {
                deleteModal.classList.add('is-open');
                deleteModal.setAttribute('aria-hidden', 'false');
            }
        });
    });

    function closeDeleteModal() {

        if (deleteModal) {
            deleteModal.classList.remove('is-open');
            deleteModal.setAttribute('aria-hidden', 'true');
        }

        rowToDelete = null;
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    }

    if (confirmDeleteBtn) {

        confirmDeleteBtn.addEventListener('click', () => {

            if (!rowToDelete) return;

            rowToDelete.remove();

            closeDeleteModal();
        });
    }

// ==========================================
// STATUS MODAL
// ==========================================

const statusModal = document.getElementById('statusModal');
const statusTitle = document.getElementById('statusModalTitle');
const statusText = document.getElementById('statusModalText');
const cancelStatusBtn = document.getElementById('cancelStatusBtn');
const confirmStatusBtn = document.getElementById('confirmStatusBtn');

let activeToggle = null;
let nextState = false;

document.querySelectorAll('.status-toggle-checkbox').forEach(toggle => {

    toggle.addEventListener('click', function (e) {

        e.preventDefault();

        activeToggle = this;

        const row = this.closest('tr');
        const productName =
            row.querySelector('.product-name').textContent.trim();

        const statusLabel =
            row.querySelector('.status-text');

        const currentStatus =
            statusLabel.textContent.trim();

        // ACTIVE -> ask INACTIVE
        if (currentStatus === 'Active') {

            nextState = false;

            statusTitle.textContent = 'Deactivate Product';

            statusText.textContent =
                `Are you sure you want to inactivate "${productName}"?`;

        }

        // INACTIVE -> ask ACTIVE
        else {

            nextState = true;

            statusTitle.textContent = 'Activate Product';

            statusText.textContent =
                `Are you sure you want to activate "${productName}"?`;
        }

        statusModal.classList.add('is-open');
        statusModal.setAttribute('aria-hidden', 'false');
    });
});

function closeStatusModal() {

    statusModal.classList.remove('is-open');
    statusModal.setAttribute('aria-hidden', 'true');

    activeToggle = null;
}

if (cancelStatusBtn) {
    cancelStatusBtn.addEventListener('click', closeStatusModal);
}

if (confirmStatusBtn) {

    confirmStatusBtn.addEventListener('click', () => {

    if (!activeToggle) return;

    const row = activeToggle.closest('tr');
    const productId = row.dataset.productId;

    if (nextState) {
        window.location.href =
            `/admin/product-management/activate/${productId}/`;
    } else {
        window.location.href =
            `/admin/product-management/deactivate/${productId}/`;
    }
});
}
    // ==========================================
    // MODAL OVERLAY CLOSE
    // ==========================================

    document
        .querySelectorAll('.confirm-modal__overlay')
        .forEach(overlay => {

            overlay.addEventListener('click', () => {

                closeDeleteModal();

                if (statusModal) {
                    closeStatusModal();
                }
            });
        });

    // ==========================================
    // ESC KEY
    // ==========================================

    document.addEventListener('keydown', (e) => {

        if (e.key === 'Escape') {

            closeDeleteModal();

            if (statusModal) {
                closeStatusModal();
            }
        }
    });
});