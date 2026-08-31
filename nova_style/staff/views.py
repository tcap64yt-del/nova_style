from django.shortcuts import render,redirect,get_object_or_404
from user.models import Users
from product.models import Category,ProductImage,Products,ProductVariant
from django.contrib import messages
from django.contrib.auth import login,authenticate
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout 
from django.core.paginator import Paginator
import re
from decimal import Decimal,InvalidOperation
from django.utils import timezone
from itertools import chain
from operator import attrgetter
from django.db.models import F
from django.db.models import Count,Prefetch
from order.models import Orders,OrderItems,OrderAddress,OrderTrack,OrderReturns,OrderItemReturn,Payment
from django.db.models import Sum
from coupon.models import Coupon


def validate_coupon(data,coupon_id=None):
    errors={}

    code=data.get("code","").strip().upper()
    discount_type=data.get("discount_type","").strip()
    discount_value=data.get("discount_value","").strip()
    min_order_amount=data.get("min_order_amount","").strip()
    max_discount=data.get("max_discount","").strip()
    max_usage = data.get("max_usage", "").strip()
    start_date = data.get("start_date", "").strip()
    end_date = data.get("end_date", "").strip()

    if not code:
        errors['code']="Coupon code is required"
    elif not re.match(r"^[A-Z0-9_-]{3,20}$", code):
        errors["code"] = (
            "Coupon code must contain only uppercase letters, ""numbers, underscore or hyphen.")

    else :
        coupon_query=Coupon.objects.filter(code__iexact=code)
        if  coupon_id:
            coupon_query=coupon_query.exclude(id=coupon_id)
        if coupon_query.exists():
            errors['code']='This coupon code already exists.'
    if discount_type not in ['percentage','fixed']:
            errors['discount_type']='Please select a valid discount type'

    try:
        discount_value=Decimal(discount_value)
        if discount_value<=0:
            errors['discount_value']=('Discount value must greate than zero')
        if (discount_type =="percentage") and discount_value >Decimal("100"):
            errors['discount_value']=('Percentage discount cannot exceed 100%.')
    except (InvalidOperation,ValueError):
        errors['discount_value']=("Enter a valid discount value.")

    try :
        if max_discount:
            max_discount=Decimal(max_discount)
            if max_discount<=0:
                errors['max_discount']=("maximum discount must greater than zero")
        else:
            max_discount=None
    except(InvalidOperation,ValueError):
        errors['max_discount']=("enter a valid maximum discount amount")

    if not max_usage:
        errors['max_usage']="Maximum usage is required."
    elif not re.fullmatch(r"^[1-9]\d*$",max_usage):
        errors["max_usage"]=("Maximum usage must positive number.")
    else:
        max_usage=int(max_usage)
    try:
        if start_date:
            start_date=timezone.datetime.strptime(start_date,"%Y-%m-%d").date()
        else:
            start_date = None
    except ValueError:
        errors['start_date']="invalid start date"

    try:

        if end_date:
            end_date = timezone.datetime.strptime(end_date,"%Y-%m-%d").date()
        else:
            end_date = None

    except ValueError:
        errors["end_date"] = "Invalid end date."


    if start_date and end_date:
        if end_date < start_date:

            errors["end_date"] = ("End date cannot be before start date.")


    cleaned_data = {
        "code": code,
        "discount_type": discount_type,
        "discount_value": discount_value if isinstance(discount_value, Decimal) else None,
        "min_order_amount": min_order_amount,
        "max_discount": max_discount,
        "max_usage": max_usage if isinstance(max_usage, int) else None,
        "start_date": start_date,
        "end_date": end_date,
    }

    return errors, cleaned_data


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

    paginator=Paginator(users,3)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    total=Users.objects.count()

    return render(request,'staff/admin_user_management.html',{"users":page_obj,"total":total,"sort":sort,"search":search,'page_obj':page_obj,"active_page": "admin_user_management",})


def block_user(request, user_id):
    user = Users.objects.filter(id=user_id).first()
    if user:
        user.status = False
        user.save(update_fields=["status"])
        messages.success(request, "user unblocked")
    return redirect('user_management')

