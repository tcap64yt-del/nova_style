from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,CartItem
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse


@login_required(login_url="login")
def cart(request):
    profile=request.user
    cart=Cart.objects.filter(user=request.user).first()
    if cart:
        CartItem.objects.filter(cart=cart).filter(Q(variant__is_active=False)| Q(variant__product__is_active=False)).delete()
        cart_items=CartItem.objects.filter(cart=cart,variant__is_active=True,variant__product__is_active=True).select_related("variant","variant__product").prefetch_related("variant__images")
    
    cart_count=cart_items.count()
    cart_items=[]
    subtotal=0
    if cart:
        cart_items=cart.items.all()
        for item in cart_items:
            subtotal+=item.variant.discounted_price*item.quantity

    return render(request,"cart/cart.html",{"cart_items":cart_items,"subtotal":subtotal,"cart_count":cart_count,"profile":profile})

@login_required(login_url="login")
def remove_cart_item(request,item_id):
    item=get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    cart=item.cart
    item.delete()
    subtotal = 0
    for cart_item in cart.items.all():
        subtotal += cart_item.variant.discounted_price * cart_item.quantity

    return JsonResponse({"success": True,"message": "Item removed from cart.","subtotal": subtotal,"cart_count": cart.items.count(),})

@login_required(login_url="login")
def increase_quantity(request,item_id):
    
    item =get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    if item.quantity >= item.variant.stock:
        return JsonResponse({"success": False,"message": "Out of stock."})
    elif item.quantity >= 5:
        return JsonResponse({"success": False,"message": "Maximum 5 quantities allowed."})

    item.quantity += 1
    item.save(update_fields=["quantity"])
    subtotal = 0
    for cart_item in item.cart.items.all():
        subtotal += cart_item.variant.discounted_price * cart_item.quantity

    return JsonResponse({"success": True,"message": "Quantity increased.","quantity": item.quantity,"subtotal": subtotal,"item_total": item.quantity * item.variant.discounted_price,"cart_count": item.cart.items.count()})

@login_required(login_url="login")
def decrease_quantity(request,item_id):
    item=get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save(update_fields=["quantity"])
    else:
        return JsonResponse({"success": False,"message": "Minimum quantity is 1."})
    
    subtotal = 0
    for cart_item in item.cart.items.all():
        subtotal += cart_item.variant.discounted_price * cart_item.quantity

    return JsonResponse({"success": True,"message": "Quantity decreased.","quantity": item.quantity,"subtotal": subtotal,"item_total": item.quantity * item.variant.discounted_price,"cart_count": item.cart.items.count()})