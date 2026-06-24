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

    def __str__(self):
        return self.name
        


class Products(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table="products"

class ProductVariant(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE,related_name="variants")
    size=models.CharField(max_length=50)
    color=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    offer=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    class Meta:
        db_table="productvariant"
        unique_together=("product","size","color")
    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"
    
    @property
    def orginal_price(self):
        return self.price
    
    @property
    def final_price(self):
        price=Decimal(self.price)
        category_offer=Decimal(self.product.category.offer or 0)
        variant_offer=Decimal(self.offer or 0)
        price=price-(price*category_offer/Decimal("100"))
        price=price-(price*variant_offer/Decimal("100"))
        return price.quantize(Decimal("0.01"))
    
    @property
    def discount_percentage(self):
        return self.offer 

class ProductImage(models.Model):
    variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name="images")
    image=models.ImageField(upload_to="products/")
    is_primary=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table="productimage"

    def __str__(self):
        return f"image for {self.variant}"


class Review(models.Model):
    user=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='reviews')
    product=models.ForeignKey(Products,on_delete=models.CASCADE,related_name="reviews")
    rating=models.IntegerField()
    title=models.CharField(max_length=50)
    comment=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="review"

    def __str__(self):
        return f"{self.user.name}"
    