def unblock_user(request, user_id):
    user = Users.objects.filter(id=user_id).first()
    user.status = True
    user.save()
    messages.success(request, "user blocked")
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

    
    return render(request,'staff/admin_category_management.html',{"categories":page_obj,"total_categories":total_categories,'page_obj':page_obj,"search":search,"sort":sort,"active_page": "admin_category_management",})

@login_required(login_url='admin_login')
def new_category(request):
    errors={}
    if request.method =="POST":
        name=request.POST.get("name","").strip()
        offer=request.POST.get("offer","").strip()
        image=request.FILES.get("image_url")
        if not name:
            errors["name"]="category name is required"
        if len(name)<3:
            errors["name"]="category name must contain atleast 3 letters"
        if not re.fullmatch(r"[A-Za-z ]+",name):
            errors["name"]="only letters are allowed"
        if Category.objects.filter(name__iexact=name).exists():
            errors['name']="category name already exists."
        offer_value=None
        if offer:
            if not re.fullmatch(r'^\d+(\.\d+)?$', offer):
                errors["offer"] = "Offer must be a positive number."
            else:
                offer_value=float(offer)
                if offer_value<0 or offer_value>100:
                    errors["offer"]="offer must be between 0 and 100."
        if not image:
            errors["image"] = "Category image is required."
        if errors:
            return render(request,"staff/new_category.html",{"errors":errors,"name":name,"offer":offer,})
        Category.objects.create( name=name,offer=offer if request.POST.get("offer") else None,image_url=image,) 
        messages.success(request,"category added successfully.")
        return redirect("category_management")
    return render(request, "staff/new_category.html")


@login_required(login_url='admin_login')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    errors={}
    if request.method == "POST":
        method = request.POST.get("_method", "POST").upper()
        if method != "PATCH":
            return redirect("category_management")
        name = request.POST.get('name', '').strip()
        offer = request.POST.get('offer')

        if not name:
            errors["name"]="Category name is required"
        if len(name)<3:
            errors["name"]="Category name must contain atleast 3 letters"
        if not re.fullmatch(r"[A-Za-z ]+",name):
            errors["name"]="only letters are allowed"
        if Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
            errors['name']="Category name already exists."
        offer_value=None
        if offer:
            if not re.fullmatch(r'^\d+(\.\d+)?$', offer):
                errors["offer"] = "Offer must be a positive number."
            else:
                offer_value=float(offer)
                if offer_value<0 or offer_value>100:
                    errors["offer"]="offer must be between 0 and 100."
        
        uploaded_image = request.FILES.get('image')
        if not uploaded_image and not category.image_url:
            errors["image"] = "Category image is required."
            return render(request, 'staff/edit_category.html', {"category": category})
        if errors:
            return render(request,"staff/edit_category.html",{"category":category,"errors":errors})
        
        category.name = name
        category.offer = offer_value

        if uploaded_image:
            category.image_url = uploaded_image
           
        category.save()

        messages.success(request, "category updated.")
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
    messages.success(request, "category updated.")

    return redirect("category_management")

@login_required(login_url="admin_login")
def product_management(request):
        
        search=request.GET.get("search","").strip()
        sort=request.GET.get("sort","all")
        products=Products.objects.annotate(count=Count('variants')).prefetch_related("variants")


        if search:
            products=products.filter(Q(name__icontains=search) | Q(category__name__icontains=search))

        if sort=="active":
            products=products.filter(is_active=True).order_by("-created_at")
        elif sort =="inactive":
            products=products.filter(is_active=False).order_by("-created_at")
        else:
            products=products.order_by("-created_at")

        paginator=Paginator(products,5)
        page_number=request.GET.get("page")
        page_obj=paginator.get_page(page_number)

        
        return render(request,"staff/admin_product_management.html",{"products":page_obj,"page_obj":page_obj,"search":search,"sort":sort,"active_page":"admin_product_management"})

