from django.urls import path,include
from . import views
urlpatterns = [
    path('checkout/',views.checkout,name="checkout"), 
    path('success/<int:order_id>/',views.success,name="success"), 
    path('details/<int:order_id>/',views.order_details,name="order_details"), 
    path('cancel-order/<int:order_id>/',views.cancel_order,name="cancel_order"), 
    path('cancel-product/<int:item_id>/',views.cancel_product,name="cancel_product"), 
    path('order-return/<int:order_id>/',views.order_return,name="order_return"), 


]