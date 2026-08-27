document.addEventListener("DOMContentLoaded", function () {


    /* =========================================================
       ELEMENTS
    ========================================================= */

    const mainContent =
        document.querySelector(".main-content");

    const listView =
        document.getElementById("listViewContainer");

    const detailsView =
        document.getElementById("detailsViewContainer");


    const backButton =
        document.getElementById("backToOrdersBtn");


    const editButton =
        document.getElementById("detailsEditOrderBtn");


    const modal =
        document.getElementById("editOrderModal");


    const cancelModalButton =
        document.getElementById("cancelModalBtn");


    const modalOverlay =
        document.querySelector(".confirm-modal__overlay");


    const searchInput =
        document.getElementById("searchInput");


    const searchButton =
        document.getElementById("searchButton");


    const clearButton =
        document.getElementById("clearButton");


    const statusDropdown =
        document.getElementById("statusDropdown");


    const statusFilterContainer =
        document.querySelector(".status-filter-container");


    const statusItems =
        document.querySelectorAll(".status-item");


    const selectedStatus =
        document.getElementById("selected-status");


    const ordersTableBody =
        document.getElementById("ordersTableBody");


    const emptyState =
        document.getElementById("emptyState");


    /* =========================================================
       DEFAULT VIEW
    ========================================================= */

    if (mainContent) {

        mainContent.classList.add("view-details");

    }


    if (detailsView) {

        detailsView.style.display = "block";

    }


    if (listView) {

        listView.style.display = "none";

    }


    /* =========================================================
       VIEW FUNCTIONS
    ========================================================= */

    function showDetailsView() {

        if (!listView || !detailsView) {
            return;
        }


        listView.style.display = "none";

        detailsView.style.display = "block";


        if (mainContent) {

            mainContent.classList.remove("view-list");

            mainContent.classList.add("view-details");

        }


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    function showListView() {

        if (!listView || !detailsView) {
            return;
        }


        detailsView.style.display = "none";

        listView.style.display = "block";


        if (mainContent) {

            mainContent.classList.remove("view-details");

            mainContent.classList.add("view-list");

        }


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    /* =========================================================
       BACK TO ORDERS
    ========================================================= */

    if (backButton) {

        backButton.addEventListener(
            "click",
            function () {

                showListView();

            }
        );

    }


    /* =========================================================
       EDIT ORDER MODAL
    ========================================================= */

    if (editButton && modal) {

        editButton.addEventListener(
            "click",
            function () {

                modal.classList.add("is-open");

                document.body.style.overflow = "hidden";

            }
        );

    }


    /* =========================================================
       CLOSE MODAL
    ========================================================= */

    function closeModal() {

        if (!modal) {
            return;
        }


        modal.classList.remove("is-open");

        document.body.style.overflow = "";

    }


    if (cancelModalButton) {

        cancelModalButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                closeModal();

            }
        );

    }


    if (modalOverlay) {

        modalOverlay.addEventListener(
            "click",
            function () {

                closeModal();

            }
        );

    }


    /* =========================================================
       ESCAPE KEY
    ========================================================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                modal.classList.contains("is-open")
            ) {

                closeModal();

            }

        }
    );


    /* =========================================================
       STATUS DROPDOWN
    ========================================================= */

    if (statusDropdown && statusFilterContainer) {

        statusDropdown.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();


                const isActive =
                    statusFilterContainer.classList.contains(
                        "active"
                    );


                statusFilterContainer.classList.toggle(
                    "active"
                );


                statusDropdown.setAttribute(
                    "aria-expanded",
                    String(!isActive)
                );

            }
        );

    }


    /* =========================================================
       STATUS FILTER ITEMS
    ========================================================= */

    statusItems.forEach(function (item) {

        item.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                const status =
                    item.dataset.status;


                const label =
                    item.textContent.trim();


                if (selectedStatus) {

                    selectedStatus.textContent =
                        label;

                }


                statusItems.forEach(
                    function (statusItem) {

                        statusItem.classList.remove(
                            "active"
                        );

                    }
                );


                item.classList.add("active");


                if (statusFilterContainer) {

                    statusFilterContainer.classList.remove(
                        "active"
                    );

                }


                if (statusDropdown) {

                    statusDropdown.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }


                filterOrders(status);

            }
        );

    });


    /* =========================================================
       CLOSE STATUS MENU OUTSIDE
    ========================================================= */

    document.addEventListener(
        "click",
        function (event) {

            if (
                statusFilterContainer &&
                !statusFilterContainer.contains(
                    event.target
                )
            ) {

                statusFilterContainer.classList.remove(
                    "active"
                );


                if (statusDropdown) {

                    statusDropdown.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }

        }
    );


    /* =========================================================
       SEARCH
    ========================================================= */

    function performSearch() {

        if (!searchInput) {
            return;
        }


        const searchValue =
            searchInput.value.trim().toLowerCase();


        if (clearButton) {

            if (searchValue.length > 0) {

                clearButton.classList.add("show");

            } else {

                clearButton.classList.remove("show");

            }

        }


        filterOrders(
            getCurrentStatus(),
            searchValue
        );

    }


    if (searchButton) {

        searchButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                performSearch();

            }
        );

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                performSearch();

            }
        );

    }


    /* =========================================================
       CLEAR SEARCH
    ========================================================= */

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            function () {

                if (searchInput) {

                    searchInput.value = "";

                }


                clearButton.classList.remove(
                    "show"
                );


                filterOrders(
                    getCurrentStatus(),
                    ""
                );


                if (searchInput) {

                    searchInput.focus();

                }

            }
        );

    }


    /* =========================================================
       CURRENT STATUS
    ========================================================= */

    function getCurrentStatus() {

        const activeStatus =
            document.querySelector(
                ".status-item.active"
            );


        if (!activeStatus) {

            return "all";

        }


        return activeStatus.dataset.status || "all";

    }


    /* =========================================================
       FILTER ORDERS
    ========================================================= */

    function filterOrders(
        status = "all",
        search = ""
    ) {

        if (!ordersTableBody) {
            return;
        }


        const rows =
            ordersTableBody.querySelectorAll(
                "tr"
            );


        let visibleRows = 0;


        rows.forEach(function (row) {

            const rowStatus =
                row.dataset.status || "";


            const rowText =
                row.textContent
                    .toLowerCase();


            const statusMatch =
                status === "all" ||
                rowStatus === status;


            const searchMatch =
                search === "" ||
                rowText.includes(search);


            if (
                statusMatch &&
                searchMatch
            ) {

                row.style.display = "";

                visibleRows++;

            } else {

                row.style.display = "none";

            }

        });


        if (emptyState) {

            if (visibleRows === 0) {

                emptyState.classList.add("show");

            } else {

                emptyState.classList.remove(
                    "show"
                );

            }

        }

    }


    /* =========================================================
       ORDER ROW CLICK
    ========================================================= */

    if (ordersTableBody) {

        ordersTableBody.addEventListener(
            "click",
            function (event) {

                const row =
                    event.target.closest(
                        "tr"
                    );


                if (!row) {
                    return;
                }


                /*
                 * Don't open details if the user
                 * clicked an action button.
                 */

                if (
                    event.target.closest(
                        ".btn-action"
                    )
                ) {

                    return;

                }


                showDetailsView();

            }
        );

    }


    /* =========================================================
       RETURN BUTTON
    ========================================================= */

    const returnsButton =
        document.getElementById(
            "returnsBtn"
        );


    if (returnsButton) {

        returnsButton.addEventListener(
            "click",
            function () {

                /*
                 * Keep current design.
                 * Add return-page URL here later
                 * if you have one.
                 */

            }
        );

    }


    /* =========================================================
       INITIAL SEARCH / FILTER
    ========================================================= */

    filterOrders(
        "all",
        ""
    );

});