@login_required(login_url='admin_login')
def add_product(request):
    categories=Category.objects.all()
    errors={}
    if request.method=="POST":
        
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
        
        variants=[]
        variant_count=max(len(prices),len(sizes),len(colors),len(stocks),len(statuses))

        for i in range(variant_count):
            variants.append({"index":i,"price":prices[i] if i < len(prices) else "", "size": sizes[i] if i < len(sizes) else "","color": colors[i] if i < len(colors) else "","stock": stocks[i] if i < len(stocks) else "","offer": offer[i] if i < len(offer) else "","start_date": start_date[i] if i < len(start_date) else "","end_date": end_date[i] if i < len(end_date) else "","status": statuses[i] if i < len(statuses) else "true","errors":{}})

        

        if not product_name:
            errors["product_name"] = "product name is required."

        elif len(product_name) < 3:
            errors["product_name"] = "product name must contain atleast 3 characters."

        elif not re.match(r'^[A-Za-z0-9 ]+$', product_name):
            errors["product_name"] = "only letters and numbers are allowed."

        elif Products.objects.filter(name__iexact=product_name).exists():
            errors["product_name"] = "alread name exists."
        if not description:
            errors["description"] = "description is required."

        elif len(description) < 15:
            errors["description"] = "description must contain at least 15 letters."

        if not category:
            errors["category"] = "please select a category."

        if show_on_list not in ["yes", "no"]:
            errors["show_on_list"] = "please select Yes or No."

        if not variants:
            errors["variant"]="atleast one variant is required"
        
        for i ,variant in enumerate(variants):
            if not variant["price"]:
                variant["errors"]["price"] = "Price is required"
            elif float(variant["price"]) <= 0:
                variant["errors"]["price"] = "Price must postive number "

            if not variant["stock"]:
                variant["errors"]["stock"] = "Stock is required"
            elif int(variant["stock"]) <= 0:
                variant["errors"]["stock"] = "Stock must be atleast 1"

            if not str(variant["size"]).strip():
                variant["errors"]["size"] = "Size is required"

            if not str(variant["color"]).strip():
                variant["errors"]["color"] = "Color is required"
            offer_value=variant["offer"]
            if offer_value and float(offer_value)>0:
                if not start_date[i]:
                    variant["errors"]["start_date"]=("start date required  ")
                if not end_date[i]:
                    variant["errors"]["end_date"]=("end date required  ")
                if start_date[i] and end_date[i]:

                    if start_date[i] > end_date[i]:
                        variant["errors"]["start_date"] = ("Start date cannot be after end date.")
                        variant["errors"]["end_date"] = ("End date must be after start date.")
            variant_images = request.FILES.getlist(f"images_{i}[]")
        
            if len(variant_images)<3:
                variant["errors"]["images"]=("upload atleast 3 image")

        variant_has_errors=any(variant["errors"] for variant in variants)

        if errors or variant_has_errors:
            messages.error(request,"Failed")

            return render(request,"staff/add_product.html",{"active_page":"admin_product_management","categories":categories,"errors":errors,"variants":variants,"product_name":product_name,"description":description,"selected_category":category})


        category_obj=get_object_or_404(Category,id=category)

        product=Products.objects.create(name=product_name,description=description,category_id=category_obj.id,is_active=(show_on_list=="yes"))
        for i in range(len(prices)):

            variant=ProductVariant.objects.create(product=product,size=sizes[i],color=colors[i],price=prices[i], offer=offer[i] if offer[i] else None,start_date=start_date[i] if start_date[i] else None,end_date=end_date[i] if end_date[i] else None,stock=stocks[i],is_active=(statuses[i] == "true"))
            variant_images=request.FILES.getlist(f"images_{i}[]")

            for i,image in enumerate(variant_images):
                ProductImage.objects.create(variant=variant,image=image,is_primary=(i==0))
        messages.success(request, "Product added successfully.")
        return redirect("product_management")
    return render(request,"staff/add_product.html",{"active_page":"admin_product_management","categories":categories,"errors":{},"variants":[{"index":0,"errors":{}  }]})




