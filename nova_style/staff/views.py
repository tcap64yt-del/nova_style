from django.shortcuts import render,redirect,get_object_or_404
from user.models import Users
from product.models import Category,ProductImage,Products,ProductVariant
from django.contrib import messages
from django.contrib.auth import login,authenticate
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout 
from django.core.paginator import Paginator
from product.forms import CategoryForm
import re
from django.db.models import Count,Prefetch

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            return redirect('user_management')
        return redirect('home')
    

    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        admin=authenticate(email=email,password=password)

        if admin:
            if admin.is_staff and admin.is_superuser:
                login(request,admin)
                return redirect("user_management")
        else:
            messages.error(request,"invaild credentials")

    return render(request,'staff/admin_login.html')

@login_required(login_url='admin_login')
def user_management(request):
    sort = request.GET.get('sort', 'all')
    search = request.GET.get('search', '')
    users=Users.objects.all()
    if search:
        users=users.filter(Q(name__icontains=search) |Q(email__icontains=search))

    if sort=='newest':
        users=users.order_by('-created_at')
    elif sort == 'oldest':
        users = users.order_by('created_at')

    paginator=Paginator(users,5)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    total=Users.objects.count()

    return render(request,'staff/admin_user_management.html',{"users":page_obj,"total":total,"sort":sort,"search":search,'page_obj':page_obj})


def block_user(request, user_id):
    user = Users.objects.filter(id=user_id).first()
    if user:
        user.status = False
        user.save(update_fields=["status"])
    
    return redirect('user_management')

def unblock_user(request, user_id):
    user = Users.objects.filter(id=user_id).first()
    user.status = True
    user.save()
    return redirect("user_management")

def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@login_required(login_url='admin_login')
def category_management(request):
    categories = Category.objects.annotate(
        product_count=Count("products")
    )   
    search=request.GET.get('search','')
    sort=request.GET.get("sort","all")
    if search:
        categories=categories.filter(name__icontains=search)
    if sort=="newest":
        categories=categories.order_by("-created_at")

    elif sort=="oldest":
        categories=categories.order_by("created_at")
    paginator=Paginator(categories,5)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    total_categories=Category.objects.filter(is_active=True).count()

    
    return render(request,'staff/admin_category_management.html',{"categories":page_obj,"total_categories":total_categories,'page_obj':page_obj,"search":search,"sort":sort})

@login_required(login_url='admin_login')
def new_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added")
            return redirect("category_management")
    else:
        form = CategoryForm()

    return render(request, "staff/new_category.html", {"form": form})


@login_required(login_url='admin_login')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.name = request.POST.get('categoryName', '').strip()
        category.offer = request.POST.get('offer')

        if request.FILES.get('image'):
            category.image_url = request.FILES['image']

        category.save()
        messages.success(request, "category updated")
        return redirect('category_management')

    return render(request, 'staff/edit_category.html', {"category": category})



@login_required(login_url="admin_login")
def category_status(request,category_id):
    category=get_object_or_404(Category,id=category_id)
    if category.is_active:
        category.is_active=False
    else:
        category.is_active=True
    category.save()
    return redirect("category_management")

@login_required(login_url="admin_login")
def product_management(request):
        products=Products.objects.annotate(count=Count('variants')).prefetch_related("variants")
        return render(request,"staff/admin_product_management.html",{"products":products})

@login_required(login_url='admin_login')
def add_product(request):
    categories=Category.objects.all()
    if request.method=="POST":
        errors={}
        product_name=request.POST.get("product_name","").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category")
        show_on_list = request.POST.get("show_on_list")
        prices = request.POST.getlist("price[]")
        sizes = request.POST.getlist("size[]")
        colors = request.POST.getlist("color[]")
        offer = request.POST.getlist("offer[]")
        start_date = request.POST.getlist("start_date[]")
        end_date = request.POST.getlist("end_date[]")
        stocks = request.POST.getlist("stock[]")
        statuses = request.POST.getlist("status[]")
        if not product_name:
            errors["product_name"] = "product name is required."

        elif len(product_name) < 3:
            errors["product_name"] = "product name must contain atleast 5 characters."

        elif not re.match(r'^[A-Za-z0-9 ]+$', product_name):
            errors["product_name"] = "only letters and numbers are allowed."

        if not description:
            errors["description"] = "description is required."

        elif len(description) < 15:
            errors["description"] = "description must contain at least 15 letters."

        if not category:
            errors["category"] = "please select a category."

        if show_on_list not in ["yes", "no"]:
            errors["show_on_list"] = "please select Yes or No."

        if not prices:
            errors["variant"] = "At least one variant is required."
        elif not (len(prices) == len(sizes) == len(colors) ==len(stocks) == len(offer) == len(start_date) == len(end_date)):
            errors["variant"]="invaild variant data."

        else:
            for i in range(len(prices)):
                variant_images = request.FILES.getlist(f"images_{i}[]")
                if len(variant_images)<3:
                    errors["images"]=f"upload atleast 3 images for variant{i+1}"
                price=prices[i].strip()
                stock=stocks[i].strip()
                size=sizes[i]
                color=colors[i].strip()
                if not price:
                    errors["price"] = f"Price is required for Variant {i+1}"
                    

                elif float(price) <= 0:
                    errors["price"] = f"Price must be greater than 0 for Variant {i+1}"
                    

                if not stock:
                    errors["stock"] = f"Stock is required for Variant {i+1}"

                elif not stock.isdigit():
                    errors["stock"] = f"stock must be a number for Variant {i+1}"

                elif int(stock) < 0:
                    errors["stock"] = f"Stock cannot be negative for Variant {i+1}"
                if not size:
                    errors["size"] = f"Size is required for Variant {i+1}"
                    

                if not color:
                    errors["color"] = f"Color is required for Variant {i+1}"
     
            if errors:
                return render(request,"staff/add_product.html",{"categories":categories,"errors":errors})
            category_obj=get_object_or_404(Category,id=category)

            product=Products.objects.create(name=product_name,description=description,category_id=category_obj.id,is_active=(show_on_list=="yes"))
            for i in range(len(prices)):

                variant=ProductVariant.objects.create(product=product,size=sizes[i],color=colors[i],price=prices[i], offer=offer[i] if offer[i] else 0,start_date=start_date[i] if start_date[i] else None,end_date=end_date[i] if end_date[i] else None,stock=stocks[i],is_active=(statuses[i] == "true"))
                variant_images=request.FILES.getlist(f"images_{i}[]")

                for index,image in enumerate(variant_images):
                    ProductImage.objects.create(variant=variant,image=image,is_primary=(index==0))
            messages.success(request, "Product added successfully.")
            return redirect("add_product")
            
    return render(request,"staff/add_product.html",{"categories":categories})

@login_required(login_url="admin_login")
def edit_product(request,product_id):
    return render(request,"staff/edit_product.html")