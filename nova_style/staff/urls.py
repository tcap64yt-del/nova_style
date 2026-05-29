from django.urls import path,include
from . import views
urlpatterns = [
   path('login/',views.admin_login,name='admin_login'),
   path('admin-user-management/',views.admin_user_managment,name='admin_user_ management'),

]