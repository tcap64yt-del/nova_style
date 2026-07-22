from django.db import models
from user.models import Users
from product.models import ProductVariant
# Create your models here.


class Orders(models.Model):
    STATUS_CHOICES=[
        ("pending", "Pending"),
        ("order placed", "Order Placed"),
        ("shipped", "Shipped"), 
        ("out for delivery", "Out for delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("return pending", "Return Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ]

    user=models.ForeignKey(Users,on_delete=models.CASCADE,related_name="orders")
    final_amount=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending",)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="orders"

    def __str__(self):
        return f"order {self.id}"
    
class OrderAddress(models.Model):
    ADDRESS_TYPE_CHOICES=[
        ("billing", "Billing"),
        ("shipping", "Shipping"),
        ]
    
    order=models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="addresses")
    name = models.CharField(max_length=255)
    address_type=models.CharField(max_length=20,choices=ADDRESS_TYPE_CHOICES,)
    phone=models.CharField(max_length=10)
    address=models.TextField()
    state = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    country = models.CharField(max_length=355)
    postal_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_addresses"
        constraints = [
        models.UniqueConstraint(
            fields=["order", "address_type"],
            name="unique_order_address_type")]  
    
    def __str__(self):
        return f"{self.id}"
    
class OrderItems(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
    ]
    order=models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="items")
    variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name="order_items")
    quantity=models.PositiveIntegerField()
    unit_amount=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="active",)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="order_items"
        constraints = [
        models.UniqueConstraint(
            fields=["order", "variant"],
            name="unique_order_variant")]

    
    
class OrderTrack(models.Model):
    order=models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="tracks")
    status=models.CharField(max_length=255,choices=Orders.STATUS_CHOICES)
    status_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="order_track"
   
        
class OrderCancellation(models.Model):
    order = models.OneToOneField(Orders,on_delete=models.CASCADE,related_name="cancellation")
    reason = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_cancellations"

   
    
class OrderItemCancellation(models.Model):
    order_item=models.ForeignKey(OrderItems,on_delete=models.SET_NULL,null=True,related_name="cancellation")
    quantity=models.PositiveIntegerField()
    reason=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_item_cancellation"

class OrderReturns(models.Model):
    STATUS_CHOICES = [("approved", "Approved"),("rejected", "Rejected"),("pending", "Pending"),]

    order = models.OneToOneField(Orders,on_delete=models.CASCADE,related_name="returns")
    reason = models.CharField(max_length=255)
   
    description = models.TextField(blank=True, null=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending",)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_returns"

   