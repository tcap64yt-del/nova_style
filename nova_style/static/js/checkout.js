// Nova Style Checkout - Interactions

document.addEventListener("DOMContentLoaded", () => {

    // -----------------------------
    // DOM Elements
    // -----------------------------
    const form = document.getElementById("checkoutForm");
    const purchaseBtn = document.getElementById("completePurchaseButton");

    const paymentCards = document.querySelectorAll(".payment-method-card");

    const billingSameToggle = document.getElementById("billingSameToggle");
    const billingCheckboxCircle = document.getElementById("billingCheckboxCircle");
    const billingFieldsContainer = document.getElementById("billingFieldsContainer");
    const billingCheckbox = document.getElementById("billing_same");

    // -----------------------------
    // Payment Method Selection
    // -----------------------------
    paymentCards.forEach(card => {

        card.querySelector(".payment-card-header").addEventListener("click", () => {

            paymentCards.forEach(c => {
                c.classList.remove("active");
                c.querySelector(".payment-radio")?.classList.remove("checked");
            });

            card.classList.add("active");
            card.querySelector(".payment-radio")?.classList.add("checked");

        });

    });

    // -----------------------------
    // Billing Toggle
    // -----------------------------
    let billingSame = false;

    billingSameToggle.addEventListener("click", () => {

        billingSame = !billingSame;

        billingCheckbox.checked = billingSame;

        billingCheckboxCircle.classList.toggle("checked", billingSame);
        billingFieldsContainer.classList.toggle("collapsed", billingSame);

    });

    // -----------------------------
    // Validation
    // -----------------------------
    function clearErrors() {

        document.querySelectorAll(".error-message").forEach(el => {
            el.textContent = "";
        });

        document.querySelectorAll(".input-error").forEach(el => {
            el.classList.remove("input-error");
        });

    }

        function showError(id, message) {


            const input = document.getElementById(id);
            const error = document.getElementById(id + "-error");

            if (input)
                input.classList.add("input-error");

            if (error)
                error.textContent = message;

        }

    function required(id, message) {

        const input = document.getElementById(id);

        if (!input.value.trim()) {
            showError(id, message);
            return false;
        }

        return true;
    }

    
function validateAddress(prefix){

    let valid = true;

    function error(field, message){

        valid = false;

        const input = document.getElementById(prefix + "-" + field);
        const error = document.getElementById(prefix + "-" + field + "-error");

        if(input)
            input.classList.add("input-error");

        if(error)
            error.textContent = message;

    }

    const name = document.getElementById(prefix + "-name").value.trim();
    const phone = document.getElementById(prefix + "-phone").value.trim();
    const address = document.getElementById(prefix + "-address").value.trim();
    const district = document.getElementById(prefix + "-district").value.trim();
    const state = document.getElementById(prefix + "-state").value.trim();
    const country = document.getElementById(prefix + "-country").value.trim();
    const postal = document.getElementById(prefix + "-postal").value.trim();

    // Name
    if(!name)
        error("name","Name is required.");
    else if(name.length < 3)
        error("name","Minimum 3 letters.");
    else if(!/^[A-Za-z ]+$/.test(name))
        error("name","Only letters allowed.");

    // Phone
    if(!phone)
        error("phone","Phone is required.");
    else if(!/^[0-9]{10}$/.test(phone))
        error("phone","Phone must 10 digits.");

    // Address
    if(!address)
        error("address","Address is required.");
    else if(address.length < 10)
        error("address","Minimum 10 letters.");

    // District
    if(!district)
        error("district","District is required.");
    else if(district.length < 3)
        error("district","Minimum 3 letters.");
    else if(!/^[A-Za-z ]+$/.test(district))
        error("district","Only letters allowed.");

    // State
    if(!state)
        error("state","State is required.");
    else if(state.length < 3)
        error("state","Minimum 3 letters.");
    else if(!/^[A-Za-z ]+$/.test(state))
        error("state","Only letters allowed.");

    // Country
    if(!country)
        error("country","Country is required.");
    else if(country.length < 3)
        error("country","Minimum 3 letters.");
    else if(!/^[A-Za-z ]+$/.test(country))
        error("country","Only letters allowed.");

    // Postal
    if(!postal)
        error("postal","Postal code is required.");
    else if(!/^[0-9]{6}$/.test(postal))
        error("postal","Postal code must be exactly 6 digits.");

    return valid;
}
form.addEventListener("submit", async function (e) {

    e.preventDefault();

    clearErrors();

    let valid = true;

    valid = validateAddress("shipping");

    if (!billingCheckbox.checked) {
        valid = validateAddress("billing") && valid;
    }

    if (!valid) {
        return;
    }

    const paymentMethod = document.querySelector(
        'input[name="payment_method"]:checked'
    )?.value;


    purchaseBtn.disabled = true;
    purchaseBtn.innerHTML = "Processing...";

    // -----------------------------
    // RAZORPAY
    // -----------------------------

    if (paymentMethod === "razorpay") {

        try {

            const formData = new FormData(form);

            const response = await fetch(
    form.action,
    {
        method: "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    }
);

const contentType =
    response.headers.get("content-type") || "";



// Django returned normal checkout HTML
if (contentType.includes("text/html")) {

    const html = await response.text();

    document.open();
    document.write(html);
    document.close();

    return;
}


// Django returned JSON → Razorpay can open normally
const data = await response.json();

console.log("Django response:", data);

            if (data.status !== "razorpay") {

                console.error(data);

              

                purchaseBtn.disabled = false;
                purchaseBtn.innerHTML = "Complete Purchase";

                return;
            }

            // -----------------------------
            // OPEN RAZORPAY
            // -----------------------------

            const options = {

                key: data.razorpay_key,

                amount: data.amount,

                currency: "INR",

                name: "Nova Style",

                description: "Order Payment",

                order_id: data.razorpay_order_id,

                handler: async function (paymentResponse) {


    const response = await fetch(
        "/order/checkout/verify-razorpay/",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },

            body: JSON.stringify({
                order_id: data.order_id,
                razorpay_payment_id:
                    paymentResponse.razorpay_payment_id,
                razorpay_order_id:
                    paymentResponse.razorpay_order_id,
                razorpay_signature:
                    paymentResponse.razorpay_signature
            })
        }
    );

    const result = await response.json();


    if (result.status === "success") {
        window.location.href = result.redirect_url;
    }
},
                prefill: {
                    name: document.getElementById(
                        "shipping-name"
                    )?.value || "",

                    contact: document.getElementById(
                        "shipping-phone"
                    )?.value || ""
                },

                theme: {
                    color: "#111111"
                },

modal: {
    ondismiss: async function () {

        console.log("Razorpay closed by user");

        try {

            const failedResponse = await fetch(
                "/order/checkout/razorpay-payment-failed/",
                {
                    method: "POST",
                    credentials: "same-origin",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                        "X-Requested-With": "XMLHttpRequest"
                    },

                    body: JSON.stringify({
                        order_id: data.order_id,
                        razorpay_order_id: data.razorpay_order_id
                    })
                }
            );

            const result = await failedResponse.json();

            console.log("Dismiss response:", result);

            if (result.status === "failed" && result.redirect_url) {
                window.location.href = result.redirect_url;
                return;
            }

            purchaseBtn.disabled = false;
            purchaseBtn.innerHTML = "Complete Purchase";

        } catch (error) {

            console.error(
                "Error saving dismissed Razorpay payment:",
                error
            );

            purchaseBtn.disabled = false;
            purchaseBtn.innerHTML = "Complete Purchase";
        }
    }
}
            };

           
            const razorpay = new Razorpay(options);

          razorpay.on("payment.failed", async function (response) {

  
    try {

        const failedResponse = await fetch(
            "/order/checkout/razorpay-payment-failed/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                body: JSON.stringify({
                    order_id: data.order_id,
                    razorpay_order_id: data.razorpay_order_id
                })
            }
        );

       
        const result = await failedResponse.json();

       

        if (result.redirect_url) {
            window.location.href = result.redirect_url;
        }

    } catch (error) {

        console.error(
            "FAILED PAYMENT ERROR:",
            error
        );
    }

});
            razorpay.open();

        } catch (error) {

            console.error(
                "Razorpay error:",
                error
            );

           

            purchaseBtn.disabled = false;
            purchaseBtn.innerHTML =
                "Complete Purchase";
        }

        return;
    }

    form.submit();

});

