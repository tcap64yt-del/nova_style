import random,re
from django.apps import apps

from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login,update_session_auth_hash
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect,render,get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignupForm,LoginForm,OTPForm,ProfileForm,AvatarForm
from .models import EmailOTP,Users,Addresses,Wishlist,WishlistItem
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from product.models import Category
from order.models import OrderItems,Orders
from django.db.models import Q


ProductVariant = apps.get_model("product", "ProductVariant")
MAX_ATTEMPTS = 5
MAX_RESENDS = 3
OTP_SECONDS = 120

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
                message=f"Your OTP for account verification is {otp}. This code is valid for 2 minutes. Do not share it with anyone.",
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
    remaining_seconds = max(0, int((otp_record.expires_at - timezone.now()).total_seconds()))
    otp_expiry_ms = int(otp_record.expires_at.timestamp() * 1000)

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

    return render(request, "otp_verification.html", {"form": form,"remaining_seconds": remaining_seconds,"otp_expiry_ms": otp_expiry_ms,})


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
                messages.error(request, "Your account is blocked.")
                return redirect('login')   

            user = authenticate(request, email=email, password=password)

            if user is None:
                messages.error(request, "Invalid credentials.")
                return redirect("login")
            else:
                auth_login(request, user)
                request.session.set_expiry(3600)
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
    categories=Category.objects.filter(is_active=True)
    if request.user.is_authenticated:
        if request.user.status == False:
            auth_logout(request)
            messages.error(request, "Your account is blocked.")
            return redirect("login")
        
        email = request.user.email

        details = Users.objects.filter(email=email).first()

    return render(request, "home.html",{"details":details,"categories":categories})

@login_required(login_url='login')
def profile(request):
    details = request.user
    categories=Category.objects.all()
    form = ProfileForm(initial={"name": details.name,"email": details.email})
    avatar_form = AvatarForm()
    if request.method == "POST":
        if "save_avatar" in request.POST:

                avatar_form = AvatarForm(request.POST, request.FILES)

                if avatar_form.is_valid():
                    avatar = avatar_form.cleaned_data["avatar_url"]

                    if avatar:
                        details.avatar_url = avatar
                        details.save(update_fields=["avatar_url", "updated_at"])
                        messages.success(request,"Profile image updated successfully.")
                    else:
                        messages.success(request,"Profile image unchanged.")

                    return redirect("profile")
                else:
                    form = ProfileForm(initial={"name": details.name,"email": details.email})
                    return render(request,"profile.html",{"details": details,"form": form,"avatar_form": avatar_form,"categories": categories,"active_page": "profile","show_search": False,"show_sidebar": True,})

                        
        if "save_profile" in request.POST:
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
            
    return render(request,'profile.html',{"details":details,"form":form,"categories":categories,  "form":form,"active_page":"profile","show_search":False,"show_sidebar": True})


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
    details = request.user

    if request.method=='POST':
        current_password=request.POST.get('current_password')
        new_password=request.POST.get('new_password')
        confirm_password=request.POST.get('confirm_password')
        errors = {}

        if not current_password:
            errors["current_password"] = "Current password is required"

        elif not details.check_password(current_password):
            errors["current_password"] = "Current password is incorrect"

        if not new_password:
            errors["new_password"] = "New password is required"
        elif len(new_password) < 8:
            errors["new_password"] = "Password must be at least 8 characters"
        elif not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password) or not re.search(r'[^A-Za-z0-9\s]', new_password):
            errors["new_password"] = "Password must contain at least one letter, number, and special character."

        if not confirm_password:
            errors["confirm_password"] = "Please confirm your password"
        elif new_password != confirm_password:
            errors["confirm_password"] = "Passwords do not match"

        if errors:
            return render(request, "change_password.html", {"details": details,"errors": errors,})
        details.set_password(new_password)
        details.save()
        update_session_auth_hash(request,details)
        messages.success(request,"password updated")
        return redirect('profile')

    return render(request,'change_password.html',{"details":details})


@login_required(login_url='login')
def address_list(request):
    details=request.user
    search = request.GET.get("search", "").strip()

    all_address = Addresses.objects.filter(
        user=request.user
    )

    if search:
        all_address = all_address.filter(
            name__icontains=search
           
        )

    all_address = all_address.order_by("-created_at")
    paginator=Paginator(all_address,1)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render(request,'addresses.html',{'page_obj':page_obj,'details':details,"active_page": "addresses","show_search": True,"show_sidebar": True})


