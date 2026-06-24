from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.cart,name="cart"), 
    path("remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("increase/<int:item_id>/", views.increase_quantity, name="increase_quantity"),
    path("decrease/<int:item_id>/", views.decrease_quantity, name="decrease_quantity"),
]