async function verifyRazorpayPayment(paymentResponse, orderId) {

    try {

        const response = await fetch(
            "/order/checkout/verify-razorpay/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                body: JSON.stringify({
                    order_id: orderId,

                    razorpay_payment_id:
                        paymentResponse.razorpay_payment_id,

                    razorpay_order_id:
                        paymentResponse.razorpay_order_id,

                    razorpay_signature:
                        paymentResponse.razorpay_signature
                })
            }
        );

        const data = await response.json();


        if (data.status === "success") {
            window.location.href = data.redirect_url;
        }

    } catch (error) {

        console.error(
            "Payment verification error:",
            error
        );

    }
}
function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

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

});




const addressModal = document.getElementById("addressModal");
const addAddressModal = document.getElementById("addAddressModal");

const openAddressModal = document.getElementById("openAddressModal");
const closeAddressModal = document.getElementById("closeAddressModal");

const openAddAddress = document.getElementById("openAddAddress");
const openAddAddress2 = document.getElementById("openAddAddress2");
const closeAddAddress = document.getElementById("closeAddAddress");

if(openAddressModal){

    openAddressModal.addEventListener("click",()=>{

        addressModal.classList.add("show");

    });

}

if(closeAddressModal){

    closeAddressModal.addEventListener("click",()=>{

        addressModal.classList.remove("show");

    });

}