@login_required(login_url="admin_login")
def edit_product(request,product_id):
    products=get_object_or_404(Products.objects.prefetch_related('variants__images'),id=product_id)
    
    categories=Category.objects.all()
    errors={}

    if request.method=="POST":
        delete_image_ids = request.POST.get("deleted_image_ids","")
        delete_variant_ids= request.POST.get("deleted_variant_ids","")
        
        method = request.POST.get("_method", "POST").upper()

   
        if method != "PATCH":
            return redirect("product_management")
        if delete_variant_ids:
            ProductVariant.objects.filter(id__in=delete_variant_ids.split(",")).delete()
            
        if delete_image_ids:
            deleted_ids = delete_image_ids.split(",")

            deleted_images = ProductImage.objects.filter(id__in=deleted_ids)
            affected_variant_ids = list(deleted_images.values_list("variant_id", flat=True))

            deleted_images.delete()

            for variant_id in affected_variant_ids:
                remaining_images = ProductImage.objects.filter(variant_id=variant_id).order_by("id")

                if remaining_images.exists():
                    remaining_images.update(is_primary=False)
                    first_image = remaining_images.first()
                    first_image.is_primary = True
                    first_image.save(update_fields=["is_primary"])
        
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
        variant_ids = request.POST.getlist('variant_id[]')
        variants=[]
        variant_count=max(len(prices),len(sizes),len(colors),len(stocks),len(statuses))
        for i in range(variant_count):
            variant_images=[]
            if i<len(variant_ids) and variant_ids[i]:
                db_variant=ProductVariant.objects.get(id=variant_ids[i])
                variant_images=db_variant.images.all()
            variants.append({"id": variant_ids[i] if i < len(variant_ids) else "","index":i,"price":prices[i] if i < len(prices) else "", "size": sizes[i] if i < len(sizes) else "","color": colors[i] if i < len(colors) else "","stock": stocks[i] if i < len(stocks) else "","offer": offer[i] if i < len(offer) else "","start_date": start_date[i] if i < len(start_date) else "","end_date": end_date[i] if i < len(end_date) else "","status": statuses[i] if i < len(statuses) else "true","images": variant_images,"errors":{}})
        if not product_name:
            errors["product_name"] = "product name is required."

        elif len(product_name) < 3:
            errors["product_name"] = "product name must contain atleast 5 characters."

        elif not re.match(r'^[A-Za-z0-9 ]+$', product_name):
            errors["product_name"] = "only letters and numbers are allowed."
        elif Products.objects.filter(name__iexact=product_name).exclude(id=products.id).exists():
                    errors["product_name"] = "Product name already exists."
        if not description:
            errors["description"] = "description is required."

        elif len(description) < 15:
            errors["description"] = "description must contain at least 15 letters."

        if not category:
            errors["category"] = "please select a category."

        if show_on_list not in ["yes", "no"]:
            errors["show_on_list"] = "please select Yes or No."

        if not variants:
            errors["variant"]="atleast one variant is required"

        for i ,variant in enumerate(variants):

            if not variant["price"]:
                variant["errors"]["price"] = "Price is required"
            elif float(variant["price"]) <= 0:
                variant["errors"]["price"] = "Price must postive number "

            if not variant["stock"]:
                variant["errors"]["stock"] = "Stock is required"
            elif int(variant["stock"]) <0 :
                variant["errors"]["stock"] = "Stock must be postive number"

            if not str(variant["size"]).strip():
                variant["errors"]["size"] = "Size is required"

            if not str(variant["color"]).strip():
                variant["errors"]["color"] = "Color is required"
            offer_value=variant["offer"]
            if offer_value and float(offer_value)>0:
                if not start_date[i]:
                    variant["errors"]["start_date"]=("start date required  ")
                if not end_date[i]:
                    variant["errors"]["end_date"]=("end date required  ")
                if start_date[i] and end_date[i]:
                    if start_date[i] > end_date[i]:
                        variant["errors"]["start_date"] = ("Start date cannot be after end date.")
                        variant["errors"]["end_date"] = ("End date must be after start date.")
            variant_images = request.FILES.getlist(f"images_{i}[]")
          
            existing_count=0

            if  i < len(variant_ids) and variant_ids[i]:
                existing_variant=ProductVariant.objects.get(id=variant_ids[i])
                existing_count=existing_variant.images.count()
            total_images=existing_count+len(variant_images)
            if total_images<3:
                variant["errors"]["images"]=("upload atleast 3 image")
        seen=set()
        for i,variant in enumerate(variants):
            key=(variant["size"],variant["color"])
            if key in seen:
                variant["errors"]["duplicate"]=("color and size already exists.")
            seen.add(key)

        variant_has_errors=any(variant["errors"] for variant in variants)
        
        if errors or variant_has_errors:
            messages.error(request,"Failed")
            products.name=product_name
            products.description = description
            return render(request,"staff/edit_product.html",{"active_page":"admin_product_management","categories":categories,"errors":errors,"products":products,"variants":variants})
        category_obj=get_object_or_404(Category,id=category)
            
        products.name=product_name
        products.description=description
        products.category=category_obj
        products.is_active=(show_on_list=="yes")
        products.save()
        
        for i in range(len(prices)):
            variant_id=(variant_ids[i] if i <len(variant_ids) else "")
            if variant_id:
                    variant=ProductVariant.objects.get(id=variant_id)
                    duplicate=ProductVariant.objects.filter(product=products,size=sizes[i],color=colors[i]).exclude(id=variant.id)

                    if duplicate.exists():
                        variants[i]["errors"]["duplicate"]=("Color and size already exist.")
                        return render(request,"staff/edit_product.html",{"categories":categories,"errors":errors,"products":products,"variants":variants})


                    variant.size= sizes[i]
                    variant.color = colors[i]
                    variant.price = prices[i]
                    variant.stock = stocks[i]
                    variant.offer = offer[i] or 0
                    variant.start_date = start_date[i] or None
                    variant.end_date = end_date[i] or None
                    variant.is_active = (statuses[i] == "true")
                    variant.save()
            else:
                variant=ProductVariant.objects.create(product=products,size=sizes[i],color=colors[i],price=prices[i],stock=stocks[i],offer=offer[i]or 0,start_date=start_date[i]or None,end_date=end_date[i]or None,is_active=(statuses[i]=="true"))
                
            upload_images=request.FILES.getlist(f"images_{i}[]")

            existing_images = variant.images.count()

            for img_index, image in enumerate(upload_images):
                ProductImage.objects.create(variant=variant,image=image,is_primary=(existing_images == 0 and img_index == 0))
        messages.success(request, "Product edited successfully.")

        return redirect("edit_product",product_id=products.id,)
    

    variants=[]
    for v in products.variants.all():
      variants.append({
        "id":v.id,
        "images":[],
        "price": v.price,
        "size": v.size,
        "color": v.color,
        "stock": v.stock,
        "offer": v.offer,
        "start_date": v.start_date,
        "end_date": v.end_date,
        "status": True if v.is_active else False,
    
        "images": v.images.all(),
        "errors": {},
    })
      
    return render(request,"staff/edit_product.html",{"active_page":"admin_product_management","products":products,"categories":categories,"variants":variants,"errors":{}})

