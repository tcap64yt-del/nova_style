from django.urls import path,include
from . import views
urlpatterns = [
    path('list/',views.product_list,name="product_list"),
    path('details/<int:variant_id>/',views.product_details,name="product_details"),
    path('add-cart/',views.add_to_cart,name="add_to_cart"), 

]