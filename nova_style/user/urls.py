from django.urls import path,include
from user import views
from django.contrib.auth import views as auth_views
from user.forms import CustomPasswordResetForm

urlpatterns = [
   path("",views.home,name="home"),
   path("signup/",views.signup,name="signup"),
   path("login/",views.login,name="login"),
   path("profile/",views.profile,name="profile"),
   path("logout/", views.logout, name="logout"),
   path("profile/addresses/", views.addresses, name="addresses"),
   path("profile/addresses/new-address", views.new_address, name="new-address"),
   path("signup/otp/",views.verify_otp,name="otp_verify"),
   path("signup/otp/resend",views.resend_otp,name="resend_otp"),
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