from django.urls import path,include
from . import views

urlpatterns = [
   path('login/',views.admin_login,name='admin_login'),
   path('user-management/',views.user_managment,name='user_management'),
   path("admin/user-management/block/<int:user_id>/", views.block_user, name="block_user"),
   path("admin/user-management/unblock/<int:user_id>/", views.unblock_user, name="unblock_user"),

]