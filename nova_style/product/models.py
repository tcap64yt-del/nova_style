from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from user.models import Users
import re
class Category(models.Model):
    name=models.CharField(max_length=255)
    image_url=models.ImageField(upload_to="category/")
    offer=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="category"


class Products(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    class Meta:
        db_table="products"

class ProductVariant(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE,related_name="variants")
    size=models.CharField(max_length=50)
    color=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    offer=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    class Meta:
        db_table="productvariant"
        unique_together=("product","size","color")
   
    @property
    def orginal_price(self):
        return self.price
    
    @property
    def variant_offer_active(self):
        if not self.offer:
            return False
        today=timezone.now().date()
        if self.start_date and today <self.start_date:
            return False
        if self.end_date and today >self.end_date:
            return False

        return True
    @property
    def discounted_price(self):
        price=self.price

        if self.product.category.offer:
            price=price-(price*self.product.category.offer/Decimal("100"))
        if self.variant_offer_active:
            price=price-(price * self.offer /Decimal("100"))
        return round(price,2)
    
    @property
    def total_offer(self):
        offer=Decimal("0")
        if self.product.category.offer:
            offer+=self.product.category.offer
        if self.variant_offer_active:
            offer+=self.offer
        return offer
    


class ProductImage(models.Model):
    variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name="images")
    image=models.ImageField(upload_to="products/")
    is_primary=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table="productimage"


class Review(models.Model):
    user=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='reviews')
    product=models.ForeignKey(Products,on_delete=models.CASCADE,related_name="reviews")
    rating=models.IntegerField()
    title=models.CharField(max_length=50)
    comment=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="review"

