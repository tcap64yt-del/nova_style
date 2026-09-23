from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Cart, CartItem


@login_required(login_url="login")
def cart(request):
    details = request.user
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        CartItem.objects.filter(cart=cart).filter(
            Q(variant__is_active=False)
            | Q(variant__product__is_active=False)
            | Q(variant__product__category__is_active=False)
        ).delete()
        cart_items = (
            CartItem.objects.filter(
                cart=cart,
                variant__is_active=True,
                variant__product__category__is_active=True,
                variant__product__is_active=True,
            )
            .select_related("variant", "variant__product")
            .prefetch_related("variant__images")
        )

    cart_count = cart_items.count()
    cart_items = []
    subtotal = 0
    checkout_errors = []

    if cart:
        cart_items = cart.items.all()
        checkout_errors = []

        for item in cart_items:
            subtotal += item.variant.discounted_price * item.quantity

            if item.quantity > item.variant.stock:
                checkout_errors.append(
                    {
                        "name": item.variant.product.name,
                        "color": item.variant.color,
                        "size": item.variant.size,
                        "stock": item.variant.stock,
                    }
                )
    else:
        checkout_errors.append({"message": "It's empty. Please add a product."})
    return render(
        request,
        "cart/cart.html",
        {
            "details": details,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "cart_count": cart_count,
            "checkout_errors": checkout_errors,
            "show_sidebar": False,
            "show_search": False,
        },
    )


@login_required(login_url="login")
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = item.cart
    item.delete()
    subtotal = 0
    for cart_item in cart.items.all():
        subtotal += cart_item.variant.discounted_price * cart_item.quantity

    return JsonResponse(
        {
            "success": True,
            "message": "Item removed from cart.",
            "subtotal": subtotal,
            "cart_count": cart.items.count(),
        }
    )


@login_required(login_url="login")
def increase_quantity(request, item_id):

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity >= item.variant.stock:
        return JsonResponse({"success": False, "message": "Out of stock."})
    elif item.quantity >= 5:
        return JsonResponse(
            {"success": False, "message": "Maximum 5 quantities allowed."}
        )

    item.quantity += 1
    item.save(update_fields=["quantity"])
    subtotal = 0
    for cart_item in item.cart.items.all():
        subtotal += cart_item.variant.discounted_price * cart_item.quantity

    return JsonResponse(
        {
            "success": True,
            "message": "Quantity increased.",
            "quantity": item.quantity,
            "subtotal": subtotal,
            "item_total": item.quantity * item.variant.discounted_price,
            "cart_count": item.cart.items.count(),
        }
    )


@login_required(login_url="login")
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save(update_fields=["quantity"])
    else:
        return JsonResponse({"success": False, "message": "Minimum quantity is 1."})

    subtotal = 0
    for cart_item in item.cart.items.all():
        subtotal += cart_item.variant.discounted_price * cart_item.quantity

    return JsonResponse(
        {
            "success": True,
            "message": "Quantity decreased.",
            "quantity": item.quantity,
            "subtotal": subtotal,
            "item_total": item.quantity * item.variant.discounted_price,
            "cart_count": item.cart.items.count(),
        }
    )
