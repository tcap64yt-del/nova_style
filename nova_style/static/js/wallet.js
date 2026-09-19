document.addEventListener("DOMContentLoaded", function () {

    // ========================================
    // ELEMENTS
    // ========================================

    const modal = document.getElementById("topupModal");
    const openButton = document.getElementById("openTopupModal");
    const closeButton = document.getElementById("closeTopupModal");
    const topupForm = document.getElementById("topupForm");
    const continueButton = document.getElementById("topupContinue");
    const errorElement = document.getElementById("topupError");

    if (
        !modal ||
        !openButton ||
        !closeButton ||
        !topupForm ||
        !continueButton ||
        !errorElement
    ) {
        console.error("Wallet top-up elements not found.");
        return;
    }


    // ========================================
    // DJANGO URLS
    // ========================================

    const createUrl = topupForm.dataset.createUrl;
    const verifyUrl = topupForm.dataset.verifyUrl;
    const failedUrl = topupForm.dataset.failedUrl;

    console.log("Create URL:", createUrl);
    console.log("Verify URL:", verifyUrl);
    console.log("Failed URL:", failedUrl);


    // ========================================
    // OPEN MODAL
    // ========================================

    openButton.addEventListener("click", function () {

        errorElement.textContent = "";

        modal.classList.add("active");

        document.body.style.overflow = "hidden";

    });


    // ========================================
    // CLOSE MODAL
    // ========================================

    closeButton.addEventListener("click", function () {

        closeTopupModal();

    });


    function closeTopupModal() {

        modal.classList.remove("active");

        document.body.style.overflow = "";

    }


    // ========================================
    // CLICK OUTSIDE MODAL
    // ========================================

    modal.addEventListener("click", function (event) {

        if (event.target === modal) {

            closeTopupModal();

        }

    });


    // ========================================
    // ESCAPE KEY
    // ========================================

    document.addEventListener("keydown", function (event) {

        if (
            event.key === "Escape" &&
            modal.classList.contains("active")
        ) {

            closeTopupModal();

        }

    });


    // ========================================
    // SUBMIT TOP UP
    // ========================================

    topupForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        errorElement.textContent = "";


        // ------------------------------------
        // GET SELECTED AMOUNT
        // ------------------------------------

        const selectedAmount = document.querySelector(
            'input[name="amount"]:checked'
        );


        if (!selectedAmount) {

            errorElement.textContent =
                "Please select an amount.";

            return;

        }


        const amount = Number(selectedAmount.value);


        // ------------------------------------
        // VALIDATE AMOUNT
        // ------------------------------------

        const allowedAmounts = [
            100,
            500,
            1000,
            2000
        ];


        if (!allowedAmounts.includes(amount)) {

            errorElement.textContent =
                "Invalid amount.";

            return;

        }


        // ------------------------------------
        // DISABLE BUTTON
        // ------------------------------------

        continueButton.disabled = true;

        continueButton.textContent =
            "Creating Payment...";


        try {

            // ========================================
            // CREATE RAZORPAY ORDER
            // ========================================

            const response = await fetch(createUrl, {

                method: "POST",

                credentials: "same-origin",

                headers: {

                    "Content-Type":
                        "application/json",

                    "X-CSRFToken":
                        getCookie("csrftoken"),

                    "X-Requested-With":
                        "XMLHttpRequest"

                },

                body: JSON.stringify({

                    amount: amount

                })

            });


            // ------------------------------------
            // CHECK RESPONSE TYPE
            // ------------------------------------

            const contentType =
                response.headers.get("content-type") || "";


            if (!contentType.includes("application/json")) {

                const html = await response.text();

                console.error(
                    "Server returned non-JSON response:",
                    html
                );

                throw new Error(
                    `Server returned ${response.status}. Please check Django URL configuration.`
                );

            }


            const data = await response.json();


            console.log(
                "Create topup response:",
                data
            );


            // ------------------------------------
            // CHECK CREATE RESPONSE
            // ------------------------------------

            if (
                !response.ok ||
                data.status !== "success"
            ) {

                throw new Error(
                    data.message ||
                    "Unable to create payment."
                );

            }


            // ========================================
            // CLOSE CUSTOM MODAL
            // ========================================

            closeTopupModal();


            // ========================================
            // RAZORPAY OPTIONS
            // ========================================

            const options = {

                key:
                    data.razorpay_key,

                amount:
                    data.amount,

                currency:
                    "INR",

                name:
                    "Nova Style",

                description:
                    "Wallet Top Up",

                order_id:
                    data.razorpay_order_id,


                prefill: {

                    name:
                        data.customer_name || "",

                    email:
                        data.customer_email || ""

                },


                theme: {

                    color:
                        "#111111"

                },


                // ========================================
                // PAYMENT SUCCESS
                // ========================================

                handler: async function (paymentResponse) {

                    console.log(
                        "Payment success:",
                        paymentResponse
                    );


                    continueButton.disabled = true;

                    continueButton.textContent =
                        "Verifying Payment...";


                    await verifyWalletPayment(
                        paymentResponse,
                        data.topup_id
                    );

                },


                // ========================================
                // RAZORPAY CLOSED
                // ========================================

                modal: {

                    ondismiss: async function () {

                        console.log(
                            "Razorpay closed."
                        );


                        await markTopupFailed(
                            data.topup_id
                        );


                        // Reload so FAILED
                        // transaction appears

                        window.location.reload();

                    }

                }

            };


            // ========================================
            // CREATE RAZORPAY INSTANCE
            // ========================================

            const razorpay =
                new Razorpay(options);


            // ========================================
            // PAYMENT FAILED
            // ========================================

            razorpay.on(
                "payment.failed",
                async function (response) {

                    console.log(
                        "Payment failed:",
                        response
                    );


                    await markTopupFailed(
                        data.topup_id
                    );


                    alert(
                        "Payment failed. Your wallet was not credited."
                    );


                    window.location.reload();

                }
            );


            // ========================================
            // OPEN RAZORPAY
            // ========================================

            razorpay.open();


        } catch (error) {

            console.error(
                "Top-up error:",
                error
            );


            errorElement.textContent =
                error.message ||
                "Something went wrong.";


            continueButton.disabled =
                false;


            continueButton.textContent =
                "Continue to Payment";

        }

    });


    // ========================================
    // VERIFY SUCCESSFUL PAYMENT
    // ========================================

    async function verifyWalletPayment(
        paymentResponse,
        topupId
    ) {

        try {

            const response = await fetch(
                verifyUrl,
                {

                    method: "POST",

                    credentials:
                        "same-origin",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            getCookie("csrftoken"),

                        "X-Requested-With":
                            "XMLHttpRequest"

                    },


                    body: JSON.stringify({

                        topup_id:
                            topupId,

                        razorpay_payment_id:
                            paymentResponse
                                .razorpay_payment_id,

                        razorpay_order_id:
                            paymentResponse
                                .razorpay_order_id,

                        razorpay_signature:
                            paymentResponse
                                .razorpay_signature

                    })

                }
            );


            // ------------------------------------
            // CHECK RESPONSE TYPE
            // ------------------------------------

            const contentType =
                response.headers.get("content-type") || "";


            if (!contentType.includes("application/json")) {

                const html = await response.text();

                console.error(
                    "Verification returned non-JSON:",
                    html
                );

                throw new Error(
                    `Verification server error: ${response.status}`
                );

            }


            const data =
                await response.json();


            console.log(
                "Verification response:",
                data
            );


            // ========================================
            // SUCCESS
            // ========================================

            if (
                response.ok &&
                data.status === "success"
            ) {

                alert(
                    "Wallet credited successfully!"
                );


                window.location.reload();

                return;

            }


            // ========================================
            // VERIFICATION FAILED
            // ========================================

            alert(
                data.message ||
                "Payment verification failed."
            );


            continueButton.disabled =
                false;


            continueButton.textContent =
                "Continue to Payment";


        } catch (error) {

            console.error(
                "Verification error:",
                error
            );


            alert(
                "Unable to verify payment. Please contact support."
            );


            continueButton.disabled =
                false;


            continueButton.textContent =
                "Continue to Payment";

        }

    }


    // ========================================
    // MARK TOP UP AS FAILED
    // ========================================

    async function markTopupFailed(
        topupId
    ) {

        try {

            const response = await fetch(
                failedUrl,
                {

                    method: "POST",

                    credentials:
                        "same-origin",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            getCookie("csrftoken"),

                        "X-Requested-With":
                            "XMLHttpRequest"

                    },


                    body: JSON.stringify({

                        topup_id:
                            topupId

                    })

                }
            );


            const contentType =
                response.headers.get("content-type") || "";


            if (!contentType.includes("application/json")) {

                const text =
                    await response.text();

                console.error(
                    "Failed endpoint returned non-JSON:",
                    text
                );

                return null;

            }


            const data =
                await response.json();


            console.log(
                "Failed topup response:",
                data
            );


            return data;


        } catch (error) {

            console.error(
                "Failed payment request error:",
                error
            );

            return null;

        }

    }


    // ========================================
    // CSRF COOKIE
    // ========================================

    function getCookie(name) {

        let cookieValue = null;


        if (
            document.cookie &&
            document.cookie !== ""
        ) {

            const cookies =
                document.cookie.split(";");


            for (
                let cookie of cookies
            ) {

                cookie =
                    cookie.trim();


                if (
                    cookie.substring(
                        0,
                        name.length + 1
                    ) ===
                    name + "="
                ) {

                    cookieValue =
                        decodeURIComponent(
                            cookie.substring(
                                name.length + 1
                            )
                        );

                    break;

                }

            }

        }


        return cookieValue;

    }

});