@login_required(login_url="admin_login")
def activate_product(request,product_id):
    product=Products.objects.filter(id=product_id).first()
    product.is_active=True
    product.save(update_fields=["is_active"])
    
    messages.success(request, "activate")
    return redirect("product_management")
  
@login_required(login_url="admin_login")
def deactivate_product(request,product_id):
    product=Products.objects.filter(id=product_id).first()
    product.is_active=False
    product.save(update_fields=["is_active"])

    messages.success(request, "inactivate")
    return redirect("product_management")    



@login_required(login_url="admin_login")
def order_management(request):
    search=request.GET.get("search","")
    status = request.GET.get("status", "").strip().lower()

    orders=(Orders.objects.select_related("user").prefetch_related("payments","addresses","items__variant__product","items__variant__images",).order_by("-created_at"))
    if search:
        orders=orders.filter(Q(items__variant__product__name__icontains=search)|Q (addresses__name__icontains=search)).distinct()
    if status:
        orders = orders.filter(status=status)
    orders = orders.distinct()

    paginator = Paginator(orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request,"staff/order_management.html",{"orders":page_obj,"page_obj":page_obj,"search":search,"active_page": "admin_order_management","status": status,})

@login_required(login_url="admin_login")
def admin_order_detail(request,order_id):

    order=get_object_or_404(Orders.objects.select_related("user").prefetch_related("payments"),id=order_id)
    items=(OrderItems.objects.filter(order=order).select_related("variant","variant__product").prefetch_related("variant__images"))
    shipping=OrderAddress.objects.filter(order=order,address_type="shipping").first()
    tracking=OrderTrack.objects.filter(order=order).order_by("-status_time").first()
    for i in items:
        i.line_total=i.quantity * i.unit_amount

    STATUS_FLOW=["pending",'order placed','shipped','out for delivery','delivered','cancelled']
    if order.status in STATUS_FLOW:
   
        current_index=STATUS_FLOW.index(order.status)
        if current_index == len(STATUS_FLOW)-1:
            allowed_statuses=[STATUS_FLOW[current_index-1],STATUS_FLOW[current_index]]
        else:
            allowed_statuses=[STATUS_FLOW[current_index],STATUS_FLOW[current_index + 1]]

    else:
        allowed_statuses=[]
    payment = order.payments.order_by("-created_at").first()

    return render(request,"staff/admin_order_details.html",{"order":order,"payment": payment,"items":items,"shipping":shipping,"tracking":tracking,"allowed_statuses": allowed_statuses,"active_page": "admin_order_management"})