if(openAddAddress){

    openAddAddress.addEventListener("click",()=>{

        addAddressModal.classList.add("show");

    });

}

if(openAddAddress2){

    openAddAddress2.addEventListener("click",()=>{

        addressModal.classList.remove("show");

        addAddressModal.classList.add("show");

    });

}

if(closeAddAddress){

    closeAddAddress.addEventListener("click",()=>{

        addAddressModal.classList.remove("show");

    });

}

window.addEventListener("click",(e)=>{

    if(e.target===addressModal){

        addressModal.classList.remove("show");

    }

    if(e.target===addAddressModal){

        addAddressModal.classList.remove("show");

    }

});

document.querySelectorAll(".saved-address").forEach(card=>{

    card.addEventListener("click",function(){

        document.querySelectorAll(".saved-address").forEach(c=>{

            c.classList.remove("active");

        });

        this.classList.add("active");

        document.getElementById("shipping-name").value=this.dataset.name;

        document.getElementById("shipping-phone").value=this.dataset.phone;

        document.getElementById("shipping-address").value=this.dataset.address;

        document.getElementById("shipping-state").value=this.dataset.state;

        document.getElementById("shipping-district").value=this.dataset.district;

        document.getElementById("shipping-country").value=this.dataset.country;

        document.getElementById("shipping-postal").value=this.dataset.postal;

        document.getElementById("selected-name").innerText=this.dataset.name;

        document.getElementById("selected-phone").innerText=this.dataset.phone;

        document.getElementById("selected-address").innerText=this.dataset.address;

        document.getElementById("selected-location").innerText=

            this.dataset.district+", "+this.dataset.state+", "+this.dataset.country+" - "+this.dataset.postal;

        addressModal.classList.remove("show");

    });

});


const addAddressForm = document.getElementById("addAddressForm");

