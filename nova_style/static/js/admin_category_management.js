 lucide.createIcons();

    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function closeSidebar() {
      sidebar.classList.remove('mobile-open');
      sidebarOverlay.classList.remove('active');
      document.body.classList.remove('sidebar-open');
    }

    function toggleSidebar() {
      sidebar.classList.toggle('mobile-open');
      sidebarOverlay.classList.toggle('active');
      document.body.classList.toggle('sidebar-open');
    }

    mobileToggle.addEventListener('click', toggleSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);

    sidebar.querySelectorAll('a, button').forEach((el) => {
      el.addEventListener('click', () => {
        if (window.innerWidth < 1025) closeSidebar();
      });
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth >= 1025) closeSidebar();
    });

    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearButton');

    if (searchInput && clearButton) {
      const toggleClearButton = () => {
        clearButton.style.visibility = searchInput.value.trim() ? 'visible' : 'hidden';
        clearButton.style.opacity = searchInput.value.trim() ? '1' : '0';
        clearButton.style.pointerEvents = searchInput.value.trim() ? 'auto' : 'none';
      };

      searchInput.addEventListener('input', toggleClearButton);
      toggleClearButton();

      clearButton.addEventListener('click', (e) => {
        e.preventDefault();
        searchInput.value = '';
        toggleClearButton();

        const url = new URL(window.location.href);
        url.searchParams.delete('search');
        window.location.href = url.toString();
      });
    }
    const sortDropdown = document.getElementById('sortDropdown');

    if (sortDropdown) {
      sortDropdown.addEventListener('click', function (e) {
        e.stopPropagation();
        sortDropdown.classList.toggle('active');
      });

      document.addEventListener('click', function () {
        sortDropdown.classList.remove('active');
      });
    }




    let selectedToggle = null;
let previousState = false;

const statusModal = document.getElementById('statusModal');
const confirmBtn = document.getElementById('confirmStatusBtn');
const cancelBtn = document.getElementById('cancelStatusBtn');

document.querySelectorAll('.status-toggle-checkbox').forEach(toggle => {

    toggle.addEventListener('click', function(e) {

        e.preventDefault();

        selectedToggle = this;
        previousState = this.checked;

        const newState = !previousState;

        document.getElementById('statusModalText').textContent =
            newState
                ? 'Are you sure you want to deactivate this category?'
                : 'Are you sure you want to activate this category?';

        statusModal.classList.add('is-open');
    });

});

cancelBtn.addEventListener('click', () => {

    statusModal.classList.remove('is-open');

    if (selectedToggle) {
        selectedToggle.checked = previousState;
    }
});

confirmBtn.addEventListener('click', () => {

    const url = selectedToggle.dataset.url;

    window.location.href = url;
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