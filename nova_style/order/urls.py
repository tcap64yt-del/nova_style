from django.urls import path

from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/<int:variant_id>/", views.checkout, name="buy_now_checkout"),
    path("success/<int:order_id>/", views.success, name="success"),
    path("details/<int:order_id>/", views.order_details, name="order_details"),
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("cancel-product/<int:item_id>/", views.cancel_product, name="cancel_product"),
    path("order-return/<int:order_id>/", views.order_return, name="order_return"),
    path("product-return/<int:item_id>/", views.return_product, name="return_product"),
    path(
        "invoice/<int:order_id>/",
        views.download_invoice,
        name="download_invoice",
    ),
    path(
        "checkout/verify-razorpay/",
        views.verify_razorpay_payment,
        name="verify_razorpay_payment",
    ),
    path(
        "checkout/razorpay-payment-failed/",
        views.razorpay_payment_failed,
        name="razorpay_payment_failed",
    ),
    path("payment-failed/<int:order_id>/", views.payment_failed, name="payment_failed"),
    path("retry-payment/<int:order_id>/", views.retry_payment, name="retry_payment"),
    path("checkout/apply-coupon/", views.apply_coupon, name="apply_coupon"),
]
