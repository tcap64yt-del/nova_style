import random
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect,render
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignupForm,LoginForm,OTPForm
from .models import EmailOTP,Users

MAX_ATTEMPTS = 5
MAX_RESENDS = 3
OTP_SECONDS = 60

def generate_otp():
    return f"{random.randint(100000, 999999)}"



def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            request.session["signup_data"] = {
                "name": form.cleaned_data["name"],
                "email": form.cleaned_data["email"].lower(),
                "password": form.cleaned_data["password"],
            }

            email=request.session['signup_data']['email']
            otp = generate_otp()
            EmailOTP.objects.update_or_create(
                email=email,
                defaults={
                    "otp_code": otp,
                    "expires_at": timezone.now() + timedelta(seconds=OTP_SECONDS),
                    "attempts": 0,
                    "resend_count": 0,
                    "is_verified": False,
                },
            )
            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP is {otp}. It expires in 1 minute.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )
            messages.success(request, "OTP sent to your email.")
            return redirect("otp_verify")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})

def verify_otp(request):
    signup_data=request.session.get('signup_data')

    if not signup_data:
        return redirect("signup")
    email=signup_data['email']
    otp_record = EmailOTP.objects.filter(email=email).order_by("-created_at").first()

    if not otp_record:
        messages.error(request, "OTP not found. please resend OTP.")
        return redirect("otp_verify")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data["otp"]

            if otp_record.is_expired():
                messages.error(request, "OTP expired.")
                return redirect("signup")

            if otp_record.attempts >= MAX_ATTEMPTS:
                messages.error(request, "Too many attempts.")
                return redirect("signup")

            if entered_otp == otp_record.otp_code:
                user = Users.objects.create_user(
                    name=signup_data["name"],
                    email=signup_data["email"],
                    password=(signup_data["password"]),
                    status=True,
                )
                otp_record.is_verified=True
                otp_record.save(update_fields=['is_verified'])
                otp_record.delete()
                request.session.pop("pending_signup", None)

                messages.success(request, "Account created. Now you can login.")
                return redirect("login")

            otp_record.attempts += 1
            otp_record.save(update_fields=["attempts"])
            messages.error(request, "Invalid OTP.")
    else:
        form = OTPForm()

    return render(request, "otp_verification.html", {"form": form})


def resend_otp(request):

    signup_data=request.session.get('signup_data')

    if not signup_data:
        return redirect("signup")

    email = signup_data["email"]

    otp_record = EmailOTP.objects.get(email=email)

    if otp_record.resend_count >= MAX_RESENDS:
        messages.error(request, "Resend limit reached.")
        return redirect("signup")

    otp = generate_otp()
    otp_record.otp_code = otp
    otp_record.expires_at = timezone.now() + timedelta(seconds=OTP_SECONDS)
    otp_record.attempts = 0
    otp_record.resend_count += 1
    otp_record.last_sent_at = timezone.now()
    otp_record.save(update_fields=["otp_code", "expires_at", "attempts", "resend_count"])

    send_mail(
        subject="Your new OTP",
        message=f"Your new OTP is {otp}. It expires in 1 minute.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )

    messages.success(request, "OTP resent.")
    return redirect("otp_verify")


def login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)

            if user is None:
                messages.error(request, "Invalid credentials.")
                return render(request, "login.html", {"form": form})
            else:
                auth_login(request, user)
                request.session.set_expiry(3600)
                request.session["user_email"] = user.email
                return redirect("home")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout(request):
    auth_logout(request)
    return redirect("login")


def home(request):
     if not request.user.is_authenticated:
        return redirect("login")

     return render(request, "home.html")

def forgot_password(request):
    return render(request,'forgot_password.html')


def profile(request):
    return render(request,'profile.html')