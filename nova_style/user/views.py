import random
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect,render,get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignupForm,LoginForm,OTPForm,ProfileForm
from .models import EmailOTP,Users,Addresses
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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
            if len(entered_otp) !=6:
                messages.error(request,"Enter 6 digit number")
                return redirect("otp_verify")
            
            if otp_record.is_expired():
                messages.error(request, "OTP expired.")
                return redirect("otp_verify")

            if otp_record.attempts >= MAX_ATTEMPTS:
                messages.error(request, "ttoo many attempts.")
                return redirect("otp_verify")

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
                request.session.pop("signup_data", None)

                messages.success(request, "Account created. Now you can login.")
                return redirect("login")

            otp_record.attempts += 1
            otp_record.save(update_fields=["attempts"])
            messages.error(request, "Invalid OTP.")
            return redirect("otp_verify")
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

        # blocked user
        if request.user.status == False:
            auth_logout(request)
            messages.error(request, "Your account is blocked.")
            return redirect("login")

        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password"]

            user_obj=Users.objects.filter(email=email).first()
            if user_obj and user_obj.status==False:
                messages.error(request, "You are blocked by admin")
                return redirect('login')   

            user = authenticate(request, email=email, password=password)

            if user is None:
                messages.error(request, "Invalid credentials.")
                return redirect("login")
            else:
                auth_login(request, user)
                request.session.set_expiry(3600)
                request.session["user_id"]=user.id
                return redirect("home")
        else:
            messages.error(request,"please fill all fields.")
            return redirect("login")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout(request):
    auth_logout(request)
    return redirect("login")


def home(request):
    details = None

    if request.user.is_authenticated:
        if request.user.status == False:
            auth_logout(request)
            messages.error(request, "Your account is blocked.")
            return redirect("login")
        
        email = request.user.email

        details = Users.objects.filter(email=email).first()

    return render(request, "home.html",{"details":details})

@login_required(login_url='login')
def profile(request):
    user_id=request.user.id
    details=Users.objects.get(id=user_id)



    if request.method == "POST":
        avatar = request.FILES.get("avatar_url")
        if avatar:
            details.avatar_url = avatar

            details.save()  
            messages.success(request,"updated profile") 
            return redirect('profile')
        

        form=ProfileForm(request.POST)

        if form.is_valid():
            new_name = form.cleaned_data["name"].strip()
            new_email = form.cleaned_data["email"].strip().lower()
            current_name = (details.name or "").strip()
            current_email = (details.email or "").strip().lower()

            name_changed=new_name!= current_name
            email_changed =new_email !=current_email

            if not name_changed and not email_changed:
                messages.error(request, "No changes made.")
                return redirect('profile')

            if name_changed and not email_changed:
                details.name = new_name
                details.save(update_fields=["name"])
                messages.success(request, "Name updated successfully.")
                return redirect("profile")
            
            if email_changed:
                if Users.objects.filter(email=new_email).exclude(id=details.id).exists():
                        messages.error(request, "This email is already taken.")
                        return redirect("profile")
            
            
            EmailOTP.objects.filter(email=new_email,is_verified=False).delete()

            otp=generate_otp()
            EmailOTP.objects.update_or_create(
                email=new_email,
                defaults={
                    "otp_code": otp,
                    "expires_at": timezone.now() + timedelta(seconds=OTP_SECONDS),
                    "attempts": 0,
                    "resend_count": 0,
                    "is_verified": False,
                },
            )
            send_mail(
                subject="Your email verification OTP",
                message=f"Your OTP is {otp}. It expires in 1 minute.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[new_email],
            )
            request.session["pending_email_change_user_id"] = details.id
            request.session["pending_email_change_email"] = new_email
            request.session["pending_email_change_name"] = new_name           
            messages.success(request, "OTP sent to your email.")
            return redirect("verify_email_otp")
    else:
        form=ProfileForm(initial={"name": details.name, "email": details.email})
        
    return render(request,'profile.html',{"details":details,"form":form})


