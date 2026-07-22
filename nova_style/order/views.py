from django.shortcuts import render,get_object_or_404,redirect
from product.models import ProductVariant
from cart.models import CartItem
from user.models import Addresses
from .models import OrderAddress,OrderItems,Orders,OrderTrack,OrderCancellation,OrderItemCancellation,OrderReturns
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
@login_required(login_url="login")
def checkout (request):
    addersses=Addresses.objects.filter(user=request.user).order_by("-created_at")
    default_address=addersses.filter(is_default=True).first()
    
    profile=request.user
    buy_now = request.session.get("buy_now_variant")
    subtotal=0
    if buy_now:
        variant=get_object_or_404(ProductVariant.objects.select_related("product"),id=buy_now)
        items=[{"variant":variant,"quantity":1,"subtotal":variant.discounted_price}]
        
    else:
        items=CartItem.objects.filter(cart__user=request.user).select_related("variant","variant__product")
        print(items)
        
        for item in items:
            subtotal+=item.variant.discounted_price*item.quantity
    if request.method=="POST":

        if request.POST.get("action") == "add_address":
            address_errors={}
            name = request.POST.get("name", "").strip()
            phone = request.POST.get("phone", "").strip()
            address = request.POST.get("address", "").strip()
            district = request.POST.get("district", "").strip()
            state = request.POST.get("state", "").strip()
            country = request.POST.get("country", "").strip()
            postal_code = request.POST.get("postal_code", "").strip()
            is_default = request.POST.get("is_default") == "on"

            if not name:
                address_errors["name"] = "Name is required."

            elif len(name) < 3:
                address_errors["name"] = "Name must be at least 3 characters."

            elif not name.replace(" ", "").isalpha():
                address_errors["name"] = "Name must contain only letters."

            if not phone:
                address_errors["phone"] = "Phone is required."

            elif not phone.isdigit():
                address_errors["phone"] = "Phone must contain only numbers."

            elif len(phone) != 10:
                address_errors["phone"] = "Phone must be exactly 10 digits."


            if not address:
                address_errors["address"] = "Address is required."

            elif len(address) < 10:
                address_errors["address"] = "Address must be at least 10 characters."


            if not district:
                address_errors["district"] = "District is required."

            elif len(district) < 3:
                address_errors["district"] = "District must be at least 3 characters."

            elif not district.replace(" ", "").isalpha():
                address_errors["district"] = "District must contain only letters."


            if not state:
                address_errors["state"] = "State is required."

            elif len(state) < 3:
                address_errors["state"] = "State must be at least 3 characters."

            elif not state.replace(" ", "").isalpha():
                address_errors["state"] = "State must contain only letters."


            if not country:
                address_errors["country"] = "Country is required."

            elif len(country) < 3:
                address_errors["country"] = "Country must be at least 3 characters."

            elif not country.replace(" ", "").isalpha():
                address_errors["country"] = "Country must contain only letters."


            if not postal_code:
                address_errors["postal_code"] = "Postal code is required."

            elif not postal_code.isdigit():
                address_errors["postal_code"] = "Postal code must contain only numbers."

            elif len(postal_code) != 6:
                address_errors["postal_code"] = "Postal code must be exactly 6 digits."

            if address_errors:
                return render(request,"checkout/checkout.html",{"details":profile,"items":items,"buy_now":bool(buy_now),"subtotal":subtotal,"addresses":addersses,"default_address":default_address,"show_add_modal":True,"address_errors":address_errors,})
            Addresses.objects.create(user=request.user,name=name,phone=phone,address=address,district=district,state=state,country=country,postal_code=postal_code,is_default=is_default)
            return redirect("checkout")
        errors={}
        billing_same=request.POST.get("billing_same")=="on"
        shipping_name = request.POST.get("shippingName", "").strip()
        shipping_phone = request.POST.get("shippingPhone", "").strip()
        shipping_address = request.POST.get("shippingAddress", "").strip()
        shipping_state = request.POST.get("shippingState", "").strip()
        shipping_district = request.POST.get("shippingDistrict", "").strip()
        shipping_country = request.POST.get("shippingCountry", "").strip()
        shipping_postal = request.POST.get("shippingPostal", "").strip()

        if not shipping_name:
            errors["shipping_name"] = "Name is required."

        elif len(shipping_name) < 3:
            errors["shipping_name"] = "Name must be at least 3 characters."

        elif not shipping_name.replace(" ", "").isalpha():
            errors["shipping_name"] = "Name must contain only letters."

        if not shipping_phone:
            errors["shipping_phone"] = "Phone is required."

        elif not shipping_phone.isdigit():
            errors["shipping_phone"] = "Phone must contain only numbers."

        elif len(shipping_phone) != 10:
            errors["shipping_phone"] = "Phone must be exactly 10 digits."

        if not shipping_address:
            errors["shipping_address"] = "Address is required."

        elif len(shipping_address) < 10:
            errors["shipping_address"] = "Address must be at least 10 characters."

        if not shipping_state:
            errors["shipping_state"] = "State is required."

        elif len(shipping_state) < 3:
            errors["shipping_state"] = "State must be at least 3 characters."

        elif not shipping_state.replace(" ", "").isalpha():
            errors["shipping_state"] = "State must contain only letters."

        if not shipping_district:
            errors["shipping_district"] = "District is required."

        elif len(shipping_district) < 3:
            errors["shipping_district"] = "District must be at least 3 characters."

        elif not shipping_district.replace(" ", "").isalpha():
            errors["shipping_district"] = "District must contain only letters."

        if not shipping_country:
            errors["shipping_country"] = "Country is required."

        elif len(shipping_country) < 3:
            errors["shipping_country"] = "Country must be at least 3 characters."

        elif not shipping_country.replace(" ", "").isalpha():
            errors["shipping_country"] = "Country must contain only letters."

        if not shipping_postal:
            errors["shipping_postal"] = "Postal code is required."

        elif not shipping_postal.isdigit():
            errors["shipping_postal"] = "Postal code must contain only numbers."

        elif len(shipping_postal) != 6:
            errors["shipping_postal"] = "Postal code must be exactly 6 digits."
        if not billing_same:
            billing_phone = request.POST.get("billingPhone", "").strip()
            billing_name = request.POST.get("billingName", "").strip()
            billing_address = request.POST.get("billingAddress", "").strip()
            billing_state = request.POST.get("billingState", "").strip()
            billing_district = request.POST.get("billingDistrict", "").strip()
            billing_country = request.POST.get("billingCountry", "").strip()
            billing_postal = request.POST.get("billingPostal", "").strip()
            
            if not billing_name:
                errors["billing_name"] = "Name is required."

            elif len(billing_name) < 3:
                errors["billing_name"] = "Name must be at least 3 characters."

            elif not billing_name.replace(" ", "").isalpha():
                errors["billing_name"] = "Name must contain only letters."

            if not billing_phone:
                errors["billing_phone"] = "Phone is required."

            elif not billing_phone.isdigit():
                errors["billing_phone"] = "Phone must contain only numbers."

            elif len(billing_phone) != 10:
                errors["billing_phone"] = "Phone must be exactly 10 digits."

            if not billing_address:
                errors["billing_address"] = "Address is required."

            elif len(billing_address) < 10:
                errors["billing_address"] = "Address must be at least 10 characters."

            if not billing_state:
                errors["billing_state"] = "State is required."

            elif len(billing_state) < 3:
                errors["billing_state"] = "State must be at least 3 characters."

            elif not billing_state.replace(" ", "").isalpha():
                errors["billing_state"] = "State must contain only letters."

            if not billing_district:
                errors["billing_district"] = "District is required."

            elif len(billing_district) < 3:
                errors["billing_district"] = "District must be at least 3 characters."

            elif not billing_district.replace(" ", "").isalpha():
                errors["billing_district"] = "District must contain only letters."

            if not billing_country:
                errors["billing_country"] = "Country is required."

            elif len(billing_country) < 3:
                errors["billing_country"] = "Country must be at least 3 characters."

            elif not billing_country.replace(" ", "").isalpha():
                errors["billing_country"] = "Country must contain only letters."

            if not billing_postal:
                errors["billing_postal"] = "Postal code is required."

            elif not billing_postal.isdigit():
                errors["billing_postal"] = "Postal code must contain only numbers."

            elif len(billing_postal) != 6:
                errors["billing_postal"] = "Postal code must be exactly 6 digits."

        if errors: 
            return render(request,"checkout/checkout.html",{"errors":errors,"details":profile,"items":items,"buy_now":buy_now,"subtotal":subtotal,"default_address":default_address,"addresses":addersses})
        if buy_now:
            final_amount = variant.discounted_price
        else:
            final_amount = subtotal

        order = Orders.objects.create(user=request.user,final_amount=final_amount)
        OrderTrack.objects.create(order=order,status="pending",)
        OrderAddress.objects.create(order=order,address_type="shipping",name=shipping_name, phone=shipping_phone,address=shipping_address,state=shipping_state,district=shipping_district,country=shipping_country,postal_code=shipping_postal,)

        if billing_same:
            OrderAddress.objects.create(order=order,address_type="billing",name=shipping_name,phone=shipping_phone, address=shipping_address,state=shipping_state,district=shipping_district,country=shipping_country,postal_code=shipping_postal)

        else:
            OrderAddress.objects.create(order=order,address_type="billing",name=billing_name,phone=billing_phone,address=billing_address,state=billing_state,district=billing_district,country=billing_country,postal_code=billing_postal)
        
        if buy_now:
            OrderItems.objects.create(order=order,variant=variant,quantity=1,unit_amount=variant.discounted_price)
            variant.stock-=1
            variant.save()
        else:
            for item in items:
                variant=item.variant
                OrderItems.objects.create(order=order,variant=item.variant,quantity=item.quantity,unit_amount=item.variant.discounted_price)
                variant.stock-=item.quantity
                variant.save()
            items.delete()
        if buy_now:
            request.session.pop("buy_now_variant", None)

        
            
        return redirect("success",order_id=order.id)
    return render(request,"checkout/checkout.html",{"details":profile,"items":items,"buy_now":bool(buy_now),"subtotal":subtotal,"default_address":default_address,"addresses":addersses})

