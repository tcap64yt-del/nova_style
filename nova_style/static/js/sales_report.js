document.addEventListener("DOMContentLoaded", () => {

    const clearButton =
        document.getElementById("reportClearButton");

    const exportPdfButton =
        document.getElementById("exportPdfButton");

    const exportExcelButton =
        document.getElementById("exportExcelButton");


    // ==========================================
    // CLEAR SEARCH
    // ==========================================

    if (clearButton) {

        clearButton.addEventListener("click", () => {

            const url = new URL(window.location.href);

            url.searchParams.delete("search");
            url.searchParams.delete("page");

            window.location.href = url.toString();

        });

    }


    // ==========================================
    // EXPORT PDF
    // ==========================================

    if (exportPdfButton) {

        exportPdfButton.addEventListener("click", (event) => {

            event.preventDefault();

            const currentUrl =
                new URL(window.location.href);

            const exportUrl =
                new URL(
                    exportPdfButton.href,
                    window.location.origin
                );

            // Copy current filter + search
            currentUrl.searchParams.forEach((value, key) => {

                // Don't send pagination page
                if (key !== "page") {

                    exportUrl.searchParams.set(
                        key,
                        value
                    );

                }

            });

            // Send to Django
            window.location.href =
                exportUrl.toString();

        });

    }


    // ==========================================
    // EXPORT EXCEL
    // ==========================================

    if (exportExcelButton) {

        exportExcelButton.addEventListener("click", (event) => {

            event.preventDefault();

            const currentUrl =
                new URL(window.location.href);

            const exportUrl =
                new URL(
                    exportExcelButton.href,
                    window.location.origin
                );

            // Copy current filter + search
            currentUrl.searchParams.forEach((value, key) => {

                // Don't send pagination page
                if (key !== "page") {

                    exportUrl.searchParams.set(
                        key,
                        value
                    );

                }

            });

            // Send to Django
            window.location.href =
                exportUrl.toString();

        });

    }

});