@login_required(login_url='login')
def verify_email_otp(request): 
    pending_user_id = request.session.get("pending_email_change_user_id")
    pending_email = request.session.get("pending_email_change_email")    
    otp_record=(EmailOTP.objects.filter(email=pending_email,is_verified=False).order_by('-created_at').first())


    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data["otp"]
            
            if not otp_record:
                messages.error(request, "OTP not found. Please resend it.")
                return redirect("verify_email_otp")

            if otp_record.is_expired():
                messages.error(request, "OTP expired. Please resend it.")
                return redirect("verify_email_otp")

            if otp_record.attempts >= 5:
                messages.error(request, "Too many attempts. Please resend OTP.")
                return redirect("verify_email_otp")

            otp_record.attempts += 1
            otp_record.save(update_fields=["attempts"])

            if entered_otp != otp_record.otp_code:
                otp_record.attempts += 1
                otp_record.save(update_fields=["attempts"])
                messages.error(request, "Invalid OTP.")
                return redirect("verify_email_otp")

            user = Users.objects.get(id=pending_user_id)
            user.email = pending_email
            user.save()

            otp_record.is_verified = True
            otp_record.save(update_fields=["is_verified"])
            otp_record.delete()

            request.session.pop("pending_email_change_user_id", None)
            request.session.pop("pending_email_change_email", None)
            request.session.pop("pending_email_change_name", None)

            request.session["user_id"] = user.id

            messages.success(request, "Email updated successfully.")
            return redirect("profile")
      
    
    return render(request,'email_otp_verification.html', {"pending_email": pending_email})

@login_required (login_url="login")
def change_password(request):
    user_id=request.session.get('user_id')
    details=Users.objects.get(id=user_id)

    if request.method=='POST':
        current_password=request.POST.get('current_password')
        new_password=request.POST.get('new_password')
        confirm_password=request.POST.get('confirm_password')

        if not details.check_password(current_password):
            messages.error(request, "Current password is incorrect")
            return redirect("change_password")
        if new_password!=confirm_password:
            messages.error(request,"passwords dont match")
            return redirect('user_change_password')
        
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return redirect("change_password")
        
        details.set_password(new_password)
        details.save()
        messages.success(request,"password updated")
        return redirect('profile')

    return render(request,'change_password.html',{"details":details})


@login_required(login_url='login')
def address_list(request):
    user_id=request.session.get('user_id')
    details=Users.objects.get(id=user_id)
    all_address=Addresses.objects.filter(user_id=details.id).order_by('-created_at')
    paginator=Paginator(all_address,5)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render(request,'addresses.html',{'page_obj':page_obj,'details':details})


@login_required(login_url='login')
def new_address(request):
    user_id=request.session.get('user_id')
    details=Users.objects.get(id=user_id)

    if request.method =="POST":
        name=request.POST.get('name')
        phone=request.POST.get('phone')
        state=request.POST.get('state')
        district=request.POST.get('district')
        country=request.POST.get('country')
        postal_code=request.POST.get('postal_code')
        address=request.POST.get('address')
        is_default=request.POST.get("is_default")=="on"
        
        try:
            Addresses.objects.create(
                user=request.user,
                name=name,
                address=address,
                phone=phone,
                district=district,
                state=state,
                country=country,
                postal_code=postal_code,
                is_default=is_default
            )
            return redirect("addresses")
        except ValueError as e:
            return render(request, "new_address.html", {"details":details,"error": str(e),"form_data": request.POST})
    return render(request,'new_address.html ',{'details': details})


@login_required(login_url='login')
def edit_address(request,pk):
    user_id=request.session.get('user_id')
    details=Users.objects.get(id=user_id)

    addresses=Addresses.objects.filter(id=pk)
    address=Addresses.objects.get(id=pk)
    if request.method == "POST":
        address.name = request.POST.get("name")
        address.phone = request.POST.get("phone")
        address.state = request.POST.get("state")
        address.district = request.POST.get("district")
        address.country = request.POST.get("country")
        address.postal_code = request.POST.get("postal_code")
        address.address = request.POST.get("address")
        address.is_default = request.POST.get("is_default") == "on"

        try:
            address.save()
            return redirect("addresses")
        except ValueError as e:
            return render(request, "edit_address.html", {
                "address": address,
                "details": details,
                "error": str(e),
                "form_data": request.POST
            })

    return render(request,'edit_address.html',{"addresses":addresses,"details":details})


@login_required(login_url='login')
def set_default_address(request,pk):
    user_id=request.session.get('user_id')
    details=Users.objects.get(id=user_id)

    address = get_object_or_404(Addresses, id=pk, user=request.user)
    if request.method =='POST':
        Addresses.objects.filter(user=request.user).update(is_default=False)
        address.is_default=True
        address.save()

    return redirect('addresses')

@login_required(login_url="login")
def delete_address(request,pk):
    address = get_object_or_404(Addresses, id=pk, user=request.user)
    if request.method == "POST":
        address.delete()
    return redirect('addresses') 