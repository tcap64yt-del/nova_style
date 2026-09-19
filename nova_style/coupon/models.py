from django.db import models
from user.models import Users
from order.models import Orders
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(max_length=100, unique=True)

    discount_type = models.CharField( max_length=20,choices=DISCOUNT_TYPE_CHOICES)

    discount_value = models.DecimalField(max_digits=10,decimal_places=2)

    min_order_amount = models.DecimalField(max_digits=10,decimal_places=2)
    max_discount = models.DecimalField(max_digits=10,decimal_places=2)
    max_usage = models.PositiveIntegerField()
    usage_remaining = models.PositiveIntegerField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        db_table="coupons"

class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE,related_name="usages")
    user=models.ForeignKey(Users,on_delete=models.CASCADE,related_name="coupon_usages")
    order = models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="coupon_usage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                name="unique_coupon_per_order"
            ),
            models.UniqueConstraint(
            fields=["coupon", "user"],
            name="unique_coupon_per_user"
        )
        ]

        db_table="coupon_usages"

class UserCoupon(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,related_name="user_coupons")
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE,related_name="assigned_users")
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "user_coupons"