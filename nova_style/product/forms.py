from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    offer = forms.DecimalField(required=False)
    class Meta:
        model = Category
        fields = ["name", "image_url", "offer", ]
        error_messages={"name":{"required":"name is required."},'image_url':{"required":"image is required."}}