from django.db import models
from user.models import Users
# Create your models here.
from product.models import ProductVariant

class Cart(models.Model):
    user=models.OneToOneField(Users,on_delete=models.CASCADE,related_name="cart")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table="cart"

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    quantity=models.PositiveBigIntegerField(default=1)

    class Meta:
        db_table="cartitem"
        constraints=[models.UniqueConstraint(fields=["cart","variant"],name="unique_cart_variant")]