@login_required(login_url="admin_login")
def order_status(request,order_id):
    order=get_object_or_404(Orders,id=order_id)
    if request.method == "POST":  
        new_status=request.POST.get("status")
        
        if order.status != new_status:
            order.status =new_status
            if new_status =="delivered":
                payment = Payment.objects.filter(
    order=order
).order_by('-created_at').first()

                if payment:
                    payment.status='paid'
                    payment.save(update_fields=['status'])
                    order.payment_status='paid'
            order.save(update_fields=['status','payment_status'])
            OrderTrack.objects.create(order=order,status=new_status)
            if new_status =="cancelled":
                order_items=OrderItems.objects.filter(order=order)
                order.status ='cancelled'
                for item in order_items:
                    cancelled_qty = item.cancellation.aggregate(total=Sum("quantity"))["total"] or 0
                    remaining_qty = item.quantity - cancelled_qty
        
                    if remaining_qty > 0:
                        item.variant.stock += remaining_qty
                        item.variant.save()
        
                    item.status = "cancelled"
                    item.save(update_fields=["status"])


        return redirect('admin_order_detail',order_id=order.id)
    return redirect("admin_order_detail",order_id=order.id)

@login_required(login_url="admin_login")
def admin_order_returns(request):

    search = request.GET.get("search", "")
    status = request.GET.get("status", "all")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    order_returns = (OrderReturns.objects.select_related("order", "order__user").prefetch_related(Prefetch("order__addresses",queryset=OrderAddress.objects.filter(address_type="shipping"),to_attr="shipping")))
    item_returns = (OrderItemReturn.objects.select_related("order_item","order_item__order","order_item__order__user","order_item__variant__product",))
    if status == "pending":

        order_returns = order_returns.filter(status="pending")
        item_returns = item_returns.filter(status="pending")


    elif status == "returned":
        order_returns = order_returns.filter(status="returned")
        item_returns = item_returns.filter(status="returned")


    elif status == "rejected":
        order_returns = order_returns.filter(status="rejected")
        item_returns = item_returns.filter(status="rejected")


    if search:
        order_returns = order_returns.filter(Q(order__addresses__name__icontains=search)).distinct()
        item_returns = item_returns.filter(Q(order_item__order__addresses__name__icontains=search)).distinct()

    if start_date:
        order_returns = order_returns.filter(created_at__date__gte=start_date)
        item_returns = item_returns.filter(created_at__date__gte=start_date)
    if end_date:
        order_returns = order_returns.filter(created_at__date__lte=end_date)
        item_returns = item_returns.filter(created_at__date__lte=end_date)


    returns = sorted(chain(order_returns, item_returns),key=attrgetter("created_at"),reverse=True,)


    return render(request,"staff/admin_order_returns.html",{"returns":returns,"search": search,"status": status,"start_date": start_date,"end_date": end_date,"active_page": "admin_order_management"})


