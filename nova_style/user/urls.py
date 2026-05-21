from django.urls import path,include
from user import views


urlpatterns = [
   path("",views.home,name="home"),
   path("signup/",views.signup,name="signup"),
   path("forgot-password/",views.forgot_password,name="forgot_password"),
   path("login/",views.login,name="login"),
   path("profile/",views.profile,name="profile"),
   path("logout/", views.logout, name="logout"),
   path("signup/otp/",views.verify_otp,name="otp_verify"),
   path("signup/otp/resend",views.resend_otp,name="resend_otp"),


]