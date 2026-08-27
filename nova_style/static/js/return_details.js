 document.addEventListener('DOMContentLoaded', () => {
      // Mobile sidebar toggle
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
    });
   const overlay = document.getElementById("modalOverlay");
const approveModal = document.getElementById("approveModal");
const rejectModal = document.getElementById("rejectModal");

function openApproveModal(){

    overlay.style.display = "block";
    approveModal.style.display = "flex";

}

function openRejectModal(){

    overlay.style.display = "block";
    rejectModal.style.display = "flex";

}

function closeModal(){

    overlay.style.display = "none";
    approveModal.style.display = "none";
    rejectModal.style.display = "none";

}

overlay.onclick = closeModal;