@login_required(login_url='login')
def success(request,order_id):
    order=get_object_or_404(Orders.objects.filter(user=request.user),id=order_id)
    order_items=OrderItems.objects.filter(order=order).select_related("variant","variant__product").prefetch_related("variant__images")
    for item in order_items:
        item.line_total = item.quantity * item.unit_amount
    return render(request,"checkout/success.html",{"order_items":order_items,"order":order,})
@login_required(login_url='login')
def order_details(request,order_id):
    STATUSS = ["pending","order placed","shipped","out for delivery","delivered","return pending","approved","rejected"]

    profile=request.user
    order=get_object_or_404(Orders.objects.select_related("user"),id=order_id,user=request.user)
    items=(OrderItems.objects.filter(order=order).select_related("variant","variant__product").prefetch_related("variant__images"))
    tracking=OrderTrack.objects.filter(order=order).order_by("status_time")
    tracking_map={t.status.lower():t.status_time for t in tracking}
    steps = []

    for i, status in enumerate(STATUSS):
        steps.append({"name": status,"time": tracking_map.get(status),"index": i,})
    if all(item.status== "cancelled" for item in items):
        order.status='cancelled'
        order.save(update_fields=["status"])

    shipping=OrderAddress.objects.filter(order=order,address_type="shipping").first()
    billing=OrderAddress.objects.filter(order=order,address_type="billing").first()

    if order.status =="cancelled":
        last_track=(OrderTrack.objects.filter(order=order).exclude(status__iexact="cancelled").order_by('-status_time').first())
        if last_track:
            cancel_index = STATUSS.index(last_track.status.lower())
        else:
            cancel_index = 0
        current_index = cancel_index
        progress = cancel_index * 25
    else:
        cancel_index=None
        current_index=STATUSS.index(order.status.lower())
        progress=current_index*25

    for i in items:
        i.line_total=i.quantity * i.unit_amount

    total=0
    for item in items:
            total+=item.variant.discounted_price*item.quantity
    for item in items:
        item.line_total = item.quantity * item.unit_amount

        item.cancelled_quantity = (
            item.cancellation.aggregate(total=Sum("quantity"))["total"] or 0
        )

        item.available_quantity = item.quantity - item.cancelled_quantity
            
    return render(request,"order/order_details.html",{"details":profile,"order":order,"items":items,"shipping":shipping,"billing":billing,"tracking":tracking,"steps": steps,"total":total,"current_index": current_index,"status_list": STATUSS,"progress":progress,"cancel_index":cancel_index,"tracking_map":tracking_map})


