import razorpay
import json
from django.shortcuts import render,get_object_or_404,redirect
from product.models import ProductVariant
from cart.models import CartItem
from user.models import Addresses
from .models import OrderAddress,OrderItems,Orders,OrderTrack,OrderCancellation,OrderItemCancellation,OrderReturns,OrderItemReturn,Payment
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from reportlab.lib.colors import black
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.contrib import messages
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (getSampleStyleSheet,ParagraphStyle,)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from django.urls import reverse

from xml.sax.saxutils import escape
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



@login_required(login_url="login")
def checkout (request,variant_id=None):
    addersses=Addresses.objects.filter(user=request.user).order_by("-created_at")
    default_address=addersses.filter(is_default=True).first()
    
    profile=request.user
    buy_now = variant_id is not None    
    subtotal=0
    if buy_now:
        variant = get_object_or_404(ProductVariant.objects.select_related("product"),id=variant_id)
        items=[{"variant":variant,"quantity":1,"subtotal":variant.discounted_price}]
        
    else:
        items=CartItem.objects.filter(cart__user=request.user).select_related("variant","variant__product")
        if not items.exists():
            messages.error(request, "It's empty.")
            return redirect("product_list")


        for item in items:         
            subtotal+=item.variant.discounted_price*item.quantity

    if request.method=="POST":
        checkout_errors = []

        payment_method = request.POST.get("payment_method")
        

        if not buy_now:
            for item in items:
                variant=item.variant
                if not variant.product.category.is_active:
                   checkout_errors.append({"name": variant.product.name,"message": "Category is unavailable."})
            
                if not variant.product.is_active:
                    checkout_errors.append({"name": variant.product.name,"message": "Product is unavailable."})
            
                if not variant.is_active:
                    checkout_errors.append({"name": variant.product.name,"color": variant.color,"size": variant.size,"message": "Variant is unavailable."})
            
                if item.quantity >variant.stock:
                    checkout_errors.append({"name": variant.product.name,"color": variant.color,"size": variant.size,"stock": variant.stock})
                
        else:
            if not variant.product.category.is_active:
                checkout_errors.append({"name": variant.product.name,"message": "Category is unavailable."})

            if not variant.product.is_active:
                checkout_errors.append({"name": variant.product.name,"message": "Product is unavailable."})


            if not variant.is_active:
                checkout_errors.append({"name": variant.product.name,"color": variant.color,"size": variant.size,"message": "Variant is unavailable."})

            if variant.stock < 1:
                checkout_errors.append({"name": variant.product.name,"color": variant.color,"size": variant.size,"stock": variant.stock,})
        if checkout_errors:
            return render(request,"checkout/checkout.html",{"details": profile,"items": items,"buy_now": bool(buy_now),"subtotal": subtotal,"default_address": default_address,"addresses": addersses,"checkout_errors": checkout_errors,})

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


            elif not district.replace(" ", "").isalpha():
                address_errors["district"] = "District must contain only letters."


            if not state:
                address_errors["state"] = "State is required."


            elif not state.replace(" ", "").isalpha():
                address_errors["state"] = "State must contain only letters."


            if not country:
                address_errors["country"] = "Country is required."


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


        elif not shipping_state.replace(" ", "").isalpha():
            errors["shipping_state"] = "State must contain only letters."

        if not shipping_district:
            errors["shipping_district"] = "District is required."


        elif not shipping_district.replace(" ", "").isalpha():
            errors["shipping_district"] = "District must contain only letters."

        if not shipping_country:
            errors["shipping_country"] = "Country is required."


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

            elif not billing_state.replace(" ", "").isalpha():
                errors["billing_state"] = "State must contain only letters."

            if not billing_district:
                errors["billing_district"] = "District is required."

            elif not billing_district.replace(" ", "").isalpha():
                errors["billing_district"] = "District must contain only letters."

            if not billing_country:
                errors["billing_country"] = "Country is required."

   
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
            if variant.stock < 1:
                 checkout_errors = [{"name": variant.product.name,"color": variant.color,"size": variant.size,"stock": variant.stock,}]

                 return render( request,"checkout/checkout.html",{"details": profile,"items": items,"buy_now": True,"subtotal": subtotal,"default_address": default_address,"addresses": addersses,"checkout_errors": checkout_errors,},)

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
        
        if payment_method == "cod":
            Payment.objects.create(order=order,payment_method="cod",amount=final_amount,currency="INR",status="pending",)
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

            order.payment_status='pending'
            order.save(update_fields=['payment_status'])
            return redirect('success',order_id=order.id)
        elif payment_method == "wallet":
            Payment.objects.create(order=order,payment_method="wallet",amount=final_amount,currency="INR",status="paid",)
            order.payment_status = "paid"
            order.save(update_fields=["payment_status"])
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

            order.payment_status='pending'
            order.save(update_fields=['payment_status'])
            return redirect('success',order_id=order.id)
        elif payment_method == "razorpay":
            if buy_now:
                OrderItems.objects.create(order=order,variant=variant,quantity=1,unit_amount=variant.discounted_price)
                
            else:
                for item in items:
                    variant=item.variant
                    OrderItems.objects.create(order=order,variant=item.variant,quantity=item.quantity,unit_amount=item.variant.discounted_price)
                   
            client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
            
            razorpay_order = client.order.create({"amount": int(final_amount * 100),"currency": "INR","payment_capture": 1,})

            Payment.objects.create(order=order,payment_method="razorpay",amount=final_amount,currency="INR",status="pending",razorpay_order_id=razorpay_order["id"],)
           
            order.payment_status = "pending"
            order.save(update_fields=["payment_status"])
            return JsonResponse({"status": "razorpay","razorpay_key": settings.RAZORPAY_KEY_ID,"razorpay_order_id": razorpay_order["id"],"amount": int(final_amount * 100),"order_id": order.id,})


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
        item.pending_return = (item.returns.filter(status="pending").aggregate(total=Sum("quantity"))["total"] or 0)
        item.approved_return = (item.returns.filter(status="approved").aggregate(total=Sum("quantity"))["total"] or 0)
        item.available_return = (item.quantity- item.pending_return- item.approved_return)
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
        if order.status =="cancelled":
            return redirect("order_details",order_id=order.id)
        reason=request.POST.get("reason")
        description=request.POST.get("description")

        
        OrderCancellation.objects.create(order=order,reason=reason,description=description)
        order.status="cancelled"
        order.save(update_fields=["status"])
        
        OrderTrack.objects.get_or_create(order=order,status='cancelled')
        for item in order_items:
            cancelled_qty = item.cancellation.aggregate(total=Sum("quantity"))["total"] or 0

            remaining_qty = item.quantity - cancelled_qty

            if remaining_qty > 0:
                item.variant.stock += remaining_qty
                item.variant.save()

            item.status = "cancelled"
            item.save(update_fields=["status"])
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


