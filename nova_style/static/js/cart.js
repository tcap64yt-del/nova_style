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



// CSRF Token
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

const csrftoken = getCookie("csrftoken");


// Increase Quantity
document.querySelectorAll(".qty-plus").forEach(button => {

    button.addEventListener("click", function () {

        const id = this.dataset.id;

        fetch(`/cart/increase/${id}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            }
        })
        .then(res => res.json())
.then(data => {

    if (data.success) {

    this.parentElement.querySelector(".qty-val").textContent = data.quantity;

    document.getElementById("subtotal-val").textContent = "₹" + data.subtotal;
    document.getElementById("total-val").textContent = "₹" + data.subtotal;
    document.getElementById("cart-count").textContent = data.cart_count + " Products";

    showToast(data.message, "success");
}
else {
    showToast(data.message, "error");
}

});

    });

});


// Decrease Quantity
document.querySelectorAll(".qty-minus").forEach(button => {

    button.addEventListener("click", function () {

        const id = this.dataset.id;

        fetch(`/cart/decrease/${id}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            }
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {

    this.parentElement.querySelector(".qty-val").textContent = data.quantity;

    document.getElementById("subtotal-val").textContent = "₹" + data.subtotal;
    document.getElementById("total-val").textContent = "₹" + data.subtotal;
    document.getElementById("cart-count").textContent = data.cart_count + " Products";

    showToast(data.message, "success");

} else {
    showToast(data.message, "error");
}
        });

    });

});


// Remove Item
document.querySelectorAll(".remove-btn").forEach(button => {

    button.addEventListener("click", function () {

        const id = this.dataset.id;

        fetch(`/cart/remove/${id}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            }
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {

                document.getElementById("cart-item-" + id).remove();

                document.getElementById("subtotal-val").textContent = "₹" + data.subtotal;
                document.getElementById("total-val").textContent = "₹" + data.subtotal;
                document.getElementById("cart-count").textContent = data.cart_count + " Products";

            }

        });

    });

});

function showToast(message, type = "success") {

    const container = document.getElementById("toast-container") || (() => {
        const div = document.createElement("div");
        div.id = "toast-container";
        document.body.appendChild(div);
        return div;
    })();

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    toast.innerHTML = `
        <span>${message}</span>
        <button class="toast-close">&times;</button>
    `;

    container.appendChild(toast);

    toast.querySelector(".toast-close").onclick = () => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 400);
    };

    setTimeout(() => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}


const checkoutErrors = JSON.parse(
    document.getElementById("checkout-errors").textContent
);

document.getElementById("checkout-link").addEventListener("click", function(e) {

    if (checkoutErrors.length > 0) {
        e.preventDefault();

        document.getElementById("checkout-error").style.display = "block";
    }
});