def cancel_product(request,item_id):
    item=get_object_or_404(OrderItems.objects.select_related('order',"variant","variant__product"),id=item_id,order__user=request.user)
    
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        reason = request.POST.get("reason")
        description = request.POST.get("description")
        print(quantity, reason, description)

        OrderItemCancellation.objects.create(
            order_item=item,
            quantity=quantity,
            reason=reason,
            description=description,
        )

        item.variant.stock+=quantity
        item.variant.save()
        
        cancelled = item.cancellation.aggregate(total=Sum("quantity"))["total"] or 0

        if cancelled >= item.quantity:
            item.status = "cancelled"
            item.save(update_fields=["status"])

        all_cancelled = True

        for order_item in item.order.items.all():
            cancelled_qty = (
                order_item.cancellation.aggregate(total=Sum("quantity"))["total"] or 0
            )

            if cancelled_qty < order_item.quantity:
                all_cancelled = False
                break

        if all_cancelled:
            order=item.order
            order.status = "cancelled"
            order.save(update_fields=["status"])
            OrderTrack.objects.get_or_create(order=order,status="cancelled")
        return redirect("order_details",order_id=item.order.id)
    return redirect("order_details",order_id=item.order.id)

def cancel_order(request,order_id):
    order=get_object_or_404(Orders,id=order_id,user=request.user)
    order_items=OrderItems.objects.filter(order=order)
    if request.method =="POST":
        reason=request.POST.get("reason")
        description=request.POST.get("description")

        print(reason,description)
        
        OrderCancellation.objects.create(order=order,reason=reason,description=description)
        order.status="cancelled"
        order.save(update_fields=["status"])
        
        OrderTrack.objects.get_or_create(order=order,status='cancelled')
        for item in order_items:
            item.status="cancelled"
            item.save(update_fields=['status'])
            item.variant.stock+=item.quantity
            item.variant.save()
        return redirect("order_details",order_id=order.id)
    return redirect("order_details",order_id=order.id)

@login_required(login_url='login')
def order_return(request,order_id):
    order=get_object_or_404(Orders,id=order_id,user=request.user)

    if request.method == "POST":
        reason=request.POST.get("reason")
        description=request.POST.get("description")

        OrderReturns.objects.create(order=order,reason=reason,description=description)
        order.status="return pending"
        order.save(update_fields=['status'])
        return redirect('order_details',order_id=order.id)

    return redirect("order_details",order_id=order.id)


