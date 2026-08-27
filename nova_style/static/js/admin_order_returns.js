document.addEventListener('DOMContentLoaded', () => {

    // Mobile sidebar
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

        document.addEventListener('click', (e) => {

            const isMobile = window.innerWidth < 1025;
            const clickedInsideSidebar = sidebar.contains(e.target);
            const clickedToggle = menuToggle.contains(e.target);

            if (
                isMobile &&
                sidebar.classList.contains('mobile-open') &&
                !clickedInsideSidebar &&
                !clickedToggle
            ) {
                closeSidebar();
            }

        });

        sidebar.querySelectorAll('a, button').forEach((el) => {

            el.addEventListener('click', () => {

                if (window.innerWidth < 1025) {
                    closeSidebar();
                }

            });

        });

        window.addEventListener('resize', () => {

            if (window.innerWidth >= 1025) {
                closeSidebar();
            }

        });

    }


    // =====================================================
    // STATUS FILTER
    // =====================================================

    const tabs = document.querySelectorAll('.status-tab');

    tabs.forEach((tab) => {

        tab.addEventListener('click', function () {

            const status = this.dataset.status;

            const url = new URL(window.location.href);

            if (status === 'all') {

                url.searchParams.delete('status');

            } else {

                url.searchParams.set('status', status);

            }

            url.searchParams.delete('page');

            window.location.href = url.toString();

        });

    });


    // =====================================================
    // DATE FILTER
    // =====================================================

    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');


    function applyDateFilter() {

        const url = new URL(window.location.href);


        if (startDate.value) {

            url.searchParams.set(
                'start_date',
                startDate.value
            );

        } else {

            url.searchParams.delete('start_date');

        }


        if (endDate.value) {

            url.searchParams.set(
                'end_date',
                endDate.value
            );

        } else {

            url.searchParams.delete('end_date');

        }


        url.searchParams.delete('page');

        window.location.href = url.toString();

    }


    if (startDate) {

        startDate.addEventListener(
            'change',
            applyDateFilter
        );

    }


    if (endDate) {

        endDate.addEventListener(
            'change',
            applyDateFilter
        );

    }

});