@login_required(login_url='login')
def return_product(request,item_id):
    
    order_item = get_object_or_404( OrderItems,id=item_id,order__user=request.user,)

    if request.method == "POST":

        quantity = int(request.POST.get("quantity"))
        reason = request.POST.get("reason")
        description = request.POST.get("description")

        OrderItemReturn.objects.create(order_item=order_item,quantity=quantity,reason=reason,description=description,)

        
        return redirect('order_details',order_id=order_item.order.id)

    return redirect("order_details", order_id=order_item.order.id)


@login_required(login_url="login")
def download_invoice(request, order_id):

    # =========================================================
    # GET ORDER
    # =========================================================
    #
    # order.id is used ONLY internally to find the database row.
    # It will NOT be displayed in the invoice.
    #
    order = get_object_or_404(
        Orders.objects.select_related("user"),
        id=order_id,
        user=request.user
    )

 
    frontend_order_id = order.order_id


    items = (
        OrderItems.objects
        .filter(order=order)
        .select_related(
            "variant",
            "variant__product"
        )
    )


    billing = OrderAddress.objects.filter(
        order=order,
        address_type="billing"
    ).first()

    # =========================================================
    # SHIPPING ADDRESS
    # =========================================================

    shipping = OrderAddress.objects.filter(
        order=order,
        address_type="shipping"
    ).first()

    # =========================================================
    # PDF RESPONSE
    # =========================================================

    response = HttpResponse(
        content_type="application/pdf"
    )

    # IMPORTANT:
    # Use frontend order_id, NOT database id.
    response["Content-Disposition"] = (
        f'attachment; filename="Invoice_{frontend_order_id}.pdf"'
    )

    # =========================================================
    # PDF DOCUMENT
    # =========================================================

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,

        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,

        title=f"Nova Style Invoice {frontend_order_id}",
        author="Nova Style",
    )

    # =========================================================
    # STYLES
    # =========================================================

    styles = getSampleStyleSheet()

    # ---------------------------------------------------------
    # BRAND
    # ---------------------------------------------------------

    brand_style = ParagraphStyle(
        "Brand",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=24,
        textColor=colors.HexColor("#111111"),
        alignment=0,
    )


    brand_subtitle_style = ParagraphStyle(
        "BrandSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#666666"),
        alignment=0,
    )

 
    invoice_title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=23,
        textColor=colors.HexColor("#111111"),
        alignment=2,
    )


    normal_style = ParagraphStyle(
        "NormalInvoice",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#333333"),
    )


    small_style = ParagraphStyle(
        "SmallInvoice",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#666666"),
    )

    bold_style = ParagraphStyle(
        "BoldInvoice",
        parent=normal_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#111111"),
    )

    

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=0,
    )

    table_header_center_style = ParagraphStyle(
        "TableHeaderCenter",
        parent=table_header_style,
        alignment=1,
    )

    table_header_right_style = ParagraphStyle(
        "TableHeaderRight",
        parent=table_header_style,
        alignment=2,
    )


    product_name_style = ParagraphStyle(
        "ProductName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#111111"),
    )

    product_detail_style = ParagraphStyle(
        "ProductDetail",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#777777"),
    )

 
    total_label_style = ParagraphStyle(
        "TotalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#111111"),
        alignment=2,
    )

    total_value_style = ParagraphStyle(
        "TotalValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#111111"),
        alignment=2,
    )

 
    def money(value):
        """
        Currency formatting.

        Using Rs. instead of ₹ because standard Helvetica
        does not reliably support the rupee character.
        """
        return f"Rs. {value:,.2f}"

    def create_address(address):

        if not address:
            return Paragraph(
                "Address not available",
                normal_style
            )

        name = escape(str(address.name or ""))
        phone = escape(str(address.phone or ""))
        street = escape(str(address.address or ""))
        district = escape(str(address.district or ""))
        state = escape(str(address.state or ""))
        country = escape(str(address.country or ""))
        postal_code = escape(str(address.postal_code or ""))

        address_content = f"""
        <b>{name}</b><br/>
        {phone}<br/>
        {street}<br/>
        {district}, {state}<br/>
        {country} - {postal_code}
        """

        return Paragraph(
            address_content,
            normal_style
        )


    story = []

  
    header_left = [
        Paragraph(
            "NOVA STYLE",
            brand_style
        ),

        Spacer(1, 2),

        Paragraph(
            "FASHION • STYLE • CONFIDENCE",
            brand_subtitle_style
        ),
    ]

    header_right = [
        Paragraph(
            "INVOICE",
            invoice_title_style
        ),

        Spacer(1, 3),

        Paragraph(
            f"<b>Invoice #</b> "
            f"{escape(str(frontend_order_id))}",
            normal_style
        ),

        Paragraph(
            f"<b>Date:</b> "
            f"{order.created_at.strftime('%d %b %Y')}",
            normal_style
        ),
    ]

    header_table = Table(
        [[
            header_left,
            header_right
        ]],
        colWidths=[
            100 * mm,
            70 * mm
        ],
    )

    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),

            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )

    story.append(header_table)

    story.append(
        Spacer(1, 7)
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#222222"),
            spaceBefore=0,
            spaceAfter=10,
        )
    )

    # =========================================================
    # ORDER INFORMATION
    # =========================================================

    order_status = str(
        order.status or ""
    ).replace("_", " ").title()

    order_info = Table(
        [
            [
                Paragraph(
                    "<b>Customer</b>",
                    small_style
                ),

                Paragraph(
                    "<b>Order ID</b>",
                    small_style
                ),

                Paragraph(
                    "<b>Order Date</b>",
                    small_style
                ),

                Paragraph(
                    "<b>Status</b>",
                    small_style
                ),
            ],

            [
                Paragraph(
                    escape(str(order.user.name or "")),
                    normal_style
                ),

                # IMPORTANT:
                # order.order_id, NOT order.id
                Paragraph(
                    f"#{escape(str(frontend_order_id))}",
                    normal_style
                ),

                Paragraph(
                    order.created_at.strftime(
                        "%d %b %Y"
                    ),
                    normal_style
                ),

                Paragraph(
                    escape(order_status),
                    normal_style
                ),
            ],
        ],

        colWidths=[
            50 * mm,
            35 * mm,
            45 * mm,
            40 * mm,
        ],
    )

    order_info.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#F5F5F5")
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D8D8D8")
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.3,
                colors.HexColor("#E5E5E5")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
        ])
    )

    story.append(order_info)

    story.append(
        Spacer(1, 11)
    )


    billing_box = [
        Paragraph(
            "BILLING DETAILS",
            bold_style
        ),

        Spacer(1, 4),

        create_address(billing),
    ]

    shipping_box = [
        Paragraph(
            "SHIPPING ADDRESS",
            bold_style
        ),

        Spacer(1, 4),

        create_address(shipping),
    ]

    address_table = Table(
        [[
            billing_box,
            shipping_box
        ]],
        colWidths=[
            85 * mm,
            85 * mm
        ],
    )

    address_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#FAFAFA")
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D8D8D8")
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D8D8D8")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )

    story.append(address_table)

    story.append(
        Spacer(1, 12)
    )

    # =========================================================
    # ITEMS TABLE
    # =========================================================

    item_rows = []

    # Header
    item_rows.append([
        Paragraph(
            "ITEM",
            table_header_style
        ),

        Paragraph(
            "DESCRIPTION",
            table_header_style
        ),

        Paragraph(
            "QTY",
            table_header_center_style
        ),

        Paragraph(
            "UNIT PRICE",
            table_header_right_style
        ),

        Paragraph(
            "TOTAL",
            table_header_right_style
        ),
    ])

    total = 0

    # =========================================================
    # PRODUCTS
    # =========================================================

    for index, item in enumerate(items, start=1):

        line_total = (
            item.quantity *
            item.unit_amount
        )

        total += line_total

        product_name = escape(
            str(item.variant.product.name or "")
        )

        product_size = escape(
            str(
                getattr(
                    item.variant,
                    "size",
                    None
                ) or "N/A"
            )
        )

        description = Paragraph(
            f"""
            <b>{product_name}</b><br/>
            <font size="7.5" color="#777777">
            Size: {product_size}
            </font>
            """,
            product_name_style
        )

        item_rows.append([
            Paragraph(
                str(index),
                normal_style
            ),

            description,

            Paragraph(
                str(item.quantity),
                normal_style
            ),

            Paragraph(
                money(item.unit_amount),
                normal_style
            ),

            Paragraph(
                money(line_total),
                normal_style
            ),
        ])

    # =========================================================
    # ITEMS TABLE
    # =========================================================

    items_table = Table(
        item_rows,

        colWidths=[
            25 * mm,
            70 * mm,
            18 * mm,
            30 * mm,
            27 * mm,
        ],

        repeatRows=1,
    )

    items_table.setStyle(
        TableStyle([
            # -------------------------------------------------
            # HEADER
            # -------------------------------------------------

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#181818")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            # -------------------------------------------------
            # BODY ALTERNATING ROWS
            # -------------------------------------------------

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#FAFAFA")
                ]
            ),

            # -------------------------------------------------
            # BORDER
            # -------------------------------------------------

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D8D8D8")
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.3,
                colors.HexColor("#E5E5E5")
            ),

            # -------------------------------------------------
            # ALIGNMENT
            # -------------------------------------------------

            (
                "ALIGN",
                (2, 1),
                (2, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (3, 1),
                (4, -1),
                "RIGHT"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            # -------------------------------------------------
            # PADDING
            # -------------------------------------------------

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    story.append(items_table)

    story.append(
        Spacer(1, 5)
    )

    # =========================================================
    # TOTALS
    # =========================================================

    subtotal = total

    totals_data = [
        [
            "",
            Paragraph(
                "Subtotal",
                normal_style
            ),

            Paragraph(
                money(subtotal),
                normal_style
            ),
        ],

        [
            "",
            Paragraph(
                "Shipping",
                normal_style
            ),

            Paragraph(
                "Free",
                normal_style
            ),
        ],

        [
            "",
            Paragraph(
                "TOTAL",
                total_label_style
            ),

            Paragraph(
                money(total),
                total_value_style
            ),
        ],
    ]

    totals_table = Table(
        totals_data,

        colWidths=[
            85 * mm,
            45 * mm,
            40 * mm,
        ],
    )

    totals_table.setStyle(
        TableStyle([
            (
                "ALIGN",
                (1, 0),
                (-1, -1),
                "RIGHT"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LINEABOVE",
                (1, 2),
                (-1, 2),
                1.2,
                colors.HexColor("#111111")
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    story.append(totals_table)

    story.append(
        Spacer(1, 9)
    )

    # =========================================================
    # PAYMENT / ORDER INFORMATION
    # =========================================================

    payment_box = Table(
        [
            [
                Paragraph(
                    "PAYMENT & ORDER INFORMATION",
                    bold_style
                )
            ],

            [
                Paragraph(
                    f"""
                    Invoice generated for Order
                    <b>#{escape(str(frontend_order_id))}</b>.<br/>
                    Order Status:
                    <b>{escape(order_status)}</b><br/>
                    Thank you for shopping with Nova Style.
                    """,
                    normal_style
                )
            ],
        ],

        colWidths=[
            170 * mm
        ],
    )

    payment_box.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#F5F5F5")
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.HexColor("#FCFCFC")
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D8D8D8")
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    story.append(payment_box)

    story.append(
        Spacer(1, 12)
    )

    # =========================================================
    # FOOTER LINE
    # =========================================================

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#CCCCCC"),
            spaceBefore=2,
            spaceAfter=6,
        )
    )


    footer = Table(
        [
            [
                Paragraph(
                    """
                    <b>NOVA STYLE</b><br/>
                    Thank you for choosing us.
                    """,
                    small_style
                ),

                Paragraph(
                    """
                    This is a computer-generated invoice.<br/>
                    No signature is required.
                    """,
                    small_style
                ),
            ]
        ],

        colWidths=[
            85 * mm,
            85 * mm,
        ],
    )

    footer.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "ALIGN",
                (1, 0),
                (1, 0),
                "RIGHT"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                0
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                0
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                0
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
        ])
    )

    story.append(footer)


    doc.build(story)

    return response

@login_required(login_url="login")
def verify_razorpay_payment(request):

    try:
        data = json.loads(request.body)

        order_id = data.get("order_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not all([
            order_id,
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        ]):
            return JsonResponse({
                "status": "failed",
                "message": "Missing payment information."
            }, status=400)

        order = get_object_or_404(
            Orders,
            id=order_id,
            user=request.user
        )

        payment = get_object_or_404(Payment,order=order,razorpay_order_id=razorpay_order_id)
      
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        payment.status = "paid"

        payment.save(
            update_fields=[
                "status"
            ]
        )

        order.payment_status = "paid"

        order.save(
            update_fields=[
                "payment_status"
            ]
        )

        return JsonResponse({
            "status": "success",
            "redirect_url": reverse(
                "success",
                args=[order.id]
            )
        })

    except razorpay.errors.SignatureVerificationError:

        return JsonResponse({
            "status": "failed",
            "message": "Payment verification failed."
        }, status=400)

    except Exception as e:

        print("VERIFY PAYMENT ERROR:", e)

        return JsonResponse({
            "status": "failed",
            "message": "Unable to verify payment."
        }, status=500)