@login_required(login_url="admin_login")
def return_details(request,return_type,return_id):

    if return_type =="order":
        return_obj=get_object_or_404(OrderReturns.objects.select_related("order","order__user").prefetch_related(Prefetch("order__addresses",queryset=OrderAddress.objects.filter(address_type='shipping'),to_attr='shipping_address'),"order__items__variant__product",'order__items__variant__images'),id=return_id)
        items=return_obj.order.items.all()
        refund_amount=return_obj.order.final_amount
    else:
        return_obj=get_object_or_404(OrderItemReturn.objects.select_related("order_item","order_item__order","order_item__order__user","order_item__variant__product").prefetch_related("order_item__variant__images",Prefetch("order_item__order__addresses",queryset=OrderAddress.objects.filter(address_type="shipping"),to_attr="shipping_address")),id=return_id)
        items=[return_obj.order_item]
        refund_amount=(return_obj.quantity*return_obj.order_item.unit_amount)

    return render(request,"staff/return_details.html",{"return_type": return_type,"return_obj": return_obj, "order": return_obj.order if return_type == "order" else return_obj.order_item.order,  "items": items,"refund_amount": refund_amount,"active_page": "admin_order_management"},)

@login_required(login_url="admin_login")
def update_return_status(request,return_id,return_type):
    if return_type == "order":
        return_order = get_object_or_404(OrderReturns, id=return_id)
        order = return_order.order
    else:
        return_order = get_object_or_404(OrderItemReturn, id=return_id)
        order = return_order.order_item.order

    if request.method =="POST":
        status=request.POST.get("status")

        if status == "returned":
            if return_order.status == "pending":
                if return_type == "order":

                    for item in order.items.select_related("variant"):
                        if OrderItemReturn.objects.filter(order_item=item,status="returned").exists():
                            continue

                        ProductVariant.objects.filter(id=item.variant.id).update(stock=F("stock") + item.quantity)
                    order.status = "returned"
                    order.save(update_fields=["status"])
                    OrderTrack.objects.create(order=order,status="returned")

                else:

                    ProductVariant.objects.filter(id=return_order.order_item.variant.id).update(stock=F("stock") + return_order.quantity)

                    return_order.order_item.status = "returned"
                    return_order.order_item.save(update_fields=["status"])

                return_order.status = "returned"
                return_order.save(update_fields=["status"])

        else:

            return_order.status = "rejected"
            return_order.save(update_fields=["status"])

            if return_type == "order":
                order.status = "rejected"
                order.save(update_fields=["status"])
                OrderTrack.objects.create(order=order,status="rejected")
            else:
                return_order.order_item.status = "rejected"
                return_order.order_item.save(update_fields=["status"])

    return redirect("admin_order_returns")

@login_required(login_url="admin_login")
def admin_coupon_management(request):
    return render(request,"staff/admin_coupon_management.html",{"active_page": "admin_coupon_management"})

@login_required(login_url="admin_login")
def add_coupon(request):

    if request.method == "POST":

        errors, cleaned_data = validate_coupon(
            request.POST
        )

        if not errors:

            Coupon.objects.create(

                code=cleaned_data["code"],

                discount_type=cleaned_data["discount_type"],

                discount_value=cleaned_data["discount_value"],

                min_order_amount=cleaned_data[
                    "min_order_amount"
                ],

                max_discount=cleaned_data[
                    "max_discount"
                ],

                max_usage=cleaned_data["max_usage"],

                start_date=cleaned_data["start_date"],

                end_date=cleaned_data["end_date"],

                is_active=(
                    request.POST.get("is_active") == "on"
                )
            )

            messages.success(
                request,
                "Coupon created successfully."
            )
            redirect("admin_coupon_management")
        return render(request,"staff/add_coupon.html",{"errors": errors,"data": request.POST,"active_page":"admin_coupon_management"})

    return render(request,"staff/add_coupon.html",{"active_page":"admin_coupon_management"})