from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,CartItem
# Create your views here.
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def cart(request):
    profile=request.user
    cart_count=CartItem.objects.count()
    cart=Cart.objects.filter(user=request.user).prefetch_related("items__variant__product","items__variant__images").first()
    cart_items=[]
    subtotal=0
    if cart:
        cart_items=cart.items.all()
        for item in cart_items:
            subtotal+=item.variant.final_price*item.quantity

    return render(request,"cart/cart.html",{"cart_items":cart_items,"subtotal":subtotal,"cart_count":cart_count,"profile":profile})

@login_required(login_url="login")
def remove_cart_item(request,item_id):
    item=get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    item.delete()
    return redirect("cart")

@login_required(login_url="login")
def increase_quantity(request,item_id):
    item =get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    if item.quantity<item.variant.stock and item.quantity<5:
        item.quantity+=1
        item.save(update_fields=["quantity"])
    return redirect("cart")

@login_required(login_url="login")
def decrease_quantity(request,item_id):
    item=get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    if item.quantity>1:
        item.quantity-=1
        item.save(update_fields=["quantity"])
    return redirect("cart")