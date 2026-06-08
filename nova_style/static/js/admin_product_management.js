document.addEventListener('DOMContentLoaded', () => {
  // -----------------------------
  // Mobile sidebar toggle
  // -----------------------------
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');

  if (menuToggle && sidebar) {
    const closeSidebar = () => {
      sidebar.classList.remove('mobile-open');
    };

    const toggleSidebar = (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('mobile-open');
    };

    menuToggle.addEventListener('click', toggleSidebar);

    // Close when clicking outside on mobile
    document.addEventListener('click', (e) => {
      const isMobile = window.innerWidth < 1025;
      const clickedInsideSidebar = sidebar.contains(e.target);
      const clickedToggle = menuToggle.contains(e.target);

      if (isMobile && sidebar.classList.contains('mobile-open') && !clickedInsideSidebar && !clickedToggle) {
        closeSidebar();
      }
    });

    // Close after clicking any sidebar link/button on mobile
    sidebar.querySelectorAll('a, button').forEach((el) => {
      el.addEventListener('click', () => {
        if (window.innerWidth < 1025) {
          closeSidebar();
        }
      });
    });

    // Close sidebar when resizing to desktop
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 1025) {
        closeSidebar();
      }
    });
  }

  // -----------------------------
  // Search bar clear button & live filter
  // -----------------------------
const searchInput = document.getElementById('searchInput');
const clearButton = document.getElementById('clearButton');

if (searchInput && clearButton) {
  const toggleClearButton = () => {
    clearButton.classList.toggle(
      'show',
      searchInput.value.trim() !== ''
    );
  };

  searchInput.addEventListener('input', toggleClearButton);

  clearButton.addEventListener('click', (e) => {
    e.preventDefault();
    searchInput.value = '';
    clearButton.classList.remove('show');
    searchInput.focus();
  });

  toggleClearButton();
}

  // -----------------------------
  // Delete Product modal
  // -----------------------------
  const deleteModal = document.getElementById('deleteModal');
  const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  let rowToDelete = null;

  document.querySelectorAll('.btn-delete').forEach((btn) => {
    btn.addEventListener('click', () => {
      rowToDelete = btn.closest('tr');
      const productName = rowToDelete.querySelector('.product-name').textContent;
      const productColor = rowToDelete.querySelector('.product-color').textContent;
      
      const modalText = document.getElementById('deleteModalText');
      if (modalText) {
        modalText.textContent = `Are you sure you want to delete "${productName} (${productColor})"? This action cannot be undone.`;
      }
      
      if (deleteModal) {
        deleteModal.classList.add('is-open');
        deleteModal.setAttribute('aria-hidden', 'false');
      }
    });
  });

  const closeDeleteModal = () => {
    if (deleteModal) {
      deleteModal.classList.remove('is-open');
      deleteModal.setAttribute('aria-hidden', 'true');
    }
    rowToDelete = null;
  };

  if (cancelDeleteBtn) {
    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
  }

  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', () => {
      if (rowToDelete) {
        // Fade out animation
        rowToDelete.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        rowToDelete.style.opacity = '0';
        rowToDelete.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
          rowToDelete.remove();
          closeDeleteModal();
          
          // Check if table is empty
          const remainingRows = document.querySelectorAll('.products-table tbody tr');
          if (remainingRows.length === 0) {
            const tbody = document.querySelector('.products-table tbody');
            const colsCount = document.querySelectorAll('.products-table th').length;
            const emptyMsgRow = document.createElement('tr');
            emptyMsgRow.innerHTML = `
              <td colspan="${colsCount}" style="text-align: center; padding: 40px; color: var(--color-text-muted); font-weight: 500;">
                No products found in the inventory.
              </td>
            `;
            tbody.appendChild(emptyMsgRow);
          }
        }, 300);
      }
    });
  }

  // -----------------------------
  // Status toggle confirmation modal
  // -----------------------------
  const statusModal = document.getElementById('statusModal');
  const cancelStatusBtn = document.getElementById('cancelStatusBtn');
  const confirmStatusBtn = document.getElementById('confirmStatusBtn');
  let activeToggleCheckbox = null;
  let nextCheckedState = false;

  document.querySelectorAll('.status-toggle-checkbox').forEach((checkbox) => {
    checkbox.addEventListener('click', (e) => {
      // Prevent default checkbox toggle behavior initially until confirmed
      e.preventDefault();
      
      activeToggleCheckbox = checkbox;
      nextCheckedState = !checkbox.checked; // Since we called preventDefault, checked is the original state. Next is the opposite.
      
      const row = checkbox.closest('tr');
      const productName = row.querySelector('.product-name').textContent;
      const statusText = row.querySelector('.status-text');
      
      const modalText = document.getElementById('statusModalText');
      if (modalText) {
        if (nextCheckedState) {
          modalText.textContent = `Are you sure you want to activate status for "${productName}"?`;
        } else {
          modalText.textContent = `Are you sure you want to deactivate status for "${productName}"?`;
        }
      }
      
      if (statusModal) {
        statusModal.classList.add('is-open');
        statusModal.setAttribute('aria-hidden', 'false');
      }
    });
  });

  const closeStatusModal = () => {
    if (statusModal) {
      statusModal.classList.remove('is-open');
      statusModal.setAttribute('aria-hidden', 'true');
    }
    activeToggleCheckbox = null;
  };

  if (cancelStatusBtn) {
    cancelStatusBtn.addEventListener('click', closeStatusModal);
  }

  if (confirmStatusBtn) {
    confirmStatusBtn.addEventListener('click', () => {
      if (activeToggleCheckbox) {
        // Apply checked state change
        activeToggleCheckbox.checked = nextCheckedState;
        
        // Update visual text in row
        const row = activeToggleCheckbox.closest('tr');
        const statusTextElement = row.querySelector('.status-text');
        
        if (statusTextElement) {
          if (nextCheckedState) {
            statusTextElement.textContent = 'Active';
            statusTextElement.classList.add('active');
            statusTextElement.classList.remove('inactive');
          } else {
            statusTextElement.textContent = 'Inactive';
            statusTextElement.classList.add('inactive');
            statusTextElement.classList.remove('active');
          }
        }
        
        closeStatusModal();
      }
    });
  }

  // Escape key closes modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeDeleteModal();
      closeStatusModal();
    }
  });

});
