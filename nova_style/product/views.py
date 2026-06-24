from django.shortcuts import render,get_object_or_404,redirect
from .models import ProductImage,Products,ProductVariant,Category
from user.models import Users
from .models import Review
from django.core.paginator import Paginator
from cart.models import Cart,CartItem
from django.contrib.auth.decorators import login_required

def product_list(request):
    details=request.user
    variants=ProductVariant.objects.filter(is_active=True,product__is_active=True).select_related("product","product__category").prefetch_related("images").order_by("-created_at")

    search=request.GET.get("search","")
    category=request.GET.get("category")
    size=request.GET.get("size")
    min_price=request.GET.get("min_price")
    max_price=request.GET.get("max_price")
    sort=request.GET.get("sort")
    print(category,size,search)

    if search:
        variants=variants.filter(product__name__icontains=search)

    if category:
        variants=variants.filter(product__category_id=category)

    if size:
        variants=variants.filter(size=size)
    
    if min_price:
        variants=variants.filter(price__gte=min_price)

    if max_price:
        variants=variants.filter(price__lte=max_price)

    if sort =="price-low":
         variants = variants.order_by("price")
    elif sort =="price-high":
         variants = variants.order_by("-price")
    elif sort =="az":
        variants = variants.order_by("product__name")
    elif sort =="za":
        variants = variants.order_by("-product__name")
    elif sort =="new":
        variants=variants.order_by("-created_at")
    return render(request,'product/product_list.html',{"variants":variants,"categories":Category.objects.filter(is_active=True),"details":details})

def product_details(request,variant_id): 
    
    profile=request.user

    variant=get_object_or_404(ProductVariant.objects.select_related("product"),id=variant_id)
    product=variant.product
    if not variant.is_active or not product.is_active :
        return redirect("product_list")

    all_variants=(ProductVariant.objects.filter(product_id=product.id,is_active=True).prefetch_related("images"))
    sizes=[]
    seen=set()

    for i in all_variants:
        if i.size not in seen:
            sizes.append(i)
            seen.add(i.size)
    colors=all_variants.filter(size=variant.size)
    category=product.category
    related_products=(ProductVariant.objects.filter(product__category=category,is_active=True,product__is_active=True).exclude(id=variant_id).prefetch_related("images"))

    all_reviews=Review.objects.filter(product=product).select_related("user").order_by("-created_at")
    review_count=all_reviews.count()

    avg_rating=0
    if review_count:
        avg_rating=round(sum(i.rating for i in all_reviews)/review_count,1)
    five_star = all_reviews.filter(rating=5).count()
    four_star = all_reviews.filter(rating=4).count()
    three_star = all_reviews.filter(rating=3).count()
    two_star = all_reviews.filter(rating=2).count()
    one_star = all_reviews.filter(rating=1).count()

    def percentage(count):
        if review_count==0:
            return 0
        return round((count/review_count)*100)
    
    five_star_percent = percentage(five_star)
    four_star_percent = percentage(four_star)
    three_star_percent = percentage(three_star)
    two_star_percent = percentage(two_star)
    one_star_percent = percentage(one_star)

    page_number=int(request.GET.get("page",1))
    reviews=all_reviews[:page_number*3]
    next=(review_count>page_number*3)

    errors={}
    if request.method=="POST":
        rating=int(request.POST.get("rating",0))
        review=request.POST.get("review","")
        title = request.POST.get("title", "")
        
        if rating==0  :
            errors["rating"] = "rating  is required."
        elif not title:
            errors["title"]="title is required"
        elif len(title)<7:
            errors["title"]="atleast  7 characters required in title "
        elif not review:
            errors["review"] = "review  is required."
        elif  len(review)<15:
            errors["review"]="atleast  15 characters required"
        if not errors:
            Review.objects.create(user=request.user,product=product,rating=rating,title=title,comment=review)
            return redirect("product_details",variant_id=variant_id)
    cart_error = request.session.pop("cart_error",None)
    return render(request,"product/product_details.html",{"details":profile,"product":product,"variant":variant,"sizes":sizes,"colors":colors,"related_products":related_products,"errors":errors,"reviews":reviews,"avg_rating": avg_rating,"review_count": review_count,"five_star_percent": five_star_percent,"four_star_percent": four_star_percent,"three_star_percent": three_star_percent,"two_star_percent": two_star_percent,"one_star_percent": one_star_percent,"next":next,"page_number":page_number,"cart_error":cart_error})


@login_required(login_url="login")
def add_to_cart(request):
    errors={}
    if request.method !="POST":
        return redirect("product_list")

    variant_id=request.POST.get("variant_id")
    variant=get_object_or_404(ProductVariant.objects.select_related("product"),id=variant_id)

    if not variant.is_active:
        errors["cart"]="Variant is unavailable"
    elif not variant.product.is_active:
        errors["cart"]="Product is unavailable"

    elif  variant.stock <=0:
        errors["cart"]="out of stock"


    if not errors:
       cart,_=Cart.objects.get_or_create(user=request.user)
       cart_item,created=CartItem.objects.get_or_create(cart=cart,variant=variant,defaults={"quantity":1})
       if not created:
            if cart_item.quantity>=variant.stock:
                    errors["cart"] = "Out of stock"
            elif cart_item.quantity >=5:
                    errors["cart"] ="maximum 5 quantities allowed"
            else:
                    cart_item.quantity+=1
                    cart_item.save(update_fields=["quantity"])
    if errors:
            request.session["cart_error"]=errors["cart"]

    return redirect("product_details",variant_id=variant.id)