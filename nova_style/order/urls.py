from django.urls import path,include
from . import views
urlpatterns = [
    path('checkout/',views.checkout,name="checkout"), 
    path("checkout/<int:variant_id>/", views.checkout, name="buy_now_checkout"),
    path('success/<int:order_id>/',views.success,name="success"), 
    path('details/<int:order_id>/',views.order_details,name="order_details"), 
    path('cancel-order/<int:order_id>/',views.cancel_order,name="cancel_order"), 
    path('cancel-product/<int:item_id>/',views.cancel_product,name="cancel_product"), 
    path('order-return/<int:order_id>/',views.order_return,name="order_return"), 
    path('product-return/<int:item_id>/',views.return_product,name="return_product"), 
    path("invoice/<int:order_id>/",views.download_invoice,name="download_invoice",),
]