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
from django.db.models import Count,Prefetch
from django.http import JsonResponse
from order.models import Orders,OrderItems,OrderAddress,OrderTrack,OrderReturns

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

    return render(request,'staff/admin_user_management.html',{"users":page_obj,"total":total,"sort":sort,"search":search,'page_obj':page_obj})


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

    
    return render(request,'staff/admin_category_management.html',{"categories":page_obj,"total_categories":total_categories,'page_obj':page_obj,"search":search,"sort":sort})

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
        
        uploaded_image = request.FILES.get('image_url')

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

        
        return render(request,"staff/admin_product_management.html",{"products":page_obj,"page_obj":page_obj,"search":search,"sort":sort})

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
            variants.append({"index":i,"price":prices[i] if i < len(prices) else "", "size": sizes[i] if i < len(sizes) else "","color": colors[i] if i < len(colors) else "","stock": stocks[i] if i < len(stocks) else "","offer": offer[i] if i < len(offer) else "","status": statuses[i] if i < len(statuses) else "true","errors":{}})

        

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
            elif int(variant["stock"]) < 1:
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

            variant_images = request.FILES.getlist(f"images_{i}[]")

            if len(variant_images)<3:
                variant["errors"]["images"]=("upload atleast 3 image")

        variant_has_errors=any(variant["errors"] for variant in variants)

        if errors or variant_has_errors:
            messages.error(request,"Failed")

            return render(request,"staff/add_product.html",{"categories":categories,"errors":errors,"variants":variants,"product_name":product_name,"description":description,"selected_category":category})


        category_obj=get_object_or_404(Category,id=category)

        product=Products.objects.create(name=product_name,description=description,category_id=category_obj.id,is_active=(show_on_list=="yes"))
        for i in range(len(prices)):

            variant=ProductVariant.objects.create(product=product,size=sizes[i],color=colors[i],price=prices[i], offer=offer[i] if offer[i] else None,start_date=start_date[i] if start_date[i] else None,end_date=end_date[i] if end_date[i] else None,stock=stocks[i],is_active=(statuses[i] == "true"))
            variant_images=request.FILES.getlist(f"images_{i}[]")

            for i,image in enumerate(variant_images):
                ProductImage.objects.create(variant=variant,image=image,is_primary=(i==0))
        messages.success(request, "Product added successfully.")
        return redirect("add_product")
    return render(request,"staff/add_product.html",{"categories":categories,"errors":{},"variants":[{"index":0,"errors":{}  }]})




@login_required(login_url="admin_login")
def edit_product(request,product_id):
    products=get_object_or_404(Products.objects.prefetch_related('variants__images'),id=product_id)
    
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
            elif int(variant["stock"]) < 1:
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
            return render(request,"staff/edit_product.html",{"categories":categories,"errors":errors,"products":products,"variants":variants})
        category_obj=get_object_or_404(Category,id=category)
            
        products.name=product_name
        products.description=description
        products.category=category_obj
        products.is_active=(show_on_list=="yes")
        products.save()
        delete_image_ids = request.POST.get("deleted_image_ids","")
        delete_variant_ids= request.POST.get("deleted_variant_ids","")

        print(delete_variant_ids)

        if delete_variant_ids:
            ProductVariant.objects.filter(id__in=delete_variant_ids.split(",")).delete()
            
        if delete_image_ids:
            ProductImage.objects.filter(id__in=delete_image_ids.split(",")).delete()
        

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

        return redirect("edit_product",product_id=products.id)
    

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
      
    return render(request,"staff/edit_product.html",{"products":products,"categories":categories,"variants":variants,"errors":{}})

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


def check_category_name(request):
    name = request.GET.get("name", "").strip()
    category_id = request.GET.get("category_id")

    qs = Category.objects.filter(name__iexact=name)

    if category_id:
        qs = qs.exclude(id=category_id)

    return JsonResponse({"exists": qs.exists()})

def check_product_name(request):
    name = request.GET.get("name", "").strip()
    product_id = request.GET.get("product_id")

    qs = Products.objects.filter(name__iexact=name)

    if product_id:
        qs = qs.exclude(id=product_id)

    return JsonResponse({
        "exists": qs.exists()
    })

@login_required(login_url="admin_login")
def order_management(request):
    orders=Orders.objects.select_related("user").prefetch_related("addresses","items__variant__product","items__variant__images",).order_by("-created_at")
    return render(request,"staff/order_management.html",{"orders":orders})

@login_required(login_url="admin_login")
def admin_order_detail(request,order_id):

    order=get_object_or_404(Orders.objects.select_related("user"),id=order_id)
    items=(OrderItems.objects.filter(order=order).select_related("variant","variant__product").prefetch_related("variant__images"))
    shipping=OrderAddress.objects.filter(order=order,address_type="shipping").first()
    tracking=OrderTrack.objects.filter(order=order).order_by("-status_time").first()
    for i in items:
        i.line_total=i.quantity * i.unit_amount

    STATUS_FLOW=["pending",'order placed','shipped','out for delivery','delivered']
    if order.status in STATUS_FLOW:
   
        current_index=STATUS_FLOW.index(order.status)
        if current_index == len(STATUS_FLOW)-1:
            allowed_statuses=[STATUS_FLOW[current_index-1],STATUS_FLOW[current_index]]
        else:
            allowed_statuses=[STATUS_FLOW[current_index],STATUS_FLOW[current_index + 1]]

    else:
        allowed_statuses=[]

    return render(request,"staff/admin_order_details.html",{"order":order,"items":items,"shipping":shipping,"tracking":tracking,"allowed_statuses": allowed_statuses,})

@login_required(login_url="admin_login")
def order_status(request,order_id):
    order=get_object_or_404(Orders,id=order_id)
    if request.method == "POST":  
        new_status=request.POST.get("status")
        
        if order.status != new_status:
            order.status =new_status
            order.save(update_fields=['status'])
            OrderTrack.objects.create(order=order,status=new_status)
        return redirect('admin_order_detail',order_id=order.id)
    return redirect("admin_order_detail",order_id=order.id)


def admin_order_returns(request):
   returns=OrderReturns.objects.select_related("order").prefetch_related("order__items__variant__product",Prefetch('order__addresses',queryset=OrderAddress.objects.filter(address_type="shipping"),to_attr="shipping")).order_by("-created_at")


   return render(request,"staff/admin_order_returns.html",{"returns":returns})

def return_details(request,return_id):
    return_order=get_object_or_404(OrderReturns.objects.filter(id=return_id).select_related("order","order__user").prefetch_related(Prefetch('order__addresses',queryset=OrderAddress.objects.filter(address_type="shipping"),to_attr="shipping_address"),"order__items__variant__product","order__items__variant__images"),id=return_id)

    return render(request,"staff/return_details.html",{"return_order":return_order})

def update_return_status(request,return_id):
    return_order=get_object_or_404(OrderReturns,id=return_id)

    if request.method =="POST":
        status=request.POST.get("status")
        if status =="approved":
            return_order.status='approved'
            return_order.save(update_fields=["status"])
            order=return_order.order
            order.status="approved"

            order.save(update_fields=['status'])
            OrderTrack.objects.create(order=order,status='approved')
        else:
            return_order.status='rejected'
            return_order.save(update_fields=["status"])
            order=return_order.order
            order.status="rejected"
            order.save(update_fields=['status'])
            OrderTrack.objects.create(order=order,status='rejected')

    return redirect("return_details",return_id=return_id)