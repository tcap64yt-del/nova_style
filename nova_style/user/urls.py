from django.urls import path,include
from user import views
from django.contrib.auth import views as auth_views
from user.forms import CustomPasswordResetForm

urlpatterns = [
   path("",views.home,name="home"),
   path("signup/",views.signup,name="signup"),
   path("login/",views.login,name="login"),
   path("profile/change-password/", views.change_password, name="user_change_password"),
   path("profile/",views.profile,name="profile"),
   path("logout/", views.logout, name="logout"),

   path("profile/addresses/", views.address_list, name="addresses"),   
   path("profile/wishlist/", views.wishlist, name="wishlist"),   
   path("profile/wishlist/add/<int:variant_id>/", views.add_to_wishlist, name="add_to_wishlist"),   
   path("profile/orders/",views.orders, name="orders"),   
   path("profile/addresses/<int:pk>/", views.delete_address, name="delete_address"),
   path("profile/addresses/set-default/<int:pk>/",views.set_default_address,name="set_default_address"),
   path("profile/addresses/new-address", views.new_address, name="new_address"),
   path("profile/addresses/edit-address/<int:pk>", views.edit_address, name="edit_address"),
   
   path("signup/otp/",views.verify_otp,name="otp_verify"),
   path("signup/otp/resend",views.resend_otp,name="resend_otp"),
   path("profile/email-change/otp/", views.verify_email_otp, name="verify_email_otp"),
   path("profile/email-change/resend/", views.verify_email_otp, name="resend_email_change_otp"),   
   
   path(
        "forgot-password/",
        auth_views.PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
            template_name="registration/forgot_password.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url="/forgot-password/done/",
        ),
        name="password_reset",
    ),
    path(
        "forgot-password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

]
