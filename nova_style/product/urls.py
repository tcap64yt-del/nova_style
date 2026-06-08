from django.urls import path,include
from . import views
urlpatterns = [
    path('list/',views.product_list,name="product_list"),
    path('details/',views.product_details,name="product_details")
    
]