@login_required(login_url='login')
def new_address(request):
    details=request.user
    
    if request.method =="POST":
        name=request.POST.get('name')
        phone=request.POST.get('phone')
        state=request.POST.get('state')
        district=request.POST.get('district')
        country=request.POST.get('country')
        postal_code=request.POST.get('postal_code')
        address=request.POST.get('address')
        is_default=request.POST.get("is_default")=="on"
        errors={}
        if not name:
            errors["name"] = "Name is required"
        elif len(name) < 3:
            errors["name"] = "Name must be at least 3 characters"
        elif not name.replace(" ", "").isalpha():
            errors["name"] = "Name should contain only letters"

        if not phone:
            errors["phone"] = "Phone number is required"
        elif not phone.isdigit() or len(phone) != 10:
            errors["phone"] = "Enter a valid 10-digit phone number"

        if not postal_code:
            errors["postal_code"] = "PIN code is required"
        elif not postal_code.isdigit() or len(postal_code) != 6:
            errors["postal_code"] = "Enter a valid 6-digit PIN code"

        if not address:
            errors["address"] = "Address is required"

        if not state:
            errors["state"] = "State is required"

        if not district:
            errors["district"] = "District is required"

        if not country:
            errors["country"] = "Country is required"

        if errors:
            return render(request,"new_address.html",{"details": details,"errors": errors,"form_data": request.POST,},)
        Addresses.objects.create(user=request.user,name=name,phone=phone,state=state,district=district,country=country,postal_code=postal_code,address=address,is_default=is_default,)
        messages.success(request, "Address added successfully.")
        return redirect("addresses")
    return render(request,'new_address.html ',{'details': details,"show_sidebar": True})


@login_required(login_url='login')
def edit_address(request,pk):
    details = request.user

    address=get_object_or_404(Addresses,id=pk,user=request.user)
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        state = request.POST.get("state")
        district = request.POST.get("district")
        country = request.POST.get("country")
        postal_code = request.POST.get("postal_code")
        full_address = request.POST.get("address")
        is_default = request.POST.get("is_default") == "on"

        errors = {}

        if not name:
            errors["name"] = "Name is required"
        elif len(name) < 2:
            errors["name"] = "Name  at least 2 characters"
        elif not name.replace(" ", "").isalpha():
            errors["name"] = "Name should contain only letters"

        
        if not phone:
            errors["phone"] = "Phone number is required"
        elif not phone.isdigit() or len(phone) != 10:
            errors["phone"] = "Enter a valid 10-digit phone number"

        if not postal_code:
            errors["postal_code"] = "PIN code is required"
        elif not postal_code.isdigit() or len(postal_code) != 6:
            errors["postal_code"] = "Enter a valid 6-digit PIN code"

        if not full_address:
            errors["address"] = "Address is required"

        
        if not state:
            errors["state"] = "State is required"

        if not district:
            errors["district"] = "District is required"

        if not country:
            errors["country"] = "Country is required"

        if errors:
            return render(request,"edit_address.html",{"address": address,"details": details,"errors": errors,"form_data": request.POST,"show_sidebar": True},)

        address.name = name
        address.phone = phone
        address.state = state
        address.district = district
        address.country = country
        address.postal_code = postal_code
        address.address = full_address

        address.save()
        messages.success(request, "Address updated successfully.")
        return redirect("addresses")

    return render(request,"edit_address.html",{"address": address,"details": details,"show_sidebar": True},)
   

@login_required(login_url='login')
def set_default_address(request,pk):
    user=request.user
    details=Users.objects.get(id=user.id)

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


@login_required(login_url='login')
def wishlist(request):

    profile=request.user
    search = request.GET.get("search", "").strip()

    wishlist=Wishlist.objects.filter(user=profile).first()

    items=[]
    if wishlist:
        WishlistItem.objects.filter(wishlist=wishlist).filter(Q(variant__is_active=False) | Q(variant__product__is_active=False) |Q(variant__product__category__is_active=False)).delete()

        items=WishlistItem.objects.filter(wishlist=wishlist,variant__is_active=True,variant__product__is_active=True,variant__product__category__is_active=True).select_related("variant","variant__product").prefetch_related("variant__images")
        if search:
            items = items.filter(variant__product__name__icontains=search)
    return render(request,"wishlist/wishlist.html",{ "details":profile,"items":items,"serach":search,"active_page": "wishlist","show_search": True,"show_sidebar": True})

@login_required(login_url="login")
def add_to_wishlist(request,variant_id):
    if request.method =="POST":
        variant = ProductVariant.objects.filter(id=variant_id).first()

        if not variant:
            messages.error(request, "Product variant not found.")
        elif not variant.is_active:
            messages.error(request, "This variant is inactive.")
        elif not variant.product.is_active:
            messages.error(request, "This product is inactive.")
        elif not variant.product.category.is_active:
            messages.error(request, "This category is inactive.")
        else:
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

            item, created = WishlistItem.objects.get_or_create(
                wishlist=wishlist,
                variant=variant
            )

            if created:
                messages.success(request, "Added to wishlist.")
            else:
                item.delete()
                messages.success(request, "Removed from wishlist.")
        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
    return redirect("product_list")


@login_required(login_url='login')
def orders(request):
    profile=request.user

    orders=Orders.objects.filter(user=request.user).select_related("user").prefetch_related("addresses","items__variant__product","items__variant__images",).order_by("-created_at")

    search = request.GET.get("search", "").strip()
    if search:
        orders = orders.filter(items__variant__product__name__icontains=search)

    paginator = Paginator(orders, 5 ) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request,"orders.html",{"page_obj": page_obj,"details":profile,    "orders": orders,"active_page": "orders","show_search": True,"show_sidebar": True})


@login_required(login_url='login')
def wallet(request):
    profile=request.user

    return render(request,"wallet/wallet.html",{"show_sidebar": True,"active_page": "wallet","details":profile})