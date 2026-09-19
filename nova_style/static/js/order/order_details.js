document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("cancelModal");
    const form = document.getElementById("cancelForm");
    const quantitySelect = document.getElementById("cancelQuantity");

    document.querySelectorAll(".btn-cancel-product").forEach(button => {

        button.addEventListener("click", function (e) {

            e.preventDefault();

            form.action = this.dataset.url;

            const availableQty = Number(this.dataset.quantity);

            quantitySelect.innerHTML = "";

            for (let i = 1; i <= availableQty; i++) {
                quantitySelect.innerHTML += `
                    <option value="${i}">${i}</option>
                `;
            }

            modal.classList.add("show");
        });

    });

    document.querySelector(".close-modal").addEventListener("click", function () {
        modal.classList.remove("show");
    });

    modal.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.classList.remove("show");
        }
    });

});

const orderModal = document.getElementById("orderCancelModal");
const openOrderModal = document.getElementById("openOrderCancelModal");
const closeOrderModal = document.querySelector(".close-order-modal");

if (openOrderModal && orderModal) {
    openOrderModal.addEventListener("click", function (e) {
        e.preventDefault();
        orderModal.classList.add("show");
    });
}

if (closeOrderModal && orderModal) {
    closeOrderModal.addEventListener("click", function () {
        orderModal.classList.remove("show");
    });

    orderModal.addEventListener("click", function (e) {
        if (e.target === orderModal) {
            orderModal.classList.remove("show");
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {

    const returnModal = document.getElementById("returnOrderModal");
    const openReturnBtn = document.getElementById("openReturnOrderModal");
    const closeReturnBtn = document.querySelector(".close-return-modal");

    if (openReturnBtn) {
        openReturnBtn.onclick = function (e) {
            e.preventDefault();
            returnModal.classList.add("show");
        };
    }

    if (closeReturnBtn) {
        closeReturnBtn.onclick = function () {
            returnModal.classList.remove("show");
        };
    }

    if (returnModal) {
        returnModal.onclick = function (e) {
            if (e.target === returnModal) {
                returnModal.classList.remove("show");
            }
        };
    }

});


const returnModal = document.getElementById("returnProductModal");

document.querySelectorAll(".btn-return-product").forEach(btn => {
    btn.addEventListener("click", function(e) {
        e.preventDefault();

        document.getElementById("returnProductForm").action = this.dataset.url;

        document.getElementById("returnProductName").textContent = this.dataset.name;
        document.getElementById("returnProductQty").textContent = this.dataset.qty;
        document.getElementById("returnProductPrice").textContent = this.dataset.price;

        const select = document.getElementById("returnQuantity");
        select.innerHTML = "";

        for (let i = 1; i <= Number(this.dataset.qty); i++) {
            select.innerHTML += `<option value="${i}">${i}</option>`;
        }

        returnModal.style.display = "flex";
    });
});

document.addEventListener("DOMContentLoaded", function () {

    const payAgainButton =
        document.getElementById("payAgainButton");

    if (!payAgainButton) return;

    payAgainButton.addEventListener("click", async function () {

        if (payAgainButton.disabled) return;

        const originalText = payAgainButton.innerHTML;

        payAgainButton.disabled = true;
        payAgainButton.innerHTML = "Preparing Payment...";

        let paymentCompleted = false;

        try {

            // Create NEW Razorpay retry order
            const response = await fetch(
                payAgainButton.dataset.retryUrl,
                {
                    method: "GET",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                }
            );

            const data = await response.json();

            if (data.status !== "razorpay") {
                throw new Error(
                    data.message || "Unable to start payment."
                );
            }


            // ============================
            // RAZORPAY OPTIONS
            // ============================

            const options = {

                key: data.razorpay_key,

                amount: data.amount,

                currency: "INR",

                name: "NOVA STYLE",

                description: "Order Payment",

                order_id: data.razorpay_order_id,


                // ============================
                // SUCCESS
                // ============================

                handler: async function (razorpayResponse) {

                    paymentCompleted = true;

                    try {

                        const verifyResponse = await fetch(
                            payAgainButton.dataset.verifyUrl,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type": "application/json",
                                    "X-CSRFToken":
                                        getCookie("csrftoken")
                                },

                                body: JSON.stringify({

                                    order_id: data.order_id,

                                    razorpay_payment_id:
                                        razorpayResponse
                                            .razorpay_payment_id,

                                    razorpay_order_id:
                                        razorpayResponse
                                            .razorpay_order_id,

                                    razorpay_signature:
                                        razorpayResponse
                                            .razorpay_signature
                                })
                            }
                        );

                        const result =
                            await verifyResponse.json();


                        // PAYMENT SUCCESS
                        if (result.status === "success") {

                            window.location.href =
                                result.redirect_url ||
                                payAgainButton.dataset.successUrl;

                            return;
                        }


                        // VERIFICATION FAILED
                        window.location.href =
                            payAgainButton.dataset.failedPageUrl;

                    } catch (error) {

                        console.error(
                            "Verification error:",
                            error
                        );

                        window.location.href =
                            payAgainButton.dataset.failedPageUrl;
                    }
                },


                // ============================
                // CLOSE RAZORPAY
                // ============================

                modal: {

                    ondismiss: function () {

                        if (paymentCompleted) {
                            return;
                        }

                        // User only closed Razorpay.
                        // Stay on Order Details.
                        payAgainButton.disabled = false;
                        payAgainButton.innerHTML =
                            originalText;
                    }
                }
            };


            const razorpay =
                new Razorpay(options);


            // ============================
            // PAYMENT FAILED
            // ============================

            razorpay.on(
                "payment.failed",
                async function () {

                    try {

                        const failedResponse =
                            await fetch(
                                payAgainButton.dataset.failedUrl,
                                {
                                    method: "POST",

                                    headers: {
                                        "Content-Type":
                                            "application/json",

                                        "X-CSRFToken":
                                            getCookie("csrftoken")
                                    },

                                    body: JSON.stringify({

                                        order_id:
                                            data.order_id,

                                        razorpay_order_id:
                                            data.razorpay_order_id
                                    })
                                }
                            );

                        const result =
                            await failedResponse.json();


                        // Go to existing failed page
                        window.location.href =
                            result.redirect_url ||
                            payAgainButton.dataset.failedPageUrl;

                    } catch (error) {

                        console.error(
                            "Payment failed error:",
                            error
                        );

                        // Still go to failed page
                        window.location.href =
                            payAgainButton.dataset.failedPageUrl;
                    }
                }
            );


            // Open Razorpay
            razorpay.open();

        } catch (error) {

            console.error(
                "Razorpay retry error:",
                error
            );

            payAgainButton.disabled = false;
            payAgainButton.innerHTML = originalText;
        }
    });
});


// ============================
// CSRF COOKIE
// ============================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies =
            document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (
                cookie.substring(
                    0,
                    name.length + 1
                ) === name + "="
            ) {

                cookieValue = decodeURIComponent(
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
