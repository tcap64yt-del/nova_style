from django.urls import path,include
from . import views

urlpatterns = [
   path('login/',views.admin_login,name='admin_login'),
   path('logout/',views.admin_logout,name='admin_logout'),
   path('user-management/',views.user_management,name='user_management'),
   path('category-management/',views.category_management,name='category_management'),
   path('product-management/',views.product_management,name='product_management'),
   path('product-management/activate/<int:product_id>/',views.activate_product,name='activate_product'),
   path('product-management/deactivate/<int:product_id>/',views.deactivate_product,name='deactivate_product'),
   path('product-management/add-product/',views.add_product,name='add_product'),
   path('product-management/add-product/',views.add_product,name='add_product'),
   path('product-management/edit-product/<int:product_id>',views.edit_product,name='edit_product'),
   path('category-management/new-category/',views.new_category,name='new_category'), 
   path('category-management/edit-category/<int:category_id>',views.edit_category,name='edit_category'), 
   path('category-management/edit-category/status/<int:category_id>',views.category_status,name='category_status'), 
   path("admin/user-management/block/<int:user_id>/", views.block_user, name="block_user"),
   path("admin/user-management/unblock/<int:user_id>/", views.unblock_user, name="unblock_user"),

]