if (addAddressForm) {

    addAddressForm.addEventListener("submit", function (e) {

        let valid = true;

        document.querySelectorAll("#addAddressForm .error-message").forEach(el => {
            el.textContent = "";
        });

        document.querySelectorAll("#addAddressForm input, #addAddressForm textarea").forEach(el => {
            el.classList.remove("input-error");
        });

        function setError(id, message) {

            document.getElementById(id).classList.add("input-error");
            document.getElementById(id + "-error").textContent = message;

            valid = false;

        }

        const name = document.getElementById("address-name").value.trim();
        const phone = document.getElementById("address-phone").value.trim();
        const address = document.getElementById("address-address").value.trim();
        const district = document.getElementById("address-district").value.trim();
        const state = document.getElementById("address-state").value.trim();
        const country = document.getElementById("address-country").value.trim();
        const postal = document.getElementById("address-postal").value.trim();

        if (!name) {

            setError("address-name", "Name is required.");

        } else if (name.length < 3) {

            setError("address-name", "Name must be at least 3 letters.");

        } else if (!/^[A-Za-z ]+$/.test(name)) {

            setError("address-name", "Only letters are allowed.");

        }

        if (!phone) {

            setError("address-phone", "Phone is required.");

        } else if (!/^[0-9]+$/.test(phone)) {

            setError("address-phone", "Phone must contain only numbers.");

        } else if (phone.length !== 10) {

            setError("address-phone", "Phone must  10 digits.");

        }

        // Address
        if (!address) {

            setError("address-address", "Address is required.");

        } else if (address.length < 10) {

            setError("address-address", "Address must  atleast 10 letters.");

        }

        if (!district) {

            setError("address-district", "District is required.");

        } else if (district.length < 3) {

            setError("address-district", "District must atleast 3 letters.");

        } else if (!/^[A-Za-z ]+$/.test(district)) {

            setError("address-district", "Only letters are allowed.");

        }

        // State
        if (!state) {

            setError("address-state", "State is required.");

        } else if (state.length < 3) {

            setError("address-state", "State must atleast 3 letters.");

        } else if (!/^[A-Za-z ]+$/.test(state)) {

            setError("address-state", "Only letters are allowed.");

        }

        // Country
        if (!country) {

            setError("address-country", "Country is required.");

        } else if (country.length < 3) {

            setError("address-country", "Country must atleast 3 letters.");

        } else if (!/^[A-Za-z ]+$/.test(country)) {

            setError("address-country", "Only letters are allowed.");

        }

        // Postal Code
        if (!postal) {

            setError("address-postal", "Postal code is required.");

        } else if (!/^[0-9]+$/.test(postal)) {

            setError("address-postal", "Postal code must contain only numbers.");

        } else if (postal.length !== 6) {

            setError("address-postal", "Postal code must be exactly 6 digits.");

        }

        if (!valid) {
            e.preventDefault();
        }

    });

}



const walletModal = document.getElementById("walletModal");

const walletRadio = document.querySelector(
    'input[name="payment_method"][value="wallet"]'
);

const closeWalletModal = document.getElementById("closeWalletModal");
const cancelWallet = document.getElementById("cancelWallet");
const confirmWallet = document.getElementById("confirmWallet");


// Open wallet modal when Wallet is selected
if (walletRadio) {

    walletRadio.addEventListener("change", function () {

        if (this.checked) {

            walletModal.classList.add("show");

        }

    });

}


// Close modal
if (closeWalletModal) {

    closeWalletModal.addEventListener("click", function () {

        walletModal.classList.remove("show");

    });

}


// Cancel
if (cancelWallet) {

    cancelWallet.addEventListener("click", function () {

        walletModal.classList.remove("show");

        // Return to Razorpay
        const razorpayRadio = document.querySelector(
            'input[name="payment_method"][value="razorpay"]'
        );

        if (razorpayRadio) {
            razorpayRadio.checked = true;
        }

    });

}


// Okay
if (confirmWallet) {

    confirmWallet.addEventListener("click", function () {

 
        walletModal.classList.remove("show");

    });

}


// Close when clicking outside modal
if (walletModal) {

    walletModal.addEventListener("click", function (event) {

        if (event.target === walletModal) {

            walletModal.classList.remove("show");

        }

    });

}



function toggleCoupons() {

    const couponList = document.getElementById("couponList");
    const arrow = document.getElementById("couponArrow");

    couponList.classList.toggle("show");

    if (couponList.classList.contains("show")) {
        arrow.textContent = "▲";
    } else {
        arrow.textContent = "▼";
    }
}