@login_required(login_url="login")
def razorpay_payment_failed(request):

    try:
        data = json.loads(request.body)

        order_id = data.get("order_id")

        if not order_id:
            return JsonResponse({
                "status": "failed",
                "message": "Order ID is required."
            }, status=400)

        order = get_object_or_404(
            Orders,
            id=order_id,
            user=request.user
        )

        payment = get_object_or_404(
            Payment,
            order=order
        )

        payment.status = "failed"

        payment.save(
            update_fields=["status"]
        )

        order.payment_status = "failed"

        order.save(
            update_fields=["payment_status"]
        )

       
        return JsonResponse({
            "status": "failed",
            "message": "Payment failed.",
            "redirect_url": reverse(
                "payment_failed",
                args=[order.id]
            )
        })

    except Exception as e:

        print("PAYMENT FAILED ERROR:", e)

        return JsonResponse({
            "status": "failed",
            "message": "Unable to process failed payment."
        }, status=500)
    
@login_required(login_url="login")
def payment_failed(request, order_id):

    order = get_object_or_404(
        Orders,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "checkout/payment_failed.html",
        {
            "order": order,
        })

@login_required(login_url="login")
def retry_payment(request, order_id):

    order = get_object_or_404(
        Orders,
        id=order_id,
        user=request.user)

    if order.payment_status == "paid":
        return JsonResponse({
            "status": "already_paid",
            "message": "This order is already paid."
        })

    amount = order.final_amount

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({"amount": int(amount * 100),"currency": "INR","payment_capture": 1,})
    Payment.objects.create(order=order,payment_method="razorpay",amount=amount,currency="INR",status="pending",razorpay_order_id=razorpay_order["id"],)
    order.payment_status = "pending"
    order.save(update_fields=["payment_status"])
    return JsonResponse({"status": "razorpay","razorpay_key":settings.RAZORPAY_KEY_ID,"razorpay_order_id":razorpay_order["id"],"amount":int(amount * 100),"order_id":order.id,})